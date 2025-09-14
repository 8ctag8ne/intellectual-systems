import pygame
from src.constants import *


class UI:
    def __init__(self, screen, font, big_font):
        self.screen = screen
        self.font = font
        self.big_font = big_font

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

    def draw_pause_screen(self):
        """Малює екран паузи"""
        # Напівпрозора накладка
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Текст паузи
        self.draw_text_centered("PAUSED", self.big_font, WHITE, -50)
        self.draw_text_centered("Press ESC to continue", self.font, WHITE, 0)
        self.draw_text_centered("Press R to restart", self.font, WHITE, 30)

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