from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt

import os
import sys
import json
import pygame
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

WIDTH, HEIGHT = 400, 600
FPS = 60

# Module-level placeholders; initialized in main()
screen = None
clock = None
font = None
big_font = None
music_enabled = True

# Preload two background music tracks; place level1.mp3 and level2.mp3 in this directory
LEVEL1_MUSIC = os.path.join(SCRIPT_DIR, "level1.mp3")
LEVEL2_MUSIC = os.path.join(SCRIPT_DIR, "level2.mp3")
current_level = 1  # Track music level

# Multi-level config (T-000096 / T-000094 spec).
# Each level tightens pipe gap and increases scroll speed.
LEVELS = {
    1: {"pipe_gap": 250, "pipe_speed": 3, "music": LEVEL1_MUSIC},
    2: {"pipe_gap": 200, "pipe_speed": 4, "music": LEVEL2_MUSIC},
    3: {"pipe_gap": 150, "pipe_speed": 5, "music": LEVEL2_MUSIC},
}
MAX_LEVEL = 3
SCORE_TO_ADVANCE = 5  # Pipes passed per level before auto-progressing
LEVEL_OVERLAY_FRAMES = 60  # ~1 second at 60 FPS

# Persisted-progress file (gitignored)
SAVED_PROGRESS_FILE = os.path.join(SCRIPT_DIR, "saved_progress.json")
highest_level = 1

def load_progress():
    global highest_level
    try:
        with open(SAVED_PROGRESS_FILE, "r") as f:
            data = json.load(f)
        lvl = int(data.get("highest_level", 1))
        if 1 <= lvl <= MAX_LEVEL:
            highest_level = lvl
    except (OSError, ValueError, KeyError, TypeError):
        highest_level = 1

def save_progress():
    try:
        with open(SAVED_PROGRESS_FILE, "w") as f:
            json.dump({"highest_level": highest_level}, f)
    except OSError:
        pass

def play_music(music_file):
    if not music_enabled:
        return
    try:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

def apply_level(level):
    """Swap pipe_gap, pipe_speed, and background music for the given level."""
    global current_level, PIPE_GAP, pipe_speed
    cfg = LEVELS.get(level, LEVELS[1])
    current_level = level
    PIPE_GAP = cfg["pipe_gap"]
    pipe_speed = cfg["pipe_speed"]
    play_music(cfg["music"])

# Bird parameters (simplified for young users)
BIRD_RADIUS = 20
bird_x = 50
bird_y = HEIGHT // 2
bird_vel = 0
GRAVITY = 0.3           # reduced from 0.5 for slower fall
JUMP_STRENGTH = -8      # reduced from -10 for easier control

# Pipe parameters (defaults; overridden by apply_level)
PIPE_WIDTH = 60
PIPE_GAP = 250
pipe_speed = 3
pipes = []
SPAWN_PIPE = pygame.USEREVENT + 1

score = 0
game_over = False

# New global flag for auto-play
auto_play = False

# New global flag for game start
started = False

# Level overlay frame countdown (0 = no overlay)
level_overlay_frames = 0
overlay_level = 1

# Selected starting level on the start screen
selected_level = 1

