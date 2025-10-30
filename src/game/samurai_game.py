# import pygame
# import sys
# import math
# import random

# # Инициализация Pygame
# pygame.init()

# # Настройки экрана
# SCREEN_WIDTH = 900
# SCREEN_HEIGHT = 600
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption("Way Of The Samurai")
# background = pygame.image.load("assets/background.png").convert()
# background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
# GROUND_HEIGHT = 10  # Высота земли от нижнего края
# ground_rect = pygame.Rect(0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)
# GROUND_Y = 600
# # Зона, по которой можно ходить (можно добавить несколько!)
# walkable_area = pygame.Rect(20, 550, 820, 100)
# def get_ground_y_at(x):
#     # Простая волна: поднимается и опускается плавно
#     return int(520 + 20 * math.sin(x / 100))

# # Цвета
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
# RED = (255, 0, 0)

# class Samurai(pygame.sprite.Sprite):
#     def __init__(self):
#         super().__init__()
#         self.speed = 4
#         self.facing_right = True
#         self.scale = 2
#         self.health = 100
#         self.death_time = None  # когда умер


#         # Анимации
#         self.idle_frames = self.load_animation("assets/samurai_sprites/Idle.png", 128)
#         self.walk_frames = self.load_animation("assets/samurai_sprites/Walk.png", 128)
#         self.run_frames = self.load_animation("assets/samurai_sprites/Run.png", 128)
#         self.jump_frames = self.load_animation("assets/samurai_sprites/Jump.png", 128)
#         self.attack_frames = self.load_animation("assets/samurai_sprites/Attack_1.png", 128)
#         self.attack2_frames = self.load_animation("assets/samurai_sprites/Attack_2.png", 128)
#         self.attack3_frames = self.load_animation("assets/samurai_sprites/Attack_3.png", frame_width=128)
#         self.protection_frames = self.load_animation("assets/samurai_sprites/Protection.png", frame_width=128)


#         # Статус
#         self.current_frames = self.idle_frames
#         self.animation_index = 0
#         self.animation_speed = 150  # мс
#         self.last_update = pygame.time.get_ticks()

#         self.image = self.current_frames[0]
#         self.rect = self.image.get_rect(midbottom=(100, GROUND_Y))

#         # Прыжок
#         self.is_jumping = False
#         self.jump_velocity = -10
#         self.gravity = 1
#         self.vertical_velocity = 0
#         self.jump_timer = 0
#         self.jump_duration = 12
#         self.jump_horizontal_velocity = 0
#         self.jump_vertical_velocity = 0

#         # Атака 1
#         self.is_attacking = False
#         self.attack_cooldown = 50
#         self.last_attack_time = 10

#         # Атака 2
#         self.is_attacking_2 = False
#         self.attack2_cooldown = 300
#         self.last_attack2_time = 0
#         self.attack2_animation_index = 0
#         self.attack2_animation_speed = 70

#         # Атака 3
#         self.is_attacking_3 = False
#         self.attack3_cooldown = 400
#         self.last_attack3_time = 0
#         self.attack3_animation_index = 0
#         self.attack3_animation_speed = 120

#         self.is_protecting = False

#         self.is_dead = False
#         self.is_hurt = False

#         # Анимация получения урона
#         self.hurt_frames = self.load_animation("sprites/Hurt.png", frame_width=128)
#         self.hurt_index = 0
#         self.hurt_duration = 300  # длительность одного кадра
#         self.last_hurt_time = 0

#         # Анимация смерти
#         self.dead_frames = self.load_animation("sprites/Dead.png", frame_width=128)
#         self.dead_index = 0
#         self.dead_duration = 300
#         self.last_dead_time = 0


#     def load_animation(self, filename, frame_width):
#         try:
#             sheet = pygame.image.load(filename).convert_alpha()
#         except Exception as e:
#             print(f"Ошибка загрузки {filename}: {e}")
#             return []

