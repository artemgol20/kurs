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
MINE_SPEED = 1.2  # Увеличиваем базовую скорость
START_DELAY = 180
MIN_SPAWN_DISTANCE = 300
ENEMY_REACTION_TIME = 60  # Частота стрельбы врага (в кадрах)

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
        # Параметры для спирального движения
        self.spiral_angle = self.phi
        self.spiral_radius = self.r0
        # История позиций для следа
        self.trail = []
        self.max_trail_length = 300  # Максимальная длина следа



    def move(self, target, leader=None, strategy_id=0):
        # Сохраняем текущую позицию в историю
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        dx = target[0] - self.x
        dy = target[1] - self.y
        base_angle = math.atan2(dy, dx)
        dist = math.hypot(dx, dy)

        if strategy_id == 0:  # Жадный алгоритм
            self.tick += 1
            params = STRATEGY_PARAMS["greedy"]
            self.angle = base_angle
            self.speed = MINE_SPEED * params["speed_multiplier"]
        
        elif strategy_id == 1:  # Зигзагообразное движение
            self.tick += 1
            params = STRATEGY_PARAMS["zigzag"]
            self.angle = base_angle + math.sin(self.tick / params["period"]) * params["amplitude"]
            self.speed = MINE_SPEED * params["speed_multiplier"]
    
        elif strategy_id == 2:  # Spiral Approach via radial+angular
            self.tick += 1
            self.speed = MINE_SPEED * 2.0 
            params = STRATEGY_PARAMS["spiral"]
            # Вектор от текущей позиции к цели
            dx = target[0] - self.x
            dy = target[1] - self.y
            dist = math.hypot(dx, dy) or 1

            # Единичный радиальный вектор
            ux, uy = dx/dist, dy/dist
            # Единичный тангенциальный вектор (перпендикулярно радиальному)
            tx, ty = -uy, ux

            # Задаём компоненты скорости
            vr = 1.5   # внутрь
            vt = 3.0  # вокруг

            # Получаем результирующую скорость
            vx = ux * vr + tx * vt
            vy = uy * vr + ty * vt

            # Масштабируем так, чтобы общая скорость была MINE_SPEED
            vnorm = math.hypot(vx, vy) or 1
            vx *= self.speed / vnorm
            vy *= self.speed / vnorm

            # Смещаем мину
            self.x += vx
            self.y += vy
            return

        # elif strategy_id == 2:
        #     self.speed = MINE_SPEED * 0.03  # Уменьшаем базовую скорость
            
        #     # параметры спирали
        #     b = STRATEGY_PARAMS["spiral"]["speed_multiplier"] * 0.2  # Уменьшаем скорость закрутки
        #     dphi = STRATEGY_PARAMS["spiral"]["spiral_factor"] * 0.1  # Уменьшаем изменение угла

        #     # вычисляем угол и радиус по формуле
        #     phi = self.phi + self.tick * dphi
        #     r = self.spiral_radius * math.exp(-b * (self.tick * dphi))
        #     print(r)
        #     # обновляем координаты относительно цели
        #     self.x = target[0] + r * math.cos(phi)
        #     self.y = target[1] + r * math.sin(phi)
        #     self.tick += 1
        #     return
        
        elif strategy_id == 3:  # Фланговая атака
            self.tick += 1
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
            self.tick += 1
            
        elif strategy_id == 6:  # Спиральный зигзаг
            params = STRATEGY_PARAMS["spiral_zigzag"]
            self.speed = MINE_SPEED * params["speed_multiplier"]
            
            # Используем сохраненные начальные параметры
            if not hasattr(self, 'initial_angle'):
                self.initial_angle = math.atan2(self.y - target[1], self.x - target[0])
                self.initial_radius = math.hypot(self.x - target[0], self.y - target[1])
            
            # Вычисляем текущий угол относительно цели
            current_angle = math.atan2(self.y - target[1], self.x - target[0])
            # Вычисляем текущее расстояние до цели
            current_radius = math.hypot(self.x - target[0], self.y - target[1])
            
            # Вычисляем новый угол с учетом спирального движения
            spiral_factor = getattr(self, 'spiral_factor', params["spiral_factor"])
            new_angle = self.initial_angle + (self.tick * 0.02)  # Постепенное увеличение угла
            
            # Вычисляем новый радиус с учетом спирального затухания
            new_radius = self.initial_radius * math.exp(-spiral_factor * (self.tick * 0.02))
            
            # Добавляем зигзагообразное движение
            zigzag_amplitude = getattr(self, 'zigzag_amplitude', params["zigzag_amplitude"])
            phase_change = getattr(self, 'phase_change', params["phase_change"])
            self.zigzag_phase += phase_change
            
            # Вычисляем смещение от зигзага
            dx_zigzag = zigzag_amplitude * math.sin(self.zigzag_phase) * math.cos(new_angle + math.pi/2)
            dy_zigzag = zigzag_amplitude * math.sin(self.zigzag_phase) * math.sin(new_angle + math.pi/2)
            
            # Обновляем позицию с учетом зигзага
            self.x = target[0] + new_radius * math.cos(new_angle) + dx_zigzag
            self.y = target[1] + new_radius * math.sin(new_angle) + dy_zigzag
            self.tick += 1
            return
        

       


        if strategy_id != 6:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed

    def draw(self, screen):
        if self.alive:
            # Отрисовка следа
            if len(self.trail) > 1:
                # Создаем градиент от прозрачного к основному цвету
                for i in range(len(self.trail) - 1):
                    alpha = int(255 * (i + 1) / len(self.trail))
                    color = (0, 120, 255, alpha)
                    pygame.draw.line(screen, color, 
                                   (int(self.trail[i][0]), int(self.trail[i][1])),
                                   (int(self.trail[i+1][0]), int(self.trail[i+1][1])), 2)

            # Отрисовка мины
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