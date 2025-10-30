from __future__ import annotations
import pygame
from typing import List

class Animation:
    """Time-based animation player for pre-cut frames."""
    def __init__(self, frames: List[pygame.Surface], ms_per_frame: int = 120, loop: bool = True):
        self.frames = frames or [pygame.Surface((1,1), pygame.SRCALPHA)]
        self.ms = ms_per_frame
        self.loop = loop
        self.index = 0
        self.accum = 0

    def reset(self):
        self.index = 0
        self.accum = 0

    def update(self, dt: float):
        self.accum += dt * 1000
        while self.accum >= self.ms:
            self.accum -= self.ms
            self.index += 1
            if self.index >= len(self.frames):
                self.index = 0 if self.loop else len(self.frames) - 1

    def current_frame(self) -> pygame.Surface:
        return self.frames[self.index]

    def finished(self) -> bool:
        # True, если анимация НЕ цикличная и мы уже на последнем кадре
        return (not self.loop) and (self.index >= len(self.frames) - 1)
