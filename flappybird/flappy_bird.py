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

def reset_game():
    global bird_y, bird_vel, pipes, score, game_over, current_level
    bird_y = HEIGHT // 2
    bird_vel = 0
    pipes = []
    score = 0
    game_over = False
    current_level = 1
    play_music(LEVEL1_MUSIC)

def draw():
    screen.fill((135, 206, 235))  # sky blue background
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
        # Activate autoplay if "Autoplay" button is clicked
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if WIDTH - 140 <= mx <= WIDTH - 20 and 10 <= my <= 50:
                auto_play = True
        if not game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird_vel = JUMP_STRENGTH
            if event.type == SPAWN_PIPE:
                pipe_height = random.randint(50, HEIGHT - PIPE_GAP - 50)
                top_pipe = pygame.Rect(WIDTH, 0, PIPE_WIDTH, pipe_height)
                bottom_pipe = pygame.Rect(WIDTH, pipe_height + PIPE_GAP, PIPE_WIDTH, HEIGHT - pipe_height - PIPE_GAP)
                pipes.append({'top': top_pipe, 'bottom': bottom_pipe})
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                reset_game()

    if not game_over:
        # Auto-play logic: if enabled, decide to jump based on obstacle analysis
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
                safe_margin = 10
                # If close to the obstacle and bird is below the gap center by a margin, jump.
                if dx < 150 and bird_y > (gap_center + safe_margin):
                    bird_vel = JUMP_STRENGTH
                    
        # Update bird physics
        bird_vel += GRAVITY
        bird_y += bird_vel
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
