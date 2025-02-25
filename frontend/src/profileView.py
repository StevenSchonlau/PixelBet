import pygame
import pygame_gui
import datetime
import random
from constants import *

def load_sprites(sheet, num_frames, row=0):
    frame_width = SPRITE_SIZE
    frame_height = SPRITE_SIZE
    frames = []
    for i in range(num_frames):
        frame = sheet.subsurface(pygame.Rect(i * frame_width, row * frame_height, frame_width, frame_height))
        frames.append(frame)
    return frames

class Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_sheet):
        super().__init__()
        self.frames = load_sprites(sprite_sheet, 8)
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_speed = 10
        self.frame_counter = 0
    
    def update(self):
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            print(self.index)
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]
            self.frame_counter = 0


all_sprites = None
def init_profile_view():
    global all_sprites
    sprites = {
        "city1": Sprite(100, 0, pygame.image.load("frontend/assets/sprites/City_men_1/Walk.png").convert_alpha()),
        "city2": Sprite(0, 0, pygame.image.load("frontend/assets/sprites/City_men_2/Walk.png").convert_alpha()),
        "city3": Sprite(200, 0, pygame.image.load("frontend/assets/sprites/City_men_3/Walk.png").convert_alpha())
    }
    all_sprites = pygame.sprite.Group(sprites.values())

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

def draw_view_profile(screen, events, ui_manager, selected_game):
    screen.fill(BLACK)

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(event.ui_element.object_ids)
            print(event.ui_element.text)
            selected_game = event.ui_element.text

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    all_sprites.update()
    all_sprites.draw(screen)

    pygame.display.flip()
    return selected_game