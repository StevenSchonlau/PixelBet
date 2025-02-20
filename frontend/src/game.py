import pygame
import pygame_gui
import datetime
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, FONT

back_button = None

def initialize_game(ui_manager):
    """Initializes the game screen UI elements."""
    global back_button
    
    # Clear old buttons to prevent stacking
    ui_manager.clear_and_reset()

    # Create "Back" button to return to home
    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 100, 100, 50)),
        text="Back",
        manager=ui_manager,
        object_id="#button"
    )


def draw_game_screen(screen, events, ui_manager, selected_game):
    """Handles the game screen display and returns None when 'Back' is pressed."""
    screen.fill(BLACK)
    
    game_text = FONT.render(f"Now Playing: {selected_game}", True, WHITE)
    screen.blit(game_text, (SCREEN_WIDTH // 2 - game_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    
    # Handle button clicks
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_button:
                print("Returning to home screen")
                return None  # Returning None signals `main.py` to go back to home
    
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()

    return selected_game