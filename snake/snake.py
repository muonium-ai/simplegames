from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt

import pygame, sys, random, time

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BLOCK_SIZE = 20
FPS = 5  # slower snake speed
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
HEAD_COLOR = (255, 255, 0)  # snake head color

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

def draw_text(text, color, center):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=center)
    screen.blit(surface, rect)

def start_screen():
    while True:
        screen.fill(BLACK)
        draw_text("Snake Game", WHITE, (SCREEN_WIDTH//2, 80))
        # Define two buttons rects
        manual_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 150, 200, 50)
        autosnake_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 230, 200, 50)
        pygame.draw.rect(screen, GREEN, manual_rect)
        pygame.draw.rect(screen, BLUE, autosnake_rect)
        draw_text("Start Game", BLACK, manual_rect.center)
        draw_text("Autosnake", BLACK, autosnake_rect.center)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if manual_rect.collidepoint(event.pos):
                    return "manual"
                if autosnake_rect.collidepoint(event.pos):
                    return "autosnake"
        clock.tick(15)

def game_loop(mode):
    # Initialize snake and food
    snake = [(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)]
    direction = (BLOCK_SIZE, 0)  # start moving right
    food = (random.randrange(BLOCK_SIZE, SCREEN_WIDTH - BLOCK_SIZE, BLOCK_SIZE),
            random.randrange(BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE))
    start_time = time.time()
    
    def ai_direction(head, food, current_direction):
        import math  # For distance calculations
        possible_moves = [(BLOCK_SIZE, 0), (-BLOCK_SIZE, 0), (0, BLOCK_SIZE), (0, -BLOCK_SIZE)]
        # Avoid reversing direction if snake length > 1
        if len(snake) > 1:
            possible_moves = [mv for mv in possible_moves if mv != (-current_direction[0], -current_direction[1])]
        safe_moves = []
        for mv in possible_moves:
            new_head = (head[0] + mv[0], head[1] + mv[1])
            if 0 <= new_head[0] < SCREEN_WIDTH and 0 <= new_head[1] < SCREEN_HEIGHT:
                safe_moves.append(mv)
        if safe_moves:
            best_move = min(safe_moves, key=lambda mv: math.hypot(food[0] - (head[0] + mv[0]), food[1] - (head[1] + mv[1])))
            return best_move
        return current_direction

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if mode == "manual" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, BLOCK_SIZE):
                    direction = (0, -BLOCK_SIZE)
                elif event.key == pygame.K_DOWN and direction != (0, -BLOCK_SIZE):
                    direction = (0, BLOCK_SIZE)
                elif event.key == pygame.K_LEFT and direction != (BLOCK_SIZE, 0):
                    direction = (-BLOCK_SIZE, 0)
                elif event.key == pygame.K_RIGHT and direction != (-BLOCK_SIZE, 0):
                    direction = (BLOCK_SIZE, 0)
        
        if mode == "autosnake":
            # Automatic control: simple AI moves snake toward the food.
            head = snake[0]
            direction = ai_direction(head, food, direction)

        # Move snake
        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        # Collision with boundaries
        if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT or new_head in snake):
            break  # Game over
        
        snake.insert(0, new_head)
        
        # Check for food collision
        if new_head == food:
            food = (random.randrange(BLOCK_SIZE, SCREEN_WIDTH - BLOCK_SIZE, BLOCK_SIZE),
                    random.randrange(BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE))
        else:
            snake.pop()
        
        screen.fill(BLACK)
        # Draw food
        pygame.draw.rect(screen, RED, pygame.Rect(food[0], food[1], BLOCK_SIZE, BLOCK_SIZE))
        # Draw snake: head with HEAD_COLOR and body with GREEN
        for i, block in enumerate(snake):
            color = HEAD_COLOR if i == 0 else GREEN
            pygame.draw.rect(screen, color, pygame.Rect(block[0], block[1], BLOCK_SIZE, BLOCK_SIZE))
        
        # Display scores: elapsed time, snake length, and speed level.
        elapsed = int(time.time() - start_time)
        draw_text(f"Time: {elapsed} sec", WHITE, (80, 20))
        draw_text(f"Length: {len(snake)}", WHITE, (SCREEN_WIDTH - 80, 20))
        draw_text("Speed: Slow", WHITE, (SCREEN_WIDTH//2, 20))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    # Game Over screen
    screen.fill(BLACK)
    draw_text("Game Over", RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
    draw_text(f"Score: {int(time.time()- start_time)} sec, {len(snake)}", WHITE, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
    pygame.display.flip()
    pygame.time.wait(2000)

def main():
    mode = start_screen()
    game_loop(mode)
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
