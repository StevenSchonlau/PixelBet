import pygame
import pygame_gui
from constants import *

# Global variables
back_button = None
resolution_dropdown = None
resolution_set = False
AVAILABLE_RESOLUTIONS = ["800x600", "1024x768", "1280x720", "1920x1080"]
BASEURL = SERVER_URL

button_sound_enabled = True
winning_sound_enabled = True
losing_sound_enabled = True
money_sound_enabled = True

# Dictionary to store sound buttons
sound_buttons = {}

def toggle_sound(setting_name):
    global button_sound_enabled, winning_sound_enabled, losing_sound_enabled, money_sound_enabled, sound_buttons
    
    # Toggle the correct setting
    if setting_name == "Button Sound":
        button_sound_enabled = not button_sound_enabled
        sound_buttons["#button_sound_button"].set_text("ON" if button_sound_enabled else "OFF")
    elif setting_name == "Winning Sound":
        winning_sound_enabled = not winning_sound_enabled
        sound_buttons["#winning_sound_button"].set_text("ON" if winning_sound_enabled else "OFF")
    elif setting_name == "Losing Sound":
        losing_sound_enabled = not losing_sound_enabled
        sound_buttons["#losing_sound_button"].set_text("ON" if losing_sound_enabled else "OFF")
    elif setting_name == "Money Sound":
        money_sound_enabled = not money_sound_enabled
        sound_buttons["#money_sound_button"].set_text("ON" if money_sound_enabled else "OFF")

def is_money_sound_enabled():
    return money_sound_enabled

def is_losing_sound_enabled():
    return losing_sound_enabled 

def is_winning_sound_enabled():
    return winning_sound_enabled

def is_button_sound_enabled():
    return button_sound_enabled


def is_resolution_set():
    return resolution_set

def set_resolution_marker(marker):
    global resolution_set
    resolution_set = marker

def fetch_user_resolution():
    session = UserSession()
    resp = requests.get(f"{BASEURL}/profile/{session.get_user()}")
    if resp.status_code == 200:
        data = resp.json()
        res = f"{data.get('resolution_width',800)}x{data.get('resolution_height',600)}"
        # if backend has a weird value, fall back to first choice
        return res if res in AVAILABLE_RESOLUTIONS else AVAILABLE_RESOLUTIONS[0]
    return AVAILABLE_RESOLUTIONS[0]

def update_user_resolution(new_res):
    """POST the new resolution back to the backend."""
    session = UserSession()
    user_id = session.get_user()
    payload = {
        "resolution": new_res
    }
    requests.post(
        f"{BASEURL}/profile/{user_id}",
        json=payload
    )

                              
def initialize_settings(ui_manager):
    global back_button, resolution_dropdown, button_sound_button, winning_sound_button, losing_sound_button, money_sound_button, sound_buttons
    # Clear old UI elements
    ui_manager.clear_and_reset()
    starting = fetch_user_resolution()
    print(starting)
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

    resolution_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(
            current_width // 2 - dropdown_width // 2 - 100, 
            current_height // 2 - dropdown_height // 2, 
            dropdown_width, 
            dropdown_height
        ),
        text="Screen Resolution:",
        manager=ui_manager, 
        )

    resolution_dropdown = pygame_gui.elements.UIDropDownMenu(
        options_list=AVAILABLE_RESOLUTIONS,
        starting_option=starting,
        relative_rect=pygame.Rect( 
            current_width // 2 - dropdown_width // 2 + 100, 
            current_height // 2 - dropdown_height // 2,
            dropdown_width, 
            dropdown_height
        ),
        manager=ui_manager,
        container= None,
        object_id="#resolution_dropdown"
    )

    button_width, button_height = 100, 40
    label_width = 200

    # List of sound options
    sound_settings = [
        ("Button Sound", button_sound_enabled, "#button_sound_button"),
        ("Winning Sound", winning_sound_enabled, "#winning_sound_button"),
        ("Losing Sound", losing_sound_enabled, "#losing_sound_button"),
        ("Money Sound", money_sound_enabled, "#money_sound_button")
    ]

    # Create buttons and labels for sound settings
    for i, (label_text, enabled, object_id) in enumerate(sound_settings):
        y_position = current_height // 2 + 50 + i * 50
        
        # Label
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((current_width // 2 - 200, y_position, label_width, button_height)),
            text=f"{label_text}:",
            manager=ui_manager
        )

        # Button
        sound_buttons[object_id] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((current_width // 2 + 20, y_position, button_width, button_height)),
            text="ON" if enabled else "OFF",
            manager=ui_manager,
            object_id=object_id
        )



def draw_settings_screen(screen, events, ui_manager, selected_game):
    global back_button, resolution_dropdown, button_sound_button, winning_sound_button
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
            if event.ui_element in sound_buttons.values():
                for sound_name, object_id in [("Button Sound", "#button_sound_button"),
                                              ("Winning Sound", "#winning_sound_button"),
                                              ("Losing Sound", "#losing_sound_button"),
                                              ("Money Sound", "#money_sound_button")]:
                    if event.ui_element == sound_buttons[object_id]:
                        toggle_sound(sound_name)
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == resolution_dropdown:
                # User selected a new resolution
                selected_option = event.text  # Format: "WIDTHxHEIGHT" (e.g., "1280x720")
                width, height = map(int, selected_option.split('x'))
                new_resolution = (width, height)
                # Update the display mode to the new resolution. You might want to preserve flags.
                pygame.display.set_mode(new_resolution)
                ui_manager.set_window_resolution((width, height))
                update_user_resolution(selected_option)
                initialize_settings(ui_manager)
                

            
            
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return selected_game