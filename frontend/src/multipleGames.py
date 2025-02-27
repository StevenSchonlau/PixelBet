import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UIScrollingContainer
from constants import *

# Global variables
back_button = None
confirm_button = None
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
    global derby_buttons, confirm_button, selected_derbies

    # Reset the selected derbies list
    selected_derbies = []

    derby_buttons = []

    y_offset = 150
    spacing = 20

    for derby in DERBY_NAMES:
        UILabel(
            relative_rect=pygame.Rect((50, y_offset), (300, 40)),
            text=derby,
            manager=ui_manager,
            object_id=f"#label-{derby.replace(' ', '-').lower()}"
        )
        button = UIButton(
            relative_rect=pygame.Rect((360, y_offset), (100, 40)),
            text="Select",
            manager=ui_manager,
            object_id=f"#select-button-{derby.replace(' ', '-').lower()}"
        )
        derby_buttons.append(button)
        y_offset += 40 + spacing

    confirm_button = UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100), (200, 50)),
        text="Confirm",
        manager=ui_manager,
        object_id="#confirm-button"
    )

def initialize_games(ui_manager):
    """Initializes the multiple games screen with selected derbies."""
    ui_manager.clear_and_reset()
    global back_button

    container = UIScrollingContainer(
        relative_rect=pygame.Rect((50, 50), (700, 500)),
        manager=ui_manager,
        container=ui_manager.root_container,  # Use root_container instead of get_container
        anchors={'left': 'left',
                 'right': 'right',
                 'top': 'top',
                 'bottom': 'bottom'}
    )

    y_offset = 0
    for derby in selected_derbies:
        UILabel(
            relative_rect=pygame.Rect((0, y_offset), (container.relative_rect.width, 40)),  # Use relative_rect.width
            text=derby,
            manager=ui_manager,
            container=container,
            object_id=f"#label-{derby.replace(' ', '-').lower()}"
        )
        y_offset += 50

    back_button = UIButton(
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
                initialize_games(ui_manager)
            else:
                for button in derby_buttons:
                    if event.ui_element == button:
                        derby_name = button.object_ids[0].replace("#select-button-", "").replace("-", " ").title()
                        if derby_name in selected_derbies:
                            selected_derbies.remove(derby_name)
                            button.set_text("Select")
                        else:
                            selected_derbies.append(derby_name)
                            button.set_text("Remove")

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return "multiple_games"
