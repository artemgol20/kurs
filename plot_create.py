import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Словарь для сокращенных названий
strategy_names = {
    "Жадный алгоритм (Greedy Attack)": "Прямая",
    "Зигзагообразное движение (Evasive Zigzag)": "Зигзаз",
    "Спиральное сближение (Spiral Approach)": "Спираль",
    "Фланговая атака (Flank Attack)": "Фланговая",
    "Случайный шум (Random Perturbation)": "Рандом",
    "Спиральный зигзаг (Spiral Zigzag)": "Спираль + зигзаг"
}

# Чтение данных из CSV файла
df = pd.read_csv('simulation_results_20250528_055633.csv', encoding='windows-1251')

# Замена полных названий на сокращенные
df['strategy'] = df['strategy'].map(strategy_names)

# Фильтрация данных для 2 и 3 мин
df_2_mines = df[df['num_mines'] == 2]
df_3_mines = df[df['num_mines'] == 3]

# Создание и сохранение графика для 2 мин
plt.figure(figsize=(12, 6))
sns.barplot(data=df_2_mines, x='strategy', y='surviving_mines', order=list(strategy_names.values()))
plt.title('Количество выживших мин (2 мины)', fontsize=14)
plt.xlabel('Стратегия', fontsize=12)
plt.ylabel('Среднее количество выживших мин', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('surviving_mines_2bar.png', dpi=300, bbox_inches='tight')
plt.close()

# Создание и сохранение графика для 3 мин
plt.figure(figsize=(12, 6))
sns.barplot(data=df_3_mines, x='strategy', y='surviving_mines', order=list(strategy_names.values()))
plt.title('Количество выживших мин (3 мины)', fontsize=14)
plt.xlabel('Стратегия', fontsize=12)
plt.ylabel('Среднее количество выживших мин', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('surviving_mines_3bar.png', dpi=300, bbox_inches='tight')
plt.close() 