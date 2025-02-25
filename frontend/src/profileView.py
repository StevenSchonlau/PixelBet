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
    global username
    session = UserSession()
    current_user = session.get_user()
    data = {
        "username": username,
        "avatar": all_sprites[active_index].name
    }

    response = requests.post(f"{BASEURL}/profile/{current_user}", json=data)
    if response.status_code == 200:
        print("Profile updated:", response.json())
    else:
        print("Error:", response.status_code, response.json())


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
    def __init__(self, x=60, y=0, name="", sprite_sheet=None):
        super().__init__()
        self.name = name
        self.frames = load_sprites(sprite_sheet, 8)
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_speed = 10
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


def init_profile_view(ui_manager):
    global all_sprites, active_sprite, avatar, username
    all_sprites = [
        Sprite(name="homeless1", sprite_sheet=pygame.image.load("frontend/assets/sprites/Homeless_1/Walk.png").convert_alpha()),
        Sprite(name="homeless2", sprite_sheet=pygame.image.load("frontend/assets/sprites/Homeless_2/Walk.png").convert_alpha()),
        Sprite(name="homeless3", sprite_sheet=pygame.image.load("frontend/assets/sprites/Homeless_3/Walk.png").convert_alpha())
    ]
    user = get_profile()
    avatar = user["avatar"]
    username = user["username"]
    if avatar:
        for sprite in all_sprites:
            if sprite.name == avatar:
                active_sprite = sprite
    else:
        active_sprite = all_sprites[0]

    ui_manager.clear_and_reset()


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
    
    return pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((x, y), (button_width, button_height)),
        text=text,
        manager=ui_manager,
    )


def get_center(text):
    text_surface = FONT.render(text, True, WHITE)
    button_width = text_surface.get_width() + 40
    button_x = (SCREEN_WIDTH - button_width) // 2
    return button_x


def draw_view_profile(screen, events, ui_manager, selected_game):
    global active_sprite, active_index
    screen.fill(BLACK)

    draw_button("Back", ui_manager, 0, 0)
    draw_button("<", ui_manager, 0, 200)
    draw_button(">", ui_manager, 300, 200)
    draw_button("save", ui_manager, get_center("save"), 500)

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            text = event.ui_element.text
            print(event.ui_element.object_ids)
            print(text)
            if text == "Back":
                selected_game = None
            elif text == "<" and active_sprite:
                active_index -= 1
                active_sprite = all_sprites[active_index % len(all_sprites)]
            elif text == ">" and active_sprite:
                active_index += 1
                active_sprite = all_sprites[active_index % len(all_sprites)]
            elif text == "save":
                save_profile()

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    if active_sprite:
        active_sprite.update()
        screen.blit(active_sprite.image, active_sprite.rect)

    pygame.display.flip()
    return selected_game