#         frames = []
#         sheet_width, sheet_height = sheet.get_size()
#         for i in range(sheet_width // frame_width):
#             rect = pygame.Rect(i * frame_width, 0, frame_width, sheet_height)
#             frame = sheet.subsurface(rect)
#             scaled = pygame.transform.scale(frame, (frame_width * self.scale, sheet_height * self.scale))
#             frames.append(scaled)
#         return frames

#     def update(self):
#         keys = pygame.key.get_pressed()
#         dx = keys[pygame.K_d] - keys[pygame.K_a]
#         dy = keys[pygame.K_s] - keys[pygame.K_w]
#         running = keys[pygame.K_LSHIFT]

#         if dx > 0:
#             self.facing_right = True
#         elif dx < 0:
#             self.facing_right = False

#         now = pygame.time.get_ticks()

#         # === Анимация смерти ===
#         if self.is_dead:
#             if self.dead_index < len(self.dead_frames):
#                 if now - self.last_dead_time >= self.dead_duration:
#                     self.last_dead_time = now
#                     self.image = self.dead_frames[self.dead_index]
#                     if not self.facing_right:
#                         self.image = pygame.transform.flip(self.image, True, False)
#                     self.dead_index += 1
#             else:
#                 self.image = self.dead_frames[-1]  # фиксируем последний кадр

#             # Гравитация — чтобы не висел в воздухе
#             if self.rect.bottom < GROUND_Y:
#                 self.vertical_velocity += self.gravity
#                 self.rect.y += self.vertical_velocity
#             else:
#                 self.rect.bottom = GROUND_Y
#                 self.vertical_velocity = 0

#             if self.death_time and now - self.death_time > 5000:
#                 self.kill()
#             return

#         # === Анимация получения урона ===
#         if self.is_hurt:
#             if now - self.last_hurt_time >= self.hurt_duration:
#                 self.last_hurt_time = now
#                 self.hurt_index += 1
#                 if self.hurt_index >= len(self.hurt_frames):
#                     self.is_hurt = False
#                     self.hurt_index = 0
#                 else:
#                     self.image = self.hurt_frames[self.hurt_index]
#                     if not self.facing_right:
#                         self.image = pygame.transform.flip(self.image, True, False)

#             # Гравитация тоже действует при уроне
#             if self.rect.bottom < GROUND_Y:
#                 self.vertical_velocity += self.gravity
#                 self.rect.y += self.vertical_velocity
#             else:
#                 self.rect.bottom = GROUND_Y
#                 self.vertical_velocity = 0

#             return



#         # === Гравитация / прыжок ===
#         if self.is_jumping:
#             if self.jump_timer < self.jump_duration:
#                 self.vertical_velocity += self.gravity * 0.5
#                 self.jump_timer += 1
#             else:
#                 self.vertical_velocity += self.gravity

#             self.rect.y += self.vertical_velocity
#             self.rect.x += self.jump_horizontal_velocity
#             self.rect.y += self.jump_vertical_velocity

#             if self.rect.bottom >= GROUND_Y:
#                 self.rect.bottom = GROUND_Y
#                 self.is_jumping = False
#                 self.vertical_velocity = 0
#                 self.jump_timer = 0
#                 self.jump_horizontal_velocity = 0
#                 self.jump_vertical_velocity = 0

#         # === Атака 3 ===
#         if self.is_attacking_3:
#             now = pygame.time.get_ticks()
#             if now - self.last_update >= self.attack3_animation_speed:
#                 self.last_update = now

#                 if self.attack3_animation_index == 2:
#                     for enemy in enemies:
#                         if self.rect.colliderect(enemy.rect):
#                             enemy.take_damage(45)

#                 if self.attack3_animation_index < len(self.attack3_frames):
#                     self.image = self.attack3_frames[self.attack3_animation_index]
#                     if not self.facing_right:
#                         self.image = pygame.transform.flip(self.image, True, False)
#                     self.attack3_animation_index += 1
#                 else:
#                     self.is_attacking_3 = False
#                     self.attack3_animation_index = 0
#             return

