from __future__ import annotations
import pygame
from typing import Dict

from .base import Character, Stats
from ..core.assets import load_image, slice_sheet
from ..core.animation import Animation
from ..settings import (
    SAMURAI_SHEETS,
    FRAME_WIDTH,
    DEFAULT_SCALE,
    WALKABLE_AREA,   # земля = вся полоса; прыжок можно начать в любой её точке
)

# --- кадры урона по анимациям -----------------------------------------------
ATTACK_HITS = {
    "attack1": (2, 25),
    "attack2": (2, 35),
    "attack3": (2, 45),
}


class Samurai(Character):
    """
    Игрок: бег, ходьба в «желобе», прыжок с базовой линией, блок и атаки.
    Модель прыжка belt-scroller:
      • на земле считаемся стоящими, если «ноги» внутри WALKABLE_AREA;
      • старт прыжка возможен в любом Y полосы;
      • в воздухе рулём по X (air-control), по Y летим по физике;
      • приземляемся НА ТОТ ЖЕ базовый Y, с которого оттолкнулись.
    """

    def __init__(self, pos, enemies_group: pygame.sprite.Group):
        super().__init__(
            pos,
            Stats(
                max_hp=100,
                speed=4,
                run_speed=10,
                gravity=0.9,
                jump_velocity=-11,
            ),
        )
        self.enemies = enemies_group
        self.scale = DEFAULT_SCALE

        # Анимации/состояния
        self.animations: Dict[str, Animation] = {}
        self.current = "idle"
        self.state = "idle"
        self.load_animations()

        self.speed = self.stats.speed
        self.last_attack_name = None

        # Блок/фидбек
        self.guard_flash_ms = 120
        self.guard_flash_until = 0

        # “Труп не поворачивается”
        self.dead_facing_right = True

        # Ролл (на будущее)
        self.is_rolling = False
        self.roll_timer = 0
        self.roll_cooldown = 0
        self.roll_dir = 1
        self.roll_length_ms = 300

        # Прыжок / физика
        self.is_jumping = False
        self.vertical_velocity = 0.0

        # Air-control: насколько хорошо рулить по X в воздухе (0..1)
        self.air_control = 0.65

        # Параметры прыжка
        self.jump_velocity = -11.0
        self.gravity = 0.9

        # Базовая линия и смещение по “воздушной оси”
        self._jump_baseline_bottom = float(self.rect.bottom)  # куда вернёмся
        self._air_offset = 0.0  # < 0 — в полёте вверх; растёт к 0 при падении

        # (опционально под variable jump; сейчас не критично)
        self.jump_buffer_ms = 90
        self.jump_buffer_timer = 0
        self.max_jump_time = 220
        self.jump_time_left = 0
        self.jump_gravity_up = 0.7
        self.jump_gravity_down = 1.3

    # ---------------------------- Animations ---------------------------------
    def load_animations(self):
        for key, path in SAMURAI_SHEETS.items():
            sheet = load_image(path)
            if key == "climb":
                frame_w = sheet.get_width() // 6
                frames = slice_sheet(sheet, frame_w, self.scale)
                self.animations[key] = Animation(frames, ms_per_frame=110, loop=True)
            else:
                frames = slice_sheet(sheet, FRAME_WIDTH, self.scale)
                self.animations[key] = Animation(
                    frames,
                    ms_per_frame=120,  # одинаковая скорость для всех, включая attack2
                    loop=(key not in {"dead", "hurt", "attack1", "attack2", "attack3"}),
                )

        self.image = self.animations["idle"].current_frame()
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        self.dead_facing_right = self.facing_right

    def set_state(self, name: str, reset: bool = True):
        if self.current != name:
            self.current = name
            if reset:
                self.animations[name].reset()

    # ---------------------------- Ground utils --------------------------------
    def _feet_rect(self) -> pygame.Rect:
        return pygame.Rect(self.rect.centerx - 3, self.rect.bottom - 3, 6, 3)

    def on_ground_lane(self) -> bool:
        """Стоим на земле, если ноги внутри полосы и мы не в прыжке."""
        return (not self.is_jumping) and WALKABLE_AREA.colliderect(self._feet_rect())

    # ---------------------------- Combat / Guard ------------------------------
    def guard(self, flag: bool):
        self.is_guarding = flag
        if flag:
            self.set_state("protect")
            self.guard_flash_until = 0

    def attack(self, kind: str):
        """Атаки разрешены и в воздухе; не прерываем текущую атаку до конца."""
        if self.is_dead or kind not in ("attack1", "attack2", "attack3"):
            return
        if (
            self.current in ("attack1", "attack2", "attack3")
            and not self.animations[self.current].finished()
        ):
            return

        self.set_state(kind, reset=True)
        self.last_attack_name = kind

    # ---------------------------- Move (ground) --------------------------------
    def move(self, dx: float, dy: float):
        """
        На земле:
          • по X двигаемся всегда;
          • по Y — только если «ноги» остаются внутри WALKABLE_AREA.
        """
        move_y = dy * self.speed
        move_x = dx * self.speed

        future = self.rect.copy()
        future.x += move_x
        future.y += move_y

        feet = pygame.Rect(future.centerx - 3, future.bottom - 3, 6, 3)

        if WALKABLE_AREA.colliderect(feet):
            self.rect = future
        else:
            # хотя бы по X (чтобы не застревать у верхней/нижней кромки)
            future_x = self.rect.copy()
            future_x.x += move_x
            feet_x = pygame.Rect(future_x.centerx - 3, future_x.bottom - 3, 6, 3)
            if WALKABLE_AREA.colliderect(feet_x):
                self.rect = future_x

    # ---------------------------- Jump ----------------------------------------
    def jump(self):
        """
        Старт прыжка возможен в любой точке «желоба», если стоим на земле.
        Приземлимся обратно на ту же базовую линию (bottom), откуда оттолкнулись.
        """
        if self.is_dead or self.is_jumping:
            return
        if not self.on_ground_lane():
            return  # не разрешаем дабл-джамп из воздуха

        self.is_jumping = True
        self.vertical_velocity = self.jump_velocity
        self._jump_baseline_bottom = float(self.rect.bottom)  # запомним «землю» старта
        self._air_offset = 0.0
        self.set_state("jump")

    # ---------------------------- Update --------------------------------------
    def update(
        self,
        dt: float,
        input_dir=(0, 0),
        running: bool = False,
        jump_pressed: bool = False,
        jump_held: bool = False,
        jump_released: bool = False,
    ):
        dx, dy = input_dir

        if jump_pressed:
            self.jump()

        if self.is_jumping and not self.is_dead:
            # --- ВОЗДУХ: свободный X (с ослаблением), полёт по «воздушной оси» ---
            speed_x = self.stats.run_speed if running else self.stats.speed
            self.rect.x += int(dx * speed_x * self.air_control)

            # вертикальная кинематика относительно базовой линии
            self._air_offset += self.vertical_velocity
            self.vertical_velocity += self.gravity

            # позиционируем спрайт: база + смещение
            self.rect.bottom = int(self._jump_baseline_bottom + self._air_offset)

            # перелёт базовой линии -> приземление
            if self.vertical_velocity > 0 and self._air_offset >= 0:
                self.rect.bottom = int(self._jump_baseline_bottom)
                self._air_offset = 0.0
                self.vertical_velocity = 0.0
                self.is_jumping = False

        elif self.is_dead:
            self.set_state("dead")

        elif self.is_hurt:
            self.set_state("hurt")

        elif self.is_guarding:
            self.set_state("protect")

        elif self.current.startswith("attack"):
            # даём доиграть атаке на земле
            pass

        else:
            # --- ЗЕМЛЯ ---------------------------------------------------------
            run_flag = running and not self.is_jumping
            self.speed = self.stats.run_speed if run_flag else self.stats.speed
            self.move(dx, dy)

            if dx != 0 or dy != 0:
                self.set_state("run" if run_flag else "walk")
            else:
                self.set_state("idle")

        # направление взгляда (flip)
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

        # --- Анимации / события ударов ----------------------------------------
        anim = self.animations[self.current]
        prev_index = anim.index
        anim.update(dt)
        frame = anim.current_frame()

        # выход из "hurt"
        if self.current == "hurt":
            if not hasattr(self, "hurt_until"):
                self.hurt_until = 0
            now = pygame.time.get_ticks()
            if (self.hurt_until and now >= self.hurt_until) or self.animations["hurt"].finished():
                self.is_hurt = False
                self.hurt_until = 0
                self.set_state("protect" if self.is_guarding else "idle")

        # “Труп” не разворачиваем
        if self.is_dead:
            self.facing_right = self.dead_facing_right

        # защита: короткий “миг” вторым кадром
        if self.current == "protect":
            protect_frames = self.animations["protect"].frames
            now = pygame.time.get_ticks()
            if self.guard_flash_until and now < self.guard_flash_until and len(protect_frames) > 1:
                frame = protect_frames[1]
            else:
                frame = protect_frames[0]
                self.guard_flash_until = 0

        # попадание в “ударном” кадре
        if self.current in ATTACK_HITS:
            hit_frame, damage = ATTACK_HITS[self.current]
            if prev_index < hit_frame <= anim.index:
                self._apply_attack_damage(damage)

        # простой выход из атаки после окончания анимации (одинаковый для 1/2/3)
        if (
            self.current in ("attack1", "attack2", "attack3")
            and self.animations[self.current].finished()
        ):
            self.set_state("protect" if self.is_guarding else "idle")

        # финальный кадр (+ флип)
        self.image = frame if self.facing_right else pygame.transform.flip(frame, True, False)

    # ---------------------------- Combat utils --------------------------------
    def _apply_attack_damage(self, damage: int):
        hitbox = self.rect.inflate(10, 10)
        for enemy in list(self.enemies):
            if hitbox.colliderect(enemy.rect):
                if hasattr(self, "scene"):
                    self.scene.trigger_hitstop(0.09)  # хруст без лишней тряски
                enemy.take_damage(damage)

    def take_damage(self, amount: int):
        if self.is_dead:
            return

        if hasattr(self, "scene"):
            self.scene.trigger_hitstop(0.11)
            self.scene.trigger_screenshake(7, 0.18)

        if self.is_guarding:
            amount = max(1, int(amount * 0.25))

        self.hp -= amount
        self.is_hurt = True

        now = pygame.time.get_ticks()
        self.hurt_until = now + 250
        self.set_state("hurt", reset=True)

        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            try:
                self.dead_facing_right = self.facing_right
            except AttributeError:
                pass
