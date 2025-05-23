import pygame
import sys
import math
import random
import csv
import time
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from unittest.mock import MagicMock
import pandas as pd
import numpy as np
from tqdm import tqdm
from config import *

# Мокаем все необходимые компоненты pygame
pygame.init = MagicMock()
pygame.display = MagicMock()
pygame.display.set_mode = MagicMock()
pygame.display.flip = MagicMock()
pygame.draw = MagicMock()
pygame.draw.rect = MagicMock()
pygame.draw.circle = MagicMock()
pygame.font = MagicMock()
pygame.font.SysFont = MagicMock()
pygame.font.SysFont().render = MagicMock()
pygame.font.SysFont().render().get_rect = MagicMock()
pygame.font.SysFont().render().get_width = MagicMock()
pygame.font.SysFont().render().get_height = MagicMock()
pygame.event = MagicMock()
pygame.event.get = MagicMock(return_value=[])
pygame.time = MagicMock()
pygame.time.Clock = MagicMock()
pygame.time.Clock().tick = MagicMock()
pygame.time.wait = MagicMock()
pygame.time.get_ticks = lambda: 0
pygame.QUIT = 0
pygame.KEYDOWN = 0
pygame.K_UP = 0
pygame.K_DOWN = 0

# Импортируем необходимые классы из game_objects.py
from game_objects import Mine, Enemy, Bullet