#         # === Защита ===
#         if self.is_protecting:
#             if self.protection_frames:
#                 self.image = self.protection_frames[0]  # или кадры меняются
#                 if not self.facing_right:
#                     self.image = pygame.transform.flip(self.image, True, False)
#             return


#         # === Атака 2 ===
#         if self.is_attacking_2:
#             now = pygame.time.get_ticks()
#             if now - self.last_update >= self.attack2_animation_speed:
#                 self.last_update = now

#                 if self.attack2_animation_index == 2:
#                     for enemy in enemies:
#                         if self.rect.colliderect(enemy.rect):
#                             enemy.take_damage(35)

#                 if self.attack2_animation_index < len(self.attack2_frames):
#                     self.image = self.attack2_frames[self.attack2_animation_index]
#                     if not self.facing_right:
#                         self.image = pygame.transform.flip(self.image, True, False)
#                     self.attack2_animation_index += 1

#                 elif self.attack2_animation_index == len(self.attack2_frames):
#                     self.attack2_animation_index += 1  # задержка
#                     self.last_update = now
#                     return

#                 else:
#                     self.is_attacking_2 = False
#                     self.attack2_animation_index = 0

#             return  # Выход: не обрабатываем другие действия

#         # === Атака 1 ===
#         if self.is_attacking:
#             now = pygame.time.get_ticks()
#             if now - self.last_update >= self.animation_speed:
#                 self.last_update = now
#                 self.animation_index += 1

#                 if self.animation_index == 2:
#                     for enemy in enemies:
#                         if self.rect.colliderect(enemy.rect):
#                             enemy.take_damage(25)

#                 if self.animation_index >= len(self.attack_frames):
#                     self.is_attacking = False
#                     self.animation_index = 0
#                 else:
#                     self.image = self.attack_frames[self.animation_index]
#                     if not self.facing_right:
#                         self.image = pygame.transform.flip(self.image, True, False)

#             return  # Выход: не обрабатываем другие действия

#         # === Обычная анимация ===
#         if self.is_jumping:
#             new_frames = self.jump_frames
#         elif dx != 0 or dy != 0:
#             new_frames = self.run_frames if running else self.walk_frames
#             self.speed = 10 if running else 4
#         else:
#             new_frames = self.idle_frames
#             self.speed = 0

#         if self.current_frames != new_frames:
#             self.current_frames = new_frames
#             self.animation_index = 0
#             self.last_update = pygame.time.get_ticks()

#         now = pygame.time.get_ticks()
#         if now - self.last_update >= self.animation_speed:
#             self.last_update = now
#             self.animation_index = (self.animation_index + 1) % len(self.current_frames)

#         frame = self.current_frames[self.animation_index]
#         self.image = frame if self.facing_right else pygame.transform.flip(frame, True, False)

#         self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

#         # # Коллизия с врагами
#         # for enemy in enemies:
#         #     if self.rect.colliderect(enemy.rect):
#         #         overlap = self.rect.clip(enemy.rect)
#         #         min_overlap = 180

#         #         if overlap.width > min_overlap:
#         #             shift = (overlap.width - min_overlap) // 2
#         #             if self.rect.centerx < enemy.rect.centerx:
#         #                 self.rect.left -= shift
#         #                 enemy.rect.right += shift
#         #             else:
#         #                 self.rect.right += shift
#         #                 enemy.rect.left -= shift



#     def move(self, dx, dy):
#         # 🚫 Блокируем движение, если самурай защищается
#         if self.is_protecting:
#             return

#         # Во время прыжка блокируем ручное движение вверх/вниз
#         move_y = 0 if self.is_jumping else dy * self.speed
#         move_x = dx * self.speed

#         future_rect = self.rect.copy()
#         future_rect.x += move_x
#         future_rect.y += move_y

