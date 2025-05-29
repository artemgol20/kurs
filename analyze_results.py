import pandas as pd
import numpy as np

def analyze_simulation_results(csv_file_path):
    """
    Анализирует результаты симуляции из CSV файла и выводит статистику в консоль.
    
    Args:
        csv_file_path (str): Путь к CSV файлу с результатами симуляции
    """
    try:
        # Читаем CSV файл
        df = pd.read_csv(csv_file_path, encoding='windows-1251')
        
        # Словарь для коротких названий стратегий
        strategy_short_names = {
            "Жадный алгоритм (Greedy Attack)": "Прямая",
            "Зигзагообразное движение (Evasive Zigzag)": "Зигзаз",
            "Спиральное сближение (Spiral Approach)": "Спираль",
            "Фланговая атака (Flank Attack)": "Фланговая",
            "Случайный шум (Random Perturbation)": "Рандом",
            "Gathering (Сбор в треугольнике)": "Треугольник",
            "Спиральный зигзаг (Spiral Zigzag)": "Спираль + зигзаг"
        }
        
        print("\n=== АНАЛИЗ РЕЗУЛЬТАТОВ СИМУЛЯЦИИ ===")
        print("=" * 50)
        
        # Анализ по количеству мин
        for num_mines in sorted(df['num_mines'].unique()):
            print(f"\n=== АНАЛИЗ ДЛЯ {num_mines} МИН ===")
            print("-" * 50)
            
            df_mines = df[df['num_mines'] == num_mines]
            
            # Группируем по стратегии
            grouped = df_mines.groupby('strategy')
            
            for strategy, group in grouped:
                short_name = strategy_short_names.get(strategy, strategy)
                total_simulations = len(group)
                successful_simulations = len(group[group['enemy_destroyed'] == True])
                success_rate = (successful_simulations / total_simulations) * 100
                
                avg_time = group['time_to_kill'].mean()
                avg_survived = group['surviving_mines'].mean()
                
                print(f"\nСтратегия: {short_name}")
                print(f"Всего симуляций: {total_simulations}")
                print(f"Успешных симуляций: {successful_simulations}")
                print(f"Процент успеха: {success_rate:.2f}%")
                print(f"Среднее время до уничтожения: {avg_time:.2f} кадров")
                print(f"Среднее количество выживших мин: {avg_survived:.2f}")
                
                # Дополнительная статистика
                print("\nДополнительная статистика:")
                print(f"Мин. время: {group['time_to_kill'].min():.2f}")
                print(f"Макс. время: {group['time_to_kill'].max():.2f}")
                print(f"Мин. выживших: {group['surviving_mines'].min()}")
                print(f"Макс. выживших: {group['surviving_mines'].max()}")
                print(f"Стандартное отклонение времени: {group['time_to_kill'].std():.2f}")
                print(f"Стандартное отклонение выживших: {group['surviving_mines'].std():.2f}")
                print("-" * 50)
            
            # Общая статистика по всем стратегиям для данного количества мин
            print("\nОБЩАЯ СТАТИСТИКА ПО ВСЕМ СТРАТЕГИЯМ:")
            print(f"Среднее время по всем стратегиям: {df_mines['time_to_kill'].mean():.2f}")
            print(f"Среднее количество выживших по всем стратегиям: {df_mines['surviving_mines'].mean():.2f}")
            print(f"Общий процент успеха: {(df_mines['enemy_destroyed'].mean() * 100):.2f}%")
            print("=" * 50)
            
    except FileNotFoundError:
        print(f"Ошибка: Файл {csv_file_path} не найден")
    except pd.errors.EmptyDataError:
        print(f"Ошибка: Файл {csv_file_path} пуст")
    except Exception as e:
        print(f"Произошла ошибка при анализе файла: {str(e)}")

# Пример использования:
if __name__ == "__main__":
    # Можно передать путь к файлу как аргумент
    file_path = "simulation_results_20250528_055633.csv"
    analyze_simulation_results(file_path) 