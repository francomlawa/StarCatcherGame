"""
Star Catcher
------------
A simple 2D game built with Python and Pygame.

How to play:
- Move the basket left and right using the LEFT and RIGHT arrow keys.
- Catch yellow stars (+1) and rare golden stars (+5).
- Build combos by catching stars without missing — higher combos = bonus points.
- Grab cyan shields for one free bomb block.
- Avoid red bombs. Catching a bomb costs a life (unless shielded).
- Missing stars also costs a life. Reach higher levels as your score grows.

Controls:
- LEFT / RIGHT arrows : move the basket
- R                   : restart after game over
- ESC                 : quit
"""

import math
import os
import pygame
import random
import sys

# ---------- Basic Setup ----------
pygame.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Star Catcher")

clock = pygame.time.Clock()
FPS = 60
SCALE = min(WIDTH / 600, HEIGHT / 700)

def s(value):
    """Scale sizes for fullscreen displays."""
    return max(1, int(value * SCALE))

# ---------- Colors ----------
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
YELLOW = (255, 215, 0)
GOLD = (255, 180, 30)
RED = (220, 50, 50)
BLUE = (70, 130, 220)
CYAN = (80, 220, 255)
GREEN = (60, 220, 120)
PURPLE = (180, 100, 255)
GRAY = (180, 180, 180)

# ---------- Fonts ----------
font_small = pygame.font.SysFont("arial", s(28))
font_big = pygame.font.SysFont("arial", s(60), bold=True)
font_huge = pygame.font.SysFont("arial", s(80), bold=True)

# ---------- Background ----------
def create_gradient_background():
    surf = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = (
            int(12 + t * 30),
            int(18 + t * 45),
            int(55 + t * 90),
        )
        pygame.draw.line(surf, color, (0, y), (WIDTH, y))
    return surf


background = create_gradient_background()
bg_stars = [
    {
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "size": random.choice([1, 1, 2]),
        "phase": random.uniform(0, math.tau),
    }
    for _ in range(int(80 * SCALE))
]

# ---------- Player (Basket) ----------
player_width, player_height = s(100), s(20)
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - s(60)
player_speed = s(8)

# ---------- Falling Objects ----------
object_list = []
spawn_timer = 0
spawn_interval = 45
OBJ_RADIUS = s(14)

# ---------- Particles & Effects ----------
particles = []
flash_text = ""
flash_timer = 0
shake_timer = 0

# ---------- Game State ----------
score = 0
high_score = 0
lives = 3
level = 1
combo = 0
max_combo = 0
shield_active = False
game_over = False
fall_speed_base = 4
frame_count = 0

HIGH_SCORE_FILE = os.path.join(os.path.dirname(__file__), "highscore.txt")


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0


def save_high_score(value):
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
            f.write(str(value))
    except OSError:
        pass


high_score = load_high_score()


def combo_multiplier():
    if combo >= 6:
        return 3
    if combo >= 3:
        return 2
    return 1


def spawn_particles(x, y, color, count=None):
    count = count or s(14)
    for _ in range(count):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 7) * SCALE
        particles.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(18, 35),
            "color": color,
            "size": random.randint(max(1, s(2)), max(2, s(5))),
        })


def show_flash(text, duration=90):
    global flash_text, flash_timer
    flash_text = text
    flash_timer = duration


def spawn_object():
    roll = random.random()
    if roll < 0.08:
        obj_type = "golden"
    elif roll < 0.15:
        obj_type = "shield"
    elif roll < 0.40:
        obj_type = "bomb"
    else:
        obj_type = "star"

    x = random.randint(s(20), WIDTH - s(20))
    speed = fall_speed_base + random.uniform(0, 2)
    object_list.append({
        "x": x,
        "y": -s(20),
        "type": obj_type,
        "speed": speed,
        "rotation": random.uniform(0, 360),
        "rotation_speed": random.uniform(-4, 4),
    })


def draw_star(surface, x, y, size, color, rotation=0):
    points = []
    for i in range(10):
        angle = math.radians(i * 36 - 90 + rotation)
        radius = size if i % 2 == 0 else size / 2
        points.append((x + radius * math.cos(angle), y + radius * math.sin(angle)))
    pygame.draw.polygon(surface, color, points)


