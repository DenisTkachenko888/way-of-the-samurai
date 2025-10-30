from __future__ import annotations
import pygame, random
from ..settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BACKGROUND_FILE,
    GROUND_Y,
    BLACK,
    PLAYFIELD_MARGIN_X,
    UI_BG,
)
from ..core.assets import load_image
from ..entities.samurai import Samurai
from ..entities.enemy import Enemy
from ..ui.hud import draw_health_bar
from ..gfx.camera import Camera
from ..entities.base import clamp_sprite_to_screen


class GameplayScene:
    def __init__(self, manager):
        self.manager = manager
        self.app = manager.app

        # игра активна
        self.running = True

        # показываем ли сейчас окно "выйти из игры? [Y/N]"
        self.paused_for_quit = False

        # --- Background ---
        bg = load_image(BACKGROUND_FILE)
        self.background = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # --- Sprite groups ---
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # --- World / camera ---
        # ВАЖНО: чтобы фон не рвался справа, ограничим мир шириной экрана
        self.world_width = SCREEN_WIDTH
        self.world_height = SCREEN_HEIGHT

        self.camera = Camera(
            world_width=self.world_width,
            world_height=self.world_height,
        )

        # --- Player ---
        self.player = Samurai((100, GROUND_Y), enemies_group=self.enemies)
        self.player.scene = self
        self.all_sprites.add(self.player)

        # --- One enemy for now ---
        e = Enemy((700, GROUND_Y), self.player)
        e.scene = self
        self.enemies.add(e)
        self.all_sprites.add(e)

        # --- HUD / fonts ---
        self.font = pygame.font.Font(None, 36)
        self.font_big = pygame.font.Font(None, 64)

        # feedback / juice
        self._hitstop_timer = 0.0
        self._screenshake_timer = 0.0
        self._screenshake_power = 0
        self._screenshake_offset = (0, 0)

        # jump edge-detect
        self._last_jump = False

    # -------------------------------------------------
    # EVENT HANDLING (INPUT)
    # -------------------------------------------------
    def handle_event(self, event: pygame.event.Event):
        # ESC логика:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if not self.paused_for_quit:
                # открыть модалку "выйти из игры?"
                self.paused_for_quit = True
            else:
                # уже была открыта -> закрыть модалку (отмена)
                self.paused_for_quit = False

        # если модалка открыта - слушаем Y/N
        if self.paused_for_quit and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                # да, выйти: гасим всё приложение
                self.running = False        # сцена больше не активна
                self.app.running = False    # попросим главный цикл остановиться
            elif event.key == pygame.K_n:
                # нет, продолжить игру
                self.paused_for_quit = False


    # -------------------------------------------------
    # Juice triggers (hitstop, screenshake)
    # -------------------------------------------------
    def trigger_hitstop(self, duration=0.12):
        """Call on big hit. Freezes action for 'duration' seconds."""
        self._hitstop_timer = duration

    def trigger_screenshake(self, power=8, duration=0.20):
        """Call on hit for impact. Power = pixel shake."""
        self._screenshake_power = power
        self._screenshake_timer = duration

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------
    def update(self, dt: float):
        # если сейчас открыто окно подтверждения выхода —
        # геймплей стопается, НО сцена всё равно рисуется
        if self.paused_for_quit:
            # камеру всё равно обновим, чтобы фон не рвал мозг
            self.camera.follow_center(self.player.rect, SCREEN_WIDTH, SCREEN_HEIGHT)
            # не обновляем игрока, врагов и т.д.
            return

        # --- HITSTOP: freeze gameplay except camera ---
        if self._hitstop_timer > 0:
            self._hitstop_timer -= dt
            if self._hitstop_timer < 0:
                self._hitstop_timer = 0
            # даже в хитстопе камера следует за игроком
            self.camera.follow_center(self.player.rect, SCREEN_WIDTH, SCREEN_HEIGHT)
            return

        # --- SCREEN SHAKE ---
        if self._screenshake_timer > 0:
            self._screenshake_timer -= dt
            if self._screenshake_timer > 0:
                ox = random.randint(-self._screenshake_power, self._screenshake_power)
                oy = random.randint(-self._screenshake_power, self._screenshake_power)
                self._screenshake_offset = (ox, oy)
            else:
                self._screenshake_timer = 0
                self._screenshake_offset = (0, 0)

        # --- INPUT ---
        keys = pygame.key.get_pressed()

        dx = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
        dy = (1 if keys[pygame.K_s] else 0) - (1 if keys[pygame.K_w] else 0)
        running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        jump_now = bool(keys[pygame.K_SPACE])
        jump_pressed = jump_now and not self._last_jump
        jump_released = (not jump_now) and self._last_jump
        self._last_jump = jump_now

        # Прыжок (без h_dir / v_dir)
        if jump_now:
            self.player.jump()

        # Блок на Q
        self.player.guard(keys[pygame.K_q])

        # Атаки
        if keys[pygame.K_e]:
            self.player.attack("attack1")
        if keys[pygame.K_r]:
            self.player.attack("attack2")
        if keys[pygame.K_t]:
            self.player.attack("attack3")

        # PLAYER UPDATE:
        # Самурай сам следит за walkable_area, прыжками и посадкой.
        self.player.update(
            dt,
            input_dir=(dx, dy),
            running=running,
            jump_pressed=jump_pressed,
            jump_held=jump_now,
            jump_released=jump_released,
        )

        # ENEMIES UPDATE:
        # Врагов ограничиваем только по X, не трогаем им вертикаль.
        for enemy in list(self.enemies):
            enemy.update(dt)
            clamp_sprite_to_screen(
                enemy,
                self.world_width,
                PLAYFIELD_MARGIN_X,
            )

        # CAMERA FOLLOWS PLAYER
        self.camera.follow_center(self.player.rect, SCREEN_WIDTH, SCREEN_HEIGHT)

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------
    def draw(self, screen: pygame.Surface):
        ox, oy = self._screenshake_offset

        # фон сцены
        screen.fill(UI_BG)

        # фон-картинка со смещением камеры
        bg_rect = self.background.get_rect().move(
            -self.camera.x + ox, -self.camera.y + oy
        )
        screen.blit(self.background, bg_rect)

        # рисуем спрайты
        for sprite in self.all_sprites:
            rect = self.camera.apply(sprite.rect).move(ox, oy)
            screen.blit(sprite.image, rect)

        # HUD: полоска HP и счётчик врагов
        draw_health_bar(screen, 10, 10, self.player.hp, 100)

        enemies_txt = self.font.render(f"Enemies: {len(self.enemies)}", True, BLACK)
        screen.blit(enemies_txt, (10, 34))

        # Если сейчас пауза с подтверждением выхода — поверх рисуем модалку
        if self.paused_for_quit:
            self._draw_quit_modal(screen)

    # -------------------------------------------------
    # MODAL QUIT BOX
    # -------------------------------------------------
    def _draw_quit_modal(self, screen: pygame.Surface):
        # затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # прямоугольник модалки
        box_w, box_h = 400, 200
        box_rect = pygame.Rect(
            (SCREEN_WIDTH - box_w) // 2,
            (SCREEN_HEIGHT - box_h) // 2,
            box_w,
            box_h,
        )

        pygame.draw.rect(screen, (30, 30, 30), box_rect, border_radius=12)
        pygame.draw.rect(screen, (200, 200, 200), box_rect, 2, border_radius=12)

        # текст
        title = self.font_big.render("Exit Game?", True, (255, 255, 255))
        tip = self.font.render("Y = Quit  |  N = Resume", True, (200, 200, 200))

        title_pos = title.get_rect(center=(box_rect.centerx, box_rect.top + 70))
        tip_pos = tip.get_rect(center=(box_rect.centerx, box_rect.top + 130))

        screen.blit(title, title_pos)
        screen.blit(tip, tip_pos)
