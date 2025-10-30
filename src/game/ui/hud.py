import pygame
from ..settings import RED, GREEN, BLACK

def draw_health_bar(surface: pygame.Surface, x: int, y: int, hp: int, max_hp: int, w: int = 200, h: int = 18):
    ratio = max(0.0, min(1.0, hp / max_hp if max_hp else 0.0))
    bg_rect = pygame.Rect(x, y, w, h)
    hp_rect = pygame.Rect(x, y, int(w * ratio), h)
    pygame.draw.rect(surface, BLACK, bg_rect, border_radius=4)
    pygame.draw.rect(surface, RED, bg_rect.inflate(-2, -2), border_radius=4)
    pygame.draw.rect(surface, GREEN, hp_rect.inflate(-2, -2), border_radius=4)
