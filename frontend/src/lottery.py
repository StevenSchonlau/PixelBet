import pygame
import pygame_gui
from constants import *
import datetime
from game import fetch_net_worth, update_net_worth

global net_worth, current_width, current_height

def initialize_lottery(ui_manager):
    global net_worth, back_button, current_width, current_height
    """Initializes the lottery screen."""
    ui_manager.clear_and_reset()
    net_worth = fetch_net_worth()
    current_width, current_height = pygame.display.get_window_size()

    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(0, 0, 100, 40),
        text="Back",
        manager=ui_manager,
        object_id="#back-button",
    )

def draw_lottery_screen(screen, events, ui_manager):
    """Draws the lottery screen."""
    global net_worth, back_button, current_width, current_height
    draw_background(screen)

    balance_text = FONT.render(f"Balance: ${net_worth:.2f}", True, WHITE)
    screen.blit(balance_text, (current_width - balance_text.get_width(), 10))

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_button:
                update_net_worth(net_worth)
                return "home"
            
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return "lottery"
    