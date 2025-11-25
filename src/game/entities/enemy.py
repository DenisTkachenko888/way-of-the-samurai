from __future__ import annotations
import pygame, random
from typing import List

from .base import Character, Stats
from ..core.assets import load_image, slice_sheet
from ..settings import (
    ENEMY_SHEETS,
    FRAME_WIDTH,
    DEFAULT_SCALE,
    WALKABLE_AREA,  # используем полосу-«желоб» как землю
)


class Enemy(Character):
    """
    Враг с простой ИИ и belt-scroller-физикой:
      • На ЗЕМЛЕ можно смещаться по X и по Y (в пределах WALKABLE_AREA);
      • Прыжок разрешён в ЛЮБОЙ точке полосы; приземление — на базовую линию старта;
      • В воздухе: свободный X с ослаблением (air-control), Y — по «воздушной оси»;
      • Атаки работают и в воздухе; ударный кадр №2 наносит урон;
      • Блок с небольшим шансом; труп не разворачивается.
    """

    # ---- настройки поведения/скоростей -------------------------------------
    AIR_CONTROL_X = 0.55          # насколько хорошо рулить по X в воздухе (0..1)
    APPROACH_Y_GAIN = 0.75        # множитель «шага» по Y к цели на земле
    ATTACK_RANGE_X = 100          # дальность, на которой можно начинать атаку по X
    ALIGN_Y_TOLERANCE = 8         # точность выравнивания по глубине (Y) на земле

    def __init__(self, pos, target: Character):
        super().__init__(
            pos,
            Stats(
                max_hp=200,
                speed=2,
                run_speed=4,
                gravity=0.9,
                jump_velocity=-11.0,
            ),
        )

        self.target = target
        self.scale = DEFAULT_SCALE
        self.facing_right = False

        # Боевые параметры/состояние
        self.attack_damage = 20
        self.block_chance = 0.20

        self.state = "idle"
        self.is_attacking = False
        self.is_blocking = False
        self.is_hurt = False
        self.is_dead = False
        self.is_jumping = False

        # Вертикальная физика
        self.vertical_velocity = 0.0
        self._jump_baseline_bottom = float(pos[1])  # куда вернёмся при приземлении
        self._air_offset = 0.0

        # Тайминги (мс)
        self.attack_cooldown = 1850
        self.last_attack_time = 0
        self.animation_speed = 100
        self.animation_index = 0
        self.last_update = pygame.time.get_ticks()

        # Кэши кадров
        self.idle_frames:    List[pygame.Surface] = self._load_frames("idle")
        self.walk_frames:    List[pygame.Surface] = self._load_frames("walk")
        self.run_frames:     List[pygame.Surface] = self._load_frames("run")
        self.jump_frames:    List[pygame.Surface] = self._load_frames("jump")
        self.attack1_frames: List[pygame.Surface] = self._load_frames("attack1")
        self.attack2_frames: List[pygame.Surface] = self._load_frames("attack2")
        self.attack3_frames: List[pygame.Surface] = self._load_frames("attack3")
        self.protect_frames: List[pygame.Surface] = self._load_frames("protect")
        self.hurt_frames:    List[pygame.Surface] = self._load_frames("hurt")
        self.dead_frames:    List[pygame.Surface] = self._load_frames("dead")

        # Текущий атлас/кадр
        self.current_frames = self.idle_frames
        self.image = self.current_frames[0]
        self.rect = self.image.get_rect(midbottom=pos)

        # “труп не поворачивается”
        self.dead_facing_right = self.facing_right
        self.death_time = None

    # ---- utils --------------------------------------------------------------
    def _load_frames(self, key: str) -> List[pygame.Surface]:
        sheet = load_image(ENEMY_SHEETS[key])
        return slice_sheet(sheet, FRAME_WIDTH, self.scale)

    def _feet_rect(self) -> pygame.Rect:
        return pygame.Rect(self.rect.centerx - 3, self.rect.bottom - 3, 6, 3)

    def on_ground_lane(self) -> bool:
        """Стоим на земле, если ноги внутри полосы и не в прыжке."""
        return (not self.is_jumping) and WALKABLE_AREA.colliderect(self._feet_rect())

    # ---- главный апдейт -----------------------------------------------------
    def update(self, dt: float):
        now = pygame.time.get_ticks()

        # Если цель жива — смотреть в её сторону (по X)
        if not self.is_dead and not getattr(self.target, "is_dead", False):
            self.facing_right = self.target.rect.centerx > self.rect.centerx

        # === Death ===
        if self.is_dead:
            # проигрываем смерть, «падаем» до низа полосы
            self.play_animation(self.dead_frames, loop=False)
            if self.rect.bottom < WALKABLE_AREA.bottom:
                self.vertical_velocity += self.stats.gravity
                self.rect.bottom = min(
                    WALKABLE_AREA.bottom,
                    int(self.rect.bottom + self.vertical_velocity),
                )
            else:
                self.rect.bottom = WALKABLE_AREA.bottom
                self.vertical_velocity = 0.0

            if self.death_time and now - self.death_time > 5000:
                self.kill()
            return

        # === Hurt ===
        if self.is_hurt:
            self.play_animation(self.hurt_frames, loop=False)
            if self.animation_index >= len(self.hurt_frames) - 1:
                self.is_hurt = False
            return

        # === Attack in progress ===
        if self.is_attacking:
            self.perform_attack()
            return

        # === (Редкий) блок ---------------------------------------------------
        if not self.is_blocking and random.random() < 0.003:
            self.is_blocking = True
            self.is_guarding = True
            self.state = "block"
            self.play_animation(self.protect_frames, loop=True)
            return

        if self.is_blocking:
            self.play_animation(self.protect_frames, loop=True)
            if random.random() < 0.01:  # шанс снять блок
                self.is_blocking = False
                self.is_guarding = False
            return

        # === Прыжок (случайный, для разнообразия) ---------------------------
        if not self.is_jumping and random.random() < 0.004 and self.on_ground_lane():
            self._start_jump()

        # === ВОЗДУХ ----------------------------------------------------------
        if self.is_jumping:
            self._update_air(dt)
            # в воздухе тоже можно атаковать (редко)
            if random.random() < 0.004:
                self.start_attack()
            return

        # === ЗЕМЛЯ: решение по расстоянию -----------------------------------
        dist_x = self.target.rect.centerx - self.rect.centerx
        abs_dx = abs(dist_x)

        # небольшой подъезд/уход по Y, чтобы сойтись по «глубине» с игроком
        dy = 0
        delta_bottom = self.target.rect.bottom - self.rect.bottom
        if abs(delta_bottom) > self.ALIGN_Y_TOLERANCE:
            step = int(self.stats.speed * self.APPROACH_Y_GAIN)
            dy = max(-step, min(step, 1 if delta_bottom > 0 else -1))

        # зона удара — атакуем
        if abs_dx < self.ATTACK_RANGE_X:
            self.start_attack()
            # немного подравняем положение по X, чтобы не «липнуть»
            if abs_dx < 40:
                self.rect.x -= 1 if dist_x > 0 else -1
            # в это же время можно чуть сведить по Y
            if dy != 0:
                self._move_ground(0, dy)
            return

        # подход: бег или шаг
        run = abs_dx > 220
        frames = self.run_frames if run else self.walk_frames
        speed = self.stats.run_speed if run else self.stats.speed
        dx = speed if dist_x > 0 else -speed

        self.play_animation(frames, loop=True)
        self._move_ground(dx, dy)

        # если цель умерла — просто стоим
        if getattr(self.target, "is_dead", False):
            self.play_animation(self.idle_frames)
            return

    # ---- прыжок/воздух ------------------------------------------------------
    def _start_jump(self):
        self.is_jumping = True
        self.vertical_velocity = self.stats.jump_velocity
        self._jump_baseline_bottom = float(self.rect.bottom)
        self._air_offset = 0.0
        # отображаем прыжковые кадры (если есть)
        if self.jump_frames:
            self.current_frames = self.jump_frames
            self.animation_index = 0
            self.last_update = pygame.time.get_ticks()

    def _update_air(self, dt: float):
        # X: ослабленный контроль
        # (враг старается тянуться к игроку даже в воздухе)
        vx = (self.stats.run_speed if self.facing_right else -self.stats.run_speed)
        # корректнее: лететь в сторону цели
        to_target = 1 if self.target.rect.centerx > self.rect.centerx else -1
        self.rect.x += int(to_target * self.stats.run_speed * self.AIR_CONTROL_X)

        # «воздушная» ось Y
        self._air_offset += self.vertical_velocity
        self.vertical_velocity += self.stats.gravity
        self.rect.bottom = int(self._jump_baseline_bottom + self._air_offset)

        # приземление на базовую линию
        if self.vertical_velocity > 0 and self._air_offset >= 0:
            self.rect.bottom = int(self._jump_baseline_bottom)
            self._air_offset = 0.0
            self.vertical_velocity = 0.0
            self.is_jumping = False

        # кламп ног в полосу (на всякий случай от дрожания)
        feet = self._feet_rect()
        if not WALKABLE_AREA.colliderect(feet):
            # если вылетели за верх/низ — прижмёмся к ближайшей кромке
            if feet.top < WALKABLE_AREA.top:
                overshoot = WALKABLE_AREA.top - feet.top
                self.rect.y += overshoot
            elif feet.bottom > WALKABLE_AREA.bottom:
                overshoot = feet.bottom - WALKABLE_AREA.bottom
                self.rect.y -= overshoot

        # анимация прыжка
        if self.jump_frames:
            self.play_animation(self.jump_frames, loop=True)

    # ---- земля: перемещение с проверкой «ног» -------------------------------
    def _move_ground(self, dx: int, dy: int):
        """Смещение на земле с валидацией «ног» в пределах WALKABLE_AREA."""
        future = self.rect.copy()
        future.x += dx
        future.y += dy

        feet = pygame.Rect(future.centerx - 3, future.bottom - 3, 6, 3)
        if WALKABLE_AREA.colliderect(feet):
            self.rect = future
        else:
            # хотя бы по X, чтобы не «липнуть» у верх/ниж кромки
            future_x = self.rect.copy()
            future_x.x += dx
            feet_x = pygame.Rect(future_x.centerx - 3, future_x.bottom - 3, 6, 3)
            if WALKABLE_AREA.colliderect(feet_x):
                self.rect = future_x
            else:
                # или хотя бы по Y
                future_y = self.rect.copy()
                future_y.y += dy
                feet_y = pygame.Rect(future_y.centerx - 3, future_y.bottom - 3, 6, 3)
                if WALKABLE_AREA.colliderect(feet_y):
                    self.rect = future_y

    # ---- атака ---------------------------------------------------------------
    def start_attack(self):
        now = pygame.time.get_ticks()
        if now - self.last_attack_time > self.attack_cooldown:
            self.current_frames = random.choice(
                [self.attack1_frames, self.attack2_frames, self.attack3_frames]
            )
            self.is_attacking = True
            self.animation_index = 0
            self.last_update = now
            self.last_attack_time = now

    def perform_attack(self):
        """Покадрово проигрываем выбранный атлас атаки. На кадре #2 — хит."""
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.animation_speed:
            self.last_update = now
            self.animation_index += 1

            # ударный кадр
            if self.animation_index == 2:
                if self.rect.colliderect(self.target.rect):
                    # у цели может быть блок (is_guarding)
                    if not getattr(self.target, "is_guarding", False):
                        if hasattr(self, "scene"):
                            self.scene.trigger_hitstop(0.11)
                            self.scene.trigger_screenshake(7, 0.18)
                        self.target.take_damage(self.attack_damage)

            # конец анимации
            if self.animation_index >= len(self.current_frames):
                self.is_attacking = False
                self.animation_index = 0

        # выставляем текущий кадр
        if self.animation_index < len(self.current_frames):
            frame = self.current_frames[self.animation_index]
        else:
            frame = self.current_frames[-1]

        self.image = frame if self.facing_right else pygame.transform.flip(frame, True, False)

    # ---- общий проигрыватель анимаций ---------------------------------------
    def play_animation(self, frames: List[pygame.Surface], loop: bool = True):
        if self.current_frames is not frames:
            self.current_frames = frames
            self.animation_index = 0
            self.last_update = pygame.time.get_ticks()

        now = pygame.time.get_ticks()
        if now - self.last_update >= self.animation_speed:
            self.last_update = now
            self.animation_index += 1
            if self.animation_index >= len(frames):
                self.animation_index = 0 if loop else len(frames) - 1

        frame = self.current_frames[self.animation_index]
        self.image = frame if self.facing_right else pygame.transform.flip(frame, True, False)

    # ---- получение урона -----------------------------------------------------
    def take_damage(self, amount: int):
        if self.is_dead:
            return

        # шанс «словить» удар блоком
        if random.random() < self.block_chance:
            self.is_blocking = True
            self.is_guarding = True
            return

        # реальный урон (учитываем блок)
        if self.is_blocking or self.is_guarding:
            amount = int(amount * 0.25)

        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            self.death_time = pygame.time.get_ticks()
            self.dead_facing_right = self.facing_right
            # при смерти прижмём к «земле» полосы
            if self.rect.bottom < WALKABLE_AREA.bottom:
                self.vertical_velocity = 0.0  # дальше update дольёт до низа
        else:
            self.is_hurt = True
            self.animation_index = 0
