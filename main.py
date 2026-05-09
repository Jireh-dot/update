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

sound_opener = pygame.mixer.Sound('assets/start_sound.wav') # open game sfx
sound_click = pygame.mixer.Sound('assets/click.wav')   # Play/Main Menu/restart
sound_quit = pygame.mixer.Sound('assets/quit.wav')     # Quit button
sound_portal_unlock = pygame.mixer.Sound('assets/portal_unlock.wav') #plays only when unlocked
sound_game_over = pygame.mixer.Sound('assets/game_over.wav') #game over sfx
sound_attack_hit = pygame.mixer.Sound('assets/attack_hit.wav') #plays when enemies get hit
sound_demon_laugh = pygame.mixer.Sound('assets/demon_laugh.wav')



sound_opener.play()


sound_opener.set_volume(0.4)
sound_click.set_volume(0.7)
sound_quit.set_volume(0.7)
sound_portal_unlock.set_volume(0.8)
sound_game_over.set_volume(0.8)
sound_attack_hit.set_volume(0.6)
sound_demon_laugh.set_volume(0.6)

demon_laugh_interval = 8000  # every 8 seconds
last_demon_laugh = 0

# ---------------- MUSIC ----------------
MENU_MUSIC = "assets/hell_menu.wav"
GAME_MUSIC = "assets/bg.wav"

pygame.mixer.music.load(MENU_MUSIC)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # menu music loop

playing_game_music = False

def play_menu_music():
    global playing_game_music

    pygame.mixer.music.stop()
    pygame.mixer.music.load(MENU_MUSIC)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    playing_game_music = False


def play_game_music():
    global playing_game_music

    if not playing_game_music:
        pygame.mixer.music.stop()  # stop hell_menu.wav
        pygame.mixer.music.load(GAME_MUSIC)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # loop bg.wav

        playing_game_music = True


portal_sound_played = False


screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

with open("level.json", "r") as f:
    level_data = json.load(f)

current_level_index = 0

tmx_data = None


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
        obstacles.append(pygame.Rect(obs["x"], obs["y"], obs["w"], obs["h"]))

    tmx_path = lvl.get("tmx_file")
    tmx_data = load_pygame(tmx_path) if tmx_path else None 
    tmx_path = 'assets/level1.tmx'

    return world_w, world_h, obstacles, lvl["name"], tmx_data


def start_level(index, reset_hp=False):
    global current_level_index, WORLD_WIDTH, WORLD_HEIGHT
    global Obstacles, level_name, tmx_data
    global scroll_x, scroll_y
    global player_hp, enemies, enemy_hp
    global spawned_count, dashing, last_dash
    global portal_sound_played
    global kill_count, level_kills, total_kills
    global ENEMIES_PER_LEVEL   # <-- IMPORTANT

    kill_count = 0
    level_kills = 0

    if index == 0 and reset_hp:
        total_kills = 0

    current_level_index = index
    WORLD_WIDTH, WORLD_HEIGHT, Obstacles, level_name, tmx_data = load_level(index)

    player.topleft = (640, 360)
    scroll_x, scroll_y = 0, 0
    dashing = False
    last_dash = 0

    if reset_hp:
        player_hp = 100

    # DYNAMIC ENEMY SCALING
    ENEMIES_PER_LEVEL = 15 + current_level_index * 5

    


    enemies.clear()
    enemy_hp.clear()
    spawned_count = 0
    portal_sound_played = False

    for _ in range(ENEMIES_PER_LEVEL):
        spawn_enemy()


def reset_player_state():
        global player_hp
        player_hp = 100

WORLD_WIDTH, WORLD_HEIGHT, Obstacles, level_name, tmx_data = load_level(current_level_index)

scroll_x = 0
scroll_y = 0

kill_count = 0
level_kills = 0
total_kills = 0
level_scores = []  # stores per-level results

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
EXIT_BUTTON_RECT = pygame.Rect(1280 - 170, 10, 160, 42)
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

player = pygame.Rect(450, 300, 50, 76)

# ---------------- PLAYER SPRITESHEET ----------------
player_sheet = pygame.image.load("assets/run_right.png").convert_alpha()
player_spd = 5
player_hp = 100
portal = pygame.Rect(850, 550, 50, 76)
run_frames = []

PLAYER_FRAME_WIDTH = 96
PLAYER_FRAME_HEIGHT = 80

