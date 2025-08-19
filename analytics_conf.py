import pygame
import math
import random
from config import *
from game_objects import Mine, Enemy, Bullet

class SimulationAnalyticsConf:
    def __init__(self):
        self.current_time = 0
        self.strategy_names = {
            1: "Жадный алгоритм (Greedy Attack)",
            2: "Зигзагообразное движение (Evasive Zigzag)",
            3: "Спиральное сближение (Spiral Approach)",
            4: "Фланговая атака (Flank Attack)",
            5: "Случайный шум (Random Perturbation)",
            6: "Gathering (Сбор в треугольнике)",
            7: "Спиральный зигзаг (Spiral Zigzag)"
        }

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

    def run_simulation(self, strategy_id):
        # Фиксированное количество мин
        num_mines = 3
        
        # Создаем мины
        if strategy_id == 6:  # Gathering
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
                        'enemy_destroyed': True,
                        'config': {
                            'BULLET_SPEED': BULLET_SPEED,
                            'MINE_SPEED': MINE_SPEED,
                            'ENEMY_REACTION_TIME': ENEMY_REACTION_TIME
                        }
                    }
            
            # Проверка победы врага
            if all(not mine.alive for mine in mines):
                return {
                    'strategy': self.strategy_names[strategy_id],
                    'num_mines': num_mines,
                    'time_to_kill': timer,
                    'surviving_mines': 0,
                    'enemy_destroyed': False,
                    'config': {
                        'BULLET_SPEED': BULLET_SPEED,
                        'MINE_SPEED': MINE_SPEED,
                        'ENEMY_REACTION_TIME': ENEMY_REACTION_TIME
                    }
                }
        
        return {
            'strategy': self.strategy_names[strategy_id],
            'num_mines': num_mines,
            'time_to_kill': max_iterations,
            'surviving_mines': sum(1 for m in mines if m.alive),
            'enemy_destroyed': False,
            'config': {
                'BULLET_SPEED': BULLET_SPEED,
                'MINE_SPEED': MINE_SPEED,
                'ENEMY_REACTION_TIME': ENEMY_REACTION_TIME
            }
        }

def main():
    analytics = SimulationAnalyticsConf()
    results = []
    
    # Запускаем симуляции для каждой стратегии
    for strategy_id in range(1, 8):
        result = analytics.run_simulation(strategy_id)
        results.append(result)
        print(f"\nРезультаты для стратегии {result['strategy']}:")
        print(f"Время до завершения: {result['time_to_kill']}")
        print(f"Выжившие мины: {result['surviving_mines']}")
        print(f"Враг уничтожен: {'Да' if result['enemy_destroyed'] else 'Нет'}")
        print("Конфигурация:")
        for key, value in result['config'].items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main() 