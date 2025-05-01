import pygame
import pygame_gui
import datetime
import random
import requests
from constants import *
from user_session import UserSession
from game import fetch_bet_history

BASEURL = SERVER_URL

active_avatar_index = 0
active_room_index = 0
active_shirt_index = 0
active_theme_index = 0
username = ""
avatar = 0
owns_shirts_list = []
owns_rooms_list = []
owns_themes = []
achievements = []
ui_dict = {}
error = None
selected_friend = None
all_shirts = {}
all_rooms = {}
bet_history = []
current_width = 0
current_height = 0

def save_profile():
    global username, ui_dict, error, active_avatar_index, active_shirt_index, active_room_index
    session = UserSession()
    current_user = session.get_user()
    print(owns_shirts_list[active_shirt_index])
    
    if ui_dict["username"].get_text() == "":
        error = "Cannot leave username blank!"
        return

    data = {
        "username": ui_dict["username"].get_text(),
        "avatar": active_avatar_index,
        "active_shirt": active_shirt_index,
        "active_room": active_room_index,
        "active_theme": active_theme_index,
    }

    response = requests.post(f"{BASEURL}/profile/{current_user}", json=data)
    if response.status_code == 200:
        error = "Success!"
    else:
        error = "An error occurred"


def send_progress_email(email):
    session = UserSession()
    requests.post(f"{SERVER_URL}/send-progress-email", json={"id": session.get_user(), "email": email})

def init_profile_view(ui_manager, selected_player=None):
    global avatar, username, active_avatar_index, selected_friend, achievements
    global owns_shirts_list, all_shirts, all_rooms, owns_room_list, active_shirt_index, active_room_index
    global owns_themes, active_theme_index, bet_history, current_width, current_height
    all_shirts = {
        "default0": pygame.transform.scale(pygame.image.load("frontend/assets/sprites/default1.png"), (200, 200)),
        "default1": pygame.transform.scale(pygame.image.load("frontend/assets/sprites/default2.png"), (200, 200)),
        "redShirt0": pygame.transform.scale(pygame.image.load("frontend/assets/sprites/redShirt1.png"), (200, 200)),
        "redShirt1": pygame.transform.scale(pygame.image.load("frontend/assets/sprites/redShirt2.png"), (200, 200)),
        "pixelShirt0": pygame.transform.scale(pygame.image.load("frontend/assets/sprites/pixelShirt1.png"), (200, 200)),
        "pixelShirt1": pygame.transform.scale(pygame.image.load("frontend/assets/sprites/pixelShirt2.png"), (200, 200)),
    }
    all_rooms = {
        "default": pygame.image.load("frontend/assets/rooms/defaultRoom.png"),
        "cozy": pygame.image.load("frontend/assets/rooms/cozyRoom.png"),
        "tech": pygame.image.load("frontend/assets/rooms/techRoom.png"),
    }
    if selected_player:
        user = get_profile(selected_player.id)
        selected_friend = selected_player
    else:
        user = get_profile()
        selected_friend = None
    active_avatar_index = int(user["avatar"])
    username = user["username"]
    user_id = user["id"]

    owns_shirts_list = user["owns_shirts_list"]
    owns_room_list = user["owns_room_list"]
    owns_themes = user['owns_themes']

    active_shirt_index = int(user['active_shirt'])
    active_room_index = int(user['active_room'])
    active_theme_index = int(user['active_theme'])
    
    resp = requests.get(f"{SERVER_URL}/achievements/{user_id}")
    if resp.status_code == 200:
        achievements = resp.json().get("achievements", [])
    else:
        achievements = []
    bet_history = fetch_bet_history(user_id)
    print(bet_history)

    ui_manager.clear_and_reset()
    init_view_profile_ui(ui_manager)