for i in range(8):

    frame = player_sheet.subsurface(
        pygame.Rect(
            i * PLAYER_FRAME_WIDTH,
            0,
            PLAYER_FRAME_WIDTH,
            PLAYER_FRAME_HEIGHT
        )
    )

    # Resize sprite
    frame = pygame.transform.scale(frame, (225, 187))

    run_frames.append(frame)

current_frame = 0
animation_speed = 0.18
# ---------------- ATTACK SPRITESHEET ----------------
attack_sheet = pygame.image.load("assets/attack2_right.png").convert_alpha()

attack_frames = []

for i in range(8):

    frame = attack_sheet.subsurface(
        pygame.Rect(
            i * PLAYER_FRAME_WIDTH,
            0,
            PLAYER_FRAME_WIDTH,
            PLAYER_FRAME_HEIGHT
        )
    )

    frame = pygame.transform.scale(frame, (225, 187))

    attack_frames.append(frame)

attack_frame = 0
attack_animation_speed = 0.25
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
# ---------------- ENEMY SPRITESHEET ----------------
enemy_sheet = pygame.image.load("assets/enemy_sheet.png").convert_alpha()

enemy_frames = []

FRAME_WIDTH = 16
FRAME_HEIGHT = 16

for i in range(4):
    frame = enemy_sheet.subsurface(
        pygame.Rect(i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT)
    )

    # Resize enemy sprite
    frame = pygame.transform.scale(frame, (64, 64))

    enemy_frames.append(frame)

enemy_animation_speed = 0.12
enemy_animation_frame = 0
enemies = []
enemy_hp = []

spawned_count = 0

enemy_spd = 2
enemy_damage = 0.2

def spawn_enemy():
    global spawned_count
    for _ in range(50):
        x = random.randint(0, WORLD_WIDTH - 40)
        y = random.randint(0, WORLD_HEIGHT - 60)
        new_enemy = pygame.Rect(x, y, 48, 48)

        if not any(new_enemy.colliderect(obs) for obs in Obstacles):
            enemies.append(new_enemy)
            enemy_hp.append(3)
            spawned_count += 1
            return

# spawn initial wave
ENEMIES_PER_LEVEL = 15 + current_level_index * 5
for _ in range(ENEMIES_PER_LEVEL):
    spawn_enemy()

# ---------------- ATTACK ----------------
attack_cooldown = 400
last_attack = 0
attack_duration = 320
attacking = False
attack_time = 0
attack_rect = pygame.Rect(0, 0, 0, 0)

