from pathlib import Path
import pygame

# Window & timing
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60
WALKABLE_AREA = pygame.Rect(
    20,   # x левого края зоны берега
    480,  # y верхней границы берега (ОБРАТИ ВНИМАНИЕ: тут подбери под свой фон; я ставлю 480 как ты просил чтобы не в воду)
    820,  # ширина доступной полосы
    140   # высота полосы (горизонтальная "дорожка", по которой можно гулять вверх/вниз)
)
# --- Playfield ---
PLAYFIELD_MARGIN_X = 64  # на столько пикселей разрешаем «заходить» за края

# --- UI colors/sizes ---
UI_BTN_SIZE = (36, 28)  # ширина, высота
UI_GAP = 8  # зазор между кнопками
UI_BG = (230, 235, 239)  # фон панели (как на скрине)
UI_RED = (245, 82, 82)  # красная кнопка
UI_DARK = (35, 38, 41)  # тёмные иконки

# World
GROUND_Y = 600  # bottom line for characters

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

# Paths
ROOT = Path(__file__).resolve().parents[2]  # .../WayOfTheSamurai
ASSETS = ROOT / "assets"

# Background
BACKGROUND_FILE = ASSETS / "background.png"

# Samurai sprite sheets
SAMURAI_DIR = ASSETS / "samurai_sprites"
SAMURAI_SHEETS = {
    "idle": SAMURAI_DIR / "Idle.png",
    "walk": SAMURAI_DIR / "Walk.png",
    "run": SAMURAI_DIR / "Run.png",
    "jump": SAMURAI_DIR / "Jump.png",
    "attack1": SAMURAI_DIR / "Attack_1.png",
    "attack2": SAMURAI_DIR / "Attack_2.png",
    "attack3": SAMURAI_DIR / "Attack_3.png",
    "protect": SAMURAI_DIR / "Protection.png",
    "hurt": SAMURAI_DIR / "Hurt.png",
    "dead": SAMURAI_DIR / "Dead.png",
    "climb": SAMURAI_DIR / "Climb.png",
}

# Enemy sprite sheets
ENEMY_DIR = ASSETS / "enemy_sprites"
ENEMY_SHEETS = {
    "idle": ENEMY_DIR / "Idle.png",
    "walk": ENEMY_DIR / "Walk.png",
    "run": ENEMY_DIR / "Run.png",
    "jump": ENEMY_DIR / "Jump.png",
    "attack1": ENEMY_DIR / "Attack_1.png",
    "attack2": ENEMY_DIR / "Attack_2.png",
    "attack3": ENEMY_DIR / "Attack_3.png",
    "protect": ENEMY_DIR / "Protect.png",
    "hurt": ENEMY_DIR / "Hurt.png",
    "dead": ENEMY_DIR / "Dead.png",
}

# Sprite slicing defaults
FRAME_WIDTH = 128
DEFAULT_SCALE = 2
