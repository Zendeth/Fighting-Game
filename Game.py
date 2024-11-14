import pygame
import sys

from Animation import *
from Player import *

# Initialize pygame
pygame.init()

screen = pygame.display.set_mode((800, 600))
background = pygame.image.load("Background/Background.png").convert()
background_width, background_height = background.get_size()
scaled_background = pygame.transform.scale(background, (background_width * 2, background_height * 2))

SCREEN_WIDTH, SCREEN_HEIGHT = scaled_background.get_size()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Versus Game")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)  # Color for the hitbox

GROUND = SCREEN_HEIGHT - SCALED_HEIGHT

character_folders = ["Biker", "Cyborg", "Punk"]
character_animations, character_hitboxes = load_character_animations(character_folders)


# Initialize players
player1 = Player(100, GROUND, screen, {"left": pygame.K_q, "right": pygame.K_d, "jump": pygame.K_z, "attack": pygame.K_SPACE, "parry": pygame.K_f}, character_hitboxes, character_animations, "Biker")
player2 = Player(600, GROUND, screen, {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP, "attack": pygame.K_RETURN, "parry": pygame.K_KP0}, character_hitboxes, character_animations, "Cyborg")


# Game loop
clock = pygame.time.Clock()
running = True
while running:
    screen.blit(scaled_background, (0, 0))
    dt = clock.tick(60) / 1000  # Delta time in seconds

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Cooldown
    player1.parry_cool_down -= dt
    player2.parry_cool_down -= dt

    # Game logic
    player1.move(player2, dt)
    player2.move(player1, dt)

    # Check for attacks
    keys = pygame.key.get_pressed()
    if keys[player1.controls["attack"]]:
        player1.attack(player2)
    if keys[player2.controls["attack"]]:
        player2.attack(player1)
    
    player1.update(dt)
    player2.update(dt)

    # Draw players
    player1.draw()
    player2.draw()

    # Check for game over
    if player1.health <= 0:
        print("Player 2 wins!")
        running = False
    elif player2.health <= 0:
        print("Player 1 wins!")
        running = False

    # Refresh screen
    pygame.display.flip()
    #clock.tick(60)

pygame.quit()
sys.exit()
