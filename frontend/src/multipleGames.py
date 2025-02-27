import pygame
import pygame_gui
import datetime
import random
from constants import *

# Global variables
back_button = None
confirm_button = None  # Declare confirm_button as a global variable
race_timer_label = None
message_label = None
racing_phase = False
winner_announced = False
bets_placed = []
bet_history = []
user_balance = 1000
games = {}
active_game = None

# List of Derby names
DERBY_NAMES = [
    "Golden Gallop Derby", "Lightning Hooves Derby", "Midnight Run Derby", "Sunset Sprint Derby", "Thundering Tracks Derby"
]
selected_derbies = []

def prompt_user_for_derbies(ui_manager):
    """Prompts the user to select derbies to display."""
    ui_manager.clear_and_reset()
    global derby_buttons, confirm_button  # Declare derby_buttons and confirm_button as global

    derby_buttons = []

    y_offset = 150
    spacing = 20

    # Create buttons for each derby
    for derby in DERBY_NAMES:
        button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((200, y_offset), (400, 40)),
            text=derby,
            manager=ui_manager,
            object_id="#derby-button",
        )
        derby_buttons.append(button)
        y_offset += 40 + spacing

    confirm_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100), (200, 50)),
        text="Confirm Selection",
        manager=ui_manager,
        object_id="#confirm-button"
    )

def initialize_games(ui_manager):
    """Initializes the multiple games screen with selected derbies."""
    ui_manager.clear_and_reset()
    global back_button, game_buttons

    x_offset = 50
    for derby in selected_derbies:
        game_data = {
            "name": derby,
            "button": pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((x_offset, 20), (200, 40)),
                text=derby,
                manager=ui_manager
            )
        }
        games[derby] = game_data
        x_offset += 220

    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((20, SCREEN_HEIGHT - 60), (100, 40)),
        text="Back",
        manager=ui_manager,
        object_id="#back-button",
    )

def draw_multiple_games_screen(screen, events, ui_manager):
    draw_background(screen)
    
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_button:
                return "home"
            elif event.ui_element == confirm_button:
                for button in derby_buttons:
                    if button.check_pressed():
                        selected_derbies.append(button.text)
                initialize_games(ui_manager)
            else:
                for game_id, game_data in games.items():
                    if event.ui_element == game_data["button"]:
                        handle_game_selection(game_id)

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return "multiple_games"
