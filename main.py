import pygame
import json
import random
import pytmx
from pytmx.util_pygame import load_pygame


pygame.init()


    # ---------------- SOUND EFFECTS ----------------
pygame.mixer.init()

pygame.mixer.set_num_channels(32)

    # Reserve channels for combat sounds
attack_channel = pygame.mixer.Channel(1)

portal_channel = pygame.mixer.Channel(3)

sound_opener = pygame.mixer.Sound('assets/start_sound.wav')
sound_click = pygame.mixer.Sound('assets/click.wav')   # Play/Main Menu
sound_quit = pygame.mixer.Sound('assets/quit.wav')     # Quit button
sound_portal_unlock = pygame.mixer.Sound('assets/portal_unlock.wav')
sound_game_over = pygame.mixer.Sound('assets/game_over.wav')
sound_attack_hit = pygame.mixer.Sound('assets/attack_hit.wav')


sound_opener.play()

sound_click.set_volume(0.7)
sound_quit.set_volume(0.7)
sound_portal_unlock.set_volume(0.8)
sound_game_over.set_volume(0.8)
sound_attack_hit.set_volume(0.6)


    # ---------------- MUSIC ----------------
pygame.mixer.music.load("assets/hell_menu.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0)  # loop forever

playing_game_music = False




screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

with open("level.json", "r") as f:
        level_data = json.load(f)

current_level_index = 0

tmx_data = None


    # ---------------- LEVEL CACHE ----------------
tmx_cache = {}
map_surface_cache = {}
current_map_surface = None

def load_level(index):
        lvl = level_data["levels"][index]

        world_w = lvl["world_width"]
        world_h = lvl["world_height"]

        obstacles = [
            pygame.Rect(-20, 0, 20, world_h),
            pygame.Rect(world_w, 0, 20, world_h),
            pygame.Rect(0, -20, world_w, 20),
            pygame.Rect(0, world_h, world_w, 20),
        ]

        for obs in lvl["obstacles"]:
            obstacles.append(
                pygame.Rect(obs["x"], obs["y"], obs["w"], obs["h"])
            )

        tmx_path = lvl.get("tmx_file", "assets/level1.tmx")

        # LOAD ONLY ONCE
        if tmx_path not in tmx_cache:
            tmx_cache[tmx_path] = load_pygame(tmx_path)

        tmx_data = tmx_cache[tmx_path]

        return world_w, world_h, obstacles, lvl["name"], tmx_data


def start_level(index, reset_hp=False):
        global current_level_index, WORLD_WIDTH, WORLD_HEIGHT
        global Obstacles, level_name, tmx_data
        global scroll_x, scroll_y
        global player_hp, enemies, enemy_hp
        global spawned_count, dashing, last_dash
        global kill_count, portal_sound_played
        global game_over_sound_played
        global current_map_surface, map_surface_cache
        global dash_start_time, dash_velocity_x, dash_velocity_y

        current_level_index = index

        player.topleft = (640, 360)
        enemies.clear()


        WORLD_WIDTH, WORLD_HEIGHT, Obstacles, level_name, tmx_data = load_level(index)

        # PRE-RENDER MAP
        if index not in map_surface_cache:
            map_surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT)).convert()

            for layer in tmx_data.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer):
                    for x, y, gid in layer:
                        tile = tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            map_surface.blit(
                                tile,
                                (x * tmx_data.tilewidth,
                                y * tmx_data.tileheight)
                            )

            map_surface_cache[index] = map_surface

        current_map_surface = map_surface_cache[index]

        player.topleft = (640, 360)
        scroll_x, scroll_y = 0, 0

        dashing = False
        last_dash = 0

        if reset_hp:
            player_hp = 100

        enemies.clear()


        spawned_count = 0
        kill_count = 0

        portal_sound_played = False
        game_over_sound_played = False

        enemy_count = get_enemy_count(current_level_index)

        for _ in range(enemy_count):
            spawn_enemy()



