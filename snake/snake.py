from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt

import pygame, sys, random, time
from collections import deque  # Add this import

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
    direction = (BLOCK_SIZE, 0)
    food = (random.randrange(BLOCK_SIZE, SCREEN_WIDTH - BLOCK_SIZE, BLOCK_SIZE),
            random.randrange(BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE))
    start_time = time.time()
    current_fps = FPS
    
    # Initialize position history (but don't use it for collision detection)
    position_history = deque(maxlen=100)
    position_history.append(snake[0])
    
    def ai_direction(head, food, current_direction):
        import math
        possible_moves = [(BLOCK_SIZE, 0), (-BLOCK_SIZE, 0), (0, BLOCK_SIZE), (0, -BLOCK_SIZE)]
        if len(snake) > 1:
            possible_moves = [mv for mv in possible_moves if mv != (-current_direction[0], -current_direction[1])]

        def is_safe_move(move, look_ahead=1):
            next_pos = (head[0] + move[0], head[1] + move[1])
            
            # Check wall collisions
            if not (0 <= next_pos[0] < SCREEN_WIDTH and 0 <= next_pos[1] < SCREEN_HEIGHT):
                return False
            
            # Check only against actual snake body (excluding tail if moving)
            future_snake = snake[:-1] if len(snake) > 1 else []
            if next_pos in future_snake:
                return False
            
            if look_ahead > 1:
                future_moves = [(BLOCK_SIZE, 0), (-BLOCK_SIZE, 0), (0, BLOCK_SIZE), (0, -BLOCK_SIZE)]
                future_moves = [mv for mv in future_moves if mv != (-move[0], -move[1])]
                
                has_safe_future = False
                for future_move in future_moves:
                    future_pos = (next_pos[0] + future_move[0], next_pos[1] + future_move[1])
                    if (0 <= future_pos[0] < SCREEN_WIDTH and 
                        0 <= future_pos[1] < SCREEN_HEIGHT and 
                        future_pos not in future_snake):
                        has_safe_future = True
                        break
                if not has_safe_future:
                    return False
            
            return True

        # Filter safe moves
        safe_moves = [mv for mv in possible_moves if is_safe_move(mv, look_ahead=2)]
        
        if safe_moves:
            # Among safe moves, prefer those that get us closer to food
            best_move = min(safe_moves, 
                          key=lambda mv: math.hypot(food[0] - (head[0] + mv[0]), 
                                                  food[1] - (head[1] + mv[1])))
            return best_move
        
        # If no safe moves leading to food, try any safe move
        safe_moves = [mv for mv in possible_moves if is_safe_move(mv, look_ahead=1)]
        if safe_moves:
            return random.choice(safe_moves)
        
        # If still no safe moves, continue in current direction (will likely end game)
        return current_direction

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            # Handle keyboard for manual mode
            if mode == "manual" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, BLOCK_SIZE):
                    direction = (0, -BLOCK_SIZE)
                elif event.key == pygame.K_DOWN and direction != (0, -BLOCK_SIZE):
                    direction = (0, BLOCK_SIZE)
                elif event.key == pygame.K_LEFT and direction != (BLOCK_SIZE, 0):
                    direction = (-BLOCK_SIZE, 0)
                elif event.key == pygame.K_RIGHT and direction != (-BLOCK_SIZE, 0):
                    direction = (BLOCK_SIZE, 0)
            # Handle arrow button clicks for snake speed adjustment
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                left_arrow = pygame.Rect(SCREEN_WIDTH//2 - 120, 10, 30, 30)
                right_arrow = pygame.Rect(SCREEN_WIDTH//2 + 70, 10, 30, 30)
                if left_arrow.collidepoint(mx, my):
                    current_fps = max(1, current_fps - 1)
                elif right_arrow.collidepoint(mx, my):
                    current_fps = min(20, current_fps + 1)
        
        if mode == "autosnake":
            head = snake[0]
            direction = ai_direction(head, food, direction)

        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        position_history.append(new_head)
        
        # Simplified collision detection using actual snake body
        if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT or
            (len(snake) > 2 and new_head in snake[1:])):  # Only check body collision if snake length > 2
            break
        
        snake.insert(0, new_head)
        
        if new_head == food:
            while True:
                candidate = (random.randrange(BLOCK_SIZE, SCREEN_WIDTH - BLOCK_SIZE, BLOCK_SIZE),
                             random.randrange(BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE))
                if candidate not in snake:  # Only check against actual snake body
                    food = candidate
                    break
        else:
            snake.pop()
        
        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, pygame.Rect(food[0], food[1], BLOCK_SIZE, BLOCK_SIZE))
        for i, block in enumerate(snake):
            color = HEAD_COLOR if i == 0 else GREEN
            pygame.draw.rect(screen, color, pygame.Rect(block[0], block[1], BLOCK_SIZE, BLOCK_SIZE))
        
        elapsed = int(time.time() - start_time)
        draw_text(f"Time: {elapsed} sec", WHITE, (80, 20))
        draw_text(f"Length: {len(snake)}", WHITE, (SCREEN_WIDTH - 80, 20))
        # Draw speed text
        draw_text(f"Speed: {current_fps} FPS", WHITE, (SCREEN_WIDTH//2, 20))
        # Draw left arrow button
        left_btn = pygame.Rect(SCREEN_WIDTH//2 - 120, 10, 30, 30)
        pygame.draw.rect(screen, BLUE, left_btn)
        draw_text("<", BLACK, left_btn.center)
        # Draw right arrow button
        right_btn = pygame.Rect(SCREEN_WIDTH//2 + 70, 10, 30, 30)
        pygame.draw.rect(screen, BLUE, right_btn)
        draw_text(">", BLACK, right_btn.center)
        
        pygame.display.flip()
        clock.tick(current_fps)
    
    # Game Over screen
    screen.fill(BLACK)
    final_score = f"Score: {int(time.time()- start_time)} sec, {len(snake)}"
    draw_text("Game Over", RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
    draw_text(final_score, WHITE, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
    pygame.display.flip()
    pygame.time.wait(2000)
    return final_score  # Return the score

def main():
    while True:
        try:
            mode = start_screen()
            score = game_loop(mode)
        except SystemExit:
            break
        except:
            break
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
