import pygame
import sys
import math
import random
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
    while True:
        if spawn_type == 0:  # Случайно вокруг
            x = random.randint(50, WIDTH-50)
            y = random.randint(50, HEIGHT-50)
        elif spawn_type == 1:  # Слева
            x = random.randint(50, 100)
            y = random.randint(50, HEIGHT-50)
        elif spawn_type == 2:  # Справа
            x = random.randint(WIDTH-100, WIDTH-50)
            y = random.randint(50, HEIGHT-50)
        elif spawn_type == 3:  # Сверху
            x = random.randint(50, WIDTH-50)
            y = random.randint(50, 100)
        else:  # Снизу
            x = random.randint(50, WIDTH-50)
            y = random.randint(HEIGHT-100, HEIGHT-50)
            
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
        self.velocity = [0, 0]  # Для Boids-like стратегии

    def move(self, target, leader=None):
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
            # Сдвигаем координаты так, чтобы враг был центром спирали
            X0 = self.x - target[0]
            Y0 = self.y - target[1]
            # При первом вызове запоминаем начальные полярные координаты
            if not hasattr(self, 'phi'):
                self.phi = math.atan2(Y0, X0)
                self.r0  = math.hypot(X0, Y0) or 1

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
            
        elif strategy_id == 3:  # Фланговая атака
            if self.x < target[0]:
                self.angle = base_angle + math.pi / 4
            else:
                self.angle = base_angle - math.pi / 4
        
        elif strategy_id == 4:  # Случайный шум
            self.angle = base_angle + random.uniform(-1.0, 1.0)
            
        elif strategy_id == 5:  # Gathering (Сбор в треугольнике)
            # Просто движемся к цели с увеличенной скоростью
            self.angle = base_angle
            self.speed = MINE_SPEED * 1.5  # Увеличиваем скорость для этой стратегии
            
        elif strategy_id == 6:  # Спиральный зигзаг
            self.speed = MINE_SPEED * 1.0

            # Центр относительно цели
            X0 = self.x - target[0]
            Y0 = self.y - target[1]

            if not hasattr(self, 'phi'):
                self.phi = math.atan2(Y0, X0)
                self.r0  = math.hypot(X0, Y0) or 1

            # Параметр скрутки
            b = 0.2
            curr_r = math.hypot(X0, Y0)

            # Увеличиваем угол с поправкой на расстояние
            speed_factor = self.r0 / (curr_r + 1)
            delta_phi = self.speed * speed_factor / self.r0
            self.phi += delta_phi

            # Затухающая спираль
            r = self.r0 * math.exp(-b * self.phi)

            # Поперечное отклонение (амплитуда и частота можно регулировать)
            zigzag_amplitude = 20
            zigzag_frequency = 0.2  # 0.4 = частота, можно подбирать

            # Смещение перпендикулярно спиральной траектории
            dx_zigzag = zigzag_amplitude * math.cos(self.tick * zigzag_frequency) * math.cos(self.phi + math.pi/2)
            dy_zigzag = zigzag_amplitude * math.cos(self.tick * zigzag_frequency) * math.sin(self.phi + math.pi/2)

            # Итоговая позиция
            self.x = target[0] + r * math.cos(self.phi) + dx_zigzag
            self.y = target[1] + r * math.sin(self.phi) + dy_zigzag
            return

        # Применяем движение для всех стратегий кроме спирального зигзага
        if strategy_id != 6:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed

    def draw(self):
        color = (0, 255, 0) if self == mines[0] and strategy_id == 5 else MINE_COLOR
        pygame.draw.circle(window, color, (int(self.x), int(self.y)), MINE_RADIUS)
        pygame.draw.circle(window, (0, 150, 255), (int(self.x), int(self.y)), MINE_DETECT_RADIUS, 1)

class Enemy:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.bullets = []

    def update(self, mines):
        # Найти ближайшую мину
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

    def draw(self):
        pygame.draw.circle(window, ENEMY_COLOR, (self.x, self.y), ENEMY_RADIUS)
        pygame.draw.circle(window, (255, 50, 50), (self.x, self.y), ENEMY_DETECT_RADIUS, 1)

# Создаем мины
if strategy_id == 5:  # Gathering
    mines = create_triangle_mines()
else:
    mines = [create_mine(spawn_type) for _ in range(num_mines)]
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
                mine.move((enemy.x, enemy.y), leader if i > 0 else None)
    else:
        for mine in mines:
            if mine.alive:
                mine.move((enemy.x, enemy.y))

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
            mine.draw()
    for bullet in enemy.bullets:
        bullet.draw()
    enemy.draw()

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