class SimulationAnalytics:
    def __init__(self):
        self.results = []
        self.strategy_names = STRATEGY_NAMES
        
        # Инициализируем время
        self.start_time = 0
        self.current_time = 0

    def create_mine_on_circle(self, index, total, strategy_id):
        radius = 350
        angle = (2 * math.pi * index) / total
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

    def create_triangle_mines(self):
        center_x = 150
        center_y = HEIGHT // 2
        radius = 100
        mines = []
        for i in range(3):
            angle = i * (2 * math.pi / 3)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            mines.append(Mine(x, y))
        return mines

    def run_simulation(self, strategy_id, num_mines):
        # Создаем мины
        if strategy_id == 5:  # Gathering
            mines = self.create_triangle_mines()
        else:
            mines = [self.create_mine_on_circle(i, num_mines, strategy_id) for i in range(num_mines)]
        
        enemy = Enemy()
        max_iterations = 1000
        timer = 0
        
        while timer < max_iterations:
            self.current_time += 16
            pygame.time.get_ticks = lambda: self.current_time
            
            # Движение мин
            if strategy_id == 1:
                leader = mines[0] if mines else None
                for i, mine in enumerate(mines):
                    if mine.alive:
                        mine.move((enemy.x, enemy.y), leader if i > 0 else None, strategy_id=strategy_id)
            else:
                for mine in mines:
                    if mine.alive:
                        if strategy_id == 2:  # Спиральное сближение
                            mine.speed = MINE_SPEED * 1.3
                            # Сдвигаем координаты так, чтобы враг был центром спирали
                            X0 = mine.x - enemy.x
                            Y0 = mine.y - enemy.y
                            
                            # Используем сохраненные начальные параметры
                            if not hasattr(mine, 'phi'):
                                mine.phi = math.atan2(Y0, X0)
                                mine.r0 = math.hypot(X0, Y0) or 1
                            else:
                                # Восстанавливаем начальные параметры из сохраненных значений
                                mine.phi = mine.phi
                                mine.r0 = mine.r0

                            # Параметр спирали (чем больше, тем плотнее скрутка)
                            b = 0.2

                            # Текущее расстояние до цели
                            curr_r = math.hypot(X0, Y0)

                            # Увеличиваем угол (скорость закрутки)
                            # Чем ближе к цели, тем больше скорость
                            speed_factor = mine.r0 / (curr_r + 1)  # +1 чтобы избежать деления на 0
                            delta_phi = mine.speed * speed_factor / mine.r0
                            mine.phi += delta_phi

                            # Новое расстояние: r = r0 * exp(-b * phi)
                            r = mine.r0 * math.exp(-b * mine.phi)

                            # Обратно в декартовы, с центром в target
                            mine.x = enemy.x + r * math.cos(mine.phi)
                            mine.y = enemy.y + r * math.sin(mine.phi)
                        elif strategy_id == 6:  # Спиральный зигзаг
                            params = STRATEGY_PARAMS["spiral_zigzag"]
                            mine.speed = MINE_SPEED * params["speed_multiplier"]
                            
                            # Используем сохраненные начальные параметры
                            if not hasattr(mine, 'initial_angle'):
                                mine.initial_angle = math.atan2(mine.y - enemy.y, mine.x - enemy.x)
                                mine.initial_radius = math.hypot(mine.x - enemy.x, mine.y - enemy.y)
                            
                            # Вычисляем текущий угол относительно цели
                            current_angle = math.atan2(mine.y - enemy.y, mine.x - enemy.x)
                            # Вычисляем текущее расстояние до цели
                            current_radius = math.hypot(mine.x - enemy.x, mine.y - enemy.y)
                            
                            # Вычисляем новый угол с учетом спирального движения
                            spiral_factor = getattr(mine, 'spiral_factor', params["spiral_factor"])
                            new_angle = mine.initial_angle + (timer * 0.02)  # Постепенное увеличение угла
                            
                            # Вычисляем новый радиус с учетом спирального затухания
                            new_radius = mine.initial_radius * math.exp(-spiral_factor * (timer * 0.02))
                            
                            # Добавляем зигзагообразное движение
                            zigzag_amplitude = getattr(mine, 'zigzag_amplitude', params["zigzag_amplitude"])
                            phase_change = getattr(mine, 'phase_change', params["phase_change"])
                            mine.zigzag_phase += phase_change
                            
                            # Вычисляем смещение от зигзага
                            dx_zigzag = zigzag_amplitude * math.sin(mine.zigzag_phase) * math.cos(new_angle + math.pi/2)
                            dy_zigzag = zigzag_amplitude * math.sin(mine.zigzag_phase) * math.sin(new_angle + math.pi/2)
                            
                            # Обновляем позицию с учетом зигзага
                            mine.x = enemy.x + new_radius * math.cos(new_angle) + dx_zigzag
                            mine.y = enemy.y + new_radius * math.sin(new_angle) + dy_zigzag
                        else:
                            mine.move((enemy.x, enemy.y), strategy_id=strategy_id)
            
            # Обновление врага
            timer += 1
            if timer % ENEMY_REACTION_TIME == 0:
                enemy.update(mines)
            
            # Обновление пуль
            for bullet in enemy.bullets[:]:
                bullet.move()
                hit = False
                for mine in mines:
                    if mine.alive and math.hypot(mine.x - bullet.x, mine.y - bullet.y) < MINE_RADIUS:
                        mine.alive = False
                        hit = True
                        break
                if hit:
                    enemy.bullets.remove(bullet)
                elif (bullet.x < 0 or bullet.x > WIDTH or 
                      bullet.y < 0 or bullet.y > HEIGHT):
                    enemy.bullets.remove(bullet)
            
            # Проверка победы мин
            for mine in mines:
                if mine.alive and math.hypot(mine.x - enemy.x, mine.y - enemy.y) < MINE_DETECT_RADIUS:
                    return {
                        'strategy': self.strategy_names[strategy_id],
                        'num_mines': num_mines,
                        'time_to_kill': timer,
                        'surviving_mines': sum(1 for m in mines if m.alive),
                        'enemy_destroyed': True
                    }
            
            # Проверка победы врага
            if all(not mine.alive for mine in mines):
                return {
                    'strategy': self.strategy_names[strategy_id],
                    'num_mines': num_mines,
                    'time_to_kill': timer,
                    'surviving_mines': 0,
                    'enemy_destroyed': False
                }
        
        return {
            'strategy': self.strategy_names[strategy_id],
            'num_mines': num_mines,
            'time_to_kill': max_iterations,
            'surviving_mines': sum(1 for m in mines if m.alive),
            'enemy_destroyed': False
        }

    def run_all_tests(self):
        mine_counts = [2,3, 5, 7]
        iterations = 40

        total_tests = len(self.strategy_names) * len(mine_counts) * iterations
        with tqdm(total=total_tests, desc="Прогресс тестирования") as pbar:
            for strategy_id in range(len(self.strategy_names)):
                for num_mines in mine_counts:
                    if strategy_id == 5:  # Gathering всегда использует 3 мины
                        num_mines = 3
                    
                    for i in range(iterations):
                        result = self.run_simulation(strategy_id, num_mines)
                        self.results.append(result)
                        pbar.update(1)

    def save_results(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'simulation_results_{timestamp}.csv'
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['strategy', 'num_mines', 'time_to_kill', 
                                                 'surviving_mines', 'enemy_destroyed'])
            writer.writeheader()
            writer.writerows(self.results)
        
        return filename

    def plot_results(self):
        df = pd.DataFrame(self.results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        strategy_short_names = {
            "Жадный алгоритм (Greedy Attack)": "Greedy",
            "Зигзагообразное движение (Evasive Zigzag)": "Zigzag",
            "Спиральное сближение (Spiral Approach)": "Spiral",
            "Фланговая атака (Flank Attack)": "Flank",
            "Случайный шум (Random Perturbation)": "Random",
            "Gathering (Сбор в треугольнике)": "Gathering",
            "Спиральный зигзаг (Spiral Zigzag)": "Spiral Zigzag"
        }
        df['strategy_short'] = df['strategy'].map(strategy_short_names)
        
        for num_mines in df['num_mines'].unique():
            df_mines = df[df['num_mines'] == num_mines]
            
            plt.figure(figsize=(15, 8))
            sns.boxplot(x='strategy_short', y='time_to_kill', data=df_mines)
            plt.xticks(rotation=30, ha='right')
            plt.title(f'Время до уничтожения цели (количество мин: {num_mines})')
            plt.xlabel('Стратегия')
            plt.ylabel('Время (секунды)')
            plt.tight_layout()
            plt.savefig(f'time_to_kill_{num_mines}.png', dpi=300, bbox_inches='tight')
            plt.close()

            plt.figure(figsize=(15, 8))
            sns.boxplot(x='strategy_short', y='surviving_mines', data=df_mines)
            plt.xticks(rotation=30, ha='right')
            plt.title(f'Количество выживших мин (количество мин: {num_mines})')
            plt.xlabel('Стратегия')
            plt.ylabel('Количество мин')
            plt.tight_layout()
            plt.savefig(f'surviving_mines_{num_mines}.png', dpi=300, bbox_inches='tight')
            plt.close()

            plt.figure(figsize=(15, 8))
            success_rate = df_mines.groupby('strategy_short')['enemy_destroyed'].mean()
            success_rate.plot(kind='bar')
            plt.title(f'Процент успешных атак (количество мин: {num_mines})')
            plt.xlabel('Стратегия')
            plt.ylabel('Процент успешных атак')
            plt.xticks(rotation=30, ha='right')
            plt.tight_layout()
            plt.savefig(f'success_rate_{num_mines}.png', dpi=300, bbox_inches='tight')
            plt.close()

def main():
    analytics = SimulationAnalytics()
    print("Начинаем тестирование...")
    analytics.run_all_tests()
    print("Тестирование завершено")
    
    filename = analytics.save_results()
    print(f"Результаты сохранены в {filename}")
    
    print("Создаем графики...")
    analytics.plot_results()
    print("Графики сохранены")

if __name__ == "__main__":
    main() 