def init_view_profile_ui(ui_manager):
    global username
    global ui_dict, current_height, current_width
    ui_manager.clear_and_reset()
    current_width, current_height = pygame.display.get_window_size()


    back_button = draw_button("Back", ui_manager, 0, 0)
    if not selected_friend:
        left_button = draw_button("<", ui_manager, 2.8, 6, "avatar_left", size="md")
        right_button = draw_button(">", ui_manager, 4.4, 6, "avatar_right", size="md")
        left_button_shirt = draw_button("<", ui_manager, 2.8, 5.3, "shirt_left", size="md")
        right_button_shirt = draw_button(">", ui_manager, 4.4, 5.3, "shirt_right", size="md")
        left_button_room = draw_button("<", ui_manager, 2.6, 0, "room_left", size="md")
        right_button_room = draw_button(">", ui_manager, 4.6, 0, "room_right", size="md")
        theme_left = draw_button("<", ui_manager, 5.5, 5.6, "theme_left", size="md")
        theme_right = draw_button(">", ui_manager, 7.4, 5.6, "theme_right", size="md")
        save_button = draw_button("save", ui_manager, 6.8, 6.3)
        username_field = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
            relative_rect=pygame.Rect((current_width // 8 * 4.8 , current_height // 8 * 6.3), (current_width // 4,50)),
            manager=ui_manager,
            object_id="username"
        )
        username_field.set_text(username)
        room_label_rect = pygame.Rect((current_width // 8 * 2.8, current_height // 8 * 0), (current_width // 4,50))
        room_label = pygame_gui.elements.UILabel(
            relative_rect=room_label_rect,
            text=f"{owns_room_list[active_room_index]}",
            manager=ui_manager,
        )
        theme_label_rect = pygame.Rect((current_width // 8 * 5.6, current_height // 8 * 5.5), (current_width // 4,50))
        theme_label = pygame_gui.elements.UILabel(
            relative_rect=theme_label_rect,
            text=f"{owns_themes[active_theme_index]} theme",
            manager=ui_manager,
        )
        ui_dict = {
            "username": username_field,
            "left": left_button,
            "right": right_button,
            "save": save_button,
            "avatar_left": left_button,
            "avatar_right": right_button,
            "shirt_left": left_button_shirt,
            "shirt_right": right_button_shirt,
            "room_left": left_button_room,
            "room_right": right_button_room,
            "room_label": room_label,
            "theme_left": theme_left,
            "theme_right": theme_right,
            "theme_label": theme_label,
        }
    else:
        username_field = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((current_width // 4 , current_height // 8 * .5), (current_width // 2,50)),
            text=selected_friend.username,
            manager=ui_manager,
            object_id="#username-label"
        )

    notification_settings = draw_button("Notifications", ui_manager, 2, 7, size="sm")
    ui_dict['Notifications'] = notification_settings
    time_limit_settings = draw_button("Time Limit", ui_manager, 2, 6.7, size="sm")
    ui_dict['Time Limit'] = time_limit_settings
    ui_dict["back"] = back_button

    #TODO - add send progress email button and text field

    send_progress_email_btn = draw_button("Send Progress", ui_manager, 2, 7.3, size="sm")
    ui_dict['send_progress_email_btn'] = send_progress_email_btn
    send_email_field = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
        relative_rect=pygame.Rect((current_width // 8 * 4.2 , current_height // 8 * 7), (current_width // 2-25,50)),
        manager=ui_manager,
        object_id="send_email_field",
        placeholder_text="email to send to"
    )
    ui_dict['send_email_field'] = send_email_field

    achievements_button = draw_button("Achievements", ui_manager, 0, 7.5, size="sm")
    ui_dict["achievements_button"] = achievements_button

def show_achievements_panel(ui_manager):
    global current_width, current_height
    """
    Creates and displays a panel overlay with the user's achievements.
    The panel includes a Close button to remove it.
    """
    panel_rect = pygame.Rect(200, 100, current_width - 400, current_height - 400)
    achievements_panel = pygame_gui.elements.UIPanel(
        relative_rect=panel_rect,
        manager=ui_manager,
        object_id="#achievements_panel"
    )
    ui_dict["achievements_panel"] = achievements_panel
    # Add a close button on the panel
    close_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((panel_rect.width - 110, 10), (100, 30)),
        text="Close",
        manager=ui_manager,
        container=achievements_panel,
        object_id="#close_achievements"
    )
    
    # List achievements inside the panel
    y_offset = 50
    if achievements:
        for ach in achievements:
            # Display each achievement title
            ach_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, y_offset, panel_rect.width - 20, 30)),
                text=ach["title"],
                manager=ui_manager,
                container=achievements_panel,
                object_id="#achievement_label"
            )
            y_offset += 40
    else:
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_offset, panel_rect.width - 20, 30)),
            text="No achievements earned yet.",
            manager=ui_manager,
            container=achievements_panel,
            object_id="#achievement_label"
        )
    
    return achievements_panel