WHITE = (240, 240, 240)
RED = (200, 70, 70)
BLUE = (80, 160, 255)
GREEN = (80, 220, 120)
YELLOW = (255, 220, 80)
GRAY = (100, 100, 100)
BLACK = (20, 20, 20)
MENU_BG = (20, 5, 5)
MENU_OUTLINE = (200, 50, 50)
MENU_TEXT = (255, 150, 150)
MENU_SHADOW = (100, 20, 20)
EXIT_BUTTON_COLOR = (28, 40, 70)
EXIT_BUTTON_HOVER = (58, 90, 170)
EXIT_BUTTON_RECT = pygame.Rect(screen.get_width() - 170, 10, 160, 42)
EXIT_BUTTON_LABEL = "MAIN MENU"

menu_items = ["Play", "Quit"]
game_over_items = ["Restart", "Quit"]
menu_selected = 0
game_over_selected = 0
menu_state = "menu"

menu_title_font = pygame.font.SysFont("couriernew", 56, bold=True)
menu_item_font = pygame.font.SysFont("couriernew", 30, bold=True)
menu_small_font = pygame.font.SysFont("couriernew", 18)
hud_font = pygame.font.SysFont("couriernew", 24)

bridge_img = pygame.image.load("assets/BGD.png").convert_alpha()

player = pygame.Rect(450, 300, 40, 66)
dan = pygame.image.load("assets/player_sprites.png").convert_alpha()
dan.set_colorkey((62, 136, 183))
dan = pygame.transform.scale(dan, (int(dan.get_width()/6), int(dan.get_height()/6)))
player_spd = 5
player_hp = 100
portal = pygame.Rect(850, 550, 110, 110)

portal_frame = 0
portal_last_update = 0
portal_anim_speed = 90

    # ---------------- DASH MECHANICS ----------------
dash_speed = 15
dash_duration = 300  # milliseconds
dash_cooldown = 500  # milliseconds
last_dash = 0
dashing = False
dash_start_time = 0
dash_velocity_x = 0
dash_velocity_y = 0

    # ---------------- ENEMIES ----------------
enemies = []
enemy_hp = []

BASE_ENEMIES = 15
def get_enemy_count(level_index):
        # Level 1 = 15 enemies
        # Level 2 = 20 enemies
        # Level 3 = 25 enemies
        # Level 4 = 30 enemies
        # Level 5 = 35 enemies
        return BASE_ENEMIES + (level_index * 5)

spawned_count = 0
kill_count = 0
portal_sound_played = False
game_over_sound_played = False


enemy_spd = 2
enemy_damage = 0.2

    # ================= ENEMY SPRITES / ANIMATION =================

enemy_sheet = pygame.image.load("assets/enemy_sheet.png").convert_alpha()

ENEMY_SCALE = 1.8


def get_frame(x, y, w, h):

        frame = pygame.Surface((w, h), pygame.SRCALPHA)

        frame.blit(enemy_sheet, (0, 0), (x, y, w, h))

        frame = pygame.transform.scale(
            frame,
            (int(w * ENEMY_SCALE), int(h * ENEMY_SCALE))
        )

        return frame


    # =========================================================
    # IDLE
    # =========================================================

enemy_idle_frames = [

        get_frame(0,   0, 80, 96),
        get_frame(82,  0, 80, 96),
        get_frame(164, 0, 80, 96),
        get_frame(246, 0, 80, 96),
        get_frame(328, 0, 80, 96),
        get_frame(410, 0, 80, 96),
    ]

    # =========================================================
    # WALK
    # =========================================================

enemy_walk_frames = [

        get_frame(0,   96, 80, 96),
        get_frame(82,  96, 80, 96),
        get_frame(164, 96, 80, 96),
        get_frame(246, 96, 80, 96),
        get_frame(328, 96, 80, 96),
        get_frame(410, 96, 80, 96),
        get_frame(492, 96, 80, 96),
        get_frame(574, 96, 80, 96),
    ]

    # =========================================================
    # ATTACK
    # =========================================================

enemy_attack_frames = [

        get_frame(0,   520, 120, 120),
        get_frame(122, 520, 120, 120),
        get_frame(244, 520, 120, 120),
        get_frame(366, 520, 120, 120),
        get_frame(488, 520, 120, 120),
        get_frame(610, 520, 120, 120),
    ]

    # =========================================================
    # DEATH
    # =========================================================

