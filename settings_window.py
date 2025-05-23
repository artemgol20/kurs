import pygame
import sys

class SettingsWindow:
    def __init__(self):
        pygame.init()
        self.WIDTH = 500
        self.HEIGHT = 700
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Настройки симуляции")
        
        self.font = pygame.font.SysFont("arial", 20)
        self.title_font = pygame.font.SysFont("arial", 28, bold=True)
        self.input_font = pygame.font.SysFont("arial", 24)
        
        # Начальные значения
        self.num_mines = 10
        self.strategy_id = 0
        self.spawn_type = 0
        self.input_active = False 
        self.input_text = "10"
        
        # Настройки скроллбара
        self.scroll_y = 0
        self.scroll_speed = 20
        self.max_scroll = 0
        
        self.strategies = [
            "Жадный алгоритм (Greedy Attack)",
            "Зигзагообразное движение (Evasive Zigzag)",
            "Спиральное сближение (Spiral Approach)",
            "Фланговая атака (Flank Attack)",
            "Случайный шум (Random Perturbation)",
            "Gathering (Сбор в треугольнике)",
            "Спиральный зигзаг (Spiral Zigzag)"
        ]
        
        self.spawn_types = [
            "Случайно вокруг",
            "Слева",
            "Справа",
            "Сверху",
            "Снизу",
            "На окружности"
        ]
        
        self.running = True
        self.settings_complete = False

    def draw_scrollbar(self, x, y, width, height, content_height):
        # Рисуем фон скроллбара
        pygame.draw.rect(self.window, (60, 60, 60), (x, y, width, height))
        
        # Вычисляем размер и позицию ползунка
        visible_ratio = height / content_height
        if visible_ratio < 1:  # Если контент больше видимой области
            thumb_height = max(30, int(height * visible_ratio))
            thumb_y = y + (height - thumb_height) * (self.scroll_y / (content_height - height))
            
            # Рисуем ползунок
            pygame.draw.rect(self.window, (100, 100, 100), 
                           (x, thumb_y, width, thumb_height))
            
            # Обновляем максимальный скролл
            self.max_scroll = content_height - height

    def draw_button(self, text, x, y, width, height, color, hover_color, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        if x < mouse[0] < x + width and y < mouse[1] < y + height:
            pygame.draw.rect(self.window, hover_color, (x, y, width, height))
            if click[0] == 1 and action:
                action()
        else:
            pygame.draw.rect(self.window, color, (x, y, width, height))
            
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(x + width/2, y + height/2))
        self.window.blit(text_surf, text_rect)

    def draw(self):
        self.window.fill((40, 40, 40))
        
        # Заголовок
        title = self.title_font.render("Настройки симуляции", True, (255, 255, 255))
        self.window.blit(title, (self.WIDTH//2 - title.get_width()//2, 20))
        
        # Количество мин
        mines_text = self.font.render("Количество мин:", True, (255, 255, 255))
        self.window.blit(mines_text, (20, 100))
        
        # Поле ввода
        input_rect = pygame.Rect(200, 95, 100, 30)
        if self.strategy_id == 5:  # Gathering
            pygame.draw.rect(self.window, (60, 60, 60), input_rect, 2)
            text_surface = self.input_font.render("3", True, (150, 150, 150))
            self.window.blit(text_surface, (input_rect.x + 5, input_rect.y + 2))
        else:
            pygame.draw.rect(self.window, (255, 255, 255) if self.input_active else (100, 100, 100), input_rect, 2)
            text_surface = self.input_font.render(self.input_text, True, (255, 255, 255))
            self.window.blit(text_surface, (input_rect.x + 5, input_rect.y + 2))
        
        # Предупреждения для специальных стратегий
        if self.strategy_id == 5:  # Gathering
            warning = self.font.render("Для этой стратегии используется 3 мины в треугольнике", True, (255, 100, 100))
            self.window.blit(warning, (20, 130))
        
        # Стратегия
        strategy_text = self.font.render("Стратегия:", True, (255, 255, 255))
        self.window.blit(strategy_text, (20, 160))
        
        # Область для списка стратегий
        strategies_area = pygame.Rect(20, 190, 460, 200)
        pygame.draw.rect(self.window, (30, 30, 30), strategies_area)
        
        # Рисуем стратегии с учетом скролла
        for i, strategy in enumerate(self.strategies):
            y_pos = 190 + i*35 - self.scroll_y
            if 190 <= y_pos <= 390:  # Видимая область
                color = (0, 150, 0) if i == self.strategy_id else (100, 100, 100)
                self.draw_button(strategy, 20, y_pos, 440, 30, color, (0, 200, 0),
                               lambda x=i: setattr(self, 'strategy_id', x))
        
        # Рисуем скроллбар
        self.draw_scrollbar(460, 190, 20, 200, len(self.strategies) * 35)
        
        # Место спавна
        spawn_text = self.font.render("Место спавна:", True, (255, 255, 255))
        self.window.blit(spawn_text, (20, 400))
        
        for i, spawn_type in enumerate(self.spawn_types):
            if self.strategy_id == 7:  # Для Лидер-ведомые
                color = (60, 60, 60)  # Серый цвет для неактивных кнопок
                hover_color = (60, 60, 60)
            else:
                color = (0, 150, 0) if i == self.spawn_type else (100, 100, 100)
                hover_color = (0, 200, 0)
            self.draw_button(spawn_type, 20, 430 + i*35, 460, 30, color, hover_color,
                           lambda x=i: setattr(self, 'spawn_type', x) if self.strategy_id != 7 else None)
        
        # Кнопка старта
        self.draw_button("Запустить симуляцию", 150, 620, 200, 40, (0, 100, 0), (0, 150, 0),
                        lambda: self.start_simulation())
        
        pygame.display.flip()

    def start_simulation(self):
        try:
            if self.strategy_id == 5:  # Gathering
                self.num_mines = 3
                self.settings_complete = True
            else:
                num = int(self.input_text)
                if 1 <= num <= 50:
                    self.num_mines = num
                    self.settings_complete = True
        except ValueError:
            pass

    def run(self):
        while self.running and not self.settings_complete:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Проверяем клик по полю ввода только если не Gathering
                    if self.strategy_id != 5:
                        input_rect = pygame.Rect(200, 95, 100, 30)
                        if input_rect.collidepoint(event.pos):
                            self.input_active = True
                        else:
                            self.input_active = False
                    else:
                        self.input_active = False
                        
                    # Обработка скролла колесиком мыши
                    if event.button == 4:  # Скролл вверх
                        self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                    elif event.button == 5:  # Скролл вниз
                        self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
                        
                elif event.type == pygame.KEYDOWN and self.input_active and self.strategy_id != 5:
                    if event.key == pygame.K_RETURN:
                        self.input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    elif event.unicode.isnumeric() and len(self.input_text) < 2:
                        self.input_text += event.unicode
            
            self.draw()
            pygame.time.Clock().tick(60)
        
        if self.settings_complete:
            return {
                'num_mines': self.num_mines,
                'strategy_id': self.strategy_id,
                'spawn_type': self.spawn_type
            }
        return None 