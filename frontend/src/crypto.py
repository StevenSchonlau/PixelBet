import pygame
import pygame_gui
from constants import *
import datetime

# Initialize global variables
mining = False
earnings = 0.0
last_update_time = datetime.datetime.now()

def initialize_crypto(ui_manager):
    """Initializes the crypto mining screen."""
    ui_manager.clear_and_reset()
    global back_button, toggle_button, earnings_display, status_message
    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((20, SCREEN_HEIGHT - 60), (100, 40)),
        text="Back",
        manager=ui_manager,
        object_id="#back-button",
    )
    toggle_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20), (200, 40)),
        text="Start Mining",
        manager=ui_manager,
        object_id="#toggle-button",
    )
    earnings_display = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100), (200, 40)),
        text=f"Earnings: ${earnings:.2f}",
        manager=ui_manager,
        object_id="#earnings-display",
    )
    status_message = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 150), (200, 40)),
        text="Mining Stopped",
        manager=ui_manager,
        object_id="#status-message",
    )

def update_earnings():
    global earnings, last_update_time
    now = datetime.datetime.now()
    elapsed_time = (now - last_update_time).total_seconds()
    if mining:
        earnings += elapsed_time * 0.01  # Increase earnings based on time
    last_update_time = now

def draw_crypto_screen(screen, events, ui_manager):
    global mining
    draw_background(screen)
    title_text = FONT.render("Crypto Mining Simulation", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    
    # Process events
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_button:
                return "home"
            elif event.ui_element == toggle_button:
                mining = not mining
                if mining:
                    toggle_button.set_text("Stop Mining")
                    status_message.set_text("Mining Started")
                else:
                    toggle_button.set_text("Start Mining")
                    status_message.set_text("Mining Stopped")

    update_earnings()
    
    # Update earnings display
    earnings_display.set_text(f"Earnings: ${earnings:.2f}")

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return "crypto"
