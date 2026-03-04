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

music_enabled = True
try:
    pygame.mixer.init()
except pygame.error:
    music_enabled = False

# Preload two background music tracks; place level1.mp3 and level2.mp3 in this directory
LEVEL1_MUSIC = "level1.mp3"
LEVEL2_MUSIC = "level2.mp3"
current_level = 1  # Track music level

def play_music(music_file):
    if not music_enabled:
        return
    try:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

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

START_BUTTON_RECT = pygame.Rect(WIDTH//2 - 130, HEIGHT//2 - 20, 120, 40)
AUTO_START_BUTTON_RECT = pygame.Rect(WIDTH//2 + 10, HEIGHT//2 - 20, 120, 40)
AUTOPLAY_BUTTON_RECT = pygame.Rect(WIDTH - 140, 10, 120, 40)

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
        pygame.draw.rect(screen, (50, 205, 50), AUTOPLAY_BUTTON_RECT)  # green button
        autoplay_text = font.render("Autoplay", True, (255, 255, 255))
        autoplay_rect = autoplay_text.get_rect(center=AUTOPLAY_BUTTON_RECT.center)
        screen.blit(autoplay_text, autoplay_rect)
    pygame.display.flip()

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif (not started or game_over) and event.type == pygame.MOUSEBUTTONDOWN:  # Modified condition
            mx, my = event.pos
            if START_BUTTON_RECT.top <= my <= START_BUTTON_RECT.bottom:
                if START_BUTTON_RECT.left <= mx <= START_BUTTON_RECT.right:  # Regular Start
                    reset_game()
                    started = True
                elif AUTO_START_BUTTON_RECT.left <= mx <= AUTO_START_BUTTON_RECT.right:  # Autoplay Start
                    reset_game()
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
                reset_game()

    if started and not game_over:
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

    draw()

pygame.quit()
