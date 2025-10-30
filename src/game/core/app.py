from __future__ import annotations
import pygame
from .scene_manager import SceneManager
from ..settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from typing import Optional

class GameApp:
    def __init__(self, start_scene_cls):
        pygame.init()
        pygame.display.set_caption("Way Of The Samurai")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.manager = SceneManager(self, start_scene_cls)
        self.running = True
        self.clock = pygame.time.Clock()
        self.manager = SceneManager(self, start_scene_cls)
        self.running = True

    def run(self):
        while self.running and self.manager.current_scene is not None:
            dt = self.clock.tick(FPS) / 1000.0  # seconds
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.manager.current_scene.handle_event(event)

            self.manager.current_scene.update(dt)
            self.manager.current_scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
