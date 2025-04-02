import pygame
import pygame_gui
import datetime
import random
import requests
from constants import *
from user_session import UserSession

BASEURL = SERVER_URL

active_avatar_index = 0
active_shirt_index = 0
username = ""
avatar = 0
owns_shirts_list = []
achievements = []
ui_dict = {}
error = None
selected_friend = None
all_shirts = {}

def save_profile():
    global username, ui_dict, error, active_avatar_index, active_shirt_index
    session = UserSession()
    current_user = session.get_user()
    
    if ui_dict["username"].get_text() == "":
        error = "Cannot leave username blank!"
        return

    data = {
        "username": ui_dict["username"].get_text(),
        "avatar": active_avatar_index,
        "active_shirt": owns_shirts_list[active_shirt_index]
    }

    response = requests.post(f"{BASEURL}/profile/{current_user}", json=data)
    if response.status_code == 200:
        error = "Success!"
    else:
        error = "An error occurred"


def get_user_notification_preferences():
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/get-user-notification-preferences", json={"id": session.get_user()})
    preference = response.json()['preference']
    if preference is not None:
        return preference
    return False

def set_notification_preferences(value):
    session = UserSession()
    requests.post(f"{SERVER_URL}/set-user-notification-preferences", json={"id": session.get_user(), "preference": value})

def send_progress_email(email):
    session = UserSession()
    requests.post(f"{SERVER_URL}/send-progress-email", json={"id": session.get_user(), "email": email})

def init_profile_view(ui_manager, selected_player=None):
    global avatar, username, active_avatar_index, selected_friend, achievements, active_shirt, owns_shirts_list, all_shirts
    all_shirts = {
        "default0": pygame.transform.scale(pygame.image.load("frontend/assets/sprites/default1.png"), (200, 200)),
        "default1": pygame.transform.scale(pygame.image.load("frontend/assets/sprites/default2.png"), (200, 200)),
        "redShirt0": pygame.transform.scale(pygame.image.load("frontend/assets/sprites/redShirt1.png"), (200, 200)),
        "redShirt1": pygame.transform.scale(pygame.image.load("frontend/assets/sprites/redShirt2.png"), (200, 200)),
        "pixelShirt0": pygame.transform.scale(pygame.image.load("frontend/assets/sprites/pixelShirt1.png"), (200, 200)),
        "pixelShirt1": pygame.transform.scale(pygame.image.load("frontend/assets/sprites/pixelShirt2.png"), (200, 200)),
    }
    if selected_player:
        user = get_profile(selected_player.id)
        selected_friend = selected_player
    else:
        user = get_profile()
        selected_friend = None
    avatar = int(user["avatar"])
    username = user["username"]
    user_id = user["id"]
    active_shirt = user["active_shirt"]
    owns_shirts_list = user["owns_shirts_list"]
    
    resp = requests.get(f"{SERVER_URL}/achievements/{user_id}")
    if resp.status_code == 200:
        achievements = resp.json().get("achievements", [])
    else:
        achievements = []

    ui_manager.clear_and_reset()
    init_view_profile_ui(ui_manager)

def init_view_profile_ui(ui_manager):
    global username
    global ui_dict
    ui_manager.clear_and_reset()

    back_button = draw_button("Back", ui_manager, 0, 0)
    if not selected_friend:
        left_button = draw_button("<", ui_manager, 2.6, 4, "avatar_left")
        right_button = draw_button(">", ui_manager, 4.6, 4, "avatar_right")
        left_button_shirt = draw_button("<", ui_manager, 2.6, 3.3, "shirt_left")
        right_button_shirt = draw_button(">", ui_manager, 4.6, 3.3, "shirt_right")
        save_button = draw_button("save", ui_manager, 3.3, 5)
        username_field = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * .5), (SCREEN_WIDTH // 2,50)),
            manager=ui_manager,
            object_id="username"
        )
        username_field.set_text(username)
        ui_dict = {"username": username_field, "left": left_button, "right": right_button, "save": save_button}
    else:
        username_field = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * .5), (SCREEN_WIDTH // 2,50)),
            text=selected_friend.username,
            manager=ui_manager,
            object_id="#username-label"
        )
    username_label_rect = pygame.Rect((SCREEN_WIDTH // 4, SCREEN_HEIGHT // 8 * .5 - 30), (SCREEN_WIDTH // 2, 30))
    username_label = pygame_gui.elements.UILabel(
        relative_rect=username_label_rect,
        text="Username:",
        manager=ui_manager,
        object_id="username_label"
    )

    notifications_on = get_user_notification_preferences()
    if notifications_on:
        email_notification_btn = draw_button("Turn off notifications", ui_manager, 1, 7)
    else:
        email_notification_btn = draw_button("Turn on notifications", ui_manager, 2, 7)

    ui_dict["back"] = back_button
    ui_dict["email_notification_btn"] = email_notification_btn

    #TODO - add send progress email button and text field

    send_progress_email_btn = draw_button("Send Progress", ui_manager, 5, 6)
    ui_dict['send_progress_email_btn'] = send_progress_email_btn
    send_email_field = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 8 , SCREEN_HEIGHT // 8 * 6), (SCREEN_WIDTH // 2-25,50)),
        manager=ui_manager,
        object_id="send_email_field",
        placeholder_text="email to send to"
    )
    ui_dict['send_email_field'] = send_email_field


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
    text_surface = FONT.render(text, True, WHITE)
    button_width = text_surface.get_width() + 40
    button_x = (SCREEN_WIDTH - button_width) // 2
    return button_x


def draw_view_profile(screen, events, ui_manager, selected_game):
    global active_avatar_index, active_shirt_index, error, ui_dict
    draw_background(screen)

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            text = event.ui_element.text
            if text == "Back":
                selected_game = None
                error = None
            elif "avatar_left" in event.ui_element.object_ids:
                active_avatar_index = (active_avatar_index - 1) % 2
            elif "avatar_right" in event.ui_element.object_ids:
                active_avatar_index = (active_avatar_index + 1) % 2
            elif "shirt_left" in event.ui_element.object_ids:
                active_shirt_index = (active_shirt_index - 1) % len(owns_shirts_list)
            elif "shirt_right" in event.ui_element.object_ids:
                active_shirt_index = (active_shirt_index + 1) % len(owns_shirts_list)
            elif text == "save":
                save_profile()
            elif text == "Turn off notifications":
                set_notification_preferences(False)
                event.ui_element.text = "Turn on notifications"
                init_view_profile_ui(ui_manager)
            elif text == "Turn on notifications":
                set_notification_preferences(True)
                event.ui_element.text = "Turn off notifications"
                init_view_profile_ui(ui_manager)
            elif text == "Send Progress":
                send_progress_email(ui_dict["send_email_field"].get_text())

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    
    if error:
        error_name = FONT.render(error, True, WHITE)
        screen.blit(error_name, ((SCREEN_WIDTH // 8) * 1, (SCREEN_HEIGHT // 8) * 6))

    y_offset = SCREEN_HEIGHT // 8 * 6
    screen.blit(FONT.render("Achievements:", True, WHITE), (50, y_offset))
    y_offset += 30

    screen.blit(all_shirts[f'{owns_shirts_list[active_shirt_index]}{active_avatar_index}'], ((SCREEN_WIDTH // 8) * 3,(SCREEN_HEIGHT // 8) * 2))

    for ach in achievements:
        # Draw title
        title = FONT.render(ach["title"], True, WHITE)
        screen.blit(title, (90, y_offset + 4))

        y_offset += 40


    pygame.display.flip()
    return selected_game