#         # Проверяем ноги
#         feet_rect = pygame.Rect(future_rect.centerx - 5, future_rect.bottom - 5, 10, 5)

#         if walkable_area.colliderect(feet_rect):
#             self.rect = future_rect

#     def attack(self):
#         now = pygame.time.get_ticks()
#         if not self.is_attacking and now - self.last_attack_time > self.attack_cooldown:
#             self.is_attacking = True
#             self.animation_index = 0
#             self.last_attack_time = now
#             self.last_update = now

#     def attack2(self):
#         now = pygame.time.get_ticks()
#         if not self.is_attacking_2 and now - self.last_attack2_time > self.attack2_cooldown:
#             self.is_attacking_2 = True
#             self.attack2_animation_index = 0
#             self.last_attack2_time = now
#             self.last_update = now

#     def attack3(self):
#         now = pygame.time.get_ticks()
#         if not self.is_attacking_3 and now - self.last_attack3_time > self.attack3_cooldown:
#             self.is_attacking_3 = True
#             self.attack3_animation_index = 0
#             self.last_update = pygame.time.get_ticks()
#             self.last_attack3_time = now

#     def protect(self, enable):
#         self.is_protecting = enable

#     def take_damage(self, amount):
#         if self.is_dead or self.is_hurt:
#             return

#         self.health -= amount
#         if self.health <= 0:
#             self.is_dead = True
#             self.dead_index = 0
#             self.last_dead_time = pygame.time.get_ticks()
#             self.death_time = pygame.time.get_ticks()
#         else:
#             self.is_hurt = True
#             self.hurt_index = 0
#             self.last_hurt_time = pygame.time.get_ticks()






# class Enemy(pygame.sprite.Sprite):
#     def __init__(self, x, y, target):
#         super().__init__()
#         self.scale = 2
#         self.health = 200
#         self.speed = 2
#         self.run_speed = 4
#         self.facing_right = False
#         self.target = target
#         self.death_time = None


#         # Состояния
#         self.state = "idle"  # [idle, walk, run, attack, jump, hurt, block, dead]
#         self.is_attacking = False
#         self.is_blocking = False
#         self.is_hurt = False
#         self.is_dead = False
#         self.is_jumping = False
#         self.vertical_velocity = 0
#         self.gravity = 1
#         self.attack_cooldown = 1850
#         self.last_attack_time = 0
#         self.block_chance = 0.2
#         self.attack_damage = 20

#         self.animation_speed = 100
#         self.animation_index = 0
#         self.last_update = pygame.time.get_ticks()

#         # Загрузка анимаций
#         self.idle_frames = self.load_animation("assets/enemy_sprites/Idle.png", 128)
#         self.walk_frames = self.load_animation("assets/enemy_sprites/Walk.png", 128)
#         self.run_frames = self.load_animation("assets/enemy_sprites/Run.png", 128)
#         self.jump_frames = self.load_animation("assets/enemy_sprites/Jump.png", 128)
#         self.attack1_frames = self.load_animation("assets/enemy_sprites/Attack_1.png", 128)
#         self.attack2_frames = self.load_animation("assets/enemy_sprites/Attack_2.png", 128)
#         self.attack3_frames = self.load_animation("assets/enemy_sprites/Attack_3.png", 128)
#         self.protect_frames = self.load_animation("assets/enemy_sprites/Protect.png", 128)
#         self.hurt_frames = self.load_animation("assets/enemy_sprites/Hurt.png", 128)
#         self.dead_frames = self.load_animation("assets/enemy_sprites/Dead.png", 128)

#         self.current_frames = self.idle_frames
#         self.image = self.current_frames[0]
#         self.rect = self.image.get_rect(midbottom=(x, y))

