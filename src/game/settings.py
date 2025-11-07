from pathlib import Path
import pygame

# --- Paths ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent               # .../src/game
PROJECT_ROOT = BASE_DIR.parent.parent                    # репозиторий корень
ASSETS_DIR = PROJECT_ROOT / "assets"

# Фон уровня (убедись, что файл действительно называется level1.png)
BACKGROUND_FILE = ASSETS_DIR / "images" / "backgrounds" / "level1.png"

# --- Window & timing -----------------------------------------------------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# --- World / Walkable area ----------------------------------------------
# Приземление игрока идёт на walkable_area.bottom — делаем низ зоны ровно 600.
GROUND_Y = 600
WALKABLE_AREA = pygame.Rect(
    20,   # left
    480,  # top (верх берега/дорожки)
    820,  # width
    120   # height -> 480 + 120 = 600 (низ зоны = земля)
)

# Дополнительный горизонтальный запас (если нужен кламп по X у врагов/камеры)
PLAYFIELD_MARGIN_X = 64

# --- Colors / UI ---------------------------------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

# Вернули UI-константы, которые импортирует gameplay.py (даже если сейчас не все используются)
UI_BTN_SIZE = (36, 28)
UI_GAP = 8
UI_BG = (230, 235, 239)   # фон старой панели/бэкграунд очистки
UI_RED = (245, 82, 82)
UI_DARK = (35, 38, 41)

# --- Sprites / Sheets ----------------------------------------------------
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
    "protect":  SAMURAI_DIR / "Protection.png",  # проверь точное имя файла
    "hurt":     SAMURAI_DIR / "Hurt.png",
    "dead":     SAMURAI_DIR / "Dead.png",
    "climb":    SAMURAI_DIR / "Climb.png",
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
    "protect":  ENEMY_DIR / "Protect.png",       # проверь точное имя файла
    "hurt":     ENEMY_DIR / "Hurt.png",
    "dead":     ENEMY_DIR / "Dead.png",
}

# --- Sprite slicing defaults --------------------------------------------
FRAME_WIDTH = 128
DEFAULT_SCALE = 2