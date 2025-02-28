import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UIScrollingContainer, UIPanel
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
    "Golden Gallop Derby", "Lightning Hooves Derby", "Midnight Run Derby",
    "Sunset Sprint Derby", "Thundering Tracks Derby"
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
    """Initializes the multiple games screen with selected derbies in a scrollable view."""
    ui_manager.clear_and_reset()
    global back_button
    # Set fixed dimensions for the scrolling container
    container_width = 700
    container_height = 490
    panel_height = 160  # Height for each game panel
    total_content_height = len(selected_derbies) * panel_height  # Compute total height needed

    # Create a scrolling container that will hold all the game panels
    container = UIScrollingContainer(
        relative_rect=pygame.Rect((50, 50), (container_width, container_height)),  # Visible area
        manager=ui_manager,
        container=ui_manager.root_container,
        anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'},
        starting_height=1
    )

    # Ensure the container's virtual size is large enough to fit all games
    container.set_scrollable_area_dimensions(
        (container_width - 20, max(container_height, total_content_height))
    )

    y_offset = 0
    for derby in selected_derbies:
        # Create a container for each game inside the scrolling container
        game_container = UIPanel(
            relative_rect=pygame.Rect((0, y_offset), (container_width - 40, 150)),
            manager=ui_manager,
            container=container,
            starting_height=1
        )
        # Derby name label
        UILabel(
            relative_rect=pygame.Rect((10, 10), (game_container.relative_rect.width - 100, 30)),
            text=derby,
            manager=ui_manager,
            container=game_container
        )
        # Close (X) button
        hide_button = UIButton(
            relative_rect=pygame.Rect((game_container.relative_rect.width - 60, 10), (50, 30)),
            text="X",
            manager=ui_manager,
            container=game_container,
            object_id=f"#hide-button-{derby.replace(' ', '-').lower()}"
        )
        # Focus button
        focus_button = UIButton(
            relative_rect=pygame.Rect((game_container.relative_rect.width - 160, 10), (90, 30)),
            text="Focus",
            manager=ui_manager,
            container=game_container,
            object_id=f"#focus-button-{derby.replace(' ', '-').lower()}"
        )
        games[derby] = game_container  # Store the panel in the games dictionary
        y_offset += panel_height  # Move down for the next panel

    # Back button (outside of the scrolling container)
    back_button = UIButton(
        relative_rect=pygame.Rect((20, SCREEN_HEIGHT - 60), (100, 40)),
        text="Back",
        manager=ui_manager
    )

def draw_multiple_games_screen(screen, events, ui_manager):
    draw_background(screen)
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for obj_id in event.ui_element.object_ids:
                print(obj_id)
            if event.ui_element == back_button:
                return "home"
            elif event.ui_element == confirm_button:
                initialize_games(ui_manager)
            elif event.ui_element.object_ids[0].startswith("#root") and event.ui_element.object_ids[3].startswith("#hide-button-"):
                derby_name = event.ui_element.object_ids[3].replace("#hide-button-", "").replace("-", " ").title()
                if derby_name in selected_derbies:
                    # Remove the derby from selected_derbies list
                    selected_derbies.remove(derby_name)
                    # Re-render the page by initializing games again
                    initialize_games(ui_manager)
            elif event.ui_element.object_ids[0].startswith("#root") and event.ui_element.object_ids[3].startswith("#focus-button-"):
                derby_name = event.ui_element.object_ids[3].replace("#focus-button-", "").replace("-", " ").title()
                active_game = derby_name
                for sd in selected_derbies :
                    if (sd != derby_name) :
                        selected_derbies.remove(sd)
                initialize_games(ui_manager)
                return "single_game"
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
