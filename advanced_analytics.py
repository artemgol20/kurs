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

class AdvancedSimulationAnalytics:
    def __init__(self):
        self.results = []
        self.strategy_names = {
            0: "Прямая",
            1: "Зигзаз",
            2: "Спираль",
            3: "Фланговая",
            4: "Рандом",
            5: "Спираль + зигзаг"
        }
        
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
        if strategy_id in [2, 5]:  # Для спиральных стратегий
            mine.phi = angle
            mine.r0 = radius
            if strategy_id == 5:  # Спиральный зигзаг
                mine.zigzag_phase = random.random() * 2 * math.pi
                mine.spiral_factor = random.uniform(0.12, 0.18)
                mine.zigzag_amplitude = random.uniform(35, 45)
                mine.phase_change = random.uniform(0.08, 0.12)
        else:
            mine.phi = angle
            mine.r0 = radius
            mine.zigzag_phase = random.random() * 2 * math.pi
            
        return mine

    def run_simulation(self, strategy_id, num_mines):
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
        mine_counts = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        iterations = 200

        total_tests = len(self.strategy_names) * len(mine_counts) * iterations
        with tqdm(total=total_tests, desc="Прогресс тестирования") as pbar:
            for strategy_id in range(len(self.strategy_names)):
                for num_mines in mine_counts:
                    for i in range(iterations):
                        result = self.run_simulation(strategy_id, num_mines)
                        self.results.append(result)
                        pbar.update(1)

    def save_results(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'advanced_simulation_results_{timestamp}.csv'
        
        with open(filename, 'w', newline='', encoding='windows-1251') as f:
            writer = csv.DictWriter(f, fieldnames=['strategy', 'num_mines', 'time_to_kill', 
                                                 'surviving_mines', 'enemy_destroyed'])
            writer.writeheader()
            writer.writerows(self.results)
        
        return filename

    def plot_results(self):
        df = pd.DataFrame(self.results)
        
        # Создаем график для каждой стратегии
        for strategy in self.strategy_names.values():
            strategy_data = df[df['strategy'] == strategy]
            
            # Группируем данные по количеству мин
            grouped = strategy_data.groupby('num_mines').agg({
                'enemy_destroyed': 'mean',
                'surviving_mines': 'mean'
            }).reset_index()
            
            # Создаем график
            plt.figure(figsize=(12, 6))
            
            # График успешности (красная линия)
            plt.plot(grouped['num_mines'], grouped['enemy_destroyed'] * 100, 
                    'r-', label='Успешность (%)', linewidth=2)
            
            # График выживших мин (синяя линия) - теперь в абсолютных значениях
            plt.plot(grouped['num_mines'], grouped['surviving_mines'], 
                    'b-', label='Количество выживших мин', linewidth=2)
            
            plt.title(f'Анализ стратегии: {strategy}', fontsize=14)
            plt.xlabel('Количество мин', fontsize=12)
            plt.ylabel('Значение', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend(fontsize=10)
            
            # Сохраняем график
            plt.savefig(f'strategy_analysis_{strategy}.png', dpi=300, bbox_inches='tight')
            plt.close()

        # Создаем столбчатые графики для 2 и 3 мин
        for num_mines in [2, 3]:
            plt.figure(figsize=(15, 8))
            
            # Фильтруем данные для конкретного количества мин
            mines_data = df[df['num_mines'] == num_mines]
            
            # Группируем данные по стратегиям
            grouped = mines_data.groupby('strategy').agg({
                'enemy_destroyed': 'mean',
                'surviving_mines': 'mean'
            }).reset_index()
            
            # Создаем позиции для баров
            x = np.arange(len(grouped))
            width = 0.35
            
            # Создаем бары
            plt.bar(x - width/2, grouped['enemy_destroyed'] * 100, width, 
                   label='Успешность (%)', color='red')
            plt.bar(x + width/2, grouped['surviving_mines'], width, 
                   label='Количество выживших мин', color='blue')
            
            plt.title(f'Сравнение стратегий для {num_mines} мин', fontsize=14)
            plt.xlabel('Стратегия', fontsize=12)
            plt.ylabel('Значение', fontsize=12)
            plt.xticks(x, grouped['strategy'], rotation=45)
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Сохраняем график
            plt.tight_layout()
            plt.savefig(f'strategy_comparison_{num_mines}mines.png', dpi=300, bbox_inches='tight')
            plt.close()

    def print_statistics(self):
        df = pd.DataFrame(self.results)
        
        print("\nИтоговая статистика по стратегиям:")
        print("-" * 50)
        
        # Общая статистика по стратегиям
        for strategy in self.strategy_names.values():
            strategy_data = df[df['strategy'] == strategy]
            
            # Общая успешность
            success_rate = strategy_data['enemy_destroyed'].mean() * 100
            
            # Среднее количество выживших мин
            avg_surviving = strategy_data['surviving_mines'].mean()
            
            # Среднее время до уничтожения врага (только для успешных атак)
            avg_time = strategy_data[strategy_data['enemy_destroyed']]['time_to_kill'].mean()
            
            print(f"\nСтратегия: {strategy}")
            print(f"Общая успешность: {success_rate:.2f}%")
            print(f"Среднее количество выживших мин: {avg_surviving:.2f}")
            print(f"Среднее время до уничтожения врага: {avg_time:.2f} тиков")
            print("-" * 50)
        
        # Подробная статистика для каждой стратегии и количества мин
        print("\nПодробная статистика по стратегиям и количеству мин:")
        print("-" * 50)
        
        for strategy in self.strategy_names.values():
            print(f"\nСтратегия: {strategy}")
            print("-" * 30)
            
            for num_mines in sorted(df['num_mines'].unique()):
                data = df[(df['strategy'] == strategy) & (df['num_mines'] == num_mines)]
                
                success_rate = data['enemy_destroyed'].mean() * 100
                surviving_rate = data['surviving_mines'].mean() / num_mines * 100
                avg_time = data[data['enemy_destroyed']]['time_to_kill'].mean()
                
                print(f"\nКоличество мин: {num_mines}")
                print(f"Успешность: {success_rate:.2f}%")
                print(f"Процент выживших мин: {surviving_rate:.2f}%")
                print(f"Среднее время до уничтожения врага: {avg_time:.2f} тиков")
                print(f"Количество успешных атак: {data['enemy_destroyed'].sum()}")
                print(f"Общее количество тестов: {len(data)}")
                
                # Добавляем распределение выживших мин
                print("\nРаспределение выживших мин:")
                for i in range(num_mines + 1):
                    count = len(data[data['surviving_mines'] == i])
                    percentage = (count / len(data)) * 100
                    print(f"Выжило {i} мин: {count} раз ({percentage:.1f}%)")
                
                print("-" * 30)

def main():
    analytics = AdvancedSimulationAnalytics()
    analytics.run_all_tests()
    filename = analytics.save_results()
    analytics.plot_results()
    analytics.print_statistics()
    print(f"\nРезультаты сохранены в файл: {filename}")

if __name__ == "__main__":
    main() 