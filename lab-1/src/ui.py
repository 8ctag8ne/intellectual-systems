# ui.py (оновлений з інформацією про правила)
import pygame
from src.constants import *


class UI:
    def __init__(self, screen, font, big_font):
        self.screen = screen
        self.font = font
        self.big_font = big_font
        self.small_font = pygame.font.Font(None, 20)
        self.tiny_font = pygame.font.Font(None, 16)

    def draw_text_centered(self, text, font, color, y_offset=0):
        """Малює текст по центру екрана"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.centerx = SCREEN_WIDTH // 2
        text_rect.centery = SCREEN_HEIGHT // 2 + y_offset
        self.screen.blit(text_surface, text_rect)
        return text_rect

    def draw_score(self, remaining_dots, total_dots):
        """Малює інформацію про залишок точок"""
        eaten_dots = total_dots - remaining_dots
        score_text = f"Eaten: {eaten_dots}/{total_dots}"
        text_surface = self.font.render(score_text, True, WHITE)
        self.screen.blit(text_surface, (10, 10))

    def draw_difficulty_info(self, difficulty_manager):
        """Малює інформацію про поточний рівень складності та активні правила"""
        current_level = difficulty_manager.get_current_level()

        # Назва рівня
        level_text = f"Level: {current_level.name} ({difficulty_manager.current_level + 1}/{difficulty_manager.get_level_count()})"
        text_surface = self.small_font.render(level_text, True, WHITE)
        self.screen.blit(text_surface, (10, 45))

        # Опис рівня
        desc_text = current_level.description
        text_surface = self.small_font.render(desc_text, True, CYAN)
        self.screen.blit(text_surface, (10, 65))

        # Активні правила
        rules_text = f"Active rules: {difficulty_manager.get_active_rules_description()}"
        # Розбиваємо довгий текст на кілька рядків якщо потрібно
        max_width = SCREEN_WIDTH - 20
        words = rules_text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if self.tiny_font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        y_pos = 85
        for line in lines[:2]:  # Показуємо максимум 2 рядки
            text_surface = self.tiny_font.render(line, True, YELLOW)
            self.screen.blit(text_surface, (10, y_pos))
            y_pos += 16

        # Підказка про керування
        controls_text = "+/- to change difficulty"
        text_surface = self.small_font.render(controls_text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.topright = (SCREEN_WIDTH - 10, 10)
        self.screen.blit(text_surface, text_rect)

    def draw_pause_screen(self, difficulty_manager=None):
        """Малює екран паузи з детальною інформацією про правила"""
        # Напівпрозора накладка
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Текст паузи
        self.draw_text_centered("PAUSED", self.big_font, WHITE, -150)
        self.draw_text_centered("Press ESC to continue", self.font, WHITE, -110)
        self.draw_text_centered("Press R to restart", self.font, WHITE, -80)

        if difficulty_manager:
            # Інформація про рівні складності
            self.draw_text_centered("DIFFICULTY LEVELS:", self.font, YELLOW, -40)

            y_offset = -10
            for i, level in enumerate(difficulty_manager.levels):
                color = WHITE
                prefix = ""
                if i == difficulty_manager.current_level:
                    color = GREEN
                    prefix = "> "

                level_text = f"{prefix}{i + 1}. {level.name}"
                self.draw_text_centered(level_text, self.small_font, color, y_offset)
                y_offset += 20

                # Показуємо опис поточного рівня
                if i == difficulty_manager.current_level:
                    desc_text = f"   {level.description}"
                    self.draw_text_centered(desc_text, self.tiny_font, CYAN, y_offset)
                    y_offset += 16

                    # Показуємо активні правила для поточного рівня
                    rules_text = f"   Rules: {difficulty_manager.get_active_rules_description()}"
                    # Розбиваємо довгий текст
                    max_width = SCREEN_WIDTH - 100
                    if self.tiny_font.size(rules_text)[0] > max_width:
                        words = rules_text.split(': ', 1)
                        if len(words) > 1:
                            self.draw_text_centered(f"   Rules:", self.tiny_font, YELLOW, y_offset)
                            y_offset += 16
                            rule_words = words[1].split(', ')
                            current_line = "   "
                            for rule in rule_words:
                                test_line = current_line + (", " if len(current_line) > 3 else "") + rule
                                if self.tiny_font.size(test_line)[0] <= max_width:
                                    current_line = test_line
                                else:
                                    if len(current_line) > 3:
                                        self.draw_text_centered(current_line, self.tiny_font, YELLOW, y_offset)
                                        y_offset += 16
                                    current_line = "   " + rule
                            if len(current_line) > 3:
                                self.draw_text_centered(current_line, self.tiny_font, YELLOW, y_offset)
                                y_offset += 16
                    else:
                        self.draw_text_centered(rules_text, self.tiny_font, YELLOW, y_offset)
                        y_offset += 16

                    y_offset += 10  # Додатковий простір після поточного рівня

            self.draw_text_centered("Use +/- or number keys (1-4) to change", self.small_font, CYAN, y_offset + 10)

    def draw_win_screen(self):
        """Малює екран перемоги"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 100, 0))  # Зелений відтінок
        self.screen.blit(overlay, (0, 0))
        self.draw_text_centered("YOU WIN!", self.big_font, WHITE, -50)
        self.draw_text_centered("All dots collected!", self.font, WHITE, 0)
        self.draw_text_centered("Press R to restart", self.font, WHITE, 30)
        self.draw_text_centered("Press ESC to quit", self.font, WHITE, 60)
        self.draw_text_centered("Use +/- to change difficulty", self.small_font, YELLOW, 90)

    def draw_lose_screen(self):
        """Малює екран поразки"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((100, 0, 0))  # Червоний відтінок
        self.screen.blit(overlay, (0, 0))
        self.draw_text_centered("GAME OVER!", self.big_font, WHITE, -50)
        self.draw_text_centered("Ghost caught you!", self.font, WHITE, 0)
        self.draw_text_centered("Press R to restart", self.font, WHITE, 30)
        self.draw_text_centered("Press ESC to quit", self.font, WHITE, 60)
        self.draw_text_centered("Use +/- to change difficulty", self.small_font, YELLOW, 90)