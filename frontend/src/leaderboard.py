import pygame
import pygame_gui
import datetime
import random
import requests
from constants import *
from user_session import UserSession

error = None

def draw_leaderboard_button(ui_manager, profile_button):
    text = "Leaderboard"
    text_surface = FONT.render(text, True, WHITE)
    button_width = text_surface.get_width() + 40
    button_height = text_surface.get_height() + 20
    button_x = 0
    button_y = profile_button.rect.height + 10
    
    button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((button_x, button_y), (button_width, button_height)),
        text=text,
        manager=ui_manager,
        object_id="#friends",
    )
def init_leaderboard_page(ui_manager):
    global ui_dict, curr_player
    ui_manager.clear_and_reset()
    profile = get_profile()
    curr_player = User(profile["username"], profile["id"])
    ui_dict = {}

    back_button = draw_button("Back", ui_manager, 0, 0)
    refresh_button = draw_button("Refresh", ui_manager, 0, .8)

def draw_leaderboard_page(screen, events, ui_manager, selected_game):
    global error

    draw_background(screen)

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            text = event.ui_element.text
            print(text)
            if text == "Back":
                selected_game = None

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    if error:
        error_name = FONT.render(error, True, WHITE)
        screen.blit(error_name, ((SCREEN_WIDTH // 8) * 2, (SCREEN_HEIGHT // 8) * 0))


    pygame.display.flip()
    return selected_game