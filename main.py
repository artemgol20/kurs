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
START_DELAY = 60
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
                # Добавляем небольшое случайное отклонение для каждой мины
                mine.phi += random.uniform(-0.1, 0.1)
                mine.r0 *= random.uniform(0.95, 1.05)
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

# Создаем мины
if strategy_id == 5:  # Gathering
    mines = create_triangle_mines()
else:
    mines = [create_mine(spawn_type, i, num_mines) for i in range(num_mines)]

enemy = Enemy()
timer = 0
running = True
clock = pygame.time.Clock()
fps = 60

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_UP:
                fps = min(fps + 10, 300)
            elif event.key == pygame.K_DOWN:
                fps = max(fps - 10, 10)

    # Отрисовка
    window.fill(BG_COLOR)
    
    # Отрисовка мин
    for mine in mines:
        mine.draw(window)
    
    # Отрисовка врага
    enemy.draw(window)
    
    # Отрисовка пуль
    for bullet in enemy.bullets:
        bullet.draw(window)

    # Обновление
    if timer >= START_DELAY:
        # Движение мин
        if strategy_id == 1:
            leader = mines[0] if mines else None
            for i, mine in enumerate(mines):
                if mine.alive:
                    mine.move((enemy.x, enemy.y), leader if i > 0 else None, strategy_id=strategy_id)
        else:
            for mine in mines:
                if mine.alive:
                    mine.move((enemy.x, enemy.y), strategy_id=strategy_id)
        
        # Обновление врага
        enemy.update(mines)
        
        # Обновление пуль
        for bullet in enemy.bullets[:]:
            bullet.move()
            # Проверка столкновений
            for mine in mines:
                if mine.alive and math.hypot(bullet.x - mine.x, bullet.y - mine.y) < MINE_RADIUS + bullet.radius:
                    mine.alive = False
                    if bullet in enemy.bullets:
                        enemy.bullets.remove(bullet)
                    break
            # Удаление пуль за пределами экрана
            if (bullet.x < 0 or bullet.x > WIDTH or 
                bullet.y < 0 or bullet.y > HEIGHT):
                if bullet in enemy.bullets:
                    enemy.bullets.remove(bullet)

        # Проверка победы мин
        for mine in mines:
            if mine.alive and math.hypot(mine.x - enemy.x, mine.y - enemy.y) < MINE_DETECT_RADIUS:
                text = big_font.render("Мины победили!", True, (0, 255, 0))
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
                window.blit(text, text_rect)
                pygame.display.flip()
                pygame.time.wait(3000)
                running = False
                break

        # Проверка победы врага
        if all(not mine.alive for mine in mines):
            text = big_font.render("Враг победил!", True, (255, 0, 0))
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            window.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False
    else:
        timer += 1
    
    # Отрисовка информации о стратегии
    strategy_text = font.render(f"Стратегия: {STRATEGY_NAMES[strategy_id]}", True, (255, 255, 255))
    window.blit(strategy_text, (10, 10))
    
    # Отрисовка количества живых мин
    alive_mines = sum(1 for mine in mines if mine.alive)
    mines_text = font.render(f"Живых мин: {alive_mines}", True, (255, 255, 255))
    window.blit(mines_text, (10, 40))

    # Отрисовка FPS
    fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
    window.blit(fps_text, (10, 70))
    
    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
sys.exit()
