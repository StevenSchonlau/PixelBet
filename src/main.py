import pygame
import os
from pygame.locals import *
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, BLUE, BUTTON_COLOR, HOVER_COLOR

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PixelBet")
icon_path = os.path.join('assets\\images', "pixelbet_logo.jpeg")  # Update path if needed
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)
else:
    print("Warning: Icon file not found!")

def main():
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))  # Clear screen
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()