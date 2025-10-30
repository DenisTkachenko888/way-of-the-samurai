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
def load_image(path: Path) -> pygame.Surface:
    for p in _try_paths(path):
        try:
            surf = pygame.image.load(str(p)).convert_alpha()
            return surf
        except Exception:
            continue
    raise FileNotFoundError(f"Image not found: {path}")

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
