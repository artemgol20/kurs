import pygame
import sys
import math
import random
from config import *
from game_objects import Mine, Enemy, Bullet
from settings_window import SettingsWindow

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

# Список стратегий для отображения
STRATEGY_NAMES = [
    "Жадный алгоритм (Greedy Attack)",
    "Зигзагообразное движение (Evasive Zigzag)",
    "Спиральное сближение (Spiral Approach)",
    "Фланговая атака (Flank Attack)",
    "Случайный шум (Random Perturbation)",
    "Gathering (Сбор в треугольнике)",
    "Спиральный зигзаг (Spiral Zigzag)"
]

def create_mine(spawn_type, index=0, total=1):
    if spawn_type == 1:  # На окружности
        # Фиксированный радиус окружности
        radius = 350
        # Угол для текущей мины (равномерно распределенный)
        angle = (2 * math.pi * index) / total
        # Вычисляем координаты на окружности
        x = WIDTH//2 + radius * math.cos(angle)
        y = HEIGHT//2 + radius * math.sin(angle)
        mine = Mine(x, y)
        
        # Разные начальные параметры для каждой мины
        if strategy_id in [2, 6]:  # Для спиральных стратегий
            # Инициализация параметров для спирального движения
            if strategy_id == 2:  # Спиральное сближение
                # Сохраняем начальный угол и радиус
                mine.phi = angle
                mine.r0 = radius
            else:  # Спиральный зигзаг
                mine.phi = angle
                mine.r0 = radius
                mine.zigzag_phase = random.random() * 2 * math.pi
                mine.spiral_factor = random.uniform(0.12, 0.18)
                mine.zigzag_amplitude = random.uniform(35, 45)
                mine.phase_change = random.uniform(0.08, 0.12)
        else:
            # Для других стратегий оставляем стандартные параметры
            mine.phi = angle
            mine.r0 = radius
            mine.zigzag_phase = random.random() * 2 * math.pi
            
        return mine
    else:  # Случайно вокруг
        while True:
            x = random.randint(50, WIDTH-50)
            y = random.randint(50, HEIGHT-50)
            # Проверяем расстояние до центра
            dist_to_center = math.hypot(x - WIDTH//2, y - HEIGHT//2)
            if dist_to_center >= MIN_SPAWN_DISTANCE:
                return Mine(x, y)

def create_triangle_mines():
    # Создаем равносторонний треугольник слева
    center_x = 150  # Фиксированная позиция слева
    center_y = HEIGHT // 2
    radius = 100  # Увеличиваем радиус треугольника
    
    mines = []
    for i in range(3):
        angle = i * (2 * math.pi / 3)  # 120 градусов между точками
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        mines.append(Mine(x, y))
    return mines


# Запуск окна настроек
settings = SettingsWindow()
settings_result = settings.run()

if not settings_result:
    pygame.quit()
    sys.exit()

num_mines = settings_result['num_mines']
strategy_id = settings_result['strategy_id']
spawn_type = settings_result['spawn_type']

pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Симуляция атаки мин")
font = pygame.font.SysFont("arial", 22)
big_font = pygame.font.SysFont("arial", 48, bold=True)

# Классы
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

    def draw(self):
        pygame.draw.circle(window, (255, 255, 0), (int(self.x), int(self.y)), self.radius)

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
            params = STRATEGY_PARAMS["greedy"]
            self.angle = base_angle
            self.speed = MINE_SPEED * params["speed_multiplier"]
        
        elif strategy_id == 1:  # Зигзагообразное движение
            params = STRATEGY_PARAMS["zigzag"]
            self.angle = base_angle + math.sin(self.tick / params["period"]) * params["amplitude"]
            self.speed = MINE_SPEED * params["speed_multiplier"]
        
        elif strategy_id == 2:  # Спиральное сближение
            self.speed = MINE_SPEED * 1.3
            # Сдвигаем координаты так, чтобы враг был центром спирали
            X0 = self.x - target[0]
            Y0 = self.y - target[1]
            
            # Используем сохраненные начальные параметры
            if not hasattr(self, 'phi'):
                self.phi = math.atan2(Y0, X0)
                self.r0 = math.hypot(X0, Y0) or 1
            else:
                # Восстанавливаем начальные параметры из сохраненных значений
                self.phi = self.phi
                self.r0 = self.r0

            # Параметр спирали (чем больше, тем плотнее скрутка)
            b = 0.2

            # Текущее расстояние до цели
            curr_r = math.hypot(X0, Y0)

            # Увеличиваем угол (скорость закрутки)
            # Чем ближе к цели, тем больше скорость
            speed_factor = self.r0 / (curr_r + 1)  # +1 чтобы избежать деления на 0
            delta_phi = self.speed * speed_factor / self.r0
            self.phi += delta_phi

            # Новое расстояние: r = r0 * exp(-b * phi)
            r = self.r0 * math.exp(-b * self.phi)

            # Обратно в декартовы, с центром в target
            self.x = target[0] + r * math.cos(self.phi)
            self.y = target[1] + r * math.sin(self.phi)
            return
            
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
            return

        if strategy_id not in [2, 6]:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed

    def draw(self, window):
        if self.alive:
            pygame.draw.circle(window, MINE_COLOR, (int(self.x), int(self.y)), MINE_RADIUS)
            pygame.draw.circle(window, (0, 150, 255), (int(self.x), int(self.y)), MINE_DETECT_RADIUS, 1)

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

    def draw(self, window):
        pygame.draw.circle(window, ENEMY_COLOR, (int(self.x), int(self.y)), ENEMY_RADIUS)
        pygame.draw.circle(window, (255, 50, 50), (int(self.x), int(self.y)), ENEMY_DETECT_RADIUS, 1)


# Создаем мины
if strategy_id == 5:  # Gathering
    mines = create_triangle_mines()
else:
    mines = [create_mine(spawn_type, i, num_mines) for i in range(num_mines)]
enemy = Enemy()
clock = pygame.time.Clock()
fps = 60
log = []
timer = 0
start_timer = 0
running = True

while running:
    window.fill(BG_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                fps = min(fps + 10, 300)
            elif event.key == pygame.K_DOWN:
                fps = max(fps - 10, 10)

    # Начальная задержка
    if start_timer < START_DELAY:
        start_timer += 1
        text = big_font.render(f"Подготовка к атаке... {3 - start_timer // 60}", True, (255, 255, 255))
        window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        clock.tick(fps)
        continue

    # Отображение названия стратегии
    strategy_text = font.render(f"Стратегия: {STRATEGY_NAMES[strategy_id]}", True, (255, 255, 255))
    window.blit(strategy_text, (WIDTH // 2 - strategy_text.get_width() // 2, 10))

    # Движение мин
    if strategy_id == 1:
        leader = mines[0] if mines else None
        for i, mine in enumerate(mines):
            if mine.alive:
                mine.move((enemy.x, enemy.y), leader if i > 0 else None, strategy_id)
    else:
        for mine in mines:
            if mine.alive:
                mine.move((enemy.x, enemy.y), strategy_id=strategy_id)

    # Обновление врага
    timer += 1
    if timer % ENEMY_REACTION_TIME == 0:  # Используем глобальную переменную
        enemy.update(mines)

    # Обновление пуль
    for bullet in enemy.bullets[:]:  # Создаем копию списка для безопасного удаления
        bullet.move()
        hit = False
        for mine in mines:
            if mine.alive and math.hypot(mine.x - bullet.x, mine.y - bullet.y) < MINE_RADIUS:
                mine.alive = False
                hit = True
                log.append("Враг уничтожил мину!")
                break
        if hit:
            enemy.bullets.remove(bullet)
        elif (bullet.x < 0 or bullet.x > WIDTH or 
              bullet.y < 0 or bullet.y > HEIGHT):
            enemy.bullets.remove(bullet)
            log.append("Враг промазал!")

    # Проверка победы мин
    for mine in mines:
        if mine.alive and math.hypot(mine.x - enemy.x, mine.y - enemy.y) < MINE_DETECT_RADIUS:
            text = big_font.render("Мины победили!", True, (0, 255, 0))
            window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit()

    # Проверка победы врага
    if all(not mine.alive for mine in mines):
        text = big_font.render("Враг победил!", True, (255, 0, 0))
        window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    # Отрисовка
    for mine in mines:
        if mine.alive:
            mine.draw(window)
    for bullet in enemy.bullets:
        bullet.draw()
    enemy.draw(window)

    fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
    count_text = font.render(f"Мин осталось: {sum(1 for m in mines if m.alive)}", True, (255, 255, 255))
    window.blit(fps_text, (10, 10))
    window.blit(count_text, (10, 40))

    # Лог попаданий
    for i, line in enumerate(log[-10:]):
        entry = font.render(line, True, (200, 200, 200))
        window.blit(entry, (WIDTH - 200, 20 + 20 * i))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
