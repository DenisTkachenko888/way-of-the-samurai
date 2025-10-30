from __future__ import annotations
import pygame
from typing import Dict
from .base import Character, Stats
from ..core.assets import load_image, slice_sheet
from ..core.animation import Animation
from ..settings import SAMURAI_SHEETS, FRAME_WIDTH, DEFAULT_SCALE

# кадр удара и нанесённый урон
ATTACK_HITS = {
    "attack1": (2, 25),
    "attack2": (2, 35),
    "attack3": (2, 45),
}

# ВАЖНО: доступная зона "берега"
# Настрой эти цифры под фон (y и height = толщина полосы по вертикали)
walkable_area = pygame.Rect(
    20,   # x начала берега
    550,  # верхняя граница берега (уменьшай это число чтобы разрешить ходить выше)
    820,  # ширина зоны
    100,  # высота зоны (увеличивай чтобы сделать "полосу берега" толще)
)


class Samurai(Character):
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

        # анимации и состояние
        self.animations: Dict[str, Animation] = {}
        self.current = "idle"
        self.state = "idle"

        self.load_animations()
        self.speed = self.stats.speed
        self.last_attack_name = None

        self.guard_flash_ms = 120
        self.guard_flash_until = 0

        self.dead_facing_right = True

        # катание/ролл (заложено на будущее)
        self.is_rolling = False
        self.roll_timer = 0
        self.roll_cooldown = 0
        self.roll_dir = 1
        self.roll_length_ms = 300

        # прыжок / физика
        self.is_jumping = False
        self.vertical_velocity = 0
        self.jump_velocity = -11      # стартовая скорость вверх
        self.gravity = 0.9            # ускорение вниз

        # вспомогательные таймеры, могут быть использованы если хочешь variable jump,
        # но сейчас не критично
        self.jump_buffer_ms = 90
        self.jump_buffer_timer = 0
        self.max_jump_time = 220
        self.jump_time_left = 0
        self.jump_gravity_up = 0.7
        self.jump_gravity_down = 1.3

    # ----------------------------
    # Animation setup
    # ----------------------------
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
                    ms_per_frame=120,
                    loop=(key not in {"dead", "hurt", "attack1", "attack2", "attack3"}),
                )

        # image и rect должны существовать после загрузки анимаций
        self.image = self.animations["idle"].current_frame()
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        self.dead_facing_right = self.facing_right

    def set_state(self, name: str, reset=True):
        if self.current != name:
            self.current = name
            if reset:
                self.animations[name].reset()

    # ----------------------------
    # Combat / guard / roll
    # ----------------------------
    def guard(self, flag: bool):
        self.is_guarding = flag
        if flag:
            self.set_state("protect")
            self.guard_flash_until = 0  # пока просто держим первый кадр защиты

    def attack(self, kind: str):
        if self.is_dead:
            return
        if kind not in ("attack1", "attack2", "attack3"):
            return
        # не прерываем текущую атаку пока она не доиграла
        if (
            self.current in ("attack1", "attack2", "attack3")
            and not self.animations[self.current].finished()
        ):
            return

        self.set_state(kind, reset=True)
        self.last_attack_name = kind

    def start_roll(self, direction=1):
        if not self.is_rolling and self.roll_cooldown <= 0 and not self.is_dead:
            self.is_rolling = True
            self.roll_timer = self.roll_length_ms
            self.roll_dir = direction
            self.set_state("roll" if "roll" in self.animations else "walk")
            self.is_guarding = False

    # ----------------------------
    # Movement / Jump / Physics
    # ----------------------------
    def move(self, dx, dy):
        """
        Классическая beat'em up логика:
        - по X двигаемся всегда (dx * speed)
        - по Y двигаемся ТОЛЬКО если мы не в прыжке
          и если наши "ноги" после движения останутся в walkable_area.
        """
        move_y = 0 if self.is_jumping else dy * self.speed
        move_x = dx * self.speed

        future_rect = self.rect.copy()
        future_rect.x += move_x
        future_rect.y += move_y

        feet_rect = pygame.Rect(
            future_rect.centerx - 5,
            future_rect.bottom - 5,
            10,
            5,
        )

        if walkable_area.colliderect(feet_rect):
            self.rect = future_rect
        else:
            # если не можем сдвинуться по диагонали,
            # попробуем хотя бы чисто по X (чтобы не застревать)
            future_rect_only_x = self.rect.copy()
            future_rect_only_x.x += move_x

            feet_rect_only_x = pygame.Rect(
                future_rect_only_x.centerx - 5,
                future_rect_only_x.bottom - 5,
                10,
                5,
            )

            if walkable_area.colliderect(feet_rect_only_x):
                self.rect = future_rect_only_x
            # иначе не двигаем вообще

    def jump(self):
        """
        Прыжок: задаём вертикальную скорость вверх.
        Никаких h_dir/v_dir больше нет.
        """
        if not self.is_jumping and not self.is_dead:
            # проверяем, что старт прыжка имеет смысл (мы стоим ногами на земле зоны)
            temp_rect = self.rect.copy()
            temp_rect.y += self.jump_velocity
            feet_rect = pygame.Rect(
                temp_rect.centerx - 5,
                temp_rect.bottom - 5,
                10,
                5,
            )
            if walkable_area.colliderect(feet_rect):
                self.is_jumping = True
                self.vertical_velocity = self.jump_velocity
                self.set_state("jump")

    # ----------------------------
    # Update per frame
    # ----------------------------
    def update(
        self,
        dt: float,
        input_dir=(0, 0),
        running=False,
        jump_pressed=False,
        jump_held=False,
        jump_released=False,
    ):
        ms = int(dt * 1000)

        dx, dy = input_dir

        # В полёте (is_jumping == True) движение по Y руками запрещено,
        # но по X можно рулить, как в файтингах / beat'em up.
        # На земле (is_jumping == False) можно двигаться по Y внутри зоны.

        if jump_pressed:
            # (jump() уже вызывается в сцене, но оставим на случай,
            # если потом будешь вызывать только отсюда)
            self.jump()

        if self.is_jumping and not self.is_dead:
            # --- ВОЗДУХ ---
            old_rect = self.rect.copy()

            # полёт по вертикали
            self.rect.y += int(self.vertical_velocity)

            # проверка "ног" после смещения
            feet_rect = pygame.Rect(
                self.rect.centerx - 5,
                self.rect.bottom - 5,
                10,
                5,
            )

            if not walkable_area.colliderect(feet_rect):
                # Вылетели за пределы зоны -> отменяем это смещение,
                # считаем что упёрлись
                self.rect = old_rect
                self.vertical_velocity = 0
                self.is_jumping = False
            else:
                # продолжаем падать
                self.vertical_velocity += self.gravity

            # Приземление: если мы двигаемся вниз и дойдём до низа зоны
            if self.vertical_velocity > 0 and walkable_area.colliderect(feet_rect):
                if self.rect.bottom + int(self.vertical_velocity) >= walkable_area.bottom:
                    self.rect.bottom = walkable_area.bottom
                    self.vertical_velocity = 0
                    self.is_jumping = False

        elif self.is_dead:
            self.set_state("dead")

        elif self.is_hurt:
            self.set_state("hurt")

        elif self.is_guarding:
            self.set_state("protect")

        elif self.current.startswith("attack"):
            # во время удара не меняем состояние тут
            pass

        else:
            # --- НА ЗЕМЛЕ ---
            run_flag = running and not self.is_jumping
            self.move(dx, dy)

            if dx != 0 or dy != 0:
                # бег / ходьба
                self.speed = self.stats.run_speed if run_flag else self.stats.speed
                self.set_state("run" if run_flag else "walk")
            else:
                self.set_state("idle")

        # направление спрайта (flip)
        dx, _ = input_dir
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

        # --- Анимация ---
        anim = self.animations[self.current]
        prev_index = anim.index
        anim.update(dt)
        frame = anim.current_frame()

        # логика выхода из "hurt"
        if self.current == "hurt":
            if not hasattr(self, "hurt_until"):
                self.hurt_until = 0
            now = pygame.time.get_ticks()
            if (self.hurt_until and now >= self.hurt_until) or self.animations["hurt"].finished():
                self.is_hurt = False
                self.hurt_until = 0
                self.set_state("protect" if self.is_guarding else "idle")

        # если умер - зафиксируем сторону
        if self.is_dead:
            self.facing_right = self.dead_facing_right

        # защита: моргнём вторым кадром на короткое время
        if self.current == "protect":
            protect_frames = self.animations["protect"].frames
            now = pygame.time.get_ticks()
            if (
                self.guard_flash_until
                and now < self.guard_flash_until
                and len(protect_frames) > 1
            ):
                frame = protect_frames[1]
            else:
                frame = protect_frames[0]
                self.guard_flash_until = 0

        # попадание по врагу в нужном кадре
        if self.current in ATTACK_HITS:
            hit_frame, damage = ATTACK_HITS[self.current]
            if prev_index < hit_frame <= anim.index:
                self._apply_attack_damage(damage)

        # выход из атаки после окончания анимации
        if (
            self.current in ("attack1", "attack2", "attack3")
            and self.animations[self.current].finished()
        ):
            self.set_state("protect" if self.is_guarding else "idle")

        # финальный кадр (+флип, если смотрим влево)
        self.image = (
            frame if self.facing_right else pygame.transform.flip(frame, True, False)
        )

    def _apply_attack_damage(self, damage: int):
        hitbox = self.rect.inflate(10, 10)
        for enemy in list(self.enemies):
            if hitbox.colliderect(enemy.rect):
                if hasattr(self, "scene"):
                    # только hitstop, без screenshake
                    self.scene.trigger_hitstop(0.09)
                enemy.take_damage(damage)


    def take_damage(self, amount: int):
        if self.is_dead:
            return

        # визуальный фидбек игроку при попадании по нему
        if hasattr(self, "scene"):
            self.scene.trigger_hitstop(0.11)
            self.scene.trigger_screenshake(7, 0.18)

        # блок снижает урон
        if self.is_guarding:
            amount = max(1, int(amount * 0.25))

        self.hp -= amount
        self.is_hurt = True

        now = pygame.time.get_ticks()
        self.hurt_until = now + 250  # держать hurt состояние ~250 мс
        self.set_state("hurt", reset=True)

        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            try:
                self.dead_facing_right = self.facing_right
            except AttributeError:
                pass
