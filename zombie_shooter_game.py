import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Shooter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (100, 100, 100)
DARK_GREEN = (0, 100, 0)

# Game variables
clock = pygame.time.Clock()
FPS = 60

# Load fonts
font_small = pygame.font.SysFont('Arial', 20)
font_medium = pygame.font.SysFont('Arial', 30)
font_large = pygame.font.SysFont('Arial', 50)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
LEVEL_COMPLETE = 3

# Player class
class Player:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
        self.speed = 5
        self.health = 100
        self.bullets = []
        self.gun_type = 0  # 0: pistol, 1: shotgun, 2: machine gun
        self.gun_names = ["Pistol", "Shotgun", "Machine Gun"]
        self.score = 0
        self.lives = 3
    
    def update(self, keys):
        # Movement
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > HEIGHT // 2:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.y += self.speed
        
        self.rect.center = (self.x, self.y)
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.bullets.remove(bullet)
    
    def shoot(self):
        if self.gun_type == 0:  # Pistol - single bullet
            self.bullets.append(Bullet(self.x, self.y - self.height//2, 0, -10, 10))
        elif self.gun_type == 1:  # Shotgun - spread of bullets
            for angle in range(-2, 3):
                self.bullets.append(Bullet(self.x, self.y - self.height//2, angle, -10, 8))
        elif self.gun_type == 2:  # Machine gun - rapid fire (handled in game loop)
            self.bullets.append(Bullet(self.x, self.y - self.height//2, 0, -12, 5))
    
    def change_gun(self):
        self.gun_type = (self.gun_type + 1) % 3
    
    def draw(self):
        # Draw player (aircraft)
        pygame.draw.polygon(screen, BLUE, [
            (self.x, self.y - self.height//2),
            (self.x + self.width//2, self.y + self.height//2),
            (self.x - self.width//2, self.y + self.height//2)
        ])
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw()
        
        # Draw health bar
        health_bar_length = 50
        health_ratio = self.health / 100
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 20, health_bar_length, 5))
        pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 20, health_bar_length * health_ratio, 5))

# Bullet class
class Bullet:
    def __init__(self, x, y, dx, dy, damage):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = 5
        self.damage = damage
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius*2, self.radius*2)
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (self.x, self.y)
    
    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)

# Zombie class
class Zombie:
    def __init__(self, level):
        self.width = 40
        self.height = 60
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(-300, -50)
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
        
        # Zombie gets faster and stronger with each level
        self.speed = random.uniform(1, 2) * (1 + level * 0.5)
        self.health = 30 * (1 + level * 0.5)
        self.damage = 5 * (1 + level * 0.3)
        self.score_value = 10 * (level + 1)
        
        # Different zombie types
        self.zombie_type = random.randint(0, 2)
        if self.zombie_type == 0:  # Regular zombie
            self.color = GREEN
        elif self.zombie_type == 1:  # Fast zombie
            self.color = YELLOW
            self.speed *= 1.5
            self.health *= 0.7
        else:  # Tank zombie
            self.color = RED
            self.speed *= 0.7
            self.health *= 2
            self.width *= 1.3
            self.height *= 1.3
            self.rect.width = self.width
            self.rect.height = self.height
    
    def update(self):
        self.y += self.speed
        self.rect.center = (self.x, self.y)
    
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw eyes
        eye_radius = 5
        pygame.draw.circle(screen, RED, (int(self.x - self.width//4), int(self.y - self.height//4)), eye_radius)
        pygame.draw.circle(screen, RED, (int(self.x + self.width//4), int(self.y - self.height//4)), eye_radius)
        
        # Draw health bar
        health_bar_length = 40
        max_health = 30 * (1 + self.zombie_type * 0.5)
        health_ratio = self.health / max_health
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 10, health_bar_length, 5))
        pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 10, health_bar_length * health_ratio, 5))

# Powerup class
class Powerup:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(-300, -50)
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
        self.speed = 2
        self.type = random.randint(0, 2)  # 0: health, 1: gun upgrade, 2: extra life
        
        if self.type == 0:
            self.color = GREEN  # Health
        elif self.type == 1:
            self.color = YELLOW  # Gun upgrade
        else:
            self.color = BLUE  # Extra life
    
    def update(self):
        self.y += self.speed
        self.rect.center = (self.x, self.y)
    
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        
        if self.type == 0:
            # Draw health symbol
            pygame.draw.rect(screen, WHITE, (self.x - 10, self.y - 2, 20, 4))
            pygame.draw.rect(screen, WHITE, (self.x - 2, self.y - 10, 4, 20))
        elif self.type == 1:
            # Draw gun symbol
            pygame.draw.rect(screen, WHITE, (self.x - 10, self.y, 20, 4))
            pygame.draw.rect(screen, WHITE, (self.x + 5, self.y - 5, 4, 10))
        else:
            # Draw life symbol
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 10, 2)

# Cloud class for background
class Cloud:
    def __init__(self):
        self.width = random.randint(50, 150)
        self.height = random.randint(30, 60)
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT//2)
        self.speed = random.uniform(0.5, 1.5)
    
    def update(self):
        self.x -= self.speed
        if self.x + self.width < 0:
            self.x = WIDTH
            self.y = random.randint(0, HEIGHT//2)
    
    def draw(self):
        pygame.draw.ellipse(screen, WHITE, (self.x, self.y, self.width, self.height))

# Game class
class Game:
    def __init__(self):
        self.state = MENU
        self.level = 1
        self.max_level = 3
        self.player = Player()
        self.zombies = []
        self.powerups = []
        self.clouds = [Cloud() for _ in range(10)]
        self.zombie_spawn_timer = 0
        self.zombie_spawn_delay = 60  # frames between zombie spawns
        self.powerup_spawn_timer = 0
        self.powerup_spawn_delay = 300  # frames between powerup spawns
        self.machine_gun_timer = 0
        self.level_zombies_required = [30, 50, 100]  # Zombies to kill per level
        self.zombies_killed = 0
        self.level_background = [BLUE, PURPLE, DARK_GREEN]  # Different background per level
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                if self.state == MENU and event.key == pygame.K_SPACE:
                    self.state = PLAYING
                
                if self.state == PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.player.shoot()
                    if event.key == pygame.K_g:
                        self.player.change_gun()
                
                if self.state == GAME_OVER and event.key == pygame.K_SPACE:
                    self.__init__()  # Reset game
                
                if self.state == LEVEL_COMPLETE and event.key == pygame.K_SPACE:
                    if self.level < self.max_level:
                        self.level += 1
                        self.zombies = []
                        self.powerups = []
                        self.zombies_killed = 0
                        self.state = PLAYING
                    else:
                        self.__init__()  # Reset game after completing all levels
    
    def update(self):
        # Update clouds in all states
        for cloud in self.clouds:
            cloud.update()
        
        if self.state == PLAYING:
            keys = pygame.key.get_pressed()
            self.player.update(keys)
            
            # Machine gun continuous fire
            if self.player.gun_type == 2:
                self.machine_gun_timer += 1
                if self.machine_gun_timer >= 5:  # Fire every 5 frames
                    self.player.shoot()
                    self.machine_gun_timer = 0
            
            # Spawn zombies
            self.zombie_spawn_timer += 1
            if self.zombie_spawn_timer >= self.zombie_spawn_delay:
                self.zombies.append(Zombie(self.level - 1))
                self.zombie_spawn_timer = 0
                # Make zombies spawn faster as level progresses
                self.zombie_spawn_delay = max(10, 60 - self.level * 10)
            
            # Spawn powerups
            self.powerup_spawn_timer += 1
            if self.powerup_spawn_timer >= self.powerup_spawn_delay:
                self.powerups.append(Powerup())
                self.powerup_spawn_timer = 0
            
            # Update zombies
            for zombie in self.zombies[:]:
                zombie.update()
                
                # Check if zombie is off-screen
                if zombie.y > HEIGHT:
                    self.zombies.remove(zombie)
                    self.player.health -= zombie.damage
                
                # Check for bullet hits
                for bullet in self.player.bullets[:]:
                    if bullet.rect.colliderect(zombie.rect):
                        zombie.health -= bullet.damage
                        if bullet in self.player.bullets:
                            self.player.bullets.remove(bullet)
                
                # Check if zombie is defeated
                if zombie.health <= 0:
                    self.zombies.remove(zombie)
                    self.player.score += zombie.score_value
                    self.zombies_killed += 1
            
            # Update powerups
            for powerup in self.powerups[:]:
                powerup.update()
                
                # Check if powerup is off-screen
                if powerup.y > HEIGHT:
                    self.powerups.remove(powerup)
                
                # Check if player collects powerup
                if powerup.rect.colliderect(self.player.rect):
                    if powerup.type == 0:  # Health
                        self.player.health = min(100, self.player.health + 30)
                    elif powerup.type == 1:  # Gun upgrade
                        self.player.change_gun()
                    else:  # Extra life
                        self.player.lives += 1
                    
                    self.powerups.remove(powerup)
            
            # Check if player health is depleted
            if self.player.health <= 0:
                self.player.lives -= 1
                if self.player.lives > 0:
                    self.player.health = 100
                else:
                    self.state = GAME_OVER
            
            # Check if level is complete
            if self.zombies_killed >= self.level_zombies_required[self.level - 1]:
                self.state = LEVEL_COMPLETE
    
    def draw(self):
        # Draw background based on level
        screen.fill(self.level_background[self.level - 1])
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw()
        
        if self.state == MENU:
            # Draw title
            title = font_large.render("ZOMBIE SHOOTER", True, WHITE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
            
            # Draw instructions
            instructions = [
                "Arrow keys to move",
                "SPACE to shoot",
                "G to change weapons",
                "",
                "Survive 3 levels of zombie attacks!",
                "",
                "Press SPACE to start"
            ]
            
            for i, line in enumerate(instructions):
                text = font_medium.render(line, True, WHITE)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + i * 40))
        
        elif self.state == PLAYING:
            # Draw zombies
            for zombie in self.zombies:
                zombie.draw()
            
            # Draw powerups
            for powerup in self.powerups:
                powerup.draw()
            
            # Draw player
            self.player.draw()
            
            # Draw HUD
            level_text = font_medium.render(f"Level: {self.level}", True, WHITE)
            screen.blit(level_text, (20, 20))
            
            score_text = font_medium.render(f"Score: {self.player.score}", True, WHITE)
            screen.blit(score_text, (20, 60))
            
            lives_text = font_medium.render(f"Lives: {self.player.lives}", True, WHITE)
            screen.blit(lives_text, (20, 100))
            
            gun_text = font_medium.render(f"Gun: {self.player.gun_names[self.player.gun_type]}", True, WHITE)
            screen.blit(gun_text, (WIDTH - gun_text.get_width() - 20, 20))
            
            zombies_text = font_medium.render(f"Zombies: {self.zombies_killed}/{self.level_zombies_required[self.level - 1]}", True, WHITE)
            screen.blit(zombies_text, (WIDTH - zombies_text.get_width() - 20, 60))
        
        elif self.state == GAME_OVER:
            # Draw game over screen
            game_over_text = font_large.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//3))
            
            score_text = font_medium.render(f"Final Score: {self.player.score}", True, WHITE)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
            
            restart_text = font_medium.render("Press SPACE to play again", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT*2//3))
        
        elif self.state == LEVEL_COMPLETE:
            if self.level < self.max_level:
                # Draw level complete screen
                level_complete_text = font_large.render(f"LEVEL {self.level} COMPLETE!", True, GREEN)
                screen.blit(level_complete_text, (WIDTH//2 - level_complete_text.get_width()//2, HEIGHT//3))
                
                next_level_text = font_medium.render(f"Get ready for Level {self.level + 1}", True, WHITE)
                screen.blit(next_level_text, (WIDTH//2 - next_level_text.get_width()//2, HEIGHT//2))
                
                continue_text = font_medium.render("Press SPACE to continue", True, WHITE)
                screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT*2//3))
            else:
                # Draw game complete screen
                game_complete_text = font_large.render("CONGRATULATIONS!", True, GREEN)
                screen.blit(game_complete_text, (WIDTH//2 - game_complete_text.get_width()//2, HEIGHT//3))
                
                victory_text = font_medium.render("You have defeated all the zombies!", True, WHITE)
                screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, HEIGHT//2))
                
                score_text = font_medium.render(f"Final Score: {self.player.score}", True, WHITE)
                screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 50))
                
                restart_text = font_medium.render("Press SPACE to play again", True, WHITE)
                screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT*2//3))
        
        pygame.display.flip()
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
