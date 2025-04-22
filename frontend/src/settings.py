import pygame
import pygame_gui
from constants import *

# Global variables
back_button = None
resolution_dropdown = None
AVAILABLE_RESOLUTIONS = ["800x600", "1024x768", "1280x720", "1920x1080"]

                              
def initialize_settings(ui_manager):
    global back_button, resolution_dropdown
    # Clear old UI elements
    ui_manager.clear_and_reset()
    current_width, current_height = pygame.display.get_window_size()

    # Create "Back" button to return to home
    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 0, 100, 40)),
        text="Back",
        manager=ui_manager,
        object_id="#back_button"
    )
    dropdown_width = 200
    dropdown_height = 40

    resolution_dropdown = pygame_gui.elements.UIDropDownMenu(
        options_list=AVAILABLE_RESOLUTIONS,
        starting_option=AVAILABLE_RESOLUTIONS[0],
        relative_rect=pygame.Rect(
        (current_width // 2 - dropdown_width // 2, current_height // 2 - dropdown_height // 2,
         dropdown_width, dropdown_height)
    ),
        manager=ui_manager,
        container= None,
        object_id="#resolution_dropdown"
    )


def draw_settings_screen(screen, events, ui_manager, selected_game):
    global back_button, resolution_dropdown
    current_width, current_height = pygame.display.get_window_size()
    
    draw_background(screen)

    # Show game and balance info
    game_text = FONT.render(f"Settings", True, WHITE)
    screen.blit(game_text, (current_width // 2 - game_text.get_width() // 2, 50))

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_button:
                print("Returning to home screen")
                return None  # Go back to home
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == resolution_dropdown:
                # User selected a new resolution
                selected_option = event.text  # Format: "WIDTHxHEIGHT" (e.g., "1280x720")
                width, height = map(int, selected_option.split('x'))
                new_resolution = (width, height)
                # Update the display mode to the new resolution. You might want to preserve flags.
                pygame.display.set_mode(new_resolution)
                ui_manager.set_window_resolution((width, height))
                initialize_settings(ui_manager)

            
            
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return selected_game