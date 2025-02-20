from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import math
import random
from typing import List, Tuple, Optional
from enum import Enum
import time

# Initialize Pygame
pygame.init()

# Constants
class GameConfig:
    FPS = 60
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # Player settings
    PLAYER_ACCELERATION = 0.5
    PLAYER_MAX_SPEED = 10
    PLAYER_ROTATION_SPEED = 5
    PLAYER_FRICTION = 0.98
    PLAYER_INVULNERABILITY_TIME = 3.0
    PLAYER_INITIAL_LIVES = 3
    
    # Projectile settings
    PROJECTILE_SPEED = 15
    PROJECTILE_LIFETIME = 2.0
    MAX_PROJECTILES = 4
    
    # Asteroid settings
    ASTEROID_SPEEDS = {"large": 1.5, "medium": 2, "small": 2.5}
    ASTEROID_SIZES = {"large": 40, "medium": 20, "small": 10}
    ASTEROID_SCORES = {"large": 20, "medium": 50, "small": 100}
    INITIAL_ASTEROIDS = 4

    # Menu settings
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 50
    
    # Asteroid colors by size
    ASTEROID_COLORS = {
        "large": (255, 100, 100),    # Red
        "medium": (100, 255, 100),   # Green
        "small": (100, 100, 255)     # Blue
    }
    
    # Autoplay settings
    AUTOPLAY_ROTATION_SPEED = 3
    AUTOPLAY_SHOOT_DELAY = 0.5
    AUTOPLAY_SAFETY_DISTANCE = 100

    # Add victory text settings
    VICTORY_TEXT_SIZE = 64
    STATS_TEXT_SIZE = 36
    
    # Add stats tracking
    ASTEROID_COUNTS = {
        "large": 0,
        "medium": 0,
        "small": 0
    }

    # Add score display position
    SCORE_BOX_TOP = 150
    BUTTON_TOP = 400  # Move buttons lower

class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y  # Fix: This line was incomplete
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def rotate(self, angle: float):
        """Rotate vector by angle (in degrees)"""
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        x = self.x * cos_a - self.y * sin_a
        y = self.x * sin_a + self.y * cos_a
        return Vector2D(x, y)
    
    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self):
        length = self.length()
        if length != 0:
            self.x /= length
            self.y /= length

class Player:
    def __init__(self, position: Vector2D):
        self.position = position
        self.velocity = Vector2D(0, 0)
        self.acceleration = Vector2D(0, 0)
        self.angle = 0
        self.lives = GameConfig.PLAYER_INITIAL_LIVES
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.points = [Vector2D(0, -20), Vector2D(-10, 20), Vector2D(10, 20)]
    
    def update(self):
        # Update physics
        self.velocity = self.velocity + self.acceleration
        speed = self.velocity.length()
        if speed > GameConfig.PLAYER_MAX_SPEED:
            self.velocity = self.velocity * (GameConfig.PLAYER_MAX_SPEED / speed)
            
        self.position = self.position + self.velocity
        self.acceleration = self.acceleration * 0
        
        # Apply friction
        self.velocity = self.velocity * GameConfig.PLAYER_FRICTION
        
        # Wrap around screen
        self.position.x %= GameConfig.WINDOW_WIDTH
        self.position.y %= GameConfig.WINDOW_HEIGHT
        
        # Update invulnerability
        if self.invulnerable:
            self.invulnerable_timer -= 1/GameConfig.FPS
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

    def thrust(self):
        thrust_vector = Vector2D(0, -GameConfig.PLAYER_ACCELERATION).rotate(self.angle)
        self.acceleration = self.acceleration + thrust_vector

    def rotate(self, angle_change: float):
        self.angle += angle_change

    def draw(self, screen: pygame.Surface):
        if self.invulnerable and int(self.invulnerable_timer * 10) % 2:
            return  # Flash when invulnerable
        
        # Transform points
        transformed = []
        for point in self.points:
            rotated = point.rotate(self.angle)
            position = Vector2D(
                self.position.x + rotated.x,
                self.position.y + rotated.y
            )
            transformed.append((position.x, position.y))
        
        pygame.draw.polygon(screen, GameConfig.WHITE, transformed, 1)

