import pygame
import os
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from pygame.locals import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
print(pygame.display.Info())
pygame.display.set_caption("PixelBet")
print("FILE", __file__)
icon_path = os.path.join('assets\\images', "pixelbet_logo.jpeg")  # Update path if needed
print(icon_path)
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