import pygame
import pygame_gui
import datetime
import random
from constants import *
from profileView import draw_view_profile_button

# List of alternative game names
GAME_NAMES = [
    "Blackjack", "Poker", "Baccarat", "Craps", "Keno", "Roulette"
]

# List of alternative Horse Derby names
DERBY_NAMES = [
    "Golden Gallop Derby", "Lightning Hooves Derby", "Midnight Run Derby", "Sunset Sprint Derby", "Thundering Tracks Derby"
]

used_derbies = []
last_update_minute = datetime.datetime.now().minute
random.shuffle(DERBY_NAMES)
random.shuffle(GAME_NAMES)
current_games = [
    {"name": DERBY_NAMES.pop()},
    {"name": GAME_NAMES.pop()},
    {"name": GAME_NAMES.pop()}
]
button_mapping = {}

def initialize_home(ui_manager):
    """Initializes the home screen with dynamically generated game buttons."""
    global button_mapping
    ui_manager.clear_and_reset()
    button_mapping.clear()
    y_offset = 150
    spacing = 20
    
    # Create game buttons with dynamic sizing based on text width
    for game in current_games:
        button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((200, y_offset), (400, 40)),
            text=game["name"],
            manager=ui_manager,
            object_id="#game-button",
        )
        button_mapping[button] = game["name"]
        y_offset += 40 + spacing
    
    # Create "Mine Crypto" button
    crypto_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 550), (200, 50)),
        text="Mine Crypto",
        manager=ui_manager,
        object_id="#crypto-button",
    )
    button_mapping[crypto_button] = "Mine Crypto"
    draw_view_profile_button(ui_manager)

def update_games():
    global last_update_minute, current_games, used_derbies, DERBY_NAMES
    now = datetime.datetime.now()
    if now.minute != last_update_minute:  # Update at the start of a new global minute
        last_update_minute = now.minute
        
        # Ensure unique derby name until all are used
        if len(used_derbies) == len(DERBY_NAMES):
            used_derbies = []  # Reset when all names have been used
        
        available_derbies = list(set(DERBY_NAMES) - set(used_derbies))
        new_derby = random.choice(available_derbies)
        used_derbies.append(new_derby)
        
        available_games = list(set(GAME_NAMES))  # Ensure unique game names
        random.shuffle(available_games)
        current_games = [
            {"name": new_derby},  # Change only the Derby name
            {"name": available_games.pop()},
            {"name": available_games.pop()}
        ]
        for button, game in zip(button_mapping.keys(), current_games):
            button.set_text(game["name"])  # Update button text
            


def draw_clock(screen):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    clock_surface = FONT.render(current_time, True, WHITE)
    screen.blit(clock_surface, (SCREEN_WIDTH - 120, 10))

def draw_home_screen(screen, events, ui_manager):
    global selected_game, current_screen
    current_screen = "home"
    selected_game = None
    draw_background(screen)
    
    title_text = FONT.render("Select a Game", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    
    # Process button clicks
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(event.ui_element.object_ids)
            print(event.ui_element.text)
            
            if event.ui_element.text == "Mine Crypto":
                selected_game = "crypto"
            else:
                selected_game = event.ui_element.text
            
            #selected_game = event.ui_element.text

    # Draw clock
    draw_clock(screen)
    update_games()

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()
    return selected_game
