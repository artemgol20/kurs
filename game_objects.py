import pygame
import math
import random

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
MINE_SPEED = 1.2
START_DELAY = 180
MIN_SPAWN_DISTANCE = 300
ENEMY_REACTION_TIME = 60

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

    def move(self, target, leader=None, strategy_id=0):
        self.tick += 1
        dx = target[0] - self.x
        dy = target[1] - self.y
        base_angle = math.atan2(dy, dx)
        dist = math.hypot(dx, dy)

        if strategy_id == 0:  # Жадный алгоритм
            self.angle = base_angle
        
        elif strategy_id == 1:  # Зигзагообразное движение
            self.angle = base_angle + math.sin(self.tick / 10) * 1.0
        
        elif strategy_id == 2:  # Спиральное сближение
            self.speed = MINE_SPEED * 1.3
            X0 = self.x - target[0]
            Y0 = self.y - target[1]
            if not hasattr(self, 'phi'):
                self.phi = math.atan2(Y0, X0)
                self.r0  = math.hypot(X0, Y0) or 1

            b = 0.2
            curr_r = math.hypot(X0, Y0)
            speed_factor = self.r0 / (curr_r + 1)
            delta_phi = self.speed * speed_factor / self.r0
            self.phi += delta_phi
            r = self.r0 * math.exp(-b * self.phi)
            self.x = target[0] + r * math.cos(self.phi)
            self.y = target[1] + r * math.sin(self.phi)
            
        elif strategy_id == 3:  # Фланговая атака
            if self.x < target[0]:
                self.angle = base_angle + math.pi / 4
            else:
                self.angle = base_angle - math.pi / 4
        
        elif strategy_id == 4:  # Случайный шум
            self.angle = base_angle + random.uniform(-1.0, 1.0)
            
        elif strategy_id == 5:  # Gathering
            self.angle = base_angle
            self.speed = MINE_SPEED * 1.5
            
        elif strategy_id == 6:  # Спиральный зигзаг
            self.speed = MINE_SPEED * 1.0
            X0 = self.x - target[0]
            Y0 = self.y - target[1]

            if not hasattr(self, 'phi'):
                self.phi = math.atan2(Y0, X0)
                self.r0  = math.hypot(X0, Y0) or 1

            b = 0.2
            curr_r = math.hypot(X0, Y0)
            speed_factor = self.r0 / (curr_r + 1)
            delta_phi = self.speed * speed_factor / self.r0
            self.phi += delta_phi
            r = self.r0 * math.exp(-b * self.phi)

            zigzag_amplitude = 20
            zigzag_frequency = 0.2

            dx_zigzag = zigzag_amplitude * math.cos(self.tick * zigzag_frequency) * math.cos(self.phi + math.pi/2)
            dy_zigzag = zigzag_amplitude * math.cos(self.tick * zigzag_frequency) * math.sin(self.phi + math.pi/2)

            self.x = target[0] + r * math.cos(self.phi) + dx_zigzag
            self.y = target[1] + r * math.sin(self.phi) + dy_zigzag
            return

        if strategy_id != 6:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed

class Enemy:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.bullets = []

    def update(self, mines):
        closest = None
        min_dist = ENEMY_DETECT_RADIUS
        for mine in mines:
            if mine.alive:
                dist = math.hypot(mine.x - self.x, mine.y - self.y)
                if dist < min_dist:
                    closest = mine
                    min_dist = dist
        if closest:
            self.bullets.append(Bullet(self.x, self.y, (closest.x, closest.y))) 