def draw_view_profile_button(ui_manager):
    text_surface = FONT.render("View Profile", True, WHITE)
    button_width = text_surface.get_width() + 40  # Add padding
    button_height = text_surface.get_height() + 20
    button_x = 0
    button_y = 0
    
    button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((button_x, button_y), (button_width, button_height)),
        text="View Profile",
        manager=ui_manager,
        object_id="ViewProfileButton",
    )
    return button


def get_center(text):
    global current_width
    text_surface = FONT.render(text, True, WHITE)
    button_width = text_surface.get_width() + 40
    button_x = (current_width - button_width) // 2
    return button_x


def draw_view_profile(screen, events, ui_manager, selected_game):
    global active_avatar_index, active_shirt_index, error, ui_dict, bet_history, active_avatar_index, all_rooms, owns_room_list, active_room_index
    global active_theme_index, owns_themes, current_width, current_height
    bg = all_rooms[ owns_room_list[active_room_index] ]
    bg = pygame.transform.scale(bg, (current_width, current_height))
    screen.blit(bg, (0, 0))

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            text = event.ui_element.text
            if text == "Back":
                selected_game = None
                error = None
            elif event.ui_element == ui_dict["avatar_left"]:
                active_avatar_index = (active_avatar_index - 1) % 2
            elif event.ui_element == ui_dict["avatar_right"]:
                active_avatar_index = (active_avatar_index + 1) % 2
            elif event.ui_element == ui_dict["shirt_left"]:
                active_shirt_index = (active_shirt_index - 1) % len(owns_shirts_list)
            elif event.ui_element == ui_dict["shirt_right"]:
                active_shirt_index = (active_shirt_index + 1) % len(owns_shirts_list)
            elif event.ui_element == ui_dict["room_left"]:
                active_room_index = (active_room_index - 1) % len(owns_room_list)
            elif event.ui_element == ui_dict["room_right"]:
                active_room_index = (active_room_index + 1) % len(owns_room_list)
            elif event.ui_element == ui_dict["theme_left"]:
                active_theme_index = (active_theme_index - 1) % len(owns_themes)
            elif event.ui_element == ui_dict["theme_right"]:
                active_theme_index = (active_theme_index + 1) % len(owns_themes)
            elif text == "save":
                save_profile()
            elif text == "Notifications":
                selected_game = "notifications"
            elif text == "Time Limit":
                selected_game = "time limit"
            elif text == "Send Progress":
                send_progress_email(ui_dict["send_email_field"].get_text())
            elif text == "Achievements":
                # Create and display the achievements panel overlay.
                show_achievements_panel(ui_manager)
            elif event.ui_element.object_ids and "#close_achievements" in event.ui_element.object_ids:
                if "achievements_panel" in ui_dict:
                    ui_dict["achievements_panel"].kill()
                    del ui_dict["achievements_panel"]

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    if "room_label" in ui_dict:
        ui_dict["room_label"].set_text(f"{owns_room_list[active_room_index]} room")
    if "theme_label" in ui_dict:
        ui_dict["theme_label"].set_text(f"{owns_themes[active_theme_index]} theme")

    
    if error:
        error_name = FONT.render(error, True, WHITE)
        screen.blit(error_name, ((current_width // 8) * 1, (current_height // 8) * 6))

    y_offset = screen_height // 8 * 6

    screen.blit(all_shirts[f'{owns_shirts_list[active_shirt_index]}{active_avatar_index}'], ((current_width // 8) * 3.6 - 80,(current_height // 2 + 30)))


    wins = sum(1 for bet in bet_history if bet.get("outcome") == "win")
    losses = sum(1 for bet in bet_history if bet.get("outcome") == "loss")
    wins_text = FONT.render(f"Wins: {wins}", True, (0, 255, 0))
    losses_text = FONT.render(f"Losses: {losses}", True, (255, 0, 0))
    wins_pos = (current_width - wins_text.get_width() - 10, 10)
    losses_pos = (current_width - losses_text.get_width() - 10, 10 + wins_text.get_height() + 5)
    screen.blit(wins_text, wins_pos)
    screen.blit(losses_text, losses_pos)


    pygame.display.flip()
    return selected_game
