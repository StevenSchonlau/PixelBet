import pygame
import pygame_gui
import datetime
import random
from constants import *
from profileView import draw_view_profile_button
from leaderboard import draw_leaderboard_button
from login import clear_user
from notifications import get_user_notification_preferences
from settings import set_resolution_marker

import multipleGames

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
current_width = 0
current_height = 0

                 
notification_email_sent = False
notification_preference = False

def send_notification_email():
    """sends notification email"""
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/send-notification-email", json={"id": session.get_user()})
    print(response)


def initialize_home(ui_manager):
    """Initializes the home screen with dynamically generated game buttons."""
    global button_mapping, current_width, current_height
    current_width, current_height = pygame.display.get_window_size()
    ui_manager.clear_and_reset()
    button_mapping.clear()
    y_offset = 150
    spacing = 20
    button_width = 400
    
    for game in current_games:
        button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((current_width // 2 - button_width // 2, y_offset), (button_width, 40)),
            text=game["name"],
            manager=ui_manager,
            object_id="#game-button",
        )
        button_mapping[button] = game["name"]
        y_offset += 40 + spacing
    
    # Create "Mine Crypto" button
    crypto_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, current_height - 50), (200, 50)),
        text="Mine Crypto",
        manager=ui_manager,
        object_id="#crypto-button",
    )
    button_mapping[crypto_button] = "Mine Crypto"

    #Create "Sign out" button
    sign_out_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width - 160, 60), (160, 50)),
        text="Signout",
        manager=ui_manager,
        object_id="sign_out_button",
    )
    button_mapping[sign_out_button] = "Signout"

    settings_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width - 160, 120), (160, 50)),
        text="Settings",
        manager=ui_manager,
        object_id="settings_button",
    )
    button_mapping[settings_button] = "Settings"

    # music_shop_btn = pygame_gui.elements.UIButton(
    #     relative_rect=pygame.Rect((0, 180), (180, 50)),
    #     text="Music Shop",
    #     manager=ui_manager,
    #     object_id="music_shop_btn",
    # )
    # button_mapping[music_shop_btn] = "Music Shop"
    # shirt_shop_btn = pygame_gui.elements.UIButton(
    #     relative_rect=pygame.Rect((0, 240), (180, 50)),
    #     text="Shirt Shop",
    #     manager=ui_manager,
    #     object_id="shirt_shop_btn",
    # )
    # room_shop_btn = pygame_gui.elements.UIButton(
    #     relative_rect=pygame.Rect((0, 300), (180, 50)),
    #     text="Room Shop",
    #     manager=ui_manager,
    #     object_id="room_shop_btn",
    # )
    # theme_shop_btn = pygame_gui.elements.UIButton(
    #     relative_rect=pygame.Rect((0, 360), (180, 50)),
    #     text="Theme Shop",
    #     manager=ui_manager,
    #     object_id="theme_shop_btn",
    # )


    # Cosmetic shop buttons (hidden by default)
    cosmetic_buttons = []
    cosmetic_button_mapping = [
        {"id": "music_shop_btn", "text": "Music Shop"},
        {"id": "shirt_shop_btn", "text": "Shirt Shop"},
        {"id": "room_shop_btn", "text": "Room Shop"},
        {"id": "theme_shop_btn", "text": "Theme Shop"},
        {"id": "lottery_btn", "text": "Lottery"}
    ]

    y_cosmetic = 180
    for button_data in cosmetic_button_mapping:
        button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, y_cosmetic), (180, 50)),
            text=button_data["text"],
            manager=ui_manager,
            object_id=button_data["id"]
        )
        button.hide()  # Start collapsed (hidden)
        cosmetic_buttons.append(button)
        y_cosmetic += 60  # Adjust spacing

    # Create the toggle button for cosmetic shops
    toggle_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 120), (180, 50)),
        text="Shops",
        manager=ui_manager,
        object_id="toggle_cosmetic_btn"
    )

    button_mapping[toggle_button] = cosmetic_buttons  # Link toggle button to cosmetic buttons



    # Create "Friends" button
    text_surface = FONT.render("Friends", True, WHITE)
    button_width = text_surface.get_width() + 40
    button_height = text_surface.get_height() + 20
    button_x = current_width - button_width
    button_y = current_height - button_height
    
    friend_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((button_x, button_y), (button_width, button_height)),
        text="Friends",
        manager=ui_manager,
        object_id="#friends",
    )
    button_mapping[friend_button] = "Friends"
    profile_button = draw_view_profile_button(ui_manager)
    draw_leaderboard_button(ui_manager, profile_button)
    # Create "Multiple Games" button
    multiple_games_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width // 2 - 200, current_height - 50), (400, 50)), 
        text="Multiple Games",
        manager=ui_manager,
        object_id="#multiple-games-button"
    )
    button_mapping[multiple_games_button] = "Multiple Games"
    global notification_preference
    notification_preference = get_user_notification_preferences()

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
            
        if notification_preference:
            send_notification_email()
            notification_email_sent = True
            