enemy_death_frames = [

        get_frame(0,   865, 120, 120),
        get_frame(122, 865, 120, 120),
        get_frame(244, 865, 120, 120),
        get_frame(366, 865, 120, 120),
        get_frame(488, 865, 120, 120),
        get_frame(610, 865, 120, 120),
    ]

def spawn_enemy():
        global spawned_count

        for _ in range(50):

            x = random.randint(0, WORLD_WIDTH - 40)
            y = random.randint(0, WORLD_HEIGHT - 60)

            rect = pygame.Rect(x, y, 50, 70)

            if not any(rect.colliderect(obs) for obs in Obstacles):

                enemy = {
                    "rect": rect,
                    "hp": 3 + current_level_index,
                    "state": "walk",
                    "frame": 0,
                    "last_update": pygame.time.get_ticks(),
                    "flip": False,
                    "dead": False,
                    "death_done": False
                }

                enemies.append(enemy)

                spawned_count += 1
                return

# ---------------- PORTAL SPRITES ----------------

portal_sheet = pygame.image.load("assets/portal_sheet.png").convert_alpha()

PORTAL_SCALE = 1.4

def get_portal_frame(x, y, w, h):

    frame = pygame.Surface((w, h), pygame.SRCALPHA)

    frame.blit(portal_sheet, (0, 0), (x, y, w, h))

    frame = pygame.transform.scale(
        frame,
        (int(w * PORTAL_SCALE), int(h * PORTAL_SCALE))
    )

    return frame

# ---------------- PORTAL IDLE ANIMATION ----------------

portal_frames_locked = []

FRAME_W = 75
FRAME_H = 75

# Top row = opening/idle blue portal
for i in range(8, 20):

    frame = get_portal_frame(
        i * FRAME_W,
        0,
        FRAME_W,
        FRAME_H
    )

    portal_frames_locked.append(frame)


# ---------------- UNLOCKED PORTAL ----------------
# Use brighter activation row

portal_frames_unlocked = []

for i in range(0, 12):

    frame = get_portal_frame(
        i * FRAME_W,
        150,
        FRAME_W,
        FRAME_H
    )

    portal_frames_unlocked.append(frame)


    # START FIRST LEVEL AFTER EVERYTHING EXISTS
scroll_x = 0
scroll_y = 0
start_level(current_level_index)

    # ---------------- ATTACK ----------------
attack_cooldown = 400
last_attack = 0
attack_duration = 150
attacking = False
attack_time = 0
attack_rect = pygame.Rect(0, 0, 0, 0)


TOTAL_LEVELS = len(level_data["levels"])

