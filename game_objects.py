import pygame
import math
import random
from config import *

# Настройки окна
WIDTH, HEIGHT = 1200, 800
BG_COLOR = (30, 30, 30)
MINE_COLOR = (0, 120, 255)
ENEMY_COLOR = (200, 50, 50)
MINE_RADIUS = 5
ENEMY_RADIUS = 15
MINE_DETECT_RADIUS = 40
ENEMY_DETECT_RADIUS = 150
BULLET_SPEED = 7
MINE_SPEED = 0.8
START_DELAY = 180
MIN_SPAWN_DISTANCE = 300
ENEMY_REACTION_TIME = 45

class Bullet:
    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        dx, dy = target[0] - x, target[1] - y
        dist = math.hypot(dx, dy)
        self.vx = BULLET_SPEED * dx / dist
        self.vy = BULLET_SPEED * dy / dist
        self.radius = 5

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.radius)

class Mine:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.tick = 0
        self.angle = 0
        self.speed = MINE_SPEED
        self.scout_discovered = False
        self.velocity = [0, 0]
        # Инициализация параметров для spiral_zigzag
        self.phi = math.atan2(y - HEIGHT//2, x - WIDTH//2)
        self.r0 = math.hypot(x - WIDTH//2, y - HEIGHT//2) or 1
        self.zigzag_phase = random.random() * 2 * math.pi

    def move(self, target, leader=None, strategy_id=0):
        self.tick += 1
        dx = target[0] - self.x
        dy = target[1] - self.y
        base_angle = math.atan2(dy, dx)
        dist = math.hypot(dx, dy)

        if strategy_id == 0:  # Жадный алгоритм
            self.angle = base_angle
            self.speed = MINE_SPEED * STRATEGY_PARAMS["greedy"]["speed_multiplier"]
        
        elif strategy_id == 1:  # Зигзагообразное движение
            params = STRATEGY_PARAMS["zigzag"]
            self.angle = base_angle + math.sin(self.tick / params["period"]) * params["amplitude"]
            self.speed = MINE_SPEED * params["speed_multiplier"]
        
        elif strategy_id == 2:  # Спиральное сближение
            params = STRATEGY_PARAMS["spiral"]
            self.speed = MINE_SPEED * params["speed_multiplier"]
            X0 = self.x - target[0]
            Y0 = self.y - target[1]
            if not hasattr(self, 'phi'):
                self.phi = math.atan2(Y0, X0)
                self.r0 = math.hypot(X0, Y0) or 1

            b = params["spiral_factor"]
            curr_r = math.hypot(X0, Y0)
            speed_factor = self.r0 / (curr_r + 1)
            delta_phi = self.speed * speed_factor / self.r0
            self.phi += delta_phi
            r = self.r0 * math.exp(-b * self.phi)
            self.x = target[0] + r * math.cos(self.phi)
            self.y = target[1] + r * math.sin(self.phi)
            
        elif strategy_id == 3:  # Фланговая атака
            params = STRATEGY_PARAMS["flank"]
            if self.x < target[0]:
                self.angle = base_angle + params["attack_angle"]
            else:
                self.angle = base_angle - params["attack_angle"]
            self.speed = MINE_SPEED * params["speed_multiplier"]
        
        elif strategy_id == 4:  # Случайный шум
            params = STRATEGY_PARAMS["random"]
            self.angle = base_angle + random.uniform(-params["noise_range"], params["noise_range"])
            self.speed = MINE_SPEED * params["speed_multiplier"]
            
        elif strategy_id == 5:  # Gathering
            params = STRATEGY_PARAMS["gathering"]
            self.angle = base_angle
            self.speed = MINE_SPEED * params["speed_multiplier"]
            
        elif strategy_id == 6:  # Спиральный зигзаг
            params = STRATEGY_PARAMS["spiral_zigzag"]
            self.speed = MINE_SPEED * params["speed_multiplier"]

            X0 = self.x - target[0]
            Y0 = self.y - target[1]

            if not hasattr(self, 'phi'):
                self.phi = math.atan2(Y0, X0)
                self.r0 = math.hypot(X0, Y0) or 1
                self.zigzag_phase = random.random() * 2 * math.pi

            b = params["spiral_factor"]
            curr_r = math.hypot(X0, Y0)
            speed_factor = self.r0 / (curr_r + 1)
            delta_phi = self.speed * speed_factor / self.r0
            self.phi += delta_phi
            r = self.r0 * math.exp(-b * self.phi)

            zigzag_amplitude = params["zigzag_amplitude"] * (curr_r / self.r0)
            self.zigzag_phase += params["phase_change"]

            dx_zigzag = zigzag_amplitude * (
                math.sin(self.zigzag_phase) * math.cos(self.phi + math.pi/2) +
                math.cos(self.zigzag_phase * 0.5) * math.sin(self.phi)
            )
            dy_zigzag = zigzag_amplitude * (
                math.sin(self.zigzag_phase) * math.sin(self.phi + math.pi/2) -
                math.cos(self.zigzag_phase * 0.5) * math.cos(self.phi)
            )

            micro_angle = random.uniform(-params["micro_angle_range"], params["micro_angle_range"])
            dx_micro = math.cos(self.phi + micro_angle) * params["micro_deviation"]
            dy_micro = math.sin(self.phi + micro_angle) * params["micro_deviation"]

            self.x = target[0] + r * math.cos(self.phi) + dx_zigzag + dx_micro
            self.y = target[1] + r * math.sin(self.phi) + dy_zigzag + dy_micro
            return

        if strategy_id != 6:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed

    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, MINE_COLOR, (int(self.x), int(self.y)), MINE_RADIUS)
            pygame.draw.circle(screen, (0, 150, 255), (int(self.x), int(self.y)), MINE_DETECT_RADIUS, 1)

class Enemy:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.bullets = []
        self.target_history = []
        self.last_shot_time = 0
        self.prediction_accuracy = 0.7
        self.max_history = 10

    def predict_target_position(self, mine):
        if len(self.target_history) < 2:
            return mine.x, mine.y

        dx = mine.x - self.target_history[-1][0]
        dy = mine.y - self.target_history[-1][1]
        
        predicted_x = mine.x + dx * self.prediction_accuracy
        predicted_y = mine.y + dy * self.prediction_accuracy
        
        return predicted_x, predicted_y

    def update(self, mines):
        current_time = pygame.time.get_ticks()
        
        closest = None
        min_dist = ENEMY_DETECT_RADIUS
        for mine in mines:
            if mine.alive:
                dist = math.hypot(mine.x - self.x, mine.y - self.y)
                if dist < min_dist:
                    closest = mine
                    min_dist = dist

        if closest:
            self.target_history.append((closest.x, closest.y))
            if len(self.target_history) > self.max_history:
                self.target_history.pop(0)

            if current_time - self.last_shot_time > ENEMY_REACTION_TIME * 16:
                target_x, target_y = self.predict_target_position(closest)
                deviation = random.uniform(-10, 10)
                target_x += deviation
                target_y += deviation
                self.bullets.append(Bullet(self.x, self.y, (target_x, target_y)))
                self.last_shot_time = current_time

    def draw(self, screen):
        pygame.draw.circle(screen, ENEMY_COLOR, (int(self.x), int(self.y)), ENEMY_RADIUS)
        pygame.draw.circle(screen, (255, 50, 50), (int(self.x), int(self.y)), ENEMY_DETECT_RADIUS, 1) 