#     def load_animation(self, path, width):
#         sheet = pygame.image.load(path).convert_alpha()
#         frames = []
#         sw, sh = sheet.get_size()
#         for i in range(sw // width):
#             frame = sheet.subsurface(pygame.Rect(i * width, 0, width, sh))
#             scaled = pygame.transform.scale(frame, (width * self.scale, sh * self.scale))
#             frames.append(scaled)
#         return frames

#     def update(self):
#         now = pygame.time.get_ticks()
#         distance = self.target.rect.centerx - self.rect.centerx
#         abs_dist = abs(distance)
#         direction = 1 if distance > 0 else -1
#         if not self.is_dead and not self.target.is_dead:
#             self.facing_right = direction > 0

#         if self.is_dead:
#             self.play_animation(self.dead_frames, loop=False)

#             # Фиксируем последний кадр
#             if self.animation_index >= len(self.dead_frames):
#                 self.image = self.dead_frames[-1]

#             # Гравитация
#             if self.rect.bottom < GROUND_Y:
#                 self.vertical_velocity += self.gravity
#                 self.rect.y += self.vertical_velocity
#             else:
#                 self.rect.bottom = GROUND_Y
#                 self.vertical_velocity = 0

#             # Удаляем после 5 секунд
#             if self.death_time and pygame.time.get_ticks() - self.death_time > 5000:
#                 self.kill()
#             return


#         # === Death ===
#         if self.is_dead:
#             self.play_animation(self.dead_frames, loop=False)
#             return

#         # === Hurt ===
#         if self.is_hurt:
#             self.play_animation(self.hurt_frames, loop=False)
#             if self.animation_index >= len(self.hurt_frames) - 1:
#                 self.is_hurt = False
#             return

#         # === AI Decision ===
#         if self.is_attacking:
#             self.perform_attack()
#             return

#         # === Block Randomly ===
#         if not self.is_blocking and random.random() < 0.003:
#             self.is_blocking = True
#             self.state = "block"
#             self.play_animation(self.protect_frames, loop=True)
#             return

#         if self.is_blocking:
#             self.play_animation(self.protect_frames, loop=True)
#             if random.random() < 0.01:
#                 self.is_blocking = False
#             return

#         # === Jump randomly ===
#         if not self.is_jumping and random.random() < 0.005:
#             self.vertical_velocity = -12
#             self.is_jumping = True

#         # === Gravity ===
#         if self.is_jumping:
#             self.vertical_velocity += self.gravity
#             self.rect.y += self.vertical_velocity
#             if self.rect.bottom >= 600:
#                 self.rect.bottom = 600
#                 self.is_jumping = False

#         # === Action by distance ===
#         if abs_dist < 70:
#             self.state = "adjust"
#             self.rect.x -= direction  # отталкиваемся назад
#         elif abs_dist < 100:
#             self.start_attack()
#         else:
#             self.state = "run" if abs_dist > 200 else "walk"
#             speed = self.run_speed if self.state == "run" else self.speed
#             frames = self.run_frames if self.state == "run" else self.walk_frames
#             self.play_animation(frames)
#             self.rect.x += direction * speed

#         # Отталкивание при касании (если надо — настроить площадь контакта)
#         if self.rect.colliderect(self.target.rect):
#             if abs_dist < 40:
#                 self.rect.x -= direction * 2
        
#         if self.is_dead:
#             now = pygame.time.get_ticks()
#             if self.animation_index < len(self.dead_frames):
#                 self.play_animation(self.dead_frames, loop=False)
#             else:
#                 self.image = self.dead_frames[-1]

#             if now - self.death_time > 5000:
#                 self.kill()
#             return
        
#         if self.target.is_dead:
#             # Стоим на месте, не двигаемся и не поворачиваемся
#             self.play_animation(self.idle_frames)
#             return



#     def start_attack(self):
#         now = pygame.time.get_ticks()
#         if now - self.last_attack_time > self.attack_cooldown:
#             self.current_frames = random.choice([
#                 self.attack1_frames, self.attack2_frames, self.attack3_frames
#             ])
#             self.is_attacking = True
#             self.animation_index = 0
#             self.last_update = now
#             self.last_attack_time = now