run = True
while run:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if menu_state == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        menu_selected = (menu_selected - 1) % len(menu_items)
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        menu_selected = (menu_selected + 1) % len(menu_items)
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if menu_items[menu_selected] == "Play":
                            sound_click.play()
                            menu_state = "play"
                            player.topleft = (640, 360)
                            scroll_x, scroll_y = 0, 0
                            pygame.mixer.music.load("assets/bg.wav")
                            pygame.mixer.music.play(-1, 0.0)
                        else:
                            run = False
                    if event.key == pygame.K_ESCAPE:
                        sound_quit.play()
                        pygame.time.delay(200)
                        run = False
                if event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    for index, label in enumerate(menu_items):
                        button_rect = pygame.Rect(520, 320 + index * 70, 240, 54)
                        if button_rect.collidepoint(mx, my):
                            menu_selected = index
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    for index, label in enumerate(menu_items):
                        button_rect = pygame.Rect(520, 320 + index * 70, 240, 54)
                        if button_rect.collidepoint(mx, my):
                            if label == "Play":
                                sound_click.play()
                                menu_state = "play"
                                player.topleft = (640, 360)
                                scroll_x, scroll_y = 0, 0
                                pygame.mixer.music.load("assets/bg.wav")
                                pygame.mixer.music.play(-1, 0.0)
                            else:
                                sound_quit.play()
                                pygame.time.delay(200)
                                run = False

            elif menu_state == "game_over":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        game_over_selected = (game_over_selected - 1) % len(game_over_items)

                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        game_over_selected = (game_over_selected + 1) % len(game_over_items)

                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if game_over_items[game_over_selected] == "Restart":
                            sound_click.play()
                            menu_state = "play"
                            start_level(0, reset_hp=True)

                            pygame.mixer.music.load("assets/bg.wav")
                            pygame.mixer.music.set_volume(0.5)
                            pygame.mixer.music.play(-1, 0.0)

                        else:
                            sound_quit.play()
                            pygame.time.delay(200)
                            run = False

                    if event.key == pygame.K_ESCAPE:
                        sound_quit.play()
                        pygame.time.delay(200)
                        run = False

                if event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    for index, label in enumerate(game_over_items):
                        button_rect = pygame.Rect(520, 320 + index * 70, 240, 54)
                        if button_rect.collidepoint(mx, my):
                            game_over_selected = index

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    for index, label in enumerate(game_over_items):
                        button_rect = pygame.Rect(520, 320 + index * 70, 240, 54)

                        if button_rect.collidepoint(mx, my):
                            if label == "Restart":
                                sound_click.play()
                                menu_state = "play"
                                start_level(0, reset_hp=True)

                                pygame.mixer.music.load("assets/bg.wav")
                                pygame.mixer.music.set_volume(0.5)
                                pygame.mixer.music.play(-1, 0.0)

                            else:
                                sound_quit.play()
                                pygame.time.delay(200)
                                run = False

            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sound_click.play()
                        player_hp = 100
                        start_level(0, reset_hp=True)
                        menu_state = "menu"
                        pygame.mixer.music.load("assets/hell_menu.wav")
                        pygame.mixer.music.play(-1, 0.0)
                    if event.key in (pygame.K_n, pygame.K_b):
                        if event.key == pygame.K_n:
                            next_index = (current_level_index + 1) % TOTAL_LEVELS
                        else:
                            next_index = (current_level_index - 1) % TOTAL_LEVELS
                        start_level(next_index)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if EXIT_BUTTON_RECT.collidepoint(event.pos):
                        sound_click.play()
                        player_hp = 100
                        start_level(0, reset_hp=True)
                        menu_state = "menu"
                        pygame.mixer.music.load("assets/hell_menu.wav")
                        pygame.mixer.music.play(-1, 0.0)
                    else:
                        now = pygame.time.get_ticks()
                        if now - last_attack > attack_cooldown:
                            attacking = True
                            attack_time = now
                            last_attack = now
                            mx, my = pygame.mouse.get_pos()
                            dir_x = mx - (player.x - scroll_x)
                            dir_y = my - (player.y - scroll_y)
                            length = (dir_x**2 + dir_y**2) ** 0.5
                            if length != 0:
                                dir_x /= length
                                dir_y /= length
                            attack_rect = pygame.Rect(
                                player.x + dir_x * 40,
                                player.y + dir_y * 40,
                                80,
                                80
                            )


        if menu_state == "menu":
            screen.fill(MENU_BG)
            screen.blit(bridge_img, (0, 0))

            # Title with glow shadow
            title_surf = menu_title_font.render("DANTE'S INFERNO", True, MENU_TEXT)
            shadow_surf = menu_title_font.render("DANTE'S INFERNO", True, MENU_SHADOW)
            title_pos = title_surf.get_rect(center=(screen.get_width() / 2 - 2, 140 - 2))
            screen.blit(shadow_surf, title_pos)
            screen.blit(title_surf, title_surf.get_rect(center=(screen.get_width() / 2, 140)))
            subtitle = menu_small_font.render("A 2D Top-Down Adventure Game", True, (150, 200, 255))
            screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() / 2, 190)))

            for index, label in enumerate(menu_items):
                rect = pygame.Rect(520, 320 + index * 70, 240, 54)
                selected = index == menu_selected
                bg_color = (30, 10, 10) if not selected else (60, 20, 20)
                outline = MENU_OUTLINE if selected else (120, 30, 30)
                text_color = MENU_TEXT if selected else (255, 200, 200)

                pygame.draw.rect(screen, bg_color, rect, border_radius=12)
                pygame.draw.rect(screen, outline, rect, 3, border_radius=12)
                label_surf = menu_item_font.render(label, True, text_color)
                screen.blit(label_surf, label_surf.get_rect(center=rect.center))

            hint = menu_small_font.render("Use arrow keys or mouse, press Enter to select", True, (255, 180, 180))
            screen.blit(hint, hint.get_rect(center=(screen.get_width() / 2, 520)))

        elif menu_state == "game_over":
            screen.fill((20, 0, 0))  # Dark red background for hell theme

            # Retro background scanlines
            for y in range(0, screen.get_height(), 8):
                pygame.draw.line(screen, (40, 5, 5), (0, y), (screen.get_width(), y), 1)

            # Title with glow shadow
            title_surf = menu_title_font.render("GAME OVER", True, (255, 100, 100))
            shadow_surf = menu_title_font.render("GAME OVER", True, (100, 20, 20))
            title_pos = title_surf.get_rect(center=(screen.get_width() / 2 - 2, 140 - 2))
            screen.blit(shadow_surf, title_pos)
            screen.blit(title_surf, title_surf.get_rect(center=(screen.get_width() / 2, 140)))
            subtitle = menu_small_font.render("You have perished in the depths of Hell", True, (255, 150, 150))
            screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() / 2, 190)))

            for index, label in enumerate(game_over_items):
                rect = pygame.Rect(520, 320 + index * 70, 240, 54)
                selected = index == game_over_selected
                bg_color = (40, 10, 10) if not selected else (80, 20, 20)
                outline = (200, 50, 50) if selected else (120, 30, 30)
                text_color = (255, 150, 150) if selected else (255, 200, 200)

                pygame.draw.rect(screen, bg_color, rect, border_radius=12)
                pygame.draw.rect(screen, outline, rect, 3, border_radius=12)
                label_surf = menu_item_font.render(label, True, text_color)
                screen.blit(label_surf, label_surf.get_rect(center=rect.center))

            hint = menu_small_font.render("Use arrow keys or mouse, press Enter to select", True, (255, 180, 180))
            screen.blit(hint, hint.get_rect(center=(screen.get_width() / 2, 520)))

        elif menu_state == "play":
            keys = pygame.key.get_pressed()
            cx, cy = pygame.mouse.get_pos()
            player_scroll = pygame.Rect(player.x - scroll_x, player.y - scroll_y, player.width, player.height)

            mouse_offset_x = (cx - screen.get_width() / 2) * 0.5
            mouse_offset_y = (cy - screen.get_height() / 2) * 0.5
            scroll_x += (player.x - scroll_x - screen.get_width()/2 + player.width/2 + (mouse_offset_x/2)) / 15
            scroll_y += (player.y - scroll_y - screen.get_height()/2 + player.height/2 + (mouse_offset_y/2)) / 15

            # Clamp scroll to world boundaries
            scroll_x = max(0, min(scroll_x, WORLD_WIDTH - screen.get_width()))
            scroll_y = max(0, min(scroll_y, WORLD_HEIGHT - screen.get_height()))

            # Draw map first
            screen.blit(current_map_surface, (-scroll_x, -scroll_y))

            # ---------------- HP BAR (DRAW LAST) ----------------
            pygame.draw.rect(screen, RED, (10, 10, 200, 20))
            pygame.draw.rect(screen, GREEN, (10, 10, int(2 * player_hp), 20))
            pygame.draw.rect(screen, WHITE, (10, 10, 200, 20), 2)

            # Handle dash mechanic
            current_time = pygame.time.get_ticks()
            if keys[pygame.K_SPACE]:
                if not dashing and current_time - last_dash > dash_cooldown:
                    # Start a new dash in the direction the player is moving
                    move_x = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
                    move_y = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
                    
                    # Only dash if player is pressing a direction
                    if move_x != 0 or move_y != 0:
                        length = (move_x**2 + move_y**2) ** 0.5
                        if length != 0:
                            move_x /= length
                            move_y /= length
                        dashing = True
                        last_dash = current_time
                        dash_start_time = current_time

                        dash_velocity_x = move_x * dash_speed
                        dash_velocity_y = move_y * dash_speed
            
            # Update dash state
            if dashing and current_time - dash_start_time > dash_duration:
                dashing = False
            
            # Horizontal movement and collision
            if dashing:
                dx = dash_velocity_x
            else:
                dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) * player_spd - (keys[pygame.K_LEFT] or keys[pygame.K_a]) * player_spd
            
            player.x += dx
            for obs in Obstacles:
                if player.colliderect(obs):
                    if dx > 0:
                        player.right = obs.left
                    elif dx < 0:
                        player.left = obs.right

            # Vertical movement and collision
            if dashing:
                dy = dash_velocity_y
            else:
                dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) * player_spd - (keys[pygame.K_UP] or keys[pygame.K_w]) * player_spd
            
            player.y += dy
            for obs in Obstacles:
                if player.colliderect(obs):
                    if dy > 0:
                        player.bottom = obs.top
                    elif dy < 0:
                        player.top = obs.bottom

            # ---------------- PORTAL STATE ----------------

            portal_unlocked = len(enemies) == 0

            # ---------------- PLAY PORTAL UNLOCK SOUND ONCE ----------------
            if portal_unlocked and not portal_sound_played:
                portal_channel.play(sound_portal_unlock)
                portal_sound_played = True
                
            # ---------------- PORTAL ANIMATION ----------------

            if pygame.time.get_ticks() - portal_last_update > portal_anim_speed:

                portal_last_update = pygame.time.get_ticks()

                portal_frame += 1

                if portal_unlocked:
                    portal_frame %= len(portal_frames_unlocked)
                else:
                    portal_frame %= len(portal_frames_locked)
            
            # ---------------- DRAW PORTAL SPRITE ----------------

            if portal_unlocked:
                portal_image = portal_frames_unlocked[portal_frame]
            else:
                portal_image = portal_frames_locked[portal_frame]

            portal_draw_x = portal.centerx - scroll_x - portal_image.get_width() // 2
            portal_draw_y = portal.centery - scroll_y - portal_image.get_height() // 2

            screen.blit(
                portal_image,
                (portal_draw_x, portal_draw_y)
            )
            
            # Only allow portal entry if all enemies are defeated
            if portal_unlocked and player.colliderect(portal):
                start_level((current_level_index + 1) % TOTAL_LEVELS)

            # ---------------- ENEMY AI ----------------
            for enemy in enemies:

                rect = enemy["rect"]

                if enemy["dead"]:

                    enemy["state"] = "death"

                    if pygame.time.get_ticks() - enemy["last_update"] > 140:
                        enemy["frame"] += 1
                        enemy["last_update"] = pygame.time.get_ticks()

                        if enemy["frame"] >= len(enemy_death_frames):
                            enemy["death_done"] = True
                            enemy["frame"] = len(enemy_death_frames) - 1

                    continue

                dx = player.x - rect.x
                dy = player.y - rect.y

                dist = (dx*dx + dy*dy) ** 0.5

                if dist != 0:
                    dx /= dist
                    dy /= dist

                move_x = dx * enemy_spd
                move_y = dy * enemy_spd

                enemy["flip"] = dx < 0

                def can_move(nx, ny):
                    test = rect.move(nx, ny)
                    return not any(test.colliderect(obs) for obs in Obstacles)

                moving = False

                if can_move(move_x, move_y):
                    rect.x += move_x
                    rect.y += move_y
                    moving = True

                elif can_move(move_x, 0):
                    rect.x += move_x
                    moving = True

                elif can_move(0, move_y):
                    rect.y += move_y
                    moving = True

                if enemy["state"] != "walk":
                    enemy["frame"] = 0
                    enemy["state"] = "walk"

                else:
                    enemy["state"] = "idle"
                    enemy["frame"] = 0

                # Attack player
                if rect.colliderect(player):

                    enemy["state"] = "attack"
                    enemy["frame"] = 0

                    if pygame.time.get_ticks() - enemy["last_update"] > 400:
                        player_hp -= enemy_damage

                    if player_hp < 0:
                        player_hp = 0

                # Animate
                if pygame.time.get_ticks() - enemy["last_update"] > 140:

                    enemy["frame"] += 1
                    enemy["last_update"] = pygame.time.get_ticks()

                    if enemy["state"] == "idle":
                        enemy["frame"] %= len(enemy_idle_frames)

                    elif enemy["state"] == "walk":
                        enemy["frame"] %= len(enemy_walk_frames)

                    elif enemy["state"] == "attack":
                        enemy["frame"] %= len(enemy_attack_frames)

            # ---------------- ATTACK ----------------
            if attacking:
                if pygame.time.get_ticks() - attack_time > attack_duration:
                    attacking = False
                else:
                    for enemy in enemies:

                        if enemy["dead"]:
                            continue

                        if attack_rect.colliderect(enemy["rect"]):

                            enemy["hp"] -= 1

                            hit_channel = pygame.mixer.find_channel()

                            if hit_channel:
                                hit_channel.play(sound_attack_hit)

                            if enemy["hp"] <= 0:

                                enemy["dead"] = True
                                enemy["frame"] = 0
                                enemy["last_update"] = pygame.time.get_ticks()

                                kill_count += 1

            enemies = [e for e in enemies if not e["death_done"]]

            # Draw dash indicator when active
            if dashing:
                # Draw a visual effect showing the dash is active
                progress = (current_time - dash_start_time) / dash_duration
                pygame.draw.circle(screen, (100, 200, 255), player_scroll.center, int(40 * (1 - progress)), 2)

            # ---------------- DRAW ENEMIES ----------------
            for enemy in enemies:

                rect = enemy["rect"]

                if enemy["state"] == "idle":
                    frame_list = enemy_idle_frames

                elif enemy["state"] == "walk":
                    frame_list = enemy_walk_frames

                elif enemy["state"] == "attack":
                    frame_list = enemy_attack_frames

                else:
                    frame_list = enemy_death_frames

                frame = frame_list[enemy["frame"]]

                frame = pygame.transform.flip(frame, enemy["flip"], False)

                screen.blit(
                    frame,
                    (
                        rect.x - scroll_x - 55,
                        rect.y - scroll_y - 50
                    )
                )
                


            # ---------------- ATTACK VISUAL ----------------
            if attacking:
                pygame.draw.rect(screen, YELLOW,
                    (attack_rect.x - scroll_x, attack_rect.y - scroll_y,
                    attack_rect.width, attack_rect.height), 2)

            # ---------------- PLAYER DRAW ----------------
            player_scroll = pygame.Rect(player.x - scroll_x, player.y - scroll_y, player.width, player.height)
            flip = cx < screen.get_width() / 2
            screen.blit(pygame.transform.flip(dan, flip, False),
                        (player_scroll.x - 22, player_scroll.y - 5))

            # Exit to menu button
            exit_hover = EXIT_BUTTON_RECT.collidepoint((cx, cy))
            pygame.draw.rect(screen, EXIT_BUTTON_HOVER if exit_hover else EXIT_BUTTON_COLOR, EXIT_BUTTON_RECT, border_radius=10)
            pygame.draw.rect(screen, MENU_OUTLINE, EXIT_BUTTON_RECT, 2, border_radius=10)
            exit_label = menu_small_font.render(EXIT_BUTTON_LABEL, True, MENU_TEXT)
            screen.blit(exit_label, exit_label.get_rect(center=EXIT_BUTTON_RECT.center))

            # Display level name and controls
            level_text = hud_font.render(f"Level: {level_name}", True, WHITE)
            screen.blit(level_text, (10, 40))

            # ---------------- SCOREBOARD ----------------
            score_text = hud_font.render(f"KILLS: {kill_count}", True, YELLOW)
            score_rect = score_text.get_rect(center=(screen.get_width() // 2, 30))
            screen.blit(score_text, score_rect)

            if player_hp <= 0 and not game_over_sound_played:
                sound_game_over.play()

                # Stop current music
                pygame.mixer.music.stop()

                game_over_sound_played = True
                menu_state = "game_over"



        pygame.display.flip()
        clock.tick(60)

pygame.quit()