def draw_clock(screen):
    global current_width
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    clock_surface = FONT.render(current_time, True, WHITE)
    screen.blit(clock_surface, (current_width - 120, 10))

def draw_home_screen(screen, events, ui_manager):
    global selected_game, current_screen, current_width
    current_screen = "home"
    selected_game = None
    draw_background(screen)
    
    title_text = FONT.render("Select a Game", True, WHITE)
    screen.blit(title_text, (current_width // 2 - title_text.get_width() // 2, 50))
    
    # Process button clicks
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(event.ui_element.object_ids)
            print(event.ui_element.text)
            
            if event.ui_element.text == "Mine Crypto":
                selected_game = "crypto"
            elif event.ui_element.text == "Multiple Games":
                selected_game = "multiple_games"
            elif "Derby" in event.ui_element.text:
                selected_game = event.ui_element.text
            elif "Profile" in event.ui_element.text:
                selected_game = event.ui_element.text
            elif "Friends" in event.ui_element.text:
                selected_game = event.ui_element.text
            elif "Leaderboard" in event.ui_element.text:
                selected_game = event.ui_element.text
            elif "Signout" in event.ui_element.text:
                clear_user()
                pygame.display.set_mode((800,600))
                set_resolution_marker(False)
            elif "Settings" in event.ui_element.text:
                print("Settings button clicked")
                selected_game = "settings"
            elif "Music" in event.ui_element.text and "Shops" not in event.ui_element.text:
                selected_game = "music"
            elif "Shirt" in event.ui_element.text and "Shops" not in event.ui_element.text:
                selected_game = "shirt"
            elif "Room" in event.ui_element.text and "Shops" not in event.ui_element.text:
                selected_game = "room"
            elif "Theme" in event.ui_element.text and "Shops" not in event.ui_element.text:
                selected_game = "theme"
            elif "Lottery" in event.ui_element.text:
                selected_game = "lottery"
            elif "Music" in event.ui_element.text:
                selected_game = "music"
            elif "Shirt" in event.ui_element.text:
                selected_game = "shirt"
            elif "Room" in event.ui_element.text:
                selected_game = "room"
            elif "Theme" in event.ui_element.text:
                selected_game = "theme"
            elif "Shops" in event.ui_element.text: 
                cosmetic_buttons = button_mapping[event.ui_element]
                if any(button.visible for button in cosmetic_buttons):  # If expanded
                    # Collapse the list
                    for button in cosmetic_buttons:
                        button.hide()
                    event.ui_element.set_text("Shops")  # Set to collapsed state
                else:
                    # Expand the list
                    for button in cosmetic_buttons:
                        button.show()
                    event.ui_element.set_text("Close Shops")  # Set to expanded state

            else:
                selected_game = "underDev"
            
            #selected_game = event.ui_element.text

    # Draw clock
    draw_clock(screen)
    update_games()

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()
    return selected_game
