from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import math
import random
from typing import List, Tuple, Optional
from enum import Enum

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

class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
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

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode(
            (GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Asteroids")
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.player = Player(Vector2D(
            GameConfig.WINDOW_WIDTH/2, 
            GameConfig.WINDOW_HEIGHT/2
        ))
        self.projectiles = []
        self.asteroids = self.create_initial_asteroids()
        self.score = 0
        self.game_state = "playing"

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

    def run(self):
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.fire_projectile()

            # Handle continuous key presses
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.rotate(-GameConfig.PLAYER_ROTATION_SPEED)
            if keys[pygame.K_RIGHT]:
                self.player.rotate(GameConfig.PLAYER_ROTATION_SPEED)
            if keys[pygame.K_UP]:
                self.player.thrust()

            # Update game state
            self.update()
            
            # Draw everything
            self.draw()
            
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
        
        # Draw asteroids
        for asteroid in self.asteroids:
            pygame.draw.circle(
                self.screen,
                GameConfig.WHITE,
                (int(asteroid["position"].x), int(asteroid["position"].y)),
                GameConfig.ASTEROID_SIZES[asteroid["size"]],
                1
            )
        
        # Draw HUD
        score_text = f"Score: {self.score}"
        lives_text = f"Lives: {self.player.lives}"
        font = pygame.font.Font(None, 36)
        
        score_surface = font.render(score_text, True, GameConfig.WHITE)
        lives_surface = font.render(lives_text, True, GameConfig.WHITE)
        
        self.screen.blit(score_surface, (10, 10))
        self.screen.blit(lives_surface, (GameConfig.WINDOW_WIDTH - 100, 10))
        
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
