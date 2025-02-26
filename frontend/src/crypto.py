import pygame
import pygame_gui
from constants import *

def initialize_crypto(ui_manager):
    """Initializes the crypto mining screen."""
    ui_manager.clear_and_reset()
    global back_button
    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((20, SCREEN_HEIGHT - 60), (100, 40)),
        text="Back",
        manager=ui_manager,
        object_id="#back-button",
    )

def draw_crypto_screen(screen, events, ui_manager):
    draw_background(screen)
    title_text = FONT.render("Crypto Mining Simulation", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    
    # Display mining status
    mining_status = FONT.render("Mining in progress...", True, WHITE)
    screen.blit(mining_status, (SCREEN_WIDTH // 2 - mining_status.get_width() // 2, 150))

    # Process events
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == back_button:
            return "home"

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return "crypto"
