import pygame
import math

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
MINE_SPEED = 0.8
START_DELAY = 60
MIN_SPAWN_DISTANCE = 300
ENEMY_REACTION_TIME = 45

# Список стратегий
STRATEGY_NAMES = [
    "Жадный алгоритм (Greedy Attack)",
    "Зигзагообразное движение (Evasive Zigzag)",
    "Спиральное сближение (Spiral Approach)",
    "Фланговая атака (Flank Attack)",
    "Случайный шум (Random Perturbation)",
    "Gathering (Сбор в треугольнике)",
    "Спиральный зигзаг (Spiral Zigzag)"
]

# Список типов спавна
SPAWN_TYPES = [
    "Случайно вокруг",
    "Слева",
    "Справа",
    "Сверху",
    "Снизу",
    "На окружности"
]

# Параметры стратегий
STRATEGY_PARAMS = {
    "greedy": {
        "speed_multiplier": 0.9
    },
    "zigzag": {
        "speed_multiplier": 0.85,
        "amplitude": 1.2,
        "period": 15
    },
    "spiral": {
        "speed_multiplier": 1.3,
        "spiral_factor": 0.2
    },
    "flank": {
        "speed_multiplier": 0.9,
        "attack_angle": math.pi / 3
    },
    "random": {
        "speed_multiplier": 0.8,
        "noise_range": 1.5
    },
    "gathering": {
        "speed_multiplier": 1.3
    },
    "spiral_zigzag": {
        "speed_multiplier": 1.2,
        "spiral_factor": 0.15,
        "zigzag_amplitude": 40,
        "zigzag_frequency": 0.2,
        "phase_change": 0.1,
        "micro_angle_range": 0.1,
        "micro_deviation": 5
    }
} 