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

def plot_results(self):
    df = pd.DataFrame(self.results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    strategy_short_names = {
        "Жадный алгоритм (Greedy Attack)": "Прямая",
        "Зигзагообразное движение (Evasive Zigzag)": "Зигзаз",
        "Спиральное сближение (Spiral Approach)": "Спираль",
        "Фланговая атака (Flank Attack)": "Фланговая",
        "Случайный шум (Random Perturbation)": "Рандом",
        "Gathering (Сбор в треугольнике)": "Треугольник",
        "Спиральный зигзаг (Spiral Zigzag)": "Спираль + зигзаг"
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