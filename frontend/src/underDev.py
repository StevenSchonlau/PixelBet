import pygame
import pygame_gui
from constants import *

# Global variables
back_button = None

                              
def initialize_underDev(ui_manager):
    global back_button
    # Clear old UI elements
    ui_manager.clear_and_reset()

    # Create "Back" button to return to home
    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 0, 100, 40)),  # Position: Top Right
        text="Back",
        manager=ui_manager,
        object_id="#back_button"
    )


def draw_underDev_screen(screen, events, ui_manager, selected_game):
    
    draw_background(screen)

    # Show game and balance info
    game_text = FONT.render(f"Current Game is under development", True, WHITE)
    screen.blit(game_text, (screen_width // 2 - game_text.get_width() // 2, 50))

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_button:
                print("Returning to home screen")
                return None  # Go back to home

            
            
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return selected_game