import pygame
import pygame_gui
from constants import *
import datetime

# Initialize global variables
mining = False
earnings = 0.0
last_update_time = datetime.datetime.now()
passive_income_rate = 0.01
manual_mine_rate = 1
passive_upgrade_cost = 10
manual_upgrade_cost = 10
passive_upgrade_level = 1
manual_upgrade_level = 1
max_upgrade_level = 5

def initialize_crypto(ui_manager):
    """Initializes the crypto mining screen."""
    ui_manager.clear_and_reset()
    global back_button, toggle_button, manual_mine_button, earnings_display, status_message, passive_upgrade_button, manual_upgrade_button, passive_upgrade_message, manual_upgrade_message, passive_upgrade_cost_label, manual_upgrade_cost_label

    # Create UI elements for the upgrade chart
    passive_upgrade_message = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 300, 50), (200, 40)),
        text=f"Passive Income Tier: {passive_upgrade_level}",
        manager=ui_manager,
        object_id="#passive-upgrade-message",
    )
    manual_upgrade_message = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 + 100, 50), (200, 40)),
        text=f"Manual Mining Tier: {manual_upgrade_level}",
        manager=ui_manager,
        object_id="#manual-upgrade-message",
    )
    passive_upgrade_cost_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 300, 100), (200, 40)),
        text=f"Upgrade Cost: ${passive_upgrade_cost:.2f}",
        manager=ui_manager,
        object_id="#passive-upgrade-cost",
    )
    manual_upgrade_cost_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 + 100, 100), (200, 40)),
        text=f"Upgrade Cost: ${manual_upgrade_cost:.2f}",
        manager=ui_manager,
        object_id="#manual-upgrade-cost",
    )
    passive_upgrade_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 300, 150), (200, 40)),
        text="Upgrade",
        manager=ui_manager,
        object_id="#passive-upgrade-button",
        visible=True
    )
    manual_upgrade_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 + 100, 150), (200, 40)),
        text="Upgrade",
        manager=ui_manager,
        object_id="#manual-upgrade-button",
        visible=True
    )
    
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
    manual_mine_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40), (200, 40)),
        text="Manual Mine",
        manager=ui_manager,
        object_id="#manual-mine-button",
        visible=False
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
        earnings += elapsed_time * passive_income_rate  # Increase earnings based on time
    last_update_time = now

def upgrade_passive_income():
    global earnings, passive_income_rate, passive_upgrade_cost, passive_upgrade_level, max_upgrade_level, passive_upgrade_cost_label, manual_upgrade_cost_label
    if passive_upgrade_level < max_upgrade_level:
        if earnings >= passive_upgrade_cost:
            earnings -= passive_upgrade_cost
            passive_income_rate *= 1.5
            passive_upgrade_level += 1
            passive_upgrade_cost *= 1.5
            passive_upgrade_message.set_text(f"Passive Income Tier: {passive_upgrade_level}")
            passive_upgrade_cost_label.set_text(f"Upgrade Cost: ${passive_upgrade_cost:.2f}")
        else:
            passive_upgrade_message.set_text("Insufficient resources.")
    else:
        passive_upgrade_message.set_text("Max tier reached.")

def upgrade_manual_mining():
    global earnings, manual_mine_rate, manual_upgrade_cost, manual_upgrade_level, max_upgrade_level
    if manual_upgrade_level < max_upgrade_level:
        if earnings >= manual_upgrade_cost:
            earnings -= manual_upgrade_cost
            manual_mine_rate *= 1.5
            manual_upgrade_level += 1
            manual_upgrade_cost *= 1.5
            manual_upgrade_message.set_text(f"Manual Mining Tier: {manual_upgrade_level}")
            manual_upgrade_cost_label.set_text(f"Upgrade Cost: ${manual_upgrade_cost:.2f}")
        else:
            manual_upgrade_message.set_text("Insufficient resources.")
    else:
        manual_upgrade_message.set_text("Max tier reached.")

def draw_crypto_screen(screen, events, ui_manager):
    global mining, earnings
    draw_background(screen)
    
    # Process events
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_button:
                return "home"
            elif event.ui_element == toggle_button:
                mining = not mining
                if mining:
                    toggle_button.set_text("Stop Mining")
                    manual_mine_button.show()
                    status_message.set_text("Mining In Progress")
                else:
                    toggle_button.set_text("Start Mining")
                    manual_mine_button.hide()
                    status_message.set_text("Mining Stopped")
            elif event.ui_element == manual_mine_button:
                if mining:
                    earnings += manual_mine_rate
            elif event.ui_element == passive_upgrade_button:
                upgrade_passive_income()
            elif event.ui_element == manual_upgrade_button:
                upgrade_manual_mining()

    update_earnings()
    
    # Update earnings display
    earnings_display.set_text(f"Earnings: ${earnings:.2f}")

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return "crypto"
