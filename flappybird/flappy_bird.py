from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt

import pygame
import random

pygame.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

clock = pygame.time.Clock()
FPS = 60

pygame.mixer.init()
# Preload two background music tracks; place level1.mp3 and level2.mp3 in this directory
LEVEL1_MUSIC = "level1.mp3"
LEVEL2_MUSIC = "level2.mp3"
current_level = 1  # Track music level

def play_music(music_file):
    try:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Music file {music_file} not found. Continuing without music.")

# Bird parameters (simplified for young users)
BIRD_RADIUS = 20
bird_x = 50
bird_y = HEIGHT // 2
bird_vel = 0
GRAVITY = 0.3           # reduced from 0.5 for slower fall
JUMP_STRENGTH = -8      # reduced from -10 for easier control

# Pipe parameters (easier configuration)
PIPE_WIDTH = 60
PIPE_GAP = 200         # increased gap from 150
pipe_speed = 2         # reduced speed from 3
pipes = []
SPAWN_PIPE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_PIPE, 2000)  # increased delay from 1500ms

score = 0
font = pygame.font.SysFont(None, 36)
game_over = False

# New global flag for auto-play
auto_play = False

# New global flag for game start
started = False

# Cooldown for auto-jump
auto_jump_cooldown = 0  # remove or set to 0 for immediate jump

def reset_game():
    global bird_y, bird_vel, pipes, score, game_over, current_level, started, auto_play
    bird_y = HEIGHT // 2
    bird_vel = 0
    pipes = []
    score = 0
    game_over = False
    started = False  # Reset started state
    auto_play = False  # Reset autoplay state
    current_level = 1
    play_music(LEVEL1_MUSIC)

def draw():
    screen.fill((135, 206, 235))  # sky blue background
    # Draw start buttons if game not started or game is over
    if not started or game_over:  # Modified condition
        # Regular Start button (left side)
        start_button = pygame.Rect(WIDTH//2 - 130, HEIGHT//2 - 20, 120, 40)
        pygame.draw.rect(screen, (50, 205, 50), start_button)
        start_text = font.render("Start", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=start_button.center)
        screen.blit(start_text, start_rect)

        # Autoplay Start button (right side)
        auto_start_button = pygame.Rect(WIDTH//2 + 10, HEIGHT//2 - 20, 120, 40)
        pygame.draw.rect(screen, (50, 205, 50), auto_start_button)
        auto_text = font.render("Auto Start", True, (255, 255, 255))
        auto_rect = auto_text.get_rect(center=auto_start_button.center)
        screen.blit(auto_text, auto_rect)

        # Show score if game over
        if game_over:
            score_text = font.render(f"Final Score: {score}", True, (255, 0, 0))
            screen.blit(score_text, (WIDTH//2 - 70, HEIGHT//2 - 80))
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
        # Draw "Autoplay" button (updated dimensions for longer text)
        autoplay_button = pygame.Rect(WIDTH - 140, 10, 120, 40)
        pygame.draw.rect(screen, (50, 205, 50), autoplay_button)  # green button
        autoplay_text = font.render("Autoplay", True, (255, 255, 255))
        autoplay_rect = autoplay_text.get_rect(center=autoplay_button.center)
        screen.blit(autoplay_text, autoplay_rect)
        if game_over:
            over_text = font.render("Game Over! Press Space to restart", True, (255, 0, 0))
            screen.blit(over_text, (20, HEIGHT // 2))
    pygame.display.flip()

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif (not started or game_over) and event.type == pygame.MOUSEBUTTONDOWN:  # Modified condition
            mx, my = event.pos
            if HEIGHT//2 - 20 <= my <= HEIGHT//2 + 20:
                if WIDTH//2 - 130 <= mx <= WIDTH//2 - 10:  # Regular Start
                    reset_game()
                    started = True
                elif WIDTH//2 + 10 <= mx <= WIDTH//2 + 130:  # Autoplay Start
                    reset_game()
                    started = True
                    auto_play = True
        # Activate autoplay if "Autoplay" button is clicked
        elif started and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if WIDTH - 140 <= mx <= WIDTH - 20 and 10 <= my <= 50:
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
                reset_game()

    if started and not game_over:
        # Improved autoplay logic with gap boundary awareness
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
                
                # Calculate safe zone within the gap
                safe_margin = 30
                safe_top = gap_top + safe_margin
                safe_bottom = gap_bottom - safe_margin
                
                # Jump decisions based on position relative to safe zone
                if dx < 200:  # Look ahead distance
                    if bird_y > safe_bottom or (bird_y > gap_center and bird_vel > 2):
                        # Jump if too low or falling too fast
                        bird_vel = JUMP_STRENGTH
                    elif bird_y < safe_top:
                        # Let gravity pull down if too high
                        bird_vel = max(bird_vel, 1)

        # Update bird physics
        bird_vel += GRAVITY
        bird_y += bird_vel

        # For autoplay, enforce staying within screen bounds
        if auto_play:
            if bird_y - BIRD_RADIUS <= 5:  # Near ceiling
                bird_vel = 2  # Force stronger downward movement
            elif bird_y + BIRD_RADIUS >= HEIGHT - 5:  # Near floor
                bird_vel = JUMP_STRENGTH  # Force upward movement
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

    draw()

pygame.quit()
