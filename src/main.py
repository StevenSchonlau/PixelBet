import pygame
import pygame_gui
import os
from pygame.locals import *
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, THEME_PATH
from home import draw_home_screen

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PixelBet")
icon_path = os.path.join('assets\\images', "pixelbet_logo.jpeg")  # Update path if needed
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)
else:
    print("Warning: Icon file not found!")

ui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), THEME_PATH)

ui_manager.clear_and_reset()

def main():
    clock = pygame.time.Clock()
    running = True

    while running:
        time_delta = clock.tick(FPS) / 1000.0  # pygame_gui needs delta time
        events = pygame.event.get()  # Collect all events
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            # Let pygame_gui process events
            ui_manager.process_events(event)

        screen.fill(BLACK)  # Clear screen
        draw_home_screen(screen, events, ui_manager)  # Pass events and ui_manager
        ui_manager.update(time_delta)  # Update pygame_gui
        ui_manager.draw_ui(screen)  # Draw UI elements
        
        pygame.display.flip()


if __name__ == "__main__":
    main()