import pygame
import pygame_gui
import datetime
import random
import requests
from constants import *
from user_session import UserSession

BASEURL = SERVER_URL


def get_profile():
    session = UserSession()
    current_user = session.get_user()

    response = requests.get(f"{BASEURL}/profile/{current_user}")
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Error: {response.status_code}, {response.text}")
    
    return response.json()


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
        error = None
    else:
        print("Error:", response.status_code, response.json())
        error = "An error occurred"


def load_sprites(sheet, num_frames, row=0, scale=2):
    frame_width = SPRITE_SIZE
    frame_height = SPRITE_SIZE
    frames = []
    for i in range(num_frames):
        frame = sheet.subsurface(pygame.Rect(i * frame_width, row * frame_height, frame_width, frame_height))
        scaled_frame = pygame.transform.scale(frame, (frame_width * scale, frame_height * scale))
        frames.append(scaled_frame)
    return frames


class Sprite(pygame.sprite.Sprite):
    def __init__(self, name="", sprite_sheet=None):
        super().__init__()
        self.name = name
        self.frames = load_sprites(sprite_sheet, 8)
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 8 * 3))
        self.animation_speed = 5
        self.frame_counter = 0
    
    def update(self):
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]
            self.frame_counter = 0


all_sprites = {}
active_sprite = None
active_index = 0
username = ""
avatar = ""
ui_dict = {}
error = None


def init_profile_view(ui_manager):
    global all_sprites, active_sprite, avatar, username, active_index
    all_sprites = [
        Sprite(name="homeless1", sprite_sheet=pygame.image.load("frontend/assets/sprites/Homeless_1/Walk.png").convert_alpha()),
        Sprite(name="homeless2", sprite_sheet=pygame.image.load("frontend/assets/sprites/Homeless_2/Walk.png").convert_alpha()),
        Sprite(name="homeless3", sprite_sheet=pygame.image.load("frontend/assets/sprites/Homeless_3/Walk.png").convert_alpha())
    ]
    user = get_profile()
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
    ui_elements = init_view_profile_ui(ui_manager)

def init_view_profile_ui(ui_manager):
    global username
    global ui_dict
    ui_manager.clear_and_reset()

    back_button = draw_button("Back", ui_manager, 0, 0)
    left_button = draw_button("<", ui_manager, 2.6, 4)
    right_button = draw_button(">", ui_manager, 4.6, 4)
    save_button = draw_button("save", ui_manager, 3.3, 7)
    username_field = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * .5), (SCREEN_WIDTH // 2,50)),
        manager=ui_manager,
        object_id="username"
    )
    username_field.set_text(username)
    username_label_rect = pygame.Rect((SCREEN_WIDTH // 4, SCREEN_HEIGHT // 8 * .5 - 30), (SCREEN_WIDTH // 2, 30))
    username_label = pygame_gui.elements.UILabel(
        relative_rect=username_label_rect,
        text="Username:",
        manager=ui_manager,
        object_id="username_label"
    )

    ui_dict = {"username": username_field, "back": back_button, "left": left_button, "right": right_button, "save": save_button}
    return {"username": username_field, "back": back_button, "left": left_button, "right": right_button, "save": save_button}


def draw_view_profile_button(screen, ui_manager):
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


def draw_button(text, ui_manager, x, y):
    text_surface = FONT.render(text, True, WHITE)
    button_width = text_surface.get_width() + 40
    button_height = text_surface.get_height() + 20
    button_x = (SCREEN_WIDTH // 8) * x
    button_y = (SCREEN_HEIGHT // 8) * y
    
    return pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((button_x, button_y), (button_width, button_height)),
        text=text,
        manager=ui_manager,
    )


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
            elif text == "<" and active_sprite:
                active_index = (active_index - 1) % len(all_sprites)
                active_sprite = all_sprites[active_index]
            elif text == ">" and active_sprite:
                active_index = (active_index + 1) % len(all_sprites)
                active_sprite = all_sprites[active_index]
            elif text == "save":
                save_profile()

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