from pathlib import Path
import sys

import pygame


# === Paths ===================================================================
BASE_DIR = Path(__file__).resolve().parent  # .../src/game

def resolve_assets_dir() -> Path:
    """
    Priority:
    1) Frozen (PyInstaller): _internal/assets or sys._MEIPASS/assets or exe/assets
    2) Dev/source: repo_root/assets
    Fallback: repo_root/assets (even if missing) — do not crash on import.
    """
    # --- Frozen builds first (so packaged exe uses bundled files, not your repo files) ---
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent

        internal_assets = exe_dir / "_internal" / "assets"
        if internal_assets.exists():
            return internal_assets

        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            meipass_assets = Path(meipass) / "assets"
            if meipass_assets.exists():
                return meipass_assets

        exe_assets = exe_dir / "assets"
        if exe_assets.exists():
            return exe_assets

    # --- Dev/source ---
    repo_root = BASE_DIR.parents[1]          # .../src/game -> .../src -> repo_root
    repo_assets = repo_root / "assets"
    if repo_assets.exists():
        return repo_assets

    # --- Last resort: don't break pytest import ---
    return repo_assets

ASSETS_DIR = resolve_assets_dir()

BACKGROUND_FILE = ASSETS_DIR / "images" / "backgrounds" / "level1.png"

# === Window & timing =========================================================
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# === World / Walkable area ===================================================
# Приземление идёт на WALKABLE_AREA.bottom, который привязан к "земле".
GROUND_Y = 600  # нижняя линия "земли" (экранный низ)

# Дорожка belt-scroller. Чтобы верх остался как раньше (~y=550), берём высоту 50.
WALKABLE_MARGIN_X = 20
WALKABLE_HEIGHT = 50  # было ощущение «ниже» — уменьшаем высоту, верх = 600-50 = 550

WALKABLE_AREA = pygame.Rect(
    WALKABLE_MARGIN_X,
    GROUND_Y - WALKABLE_HEIGHT,              # верх = земля минус высота дорожки
    SCREEN_WIDTH - 2 * WALKABLE_MARGIN_X,    # ширина с полями слева/справа
    WALKABLE_HEIGHT,
)

# Запас по X для клампа врагов/камеры (если используешь)
PLAYFIELD_MARGIN_X = 64

# === Colors / UI =============================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

# Константы UI (некоторые могут не использоваться прямо сейчас, оставим для совместимости)
UI_BTN_SIZE = (36, 28)
UI_GAP = 8
UI_BG = (230, 235, 239)
UI_RED = (245, 82, 82)
UI_DARK = (35, 38, 41)

# === Sprites / Sheets ========================================================
# Фактическая структура:
# assets/images/sprites/samurai_sprites/*.png
# assets/images/sprites/enemy_sprites/*.png

SAMURAI_DIR = ASSETS_DIR / "images" / "sprites" / "samurai_sprites"
SAMURAI_SHEETS = {
    "idle":     SAMURAI_DIR / "Idle.png",
    "walk":     SAMURAI_DIR / "Walk.png",
    "run":      SAMURAI_DIR / "Run.png",
    "jump":     SAMURAI_DIR / "Jump.png",
    "attack1":  SAMURAI_DIR / "Attack_1.png",
    "attack2":  SAMURAI_DIR / "Attack_2.png",
    "attack3":  SAMURAI_DIR / "Attack_3.png",
    "protect":  SAMURAI_DIR / "Protection.png",  
    "hurt":     SAMURAI_DIR / "Hurt.png",
    "dead":     SAMURAI_DIR / "Dead.png",
}

ENEMY_DIR = ASSETS_DIR / "images" / "sprites" / "enemy_sprites"
ENEMY_SHEETS = {
    "idle":     ENEMY_DIR / "Idle.png",
    "walk":     ENEMY_DIR / "Walk.png",
    "run":      ENEMY_DIR / "Run.png",
    "jump":     ENEMY_DIR / "Jump.png",
    "attack1":  ENEMY_DIR / "Attack_1.png",
    "attack2":  ENEMY_DIR / "Attack_2.png",
    "attack3":  ENEMY_DIR / "Attack_3.png",
    "protect":  ENEMY_DIR / "Protect.png",       
    "hurt":     ENEMY_DIR / "Hurt.png",
    "dead":     ENEMY_DIR / "Dead.png",
}

# === Sprite slicing defaults =================================================
FRAME_WIDTH = 128
DEFAULT_SCALE = 2