def draw_background(surface):
    surface.blit(background, (0, 0))
    for star in bg_stars:
        twinkle = 120 + int(80 * math.sin(frame_count * 0.05 + star["phase"]))
        color = (twinkle, twinkle, min(255, twinkle + 40))
        pygame.draw.circle(surface, color, (star["x"], star["y"]), star["size"])


def draw_player(surface):
    glow = combo >= 3
    if shield_active:
        pygame.draw.rect(
            surface, CYAN,
            (player_x - s(6), player_y - s(6), player_width + s(12), player_height + s(12)),
            border_radius=s(10), width=s(3),
        )
    color = PURPLE if glow else BLUE
    pygame.draw.rect(
        surface, color,
        (player_x, player_y, player_width, player_height),
        border_radius=s(6),
    )
    pygame.draw.rect(
        surface, WHITE,
        (player_x, player_y, player_width, player_height),
        s(2), border_radius=s(6),
    )


def draw_objects(surface):
    for obj in object_list:
        x, y = int(obj["x"]), int(obj["y"])
        rot = obj["rotation"]
        if obj["type"] == "star":
            draw_star(surface, x, y, s(15), YELLOW, rot)
        elif obj["type"] == "golden":
            draw_star(surface, x, y, s(18), GOLD, rot)
            pygame.draw.circle(surface, WHITE, (x, y), s(22), s(2))
        elif obj["type"] == "shield":
            pygame.draw.circle(surface, CYAN, (x, y), OBJ_RADIUS)
            pygame.draw.circle(surface, WHITE, (x, y), OBJ_RADIUS, s(2))
            draw_star(surface, x, y, s(8), WHITE, rot)
        else:
            pygame.draw.circle(surface, RED, (x, y), OBJ_RADIUS)
            pygame.draw.circle(surface, BLACK, (x, y), OBJ_RADIUS, s(2))
            fuse_y = y - OBJ_RADIUS - s(6)
            pygame.draw.line(surface, YELLOW, (x, y - OBJ_RADIUS), (x, fuse_y), s(3))


def draw_particles(surface):
    for p in particles:
        alpha = min(255, int(255 * p["life"] / 35))
        color = (*p["color"][:3], alpha) if len(p["color"]) == 3 else p["color"]
        pygame.draw.circle(surface, color[:3], (int(p["x"]), int(p["y"])), p["size"])


def draw_hud(surface):
    mult = combo_multiplier()
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    lives_text = font_small.render(f"Lives: {'♥' * lives}", True, RED)
    level_text = font_small.render(f"Level: {level}", True, CYAN)
    high_text = font_small.render(f"Best: {high_score}", True, GOLD)
    surface.blit(score_text, (s(15), s(15)))
    surface.blit(level_text, (s(15), s(50)))
    surface.blit(lives_text, (WIDTH - s(160), s(15)))
    surface.blit(high_text, (WIDTH - s(160), s(50)))

    if combo >= 2:
        combo_color = GOLD if mult >= 3 else GREEN
        combo_text = font_small.render(f"Combo x{mult} ({combo})", True, combo_color)
        surface.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, s(15)))

    if shield_active:
        shield_text = font_small.render("SHIELD ACTIVE", True, CYAN)
        surface.blit(shield_text, (WIDTH // 2 - shield_text.get_width() // 2, s(50)))


def draw_flash(surface):
    if flash_timer > 0:
        text = font_big.render(flash_text, True, GOLD if "LEVEL" in flash_text else GREEN)
        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))


