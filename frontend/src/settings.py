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
button_sound_button = None
winning_sound_enabled = True
winning_sound_button = None
losing_sound_enabled = True
losing_sound_button = None
money_sound_enabled = True
money_sound_button = None

def is_money_sound_enabled():
    return money_sound_enabled
def toggle_money_sound():   
    global money_sound_enabled, money_sound_button
    money_sound_enabled = not money_sound_enabled
    if money_sound_enabled: # if current state is enabled, be able to turn it off
        money_sound_button.set_text("Turn off money sound")
    else:
        money_sound_button.set_text("Turn on money sound")

def is_losing_sound_enabled():
    return losing_sound_enabled 
def toggle_losing_sound():
    global losing_sound_enabled, losing_sound_button
    losing_sound_enabled = not losing_sound_enabled
    if losing_sound_enabled: # if current state is enabled, be able to turn it off
        losing_sound_button.set_text("Turn off losing sound")
    else:
        losing_sound_button.set_text("Turn on losing sound")

def is_winning_sound_enabled():
    return winning_sound_enabled
def toggle_winning_sound():
    global winning_sound_enabled, winning_sound_button
    winning_sound_enabled = not winning_sound_enabled
    if winning_sound_enabled: # if current state is enabled, be able to turn it off
        winning_sound_button.set_text("Turn off winning sound")
    else:
        winning_sound_button.set_text("Turn on winning sound")

def is_button_sound_enabled():
    return button_sound_enabled
def toggle_button_sound():
    global button_sound_enabled, button_sound_button
    button_sound_enabled = not button_sound_enabled
    if button_sound_enabled: # if current state is enabled, be able to turn it off
        button_sound_button.set_text("Turn off button sound")
    else:
        button_sound_button.set_text("Turn on button sound")


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
    global back_button, resolution_dropdown, button_sound_button, winning_sound_button, losing_sound_button, money_sound_button
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

    button_sound_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width // 2 - 200, current_height // 2 + 50, 400, 40)),
        text="Turn off button sound" if button_sound_enabled else "Turn on button sound",
        manager=ui_manager,
        object_id="#button_sound_button"
    )

    winning_sound_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width // 2 - 200, current_height // 2 + 100, 400, 40)),
        text="Turn off winning sound" if winning_sound_enabled else "Turn on winning sound",
        manager=ui_manager,
        object_id="#winning_sound_button"
    )

    losing_sound_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width // 2 - 200, current_height // 2 + 150, 400, 40)),
        text="Turn off losing sound" if button_sound_enabled else "Turn on losing sound",
        manager=ui_manager,
        object_id="#losing_sound_button"
    )

    money_sound_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width // 2 - 200, current_height // 2 + 200, 400, 40)),
        text="Turn off money sound" if money_sound_enabled else "Turn on money sound",
        manager=ui_manager,
        object_id="#money_sound_button"
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
            if event.ui_element == button_sound_button:
                toggle_button_sound()
            if event.ui_element == winning_sound_button:
                toggle_winning_sound()
            if event.ui_element == losing_sound_button:
                toggle_losing_sound()
            if event.ui_element == money_sound_button:
                toggle_money_sound()
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