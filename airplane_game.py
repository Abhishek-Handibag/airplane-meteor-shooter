import pygame
import random
import sys
from pygame.locals import *

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Airplane Meteor Shooter')
clock = pygame.time.Clock()

# Create simple graphics for game objects
def create_airplane():
    surf = pygame.Surface((50, 30), pygame.SRCALPHA)
    pygame.draw.polygon(surf, BLUE, [(0, 15), (50, 15), (25, 0)])
    pygame.draw.rect(surf, BLUE, (10, 15, 30, 15))
    pygame.draw.polygon(surf, (100, 100, 255), [(15, 15), (35, 15), (25, 5)])
    return surf

def create_bullet():
    surf = pygame.Surface((6, 15), pygame.SRCALPHA)
    pygame.draw.rect(surf, (255, 255, 0), (0, 0, 6, 15))
    return surf

def create_meteor():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(surf, (150, 75, 0), (20, 20), 20)
    pygame.draw.circle(surf, (100, 50, 0), (15, 15), 5)
    pygame.draw.circle(surf, (100, 50, 0), (25, 10), 7)
    pygame.draw.circle(surf, (100, 50, 0), (10, 25), 6)
    return surf

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.image = create_airplane()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 8
        self.shoot_delay = 250  # milliseconds
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.score = 0

    def update(self):
        # Move the player with keyboard
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Bullet, self).__init__()
        self.image = create_bullet()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10  # Negative because it goes up

    def update(self):
        self.rect.y += self.speed
        # Kill the bullet if it moves off the screen
        if self.rect.bottom < 0:
            self.kill()

# Meteor class
class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super(Meteor, self).__init__()
        self.image = create_meteor()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        # If meteor goes off screen, respawn it
        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.left < -25 or self.rect.right > SCREEN_WIDTH + 20:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-3, 3)

# Game over text
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(pygame.font.get_default_font(), size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# Draw lives and score
def draw_lives_and_score(surf, x, y, lives, score):
    draw_text(surf, f"Lives: {lives}  Score: {score}", 22, x, y)

# Main game function
def game():
    global all_sprites, meteors, bullets, player
    
    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    meteors = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    
    # Create player
    player = Player()
    all_sprites.add(player)
    
    # Create meteors
    for i in range(8):
        m = Meteor()
        all_sprites.add(m)
        meteors.add(m)
    
    # Game loop
    running = True
    game_over = False
    
    while running:
        # Keep loop running at the right speed
        clock.tick(FPS)
        
        # Process input (events)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    player.shoot()
                if event.key == K_ESCAPE:
                    running = False
                    pygame.quit()
                    sys.exit()
                if game_over and event.key == K_r:
                    game()  # Restart game
        
        if not game_over:
            # Update
            all_sprites.update()
            
            # Check if bullets hit meteors
            hits = pygame.sprite.groupcollide(meteors, bullets, True, True)
            for hit in hits:
                player.score += 10
                m = Meteor()
                all_sprites.add(m)
                meteors.add(m)
            
            # Check if meteors hit the player
            hits = pygame.sprite.spritecollide(player, meteors, True)
            for hit in hits:
                player.lives -= 1
                m = Meteor()
                all_sprites.add(m)
                meteors.add(m)
                if player.lives <= 0:
                    game_over = True
        
        # Draw / render
        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_lives_and_score(screen, SCREEN_WIDTH // 2, 10, player.lives, player.score)
        
        if game_over:
            draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
            draw_text(screen, f"Final Score: {player.score}", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text(screen, "Press R to restart or ESC to quit", 22, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
        
        # Flip the display
        pygame.display.flip()

# Start the game
if __name__ == "__main__":
    game()
    pygame.quit()
