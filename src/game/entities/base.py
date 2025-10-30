from __future__ import annotations
import pygame
from dataclasses import dataclass


@dataclass
class Stats:
    max_hp: int = 100
    speed: int = 4
    gravity: float = 1.0
    jump_velocity: float = -10.0
    run_speed: int = 10


class Character(pygame.sprite.Sprite):
    def __init__(self, pos, stats: Stats):
        super().__init__()
        self.stats = stats

        # базовый спрайт-заглушка, потом будет заменён анимацией
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midbottom=pos)

        # состояние
        self.hp = stats.max_hp
        self.facing_right = True
        self.vertical_velocity = 0.0
        self.is_dead = False
        self.is_hurt = False
        self.is_jumping = False
        self.is_guarding = False

        # фиксируем сторону смерти
        self.dead_facing_right = True

    def take_damage(self, amount: int):
        """Базовая версия урона (враги могут просто использовать это)."""
        if self.is_dead:
            return

        if self.is_guarding:
            # блок снижает урон
            amount = int(amount * 0.25)

        self.hp -= amount
        self.is_hurt = True

        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            self.dead_facing_right = self.facing_right


def clamp_sprite_to_screen(
    sprite: Character,
    world_w: int,
    margin_x: int,
):
    """
    Ограничивает объект ТОЛЬКО по X,
    чтобы он не убежал слишком далеко за мир.
    НИКАКОЙ коррекции по Y — это важно для свободы по берегу.
    """
    left_bound = -margin_x
    right_bound = world_w + margin_x

    if sprite.rect.left < left_bound:
        sprite.rect.left = left_bound
    if sprite.rect.right > right_bound:
        sprite.rect.right = right_bound