def draw_game_over(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(190)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))

    text1 = font_huge.render("GAME OVER", True, RED)
    text2 = font_big.render(f"Score: {score}", True, WHITE)
    text3 = font_small.render(f"Best Combo: {max_combo}  |  Level Reached: {level}", True, GRAY)
    new_record = score >= high_score and score > 0
    text4 = font_small.render("NEW HIGH SCORE!" if new_record else f"High Score: {high_score}", True, GOLD)
    text5 = font_small.render("Press R to Restart or ESC to Quit", True, WHITE)

    center_y = HEIGHT // 2
    surface.blit(text1, (WIDTH // 2 - text1.get_width() // 2, center_y - s(120)))
    surface.blit(text2, (WIDTH // 2 - text2.get_width() // 2, center_y - s(30)))
    surface.blit(text3, (WIDTH // 2 - text3.get_width() // 2, center_y + s(20)))
    surface.blit(text4, (WIDTH // 2 - text4.get_width() // 2, center_y + s(60)))
    surface.blit(text5, (WIDTH // 2 - text5.get_width() // 2, center_y + s(110)))


def update_particles():
    global particles
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.15 * SCALE
        p["life"] -= 1
        if p["life"] <= 0:
            particles.remove(p)


def handle_catch(obj):
    global score, combo, max_combo, level, shield_active, shake_timer

    obj_type = obj["type"]
    if obj_type == "bomb":
        if shield_active:
            shield_active = False
            spawn_particles(obj["x"], obj["y"], CYAN, s(20))
            show_flash("SHIELD BLOCKED!", 60)
        else:
            lives_change(-1)
            combo = 0
            shake_timer = 15
            spawn_particles(obj["x"], obj["y"], RED, s(18))
        return

    if obj_type == "shield":
        shield_active = True
        spawn_particles(obj["x"], obj["y"], CYAN, s(16))
        show_flash("SHIELD READY!", 50)
        return

    combo += 1
    max_combo = max(max_combo, combo)
    mult = combo_multiplier()
    points = (5 if obj_type == "golden" else 1) * mult
    score += points

    color = GOLD if obj_type == "golden" else YELLOW
    spawn_particles(obj["x"], obj["y"], color, s(16 if obj_type == "golden" else 12))

    if combo in (3, 6, 10):
        show_flash(f"COMBO x{mult}!", 70)

    new_level = score // 10 + 1
    if new_level > level:
        level = new_level
        show_flash(f"LEVEL {level}!", 90)
        global spawn_interval, fall_speed_base
        if spawn_interval > s(18):
            spawn_interval -= 1
        fall_speed_base += 0.2


def lives_change(delta):
    global lives, game_over, high_score
    lives += delta
    if lives <= 0:
        game_over = True
        if score > high_score:
            high_score = score
            save_high_score(score)


def reset_game():
    global score, lives, game_over, object_list, player_x, fall_speed_base
    global spawn_interval, level, combo, max_combo, shield_active, particles
    global flash_text, flash_timer, shake_timer

    score = 0
    lives = 3
    level = 1
    combo = 0
    max_combo = 0
    shield_active = False
    game_over = False
    object_list = []
    particles = []
    flash_text = ""
    flash_timer = 0
    shake_timer = 0
    fall_speed_base = 4
    spawn_interval = 45
    player_x = WIDTH // 2 - player_width // 2


def get_shake_offset():
    if shake_timer <= 0:
        return 0, 0
    return random.randint(-s(6), s(6)), random.randint(-s(4), s(4))


# ---------- Main Game Loop ----------
running = True
while running:
    clock.tick(FPS)
    frame_count += 1

    shake_x, shake_y = get_shake_offset()
    draw_surface = pygame.Surface((WIDTH, HEIGHT))
    draw_background(draw_surface)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r and game_over:
                reset_game()

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
        player_x = max(0, min(WIDTH - player_width, player_x))

        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            spawn_object()
            spawn_timer = 0

        for obj in object_list[:]:
            obj["y"] += obj["speed"]
            obj["rotation"] += obj["rotation_speed"]

            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            obj_rect = pygame.Rect(obj["x"] - OBJ_RADIUS, obj["y"] - OBJ_RADIUS, OBJ_RADIUS * 2, OBJ_RADIUS * 2)

            if player_rect.colliderect(obj_rect):
                handle_catch(obj)
                object_list.remove(obj)
                continue

            if obj["y"] > HEIGHT + s(20):
                if obj["type"] in ("star", "golden"):
                    lives_change(-1)
                    combo = 0
                    spawn_particles(obj["x"], HEIGHT - s(10), RED, s(10))
                object_list.remove(obj)

    update_particles()
    if flash_timer > 0:
        flash_timer -= 1
    if shake_timer > 0:
        shake_timer -= 1

    draw_objects(draw_surface)
    draw_particles(draw_surface)
    draw_player(draw_surface)
    draw_hud(draw_surface)
    draw_flash(draw_surface)

    if game_over:
        draw_game_over(draw_surface)

    screen.fill(BLACK)
    screen.blit(draw_surface, (shake_x, shake_y))
    pygame.display.flip()

pygame.quit()
sys.exit()