# Button rects are computed from constants and are safe at module scope
START_BUTTON_RECT = pygame.Rect(WIDTH//2 - 130, HEIGHT//2 - 20, 120, 40)
AUTO_START_BUTTON_RECT = pygame.Rect(WIDTH//2 + 10, HEIGHT//2 - 20, 120, 40)
AUTOPLAY_BUTTON_RECT = pygame.Rect(WIDTH - 140, 10, 120, 40)

# Level-select buttons on the start screen
_LEVEL_BTN_W, _LEVEL_BTN_H = 80, 40
_LEVEL_BTN_GAP = 10
_LEVEL_ROW_TOTAL = 3 * _LEVEL_BTN_W + 2 * _LEVEL_BTN_GAP
_LEVEL_ROW_LEFT = (WIDTH - _LEVEL_ROW_TOTAL) // 2
_LEVEL_ROW_TOP = HEIGHT // 2 - 90
LEVEL_BUTTON_RECTS = {
    n: pygame.Rect(_LEVEL_ROW_LEFT + (n - 1) * (_LEVEL_BTN_W + _LEVEL_BTN_GAP),
                   _LEVEL_ROW_TOP, _LEVEL_BTN_W, _LEVEL_BTN_H)
    for n in (1, 2, 3)
}

def reset_game(start_level=1):
    global bird_y, bird_vel, pipes, score, game_over, started, auto_play
    global level_overlay_frames, overlay_level
    bird_y = HEIGHT // 2
    bird_vel = 0
    pipes = []
    score = 0
    game_over = False
    started = False  # Reset started state
    auto_play = False  # Reset autoplay state
    apply_level(start_level)
    overlay_level = start_level
    level_overlay_frames = LEVEL_OVERLAY_FRAMES

def advance_level():
    """Auto-progress to the next level; bumps highest_level + persists."""
    global score, level_overlay_frames, overlay_level, highest_level
    next_level = current_level + 1
    if next_level > MAX_LEVEL:
        return False
    apply_level(next_level)
    score = 0  # Reset per-level score so the next bump fires after SCORE_TO_ADVANCE more pipes
    overlay_level = next_level
    level_overlay_frames = LEVEL_OVERLAY_FRAMES
    if next_level > highest_level:
        highest_level = next_level
        save_progress()
    return True

def draw():
    screen.fill((135, 206, 235))  # sky blue background
    # Draw start buttons if game not started or game is over
    if not started or game_over:  # Modified condition
        # Level-select row (always rendered on start/game-over screen)
        title = font.render("Select Level:", True, (0, 0, 0))
        title_rect = title.get_rect(center=(WIDTH // 2, _LEVEL_ROW_TOP - 22))
        screen.blit(title, title_rect)
        for n, rect in LEVEL_BUTTON_RECTS.items():
            unlocked = n <= highest_level
            if not unlocked:
                color = (140, 140, 140)
            elif n == selected_level:
                color = (255, 165, 0)  # highlight selected
            else:
                color = (50, 205, 50)
            pygame.draw.rect(screen, color, rect)
            lbl = font.render(f"L{n}", True, (255, 255, 255))
            lbl_rect = lbl.get_rect(center=rect.center)
            screen.blit(lbl, lbl_rect)

        # Regular Start button (left side)
        pygame.draw.rect(screen, (50, 205, 50), START_BUTTON_RECT)
        start_text = font.render("Start", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=START_BUTTON_RECT.center)
        screen.blit(start_text, start_rect)

        # Autoplay Start button (right side)
        pygame.draw.rect(screen, (50, 205, 50), AUTO_START_BUTTON_RECT)
        auto_text = font.render("Auto Start", True, (255, 255, 255))
        auto_rect = auto_text.get_rect(center=AUTO_START_BUTTON_RECT.center)
        screen.blit(auto_text, auto_rect)

        # Show score if game over
        if game_over:
            score_text = font.render(f"Final Score: {score}", True, (255, 0, 0))
            screen.blit(score_text, (WIDTH//2 - 70, HEIGHT//2 - 130))

        # ESC to quit hint (start screen and game-over)
        esc_hint = font.render("ESC to quit", True, (0, 0, 0))
        esc_rect = esc_hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(esc_hint, esc_rect)
    else:
        # Draw bird
        pygame.draw.circle(screen, (255, 255, 0), (bird_x, int(bird_y)), BIRD_RADIUS)
        # Draw pipes
        for pipe in pipes:
            pygame.draw.rect(screen, (34, 139, 34), pipe['top'])
            pygame.draw.rect(screen, (34, 139, 34), pipe['bottom'])
        # Draw score
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        # HUD: current level (T-000094 spec)
        level_text = font.render(f"Level: {current_level}", True, (0, 0, 0))
        screen.blit(level_text, (10, 40))
        # Draw "Autoplay" button (updated dimensions for longer text)
        pygame.draw.rect(screen, (50, 205, 50), AUTOPLAY_BUTTON_RECT)  # green button
        autoplay_text = font.render("Autoplay", True, (255, 255, 255))
        autoplay_rect = autoplay_text.get_rect(center=AUTOPLAY_BUTTON_RECT.center)
        screen.blit(autoplay_text, autoplay_rect)
        # Level-up overlay (~1s)
        if level_overlay_frames > 0:
            overlay = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, HEIGHT // 2 - 40))
            msg = big_font.render(f"Level {overlay_level}", True, (255, 255, 255))
            msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(msg, msg_rect)
    pygame.display.flip()

def parse_level_argv():
    """Return level int from `--level N` argv, or None."""
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--level" and i + 1 < len(argv):
            try:
                v = int(argv[i + 1])
                if 1 <= v <= MAX_LEVEL:
                    return v
            except ValueError:
                pass
        elif a.startswith("--level="):
            try:
                v = int(a.split("=", 1)[1])
                if 1 <= v <= MAX_LEVEL:
                    return v
            except ValueError:
                pass
    return None

def main():
    global screen, clock, font, big_font, music_enabled
    global bird_y, bird_vel, pipes, score, game_over, started, auto_play
    global selected_level, level_overlay_frames

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()

    try:
        pygame.mixer.init()
    except pygame.error:
        music_enabled = False

    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 64)
    pygame.time.set_timer(SPAWN_PIPE, 2000)  # increased delay from 1500ms

    load_progress()
    selected_level = highest_level  # default to highest unlocked

    # Optional CLI level override
    cli_level = parse_level_argv()
    if cli_level is not None:
        selected_level = min(cli_level, highest_level)
        reset_game(selected_level)
        started = True

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit(0)
            elif (not started or game_over) and event.type == pygame.MOUSEBUTTONDOWN:  # Modified condition
                mx, my = event.pos
                # Level-select buttons
                clicked_level = None
                for n, rect in LEVEL_BUTTON_RECTS.items():
                    if rect.collidepoint(mx, my) and n <= highest_level:
                        clicked_level = n
                        break
                if clicked_level is not None:
                    selected_level = clicked_level
                elif START_BUTTON_RECT.top <= my <= START_BUTTON_RECT.bottom:
                    if START_BUTTON_RECT.left <= mx <= START_BUTTON_RECT.right:  # Regular Start
                        reset_game(selected_level)
                        started = True
                    elif AUTO_START_BUTTON_RECT.left <= mx <= AUTO_START_BUTTON_RECT.right:  # Autoplay Start
                        reset_game(selected_level)
                        started = True
                        auto_play = True
            # Activate autoplay if "Autoplay" button is clicked
            elif started and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if AUTOPLAY_BUTTON_RECT.left <= mx <= AUTOPLAY_BUTTON_RECT.right and AUTOPLAY_BUTTON_RECT.top <= my <= AUTOPLAY_BUTTON_RECT.bottom:
                    auto_play = True
            if started and not game_over:
                # Always allow SPACE events but let autoplay override
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if not auto_play:
                        bird_vel = JUMP_STRENGTH
                if event.type == SPAWN_PIPE:
                    pipe_height = random.randint(50, HEIGHT - PIPE_GAP - 50)
                    top_pipe = pygame.Rect(WIDTH, 0, PIPE_WIDTH, pipe_height)
                    bottom_pipe = pygame.Rect(WIDTH, pipe_height + PIPE_GAP, PIPE_WIDTH, HEIGHT - pipe_height - PIPE_GAP)
                    pipes.append({'top': top_pipe, 'bottom': bottom_pipe})
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    reset_game(selected_level)

        if started and not game_over:
            # Tick down the level-up overlay (non-blocking; ESC still works)
            if level_overlay_frames > 0:
                level_overlay_frames -= 1

            # Refined autoplay logic with smoother transitions
            if auto_play and pipes:
                next_pipe = None
                for pipe in pipes:
                    if pipe['top'].x + PIPE_WIDTH > bird_x:
                        next_pipe = pipe
                        break

                if next_pipe:
                    gap_top = next_pipe['top'].height
                    gap_bottom = gap_top + PIPE_GAP
                    gap_center = (gap_top + gap_bottom) / 2
                    dx = next_pipe['top'].x - bird_x

                    # Adjusted jump logic with waiting period after crossing
                    if dx < 160:  # Reduced look-ahead distance
                        # Only jump if significantly below center or falling fast
                        if bird_y > gap_center + 25 or (bird_y > gap_center and bird_vel > 2):
                            bird_vel = JUMP_STRENGTH
                        # Wait a bit after passing pipe before next jump
                        elif dx < PIPE_WIDTH and bird_vel < 0:
                            bird_vel = 1  # Gentle fall after passing pipe

            # Update bird physics
            bird_vel += GRAVITY
            bird_y += bird_vel

            # Simplified boundary protection for autoplay
            if auto_play:
                if bird_y - BIRD_RADIUS <= 5:
                    bird_vel = 1  # Gentle downward movement
                elif bird_y + BIRD_RADIUS >= HEIGHT - 5:
                    bird_vel = JUMP_STRENGTH
            else:
                # Normal boundary checking for manual play
                if bird_y - BIRD_RADIUS <= 0 or bird_y + BIRD_RADIUS >= HEIGHT:
                    game_over = True

            # Move pipes and check for off-screen removal
            for pipe in pipes:
                pipe['top'].x -= pipe_speed
                pipe['bottom'].x -= pipe_speed
            pipes = [pipe for pipe in pipes if pipe['top'].x + PIPE_WIDTH > 0]

            # Collision detection
            bird_rect = pygame.Rect(bird_x - BIRD_RADIUS, int(bird_y) - BIRD_RADIUS, BIRD_RADIUS * 2, BIRD_RADIUS * 2)
            for pipe in pipes:
                if bird_rect.colliderect(pipe['top']) or bird_rect.colliderect(pipe['bottom']):
                    game_over = True

            # Score update
            for pipe in pipes:
                if pipe['top'].x + PIPE_WIDTH < bird_x and not pipe.get('scored'):
                    score += 1
                    pipe['scored'] = True

            # Auto-progress: advance after SCORE_TO_ADVANCE pipes in this level
            if score >= SCORE_TO_ADVANCE and current_level < MAX_LEVEL:
                advance_level()

        draw()

    pygame.quit()


if __name__ == "__main__":
    main()
