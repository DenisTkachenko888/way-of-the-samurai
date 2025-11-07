from __future__ import annotations
import pygame, random
from typing import Dict, List
from .base import Character, Stats
from ..core.assets import load_image, slice_sheet
from ..settings import ENEMY_SHEETS, FRAME_WIDTH, DEFAULT_SCALE, GROUND_Y

class Enemy(Character):
    """
    Враг со state-машиной:
    - флаги is_attacking / is_blocking / is_hurt / is_dead / is_jumping
    - тайминги в миллисекундах (attack_cooldown, animation_speed)
    - урон наносится на кадре №2 текущей атаки
    - покадровая анимация, без системы Animation, но с нашим загрузчиком ассетов
    """

    def __init__(self, pos, target: Character):
        # базовые хара-ки: скорость, гравитация, прыжок
        super().__init__(pos, Stats(max_hp=200, speed=2, run_speed=4, gravity=1.0, jump_velocity=-12))
        x, y = pos

        # размер и ориентация
        self.scale = DEFAULT_SCALE
        self.facing_right = False

        # боевые параметры
        self.target = target
        self.death_time = None
        self.attack_damage = 20
        self.block_chance = 0.20

        # состояние
        self.state = "idle"  # [idle, walk, run, attack, jump, hurt, block, dead]
        self.is_attacking = False
        self.is_blocking  = False
        self.is_hurt      = False
        self.is_dead      = False
        self.is_jumping   = False

        # физика
        self.vertical_velocity = 0
        self.gravity = 1.0

        # тайминги (мс)
        self.attack_cooldown = 1850
        self.last_attack_time = 0
        self.animation_speed = 100
        self.animation_index = 0
        self.last_update = pygame.time.get_ticks()

        # кэши кадров
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

        self.current_frames = self.idle_frames
        self.image = self.current_frames[0]
        self.rect = self.image.get_rect(midbottom=(x, y))

        # фиксация направления трупа
        self.dead_facing_right = self.facing_right

    # ---------- загрузка кадров ----------
    def _load_frames(self, key: str) -> List[pygame.Surface]:
        """Грузим спрайт-лист из ENEMY_SHEETS и режем его на кадры шириной FRAME_WIDTH."""
        path = ENEMY_SHEETS[key]
        sheet = load_image(path)
        frames = slice_sheet(sheet, FRAME_WIDTH, self.scale)  # масштабируем по DEFAULT_SCALE
        return frames

    # ---------- апдейт ----------
    def update(self, dt: float):
        now = pygame.time.get_ticks()
        # вычисляем дистанцию по X
        distance = self.target.rect.centerx - self.rect.centerx
        abs_dist = abs(distance)
        direction = 1 if distance > 0 else -1

        # ориентация только если оба живы
        if not self.is_dead and not getattr(self.target, "is_dead", False):
            self.facing_right = direction > 0

        # === Death ===
        if self.is_dead:
            # проигрываем смерть, замораживаем на последнем кадре
            self.play_animation(self.dead_frames, loop=False)
            if self.animation_index >= len(self.dead_frames):
                self.image = self.dead_frames[-1]
            # гравитация
            if self.rect.bottom < GROUND_Y:
                self.vertical_velocity += self.gravity
                self.rect.y += int(self.vertical_velocity)
            else:
                self.rect.bottom = GROUND_Y
                self.vertical_velocity = 0
            # удаляем через 5 секунд
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

        # === Block randomly ===
        if not self.is_blocking and random.random() < 0.003:
            self.is_blocking = True
            self.is_guarding = True   # синхронизируем с базовым флагом
            self.state = "block"
            self.play_animation(self.protect_frames, loop=True)
            return

        if self.is_blocking:
            self.play_animation(self.protect_frames, loop=True)
            # шанс выйти из блока
            if random.random() < 0.01:
                self.is_blocking = False
                self.is_guarding = False
            return

        # === Jump randomly ===
        if not self.is_jumping and random.random() < 0.005:
            self.vertical_velocity = -12
            self.is_jumping = True

        # === Gravity ===
        if self.is_jumping:
            self.vertical_velocity += self.gravity
            self.rect.y += int(self.vertical_velocity)
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.is_jumping = False
                self.vertical_velocity = 0

        # === Decision by distance ===
        if abs_dist < 70:
            # очень близко — чуть отъедем назад
            self.state = "adjust"
            self.rect.x -= direction
            # и попытаемся атаковать
            self.start_attack()
        elif abs_dist < 100:
            # в зоне удара
            self.start_attack()
        else:
            # подход
            self.state = "run" if abs_dist > 200 else "walk"
            speed  = self.stats.run_speed if self.state == "run" else self.stats.speed
            frames = self.run_frames if self.state == "run" else self.walk_frames
            self.play_animation(frames)
            self.rect.x += direction * speed

        # контакт плечами — не толкать трупы
        if self.rect.colliderect(self.target.rect) and abs_dist < 40 and not self.is_dead:
            self.rect.x -= direction * 2

        # если цель умерла — просто стоим
        if getattr(self.target, "is_dead", False):
            self.play_animation(self.idle_frames)
            return

    # ---------- атака ----------
    def start_attack(self):
        now = pygame.time.get_ticks()
        if now - self.last_attack_time > self.attack_cooldown:
            self.current_frames = random.choice([
                self.attack1_frames, self.attack2_frames, self.attack3_frames
            ])
            self.is_attacking = True
            self.animation_index = 0
            self.last_update = now
            self.last_attack_time = now

    def perform_attack(self):
        """Покадрово проигрываем выбранный атлас атаки.
           На кадре #2 проверяем хитбокс и наносим урон.
        """
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.animation_speed:
            self.last_update = now
            self.animation_index += 1

            # ударный кадр
            if self.animation_index == 2:
                if self.rect.colliderect(self.target.rect):
                    # блок — у цели флаг is_guarding
                    if not getattr(self.target, "is_guarding", False):
                        if hasattr(self, 'scene'):
                            self.scene.trigger_hitstop(0.11)
                            self.scene.trigger_screenshake(7, 0.18)
                        self.target.take_damage(self.attack_damage)

            # конец анимации — выходим из атаки
            if self.animation_index >= len(self.current_frames):
                self.is_attacking = False
                self.animation_index = 0

        # выставляем текущий кадр
        if self.animation_index < len(self.current_frames):
            self.image = self.current_frames[self.animation_index]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

    # ---------- анимация ----------
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

        # применяем кадр
        self.image = self.current_frames[self.animation_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    # ---------- получение урона ----------
    def take_damage(self, amount: int):
        if self.is_dead:
            return
        # No screenshake here: only player getting hurt triggers shake
        # шанс поймать в блок
        if random.random() < self.block_chance:
            self.is_blocking = True
            self.is_guarding = True   # для совместимости с базовым уроном
            return

        # реальный урон с учётом базового флага is_guarding
        if self.is_blocking or self.is_guarding:
            amount = int(amount * 0.25)

        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            self.death_time = pygame.time.get_ticks()
            # фиксируем сторону, чтобы труп не переворачивался
            self.dead_facing_right = self.facing_right
        else:
            self.is_hurt = True
            self.animation_index = 0