#     def perform_attack(self):
#         now = pygame.time.get_ticks()
#         if now - self.last_update >= self.animation_speed:
#             self.last_update = now
#             self.animation_index += 1
#             if self.animation_index == 2:
#                 if self.rect.colliderect(self.target.rect):
#                     if not self.target.is_protecting:
#                         self.target.take_damage(self.attack_damage)
#             if self.animation_index >= len(self.current_frames):
#                 self.is_attacking = False
#                 self.animation_index = 0

#         if self.animation_index < len(self.current_frames):
#             self.image = self.current_frames[self.animation_index]
#             if not self.facing_right:
#                 self.image = pygame.transform.flip(self.image, True, False)

#     def play_animation(self, frames, loop=True):
#         if self.current_frames != frames:
#             self.current_frames = frames
#             self.animation_index = 0
#             self.last_update = pygame.time.get_ticks()

#         now = pygame.time.get_ticks()
#         if now - self.last_update >= self.animation_speed:
#             self.last_update = now
#             self.animation_index += 1
#             if self.animation_index >= len(frames):
#                 self.animation_index = 0 if loop else len(frames) - 1

#         self.image = self.current_frames[self.animation_index]
#         if not self.facing_right:
#             self.image = pygame.transform.flip(self.image, True, False)

#     def take_damage(self, amount):
#         if self.is_dead:
#             return
#         if random.random() < self.block_chance:
#             self.is_blocking = True
#             return

#         self.health -= amount
#         if self.health <= 0:
#             self.is_dead = True
#         else:
#             self.is_hurt = True
#             self.animation_index = 0
#         if self.health <= 0:
#             self.is_dead = True
#             self.death_time = pygame.time.get_ticks()


# # Группы спрайтов
# all_sprites = pygame.sprite.Group()
# enemies = pygame.sprite.Group()

# samurai = Samurai()
# all_sprites.add(samurai)

# enemy = Enemy(700, GROUND_Y, samurai)
# all_sprites.add(enemy)
# enemies.add(enemy)

# # Основной цикл игры
# running = True
# clock = pygame.time.Clock()

# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     keys = pygame.key.get_pressed()
#     dx, dy = 0, 0
    
#     if keys[pygame.K_a]: dx = -1
#     if keys[pygame.K_d]: dx = 1
#     if keys[pygame.K_w]: dy = -1
#     if keys[pygame.K_s]: dy = 1
#     if keys[pygame.K_e]:  
#         samurai.attack()
#     if keys[pygame.K_r]:
#         samurai.attack2()
#     if keys[pygame.K_t]:
#         samurai.attack3()
#     if keys[pygame.K_q]:
#         samurai.protect(True)
#     else:
#         samurai.protect(False)


    
#     if keys[pygame.K_SPACE] and not samurai.is_jumping:
#         samurai.is_jumping = True
#         samurai.vertical_velocity = samurai.jump_velocity
#         samurai.jump_timer = 0

#         # определяем направление прыжка
#         h_dir = (keys[pygame.K_d] - keys[pygame.K_a])  # → = 1, ← = -1
#         v_dir = (keys[pygame.K_s] - keys[pygame.K_w])  # ↓ = 1, ↑ = -1

#         samurai.jump_horizontal_velocity = h_dir * 5
#         samurai.jump_vertical_velocity = v_dir * 5


#     samurai.move(dx, dy)
#     all_sprites.update()
#     screen.blit(background, (0, 0))
#     all_sprites.draw(screen)

    
#     # Отображение здоровья
#     font = pygame.font.Font(None, 36)
#     health_text = font.render(f"HP: {samurai.health}", True, BLACK)
#     screen.blit(health_text, (10, 10))
    
#     pygame.display.flip()
#     clock.tick(60)

# pygame.quit()
# sys.exit()