class Projectile:
    def __init__(self, position: Vector2D, velocity: Vector2D):
        self.position = position
        self.velocity = velocity
        self.lifetime = GameConfig.PROJECTILE_LIFETIME
    
    def update(self) -> bool:
        self.position = self.position + self.velocity
        self.position.x %= GameConfig.WINDOW_WIDTH
        self.position.y %= GameConfig.WINDOW_HEIGHT
        
        self.lifetime -= 1/GameConfig.FPS
        return self.lifetime > 0
    
    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, GameConfig.WHITE, 
                         (int(self.position.x), int(self.position.y)), 2)

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        center_x = GameConfig.WINDOW_WIDTH // 2
        
        # Create buttons with new vertical position
        self.buttons = {
            'start': pygame.Rect(
                center_x - GameConfig.BUTTON_WIDTH - 20,
                GameConfig.BUTTON_TOP,  # Use new button position
                GameConfig.BUTTON_WIDTH,
                GameConfig.BUTTON_HEIGHT
            ),
            'autoplay': pygame.Rect(
                center_x + 20,
                GameConfig.BUTTON_TOP,  # Use new button position
                GameConfig.BUTTON_WIDTH,
                GameConfig.BUTTON_HEIGHT
            )
        }

        # Add victory text font
        self.victory_font = pygame.font.Font(None, GameConfig.VICTORY_TEXT_SIZE)
        self.stats_font = pygame.font.Font(None, GameConfig.STATS_TEXT_SIZE)

    def draw(self):
        self.screen.fill(GameConfig.BLACK)
        
        # Draw title
        title = self.font.render("ASTEROIDS", True, GameConfig.WHITE)
        title_rect = title.get_rect(center=(GameConfig.WINDOW_WIDTH//2, GameConfig.WINDOW_HEIGHT//3))
        self.screen.blit(title, title_rect)
        
        # Draw buttons
        for text, rect in self.buttons.items():
            pygame.draw.rect(self.screen, GameConfig.WHITE, rect, 2)
            button_text = self.font.render(text.title(), True, GameConfig.WHITE)
            text_rect = button_text.get_rect(center=rect.center)
            self.screen.blit(button_text, text_rect)
        
        pygame.display.flip()

    def handle_click(self, pos):
        for button_name, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return button_name
        return None

    def draw_victory(self, score: int, stats: dict, time_elapsed: int, shots_fired: int):
        """Draw victory screen with stats"""
        self.screen.fill(GameConfig.BLACK)
        
        # Draw victory text
        victory_text = self.victory_font.render("VICTORY!", True, GameConfig.WHITE)
        victory_rect = victory_text.get_rect(center=(GameConfig.WINDOW_WIDTH//2, 100))
        self.screen.blit(victory_text, victory_rect)
        
        # Draw stats with time and shots
        y_pos = GameConfig.SCORE_BOX_TOP
        stats_texts = [
            f"Final Score: {score}",
            f"Time: {time_elapsed} seconds",
            f"Shots Fired: {shots_fired}",
            f"Large Asteroids: {stats['large']}",
            f"Medium Asteroids: {stats['medium']}",
            f"Small Asteroids: {stats['small']}",
            f"Total Asteroids: {sum(stats.values())}"
        ]
        
        for text in stats_texts:
            stat_surface = self.stats_font.render(text, True, GameConfig.WHITE)
            stat_rect = stat_surface.get_rect(center=(GameConfig.WINDOW_WIDTH//2, y_pos))
            self.screen.blit(stat_surface, stat_rect)
            y_pos += 40
        
        # Draw buttons
        for text, rect in self.buttons.items():
            pygame.draw.rect(self.screen, GameConfig.WHITE, rect, 2)
            button_text = self.font.render(text.title(), True, GameConfig.WHITE)
            text_rect = button_text.get_rect(center=rect.center)
            self.screen.blit(button_text, text_rect)
        
        pygame.display.flip()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode(
            (GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Asteroids")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, GameConfig.STATS_TEXT_SIZE)  # Add font initialization
        self.reset_game()
        self.menu = Menu(self.screen)
        self.game_state = "menu"
        self.autoplay = False
        self.last_shot_time = 0
        self.asteroid_stats = GameConfig.ASTEROID_COUNTS.copy()
        self.shots_fired = 0
        self.start_time = time.time()
        self.final_time = 0  # Add final time variable

    def reset_game(self):
        self.player = Player(Vector2D(
            GameConfig.WINDOW_WIDTH/2, 
            GameConfig.WINDOW_HEIGHT/2
        ))
        self.projectiles = []
        self.asteroids = self.create_initial_asteroids()
        self.score = 0
        self.game_state = "playing"
        self.autoplay = False
        self.last_shot_time = 0
        self.asteroid_stats = GameConfig.ASTEROID_COUNTS.copy()
        self.shots_fired = 0
        self.start_time = time.time()
        self.final_time = 0

    def create_initial_asteroids(self) -> List:
        asteroids = []
        for _ in range(GameConfig.INITIAL_ASTEROIDS):
            # Random position at screen edge
            if random.random() < 0.5:
                x = random.choice([0, GameConfig.WINDOW_WIDTH])
                y = random.random() * GameConfig.WINDOW_HEIGHT
            else:
                x = random.random() * GameConfig.WINDOW_WIDTH
                y = random.choice([0, GameConfig.WINDOW_HEIGHT])
            
            asteroids.append({
                "position": Vector2D(x, y),
                "velocity": Vector2D(
                    random.uniform(-1, 1), 
                    random.uniform(-1, 1)
                ),
                "size": "large"
            })
        return asteroids

    def auto_control(self):
        """AI control for autoplay mode"""
        if not self.asteroids:
            return
            
        # Find nearest asteroid
        nearest = min(self.asteroids, 
                     key=lambda a: math.hypot(a["position"].x - self.player.position.x,
                                            a["position"].y - self.player.position.y))
        
        # Calculate angle to asteroid
        dx = nearest["position"].x - self.player.position.x
        dy = nearest["position"].y - self.player.position.y
        target_angle = math.degrees(math.atan2(-dy, dx)) - 90
        
        # Adjust angle
        current_angle = self.player.angle % 360
        angle_diff = (target_angle - current_angle) % 360
        if angle_diff > 180:
            angle_diff -= 360
            
        # Rotate towards asteroid
        if abs(angle_diff) > 5:
            if angle_diff > 0:
                self.player.rotate(GameConfig.AUTOPLAY_ROTATION_SPEED)
            else:
                self.player.rotate(-GameConfig.AUTOPLAY_ROTATION_SPEED)
        
        # Shoot if aiming at asteroid
        current_time = time.time()
        if (abs(angle_diff) < 10 and 
            current_time - self.last_shot_time > GameConfig.AUTOPLAY_SHOOT_DELAY):
            self.fire_projectile()
            self.last_shot_time = current_time

    def run(self):
        running = True
        while running:
            if self.game_state == "menu":
                self.menu.draw()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        action = self.menu.handle_click(event.pos)
                        if action == "start":
                            self.reset_game()
                            self.game_state = "playing"
                        elif action == "autoplay":
                            self.reset_game()
                            self.autoplay = True
                            self.game_state = "playing"

            elif self.game_state == "playing":
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.fire_projectile()

                if not self.autoplay:
                    # Manual control
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT]:
                        self.player.rotate(-GameConfig.PLAYER_ROTATION_SPEED)
                    if keys[pygame.K_RIGHT]:
                        self.player.rotate(GameConfig.PLAYER_ROTATION_SPEED)
                    if keys[pygame.K_UP]:
                        self.player.thrust()
                else:
                    # Auto control
                    self.auto_control()

                # Update game state
                self.update()
                
                # Check victory condition
                if not self.asteroids:
                    self.final_time = int(time.time() - self.start_time)  # Store final time
                    self.game_state = "victory"
                
                self.draw()

            elif self.game_state == "victory":
                self.menu.draw_victory(self.score, self.asteroid_stats, 
                                     self.final_time, self.shots_fired)  # Use final_time
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        action = self.menu.handle_click(event.pos)
                        if action == "start":
                            self.reset_game()
                            self.game_state = "playing"
                        elif action == "autoplay":
                            self.reset_game()
                            self.autoplay = True
                            self.game_state = "playing"

            # Maintain frame rate
            self.clock.tick(GameConfig.FPS)

        pygame.quit()

    def update(self):
        # Update player
        self.player.update()
        
        # Update projectiles
        self.projectiles = [p for p in self.projectiles if p.update()]
        
        # Update asteroids
        for asteroid in self.asteroids:
            asteroid["position"] = asteroid["position"] + asteroid["velocity"]
            asteroid["position"].x %= GameConfig.WINDOW_WIDTH
            asteroid["position"].y %= GameConfig.WINDOW_HEIGHT
        
        # Check collisions
        self.check_collisions()

    def fire_projectile(self):
        if len(self.projectiles) < GameConfig.MAX_PROJECTILES:
            direction = Vector2D(0, -1).rotate(self.player.angle)
            direction.normalize()
            velocity = direction * GameConfig.PROJECTILE_SPEED
            self.projectiles.append(Projectile(
                Vector2D(self.player.position.x, self.player.position.y),
                velocity
            ))
            self.shots_fired += 1

    def check_collisions(self):
        # Check projectile-asteroid collisions
        for projectile in self.projectiles[:]:
            for asteroid in self.asteroids[:]:
                dist = math.sqrt(
                    (projectile.position.x - asteroid["position"].x) ** 2 +
                    (projectile.position.y - asteroid["position"].y) ** 2
                )
                if dist < GameConfig.ASTEROID_SIZES[asteroid["size"]]:
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                    self.split_asteroid(asteroid)
                    break

    def split_asteroid(self, asteroid):
        # Track destroyed asteroid
        self.asteroid_stats[asteroid["size"]] += 1
        
        self.asteroids.remove(asteroid)
        self.score += GameConfig.ASTEROID_SCORES[asteroid["size"]]
        
        if asteroid["size"] == "large":
            new_size = "medium"
        elif asteroid["size"] == "medium":
            new_size = "small"
        else:
            return
        
        for _ in range(2):
            velocity = Vector2D(
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            )
            velocity = velocity * GameConfig.ASTEROID_SPEEDS[new_size]
            
            self.asteroids.append({
                "position": Vector2D(
                    asteroid["position"].x,
                    asteroid["position"].y
                ),
                "velocity": velocity,
                "size": new_size
            })

    def draw(self):
        self.screen.fill(GameConfig.BLACK)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        # Draw asteroids with colors
        for asteroid in self.asteroids:
            color = GameConfig.ASTEROID_COLORS[asteroid["size"]]
            pygame.draw.circle(
                self.screen,
                color,
                (int(asteroid["position"].x), int(asteroid["position"].y)),
                GameConfig.ASTEROID_SIZES[asteroid["size"]],
                1
            )
        
        # Draw HUD with additional stats
        y_pos = 10
        # Use final_time if game is won, otherwise use current time
        elapsed_time = self.final_time if self.game_state == "victory" else int(time.time() - self.start_time)
        hud_texts = [
            f"Score: {self.score}",
            f"Lives: {self.player.lives}",
            f"Time: {elapsed_time}s",
            f"Shots: {self.shots_fired}",
            f"Large: {self.asteroid_stats['large']}",
            f"Medium: {self.asteroid_stats['medium']}",
            f"Small: {self.asteroid_stats['small']}"
        ]
        
        for text in hud_texts:
            surface = self.font.render(text, True, GameConfig.WHITE)
            self.screen.blit(surface, (10, y_pos))
            y_pos += 25
        
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