screen = pygame.display.set_mode((1280, 720))
TOTAL_LEVELS = len(level_data["levels"])
attack_frame = 0
run = True
while run:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sound_quit.play()
            pygame.time.delay(int(sound_quit.get_length() * 1000))
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
                        play_game_music()
                        reset_player_state()
                        start_level(0, reset_hp=True)
                        menu_state = "play"
                        player.topleft = (640, 360)
                        scroll_x, scroll_y = 0, 0
                    else:
                        sound_quit.play()
                        pygame.time.delay(int(sound_quit.get_length() * 1000))
                        run = False
                if event.key == pygame.K_ESCAPE:
                    sound_quit.play()
                    pygame.time.delay(int(sound_quit.get_length() * 1000))
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
                            play_game_music()
                            reset_player_state()
                            start_level(0, reset_hp=True)
                            menu_state = "play"
                            player.topleft = (640, 360)
                            scroll_x, scroll_y = 0, 0
                        else:
                            sound_quit.play()
                            pygame.time.delay(int(sound_quit.get_length() * 1000))
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

                        # Restart bg.wav
                        play_game_music()

                        menu_state = "play"
                        total_kills = 0
                        start_level(0, reset_hp=True)
                    else:
                        sound_quit.play()
                        pygame.time.delay(int(sound_quit.get_length() * 1000))
                        run = False
                if event.key == pygame.K_ESCAPE:
                    sound_quit.play()
                    pygame.time.delay(int(sound_quit.get_length() * 1000))
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

                            # Restart bg.wav
                            play_game_music()

                            menu_state = "play"
                            total_kills = 0
                            start_level(0, reset_hp=True)
                        else:
                            sound_quit.play()
                            pygame.time.delay(int(sound_quit.get_length() * 1000))
                            run = False

        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sound_click.play()
                    play_game_music()
                    menu_state = "menu"
                if event.key in (pygame.K_n, pygame.K_b):
                    if event.key == pygame.K_n:
                        next_index = (current_level_index + 1) % TOTAL_LEVELS
                    else:
                        next_index = (current_level_index - 1) % TOTAL_LEVELS
                    start_level(next_index)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if EXIT_BUTTON_RECT.collidepoint(event.pos):
                    sound_click.play()
                    play_game_music()
                    menu_state = "menu"
                else:
                    now = pygame.time.get_ticks()
                    if now - last_attack > attack_cooldown:
                        attacking = True
                        attack_frame = 0
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
        
        bridge_img = pygame.image.load("assets/BGD.png").convert_alpha()

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
            pygame.draw.line(screen, (40, 10, 10), (0, y), (screen.get_width(), y), 1)

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


        # ================= SCOREBOARD (FIXED POSITION) =================

        base_y = 240  # moved slightly higher so buttons don't overlap

        # Total kills (centered)
        total_text = menu_item_font.render(
            f"TOTAL KILLS: {total_kills}",
            True,
            (255, 220, 220)
        )
        screen.blit(
            total_text,
            total_text.get_rect(center=(screen.get_width() / 2, base_y))
        )

       

    elif menu_state == "play":
    

        now = pygame.time.get_ticks()

        if now - last_demon_laugh > demon_laugh_interval:
            sound_demon_laugh.play()
            last_demon_laugh = now
            demon_laugh_interval = random.randint(5000, 12000)

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


        # Draw TMX map
        if tmx_data:
            for layer in tmx_data.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer):
                    for x, y, gid in layer:
                        tile = tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            screen.blit(tile, (x * tmx_data.tilewidth - scroll_x, y * tmx_data.tileheight - scroll_y))

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
                    dash_start_time = current_time
                    dash_velocity_x = move_x * dash_speed
                    dash_velocity_y = move_y * dash_speed
                    last_dash = current_time
        # Detect movement
        moving = False
        # Update dash state
        if dashing and current_time - dash_start_time > dash_duration:
            dashing = False
        
        # Horizontal movement and collision
        if dashing:
            dx = dash_velocity_x
        else:
            dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) * player_spd - (keys[pygame.K_LEFT] or keys[pygame.K_a]) * player_spd

            if dx != 0:
                moving = True
        
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
            if dy != 0:
                moving = True
        player.y += dy
        for obs in Obstacles:
            if player.colliderect(obs):
                if dy > 0:
                    player.bottom = obs.top
                elif dy < 0:
                    player.top = obs.bottom

        for obs in Obstacles:
            pygame.draw.rect(screen, (0, 0, 0), (obs.x - scroll_x, obs.y - scroll_y, obs.width, obs.height))

        # Check if portal is unlocked (all enemies defeated)
        portal_unlocked = (len(enemies) == 0)
        
        # Play unlock sound only once
        if portal_unlocked and not portal_sound_played:
            portal_channel.play(sound_portal_unlock)
            portal_sound_played = True

        # Draw portal in green when unlocked, red when locked
        portal_color = GREEN if portal_unlocked else RED
        pygame.draw.rect(screen, portal_color, (portal.x - scroll_x, portal.y - scroll_y, portal.width, portal.height))
        
        # Only allow portal entry if all enemies are defeated
        if portal_unlocked and player.colliderect(portal):
            level_scores.append({
                "level": current_level_index,
                "kills": level_kills
            })
            start_level((current_level_index + 1) % TOTAL_LEVELS)

        # ---------------- ENEMY AI ----------------
        for enemy in enemies:
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            dist = (dx*dx + dy*dy) ** 0.5
            if dist == 0:
                continue
            dx /= dist
            dy /= dist
            move_x = dx * enemy_spd
            move_y = dy * enemy_spd
            def can_move(nx, ny):
                test = enemy.move(nx, ny)
                return not any(test.colliderect(obs) for obs in Obstacles)
            if can_move(move_x, move_y):
                enemy.x += move_x
                enemy.y += move_y
            elif can_move(move_x, 0):
                enemy.x += move_x
            elif can_move(0, move_y):
                enemy.y += move_y
            else:
                tx = -dy
                ty = dx
                length = (tx*tx + ty*ty) ** 0.5
                if length != 0:
                    tx /= length
                    ty /= length
                    slide_speed = enemy_spd
                    for angle in (1, -1, 2, -2):
                        sx = tx * slide_speed * angle
                        sy = ty * slide_speed * angle
                        if can_move(sx, sy):
                            enemy.x += sx
                            enemy.y += sy
                            break
            if enemy.colliderect(player):
                player_hp -= enemy_damage
                if player_hp < 0:
                    player_hp = 0


        # ---------------- ATTACK ----------------
        if attacking:

            attack_frame += attack_animation_speed

            if attack_frame >= len(attack_frames):
                attack_frame = 0
                attacking = False

            else:
                for i in range(len(enemies)-1, -1, -1):
                    if attack_rect.colliderect(enemies[i]):
                        enemy_hp[i] -= 1

                        # Play hit sound
                        attack_channel.play(sound_attack_hit)

                        if enemy_hp[i] <= 0:
                            enemies.pop(i)
                            enemy_hp.pop(i)

                            level_kills += 1
                            total_kills += 1
        # Draw dash indicator when active
        if dashing:
            # Draw a visual effect showing the dash is active
            progress = (current_time - dash_start_time) / dash_duration
            pygame.draw.circle(screen, (100, 200, 255), player_scroll.center, int(40 * (1 - progress)), 2)

        # ---------------- DRAW ENEMIES ----------------
        # Update enemy animation
        enemy_animation_frame += enemy_animation_speed

        if enemy_animation_frame >= len(enemy_frames):
            enemy_animation_frame = 0
            
        for enemy in enemies:
            enemy_image = enemy_frames[int(enemy_animation_frame)]

            # Flip enemy depending on player position
            flip_enemy = player.x < enemy.x

            enemy_image = pygame.transform.flip(enemy_image, flip_enemy, False)

            screen.blit(
                enemy_image,
                (enemy.x - scroll_x - 12, enemy.y - scroll_y - 10)
            )

        # ---------------- ATTACK VISUAL ----------------
        if attacking:
            pygame.draw.rect(screen, YELLOW,
                (attack_rect.x - scroll_x, attack_rect.y - scroll_y,
                 attack_rect.width, attack_rect.height), 2)

        # Update animation
        if moving:
            current_frame += animation_speed

            if current_frame >= len(run_frames):
                current_frame = 0
        else:
            current_frame = 0
        # ---------------- PLAYER DRAW ----------------
        player_scroll = pygame.Rect(
            player.x - scroll_x,
            player.y - scroll_y,
            player.width,
            player.height
        )

        flip = cx < screen.get_width() / 2

        # ATTACK animation
        if attacking:
            player_image = attack_frames[int(attack_frame)]

        # RUN animation
        else:
            player_image = run_frames[int(current_frame)]

        # Flip sprite
        player_image = pygame.transform.flip(player_image, flip, False)

        # Draw player
        screen.blit(player_image, (player_scroll.x - 48, player_scroll.y - 30))
        # Exit to menu button
        exit_hover = EXIT_BUTTON_RECT.collidepoint((cx, cy))
        pygame.draw.rect(screen, EXIT_BUTTON_HOVER if exit_hover else EXIT_BUTTON_COLOR, EXIT_BUTTON_RECT, border_radius=10)
        pygame.draw.rect(screen, MENU_OUTLINE, EXIT_BUTTON_RECT, 2, border_radius=10)
        exit_label = menu_small_font.render(EXIT_BUTTON_LABEL, True, MENU_TEXT)
        screen.blit(exit_label, exit_label.get_rect(center=EXIT_BUTTON_RECT.center))

        # Display level name and controls
        level_text = hud_font.render(f"Level: {level_name}", True, WHITE)
        screen.blit(level_text, (10, 40))

        # ---------------- HP ----------------
        pygame.draw.rect(screen, RED, (10, 10, 200, 20))
        pygame.draw.rect(screen, GREEN, (10, 10, int(2 * player_hp), 20))
        pygame.draw.rect(screen, WHITE, (10, 10, 200, 20), 2)


        # ---------------- KILL COUNTERS (TOP CENTER) ----------------
        level_score_text = hud_font.render(f"LEVEL KILLS: {level_kills}", True, YELLOW)
        total_score_text = hud_font.render(f"TOTAL KILLS: {total_kills}", True, YELLOW)

        spacing = 30  # space between the two texts

        # measure widths
        level_w = level_score_text.get_width()
        total_w = total_score_text.get_width()

        combined_width = level_w + spacing + total_w

        start_x = (screen.get_width() - combined_width) // 2
        y = 20  # VERY TOP

        screen.blit(level_score_text, (start_x, y))
        screen.blit(total_score_text, (start_x + level_w + spacing, y))

        if player_hp <= 0:

                # Stop bg.wav music
            pygame.mixer.music.stop()

            # Play game over sound
            sound_game_over.play()

            # Allow bg.wav to restart later
            playing_game_music = False

            menu_state = "game_over"

    

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
