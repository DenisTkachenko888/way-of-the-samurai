from __future__ import annotations
from pathlib import Path
import pygame
from functools import lru_cache

def _try_paths(path: Path):
    # Fallbacks if user has slightly different paths
    candidates = [path]
    if "sprites" in str(path) and "assets" not in str(path):
        candidates.append(Path("assets") / path.name)  # fallback
    return candidates

@lru_cache(maxsize=256)
def load_image(path: Path, *, scale: tuple[int, int] | None = None) -> pygame.Surface:
    try:
        surf = pygame.image.load(str(path)).convert_alpha()
        if scale:
            surf = pygame.transform.smoothscale(surf, scale)
        return surf
    except Exception:
        # Fallback-плейсхолдер, если файла нет
        w, h = scale if scale else (128, 128)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((40, 40, 40))
        pygame.draw.rect(surf, (200, 60, 60), surf.get_rect(), 3)
        try:
            font = pygame.font.Font(None, 18)
            text = font.render(Path(path).name, True, (230, 230, 230))
            surf.blit(text, text.get_rect(center=surf.get_rect().center))
        except Exception:
            pass
        return surf

def slice_sheet(sheet: pygame.Surface, frame_width: int, scale: int = 2):
    sw, sh = sheet.get_size()
    frames = []
    for i in range(sw // frame_width):
        rect = pygame.Rect(i * frame_width, 0, frame_width, sh)
        frame = sheet.subsurface(rect)
        if scale != 1:
            frame = pygame.transform.scale(frame, (frame_width * scale, sh * scale))
        frames.append(frame)
    return frames
