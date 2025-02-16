from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, sys, random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Game settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_BULLET_SPEED = 5
ENEMY_MOVE_SPEED = 1
ENEMY_DROP_DISTANCE = 20

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = PLAYER_SPEED
        self.lives = 3
        self.shield = False
        self.shield_time = 0
        self.rapid_fire = False
        self.rapid_fire_time = 0
        self.last_shot = 0
        self.shot_delay = 250  # Milliseconds between shots

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        
        # Keep player on screen
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.type = enemy_type
        size = (40, 40)
        self.image = pygame.Surface(size)
        if enemy_type == "basic":
            self.image.fill(RED)
            self.health = 1
            self.points = 10
        elif enemy_type == "medium":
            self.image.fill(BLUE)
            self.health = 2
            self.points = 20
        elif enemy_type == "elite":
            self.image.fill(WHITE)
            self.health = 3
            self.points = 30
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += ENEMY_MOVE_SPEED * self.direction

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color=WHITE):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = speed

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((60, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 4

    def damage(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
        else:
            # Change color based on damage
            self.image.fill((GREEN[0], int(GREEN[1] * (self.health/4)), GREEN[2]))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.score = 0
        self.high_score = self.load_high_score()
        self.level = 1
        self.game_state = "start"  # start, playing, paused, game_over
        self.auto_mode = False  # Add this line
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.barriers = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.high_score))

    def create_enemies(self):
        enemy_types = ["elite", "medium", "medium", "basic", "basic"]
        for row, enemy_type in enumerate(enemy_types):
            for col in range(10):
                enemy = Enemy(100 + col * 60, 50 + row * 50, enemy_type)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

    def create_barriers(self):
        for i in range(4):
            barrier = Barrier(150 + i * 175, SCREEN_HEIGHT - 150)
            self.barriers.add(barrier)
            self.all_sprites.add(barrier)

    def show_start_screen(self):
        self.screen.fill(BLACK)
        title = self.font.render("SPACE INVADERS", True, WHITE)
        play_text = self.font.render("Press SPACE for Manual / A for Auto", True, WHITE)
        score_text = self.font.render(f"High Score: {self.high_score}", True, WHITE)
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
        self.screen.blit(play_text, (SCREEN_WIDTH//2 - play_text.get_width()//2, 300))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 400))
        
        pygame.display.flip()

    def show_game_over(self):
        self.screen.fill(BLACK)
        text = self.font.render("GAME OVER", True, WHITE)
        score = self.font.render(f"Final Score: {self.score}", True, WHITE)
        restart = self.font.render("R - Manual Mode / A - Auto Mode", True, WHITE)
        
        self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 250))
        self.screen.blit(score, (SCREEN_WIDTH//2 - score.get_width()//2, 300))
        self.screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 350))
        
        pygame.display.flip()

    def new_game(self, auto_mode=False):
        self.all_sprites.empty()
        self.enemies.empty()
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.barriers.empty()
        
        self.player = Player()
        self.all_sprites.add(self.player)
        self.create_enemies()
        self.create_barriers()
        self.score = 0
        self.level = 1
        self.auto_mode = auto_mode
        self.game_state = "playing"

    def auto_play(self):
        """AI logic for auto-play mode"""
        if self.enemies:
            # Find the lowest enemy that's somewhat aligned with the player
            target = None
            lowest_y = 0
            player_x = self.player.rect.centerx

            for enemy in self.enemies:
                # Consider enemies within a reasonable x-range of the player
                if abs(enemy.rect.centerx - player_x) < 50 and enemy.rect.bottom > lowest_y:
                    target = enemy
                    lowest_y = enemy.rect.bottom

            # Move towards the selected target or the nearest enemy if no aligned target
            if not target:
                target = min(self.enemies, key=lambda e: abs(e.rect.centerx - player_x))

            # Move towards target
            if self.player.rect.centerx < target.rect.centerx - 5:
                self.player.rect.x += self.player.speed
            elif self.player.rect.centerx > target.rect.centerx + 5:
                self.player.rect.x -= self.player.speed

            # Shoot if aligned
            if abs(self.player.rect.centerx - target.rect.centerx) < 30:
                now = pygame.time.get_ticks()
                if now - self.player.last_shot > self.player.shot_delay:
                    bullet = Bullet(self.player.rect.centerx, self.player.rect.top, BULLET_SPEED)
                    self.all_sprites.add(bullet)
                    self.player_bullets.add(bullet)
                    self.player.last_shot = now

    def run(self):
        while True:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_high_score()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state == "playing":
                            self.game_state = "paused"
                        elif self.game_state == "paused":
                            self.game_state = "playing"
                    
                    if self.game_state == "start":
                        if event.key == pygame.K_SPACE:
                            self.new_game(auto_mode=False)
                        elif event.key == pygame.K_a:
                            self.new_game(auto_mode=True)
                    
                    if self.game_state == "game_over":
                        if event.key == pygame.K_r:
                            self.new_game(auto_mode=False)
                        elif event.key == pygame.K_a:
                            self.new_game(auto_mode=True)
                    
                    if self.game_state == "playing" and not self.auto_mode:
                        if event.key == pygame.K_SPACE:
                            now = pygame.time.get_ticks()
                            if now - self.player.last_shot > self.player.shot_delay:
                                bullet = Bullet(self.player.rect.centerx, self.player.rect.top, BULLET_SPEED)
                                self.all_sprites.add(bullet)
                                self.player_bullets.add(bullet)
                                self.player.last_shot = now

            if self.game_state == "start":
                self.show_start_screen()
            elif self.game_state == "playing":
                if self.auto_mode:
                    self.auto_play()
                self.update()
                self.draw()
            elif self.game_state == "game_over":
                self.show_game_over()

    def update(self):
        self.all_sprites.update()
        
        # Check for bullet collisions
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, False, True)
        for enemy, bullets in hits.items():
            enemy.health -= len(bullets)
            if enemy.health <= 0:
                self.score += enemy.points
                enemy.kill()
        
        # Enemy movement
        move_down = False
        for enemy in self.enemies:
            if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                move_down = True
                break
        
        if move_down:
            for enemy in self.enemies:
                enemy.rect.y += ENEMY_DROP_DISTANCE
                enemy.direction *= -1
        
        # Random enemy shooting
        if self.enemies and random.random() < 0.02:
            shooter = random.choice(self.enemies.sprites())
            bullet = Bullet(shooter.rect.centerx, shooter.rect.bottom, -ENEMY_BULLET_SPEED, RED)
            self.all_sprites.add(bullet)
            self.enemy_bullets.add(bullet)
        
        # Check for game over conditions
        if pygame.sprite.spritecollide(self.player, self.enemy_bullets, True) or \
           pygame.sprite.spritecollide(self.player, self.enemies, False):
            self.player.lives -= 1
            if self.player.lives <= 0:
                if self.score > self.high_score:
                    self.high_score = self.score
                self.game_state = "game_over"
        
        # Check for level completion
        if not self.enemies:
            self.level += 1
            self.create_enemies()

    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        
        # Draw HUD
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 40))
        self.screen.blit(level_text, (SCREEN_WIDTH - 100, 10))
        
        # Add mode indicator
        mode_text = self.font.render("AUTO" if self.auto_mode else "MANUAL", True, WHITE)
        self.screen.blit(mode_text, (SCREEN_WIDTH - 100, 40))
        
        pygame.display.flip()

def main():
    game = Game()
    game.run()
    pygame.quit()

if __name__ == '__main__':
    main()
