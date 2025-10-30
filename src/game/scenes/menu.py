from __future__ import annotations
import pygame
from .gameplay import GameplayScene
from ..settings import WHITE, BLACK, SCREEN_WIDTH, SCREEN_HEIGHT

class MenuScene:
    def __init__(self, manager):
        self.manager = manager
        self.font = pygame.font.Font(None, 64)
        self.sub = pygame.font.Font(None, 28)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.manager.push(GameplayScene(self.manager))

    def update(self, dt: float):
        pass

    def draw(self, screen: pygame.Surface):
        screen.fill(BLACK)
        title = self.font.render("Way Of The Samurai", True, WHITE)
        hint = self.sub.render("Press Enter to Start", True, WHITE)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40)))
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)))
