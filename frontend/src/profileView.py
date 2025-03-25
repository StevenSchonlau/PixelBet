import pygame
import pygame_gui
import datetime
import random
import requests
from constants import *
from user_session import UserSession

BASEURL = SERVER_URL


def save_profile():
    global username, ui_dict, error
    session = UserSession()
    current_user = session.get_user()
    
    if ui_dict["username"].get_text() == "":
        error = "Cannot leave username blank!"
        return

    data = {
        "username": ui_dict["username"].get_text(),
        "avatar": all_sprites[active_index].name
    }

    response = requests.post(f"{BASEURL}/profile/{current_user}", json=data)
    if response.status_code == 200:
        print("Profile updated:", response.json())
        error = "Success!"
    else:
        print("Error:", response.status_code, response.json())
        error = "An error occurred"


def get_user_notification_preferences():
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/get-user-notification-preferences", json={"id": session.get_user()})
    print(response)
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



all_sprites = {}
active_sprite = None
active_index = 0
username = ""
avatar = ""
ui_dict = {}
error = None
selected_friend = None


def init_profile_view(ui_manager, selected_player=None):
    global all_sprites, active_sprite, avatar, username, active_index, selected_friend
    all_sprites = [
        Sprite(name="homeless1", sprite_sheet=pygame.image.load("frontend/assets/sprites/Homeless_1/Walk.png").convert_alpha()),
        Sprite(name="homeless2", sprite_sheet=pygame.image.load("frontend/assets/sprites/Homeless_2/Walk.png").convert_alpha()),
        Sprite(name="homeless3", sprite_sheet=pygame.image.load("frontend/assets/sprites/Homeless_3/Walk.png").convert_alpha())
    ]
    if selected_player:
        user = get_profile(selected_player.id)
        selected_friend = selected_player
    else:
        user = get_profile()
        selected_friend = None
    avatar = user["avatar"]
    username = user["username"]
    if avatar:
        for index, sprite in enumerate(all_sprites):
            if sprite.name == avatar:
                active_sprite = sprite
                active_index = index

    else:
        active_sprite = all_sprites[0]

    ui_manager.clear_and_reset()
    init_view_profile_ui(ui_manager)

def init_view_profile_ui(ui_manager):
    global username
    global ui_dict
    ui_manager.clear_and_reset()

    back_button = draw_button("Back", ui_manager, 0, 0)
    if not selected_friend:
        left_button = draw_button("<", ui_manager, 2.6, 4)
        right_button = draw_button(">", ui_manager, 4.6, 4)
        save_button = draw_button("save", ui_manager, 3.3, 7)
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
    global active_sprite, active_index, error
    draw_background(screen)

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            text = event.ui_element.text
            print(event.ui_element.object_ids)
            print(text)
            if text == "Back":
                selected_game = None
                error = None
            elif text == "<" and active_sprite:
                active_index = (active_index - 1) % len(all_sprites)
                active_sprite = all_sprites[active_index]
            elif text == ">" and active_sprite:
                active_index = (active_index + 1) % len(all_sprites)
                active_sprite = all_sprites[active_index]
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

    if active_sprite:
        active_sprite.update()
        screen.blit(active_sprite.image, active_sprite.rect)

        sprite_name = FONT.render(active_sprite.name, True, WHITE)
        screen.blit(sprite_name, ((SCREEN_WIDTH // 8) * 3.1, (SCREEN_HEIGHT // 8) * 4.9))
    
    if error:
        error_name = FONT.render(error, True, WHITE)
        screen.blit(error_name, ((SCREEN_WIDTH // 8) * 1, (SCREEN_HEIGHT // 8) * 6))


    pygame.display.flip()
    return selected_game