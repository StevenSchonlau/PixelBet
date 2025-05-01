import pygame
import pygame_gui
import random
import time
from constants import *
from game import fetch_net_worth, update_net_worth

global net_worth, current_width, current_height, back_button, lottery_dropdown, ticket_input, play_button, result_label, countdown_start, standard_info_button, quick_info_button, standard_popup, quick_popup

# Lottery options
LOTTERY_TYPES = ["Standard Lottery", "Quick Lottery"]
STANDARD_LOTTERY_PRICE = 15
QUICK_LOTTERY_PRICE = 2
countdown_start = None  # To track when the lottery started

def initialize_lottery(ui_manager):
    global net_worth, back_button, lottery_dropdown, ticket_input, play_button, result_label, countdown_start, current_width, current_height
    global standard_info_button, quick_info_button, standard_popup, quick_popup

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

    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((current_width // 2 - 300, current_height // 2 - 180, 200, 40)),
        text="Click to see details:",
        manager=ui_manager,
    )

    # Lottery Information Buttons
    standard_info_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width // 2 - 100, current_height // 2 - 180, 200, 40)),
        text="Standard",
        manager=ui_manager,
        object_id="#standard-info",
    )

    quick_info_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width // 2 + 110, current_height // 2 - 180, 200, 40)),
        text="Quick",
        manager=ui_manager,
        object_id="#quick-info",
    )

    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((current_width // 2 - 250, current_height // 2 - 100, 200, 40)),
        text="Select Lottery Type:",
        manager=ui_manager,
    )

    lottery_dropdown = pygame_gui.elements.UIDropDownMenu(
        options_list=LOTTERY_TYPES,
        starting_option=LOTTERY_TYPES[0],
        relative_rect=pygame.Rect((current_width // 2 - 50, current_height // 2 - 100, 300, 40)),
        manager=ui_manager,
        object_id="#lottery-dropdown",
    )

    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((current_width // 2 - 200, current_height // 2 - 50, 200, 40)),
        text="Number of Tickets:",
        manager=ui_manager,
    )

    ticket_input = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((current_width // 2, current_height // 2 - 50, 200, 40)),
        manager=ui_manager
    )

    play_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width // 2 - 100, current_height // 2, 200, 50)),
        text="Play Lottery",
        manager=ui_manager,
        object_id="#play-button",
    )

    result_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((current_width // 2 - 200, current_height // 2 + 100, 400, 40)),
        text="Waiting for result...",
        manager=ui_manager,
    )

def proceed_with_lottery():
    global countdown_start, net_worth

    selected_lottery = lottery_dropdown.selected_option[0]
    num_tickets = int(ticket_input.get_text())
    total_cost = num_tickets * (STANDARD_LOTTERY_PRICE if selected_lottery == "Standard Lottery" else QUICK_LOTTERY_PRICE)
    
    net_worth -= total_cost
    countdown_start = time.time()  # Start countdown
    result_label.set_text(f"Playing {selected_lottery}... Waiting for result.")

def draw_lottery_screen(screen, events, ui_manager):
    global net_worth, back_button, lottery_dropdown, ticket_input, play_button, result_label, countdown_start
    draw_background(screen)

    balance_text = FONT.render(f"Balance: ${net_worth:.2f}", True, WHITE)
    screen.blit(balance_text, (current_width - balance_text.get_width(), 10))

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_button:
                update_net_worth(net_worth)
                return "home"
            elif event.ui_element == play_button:
                start_lottery(ui_manager)
            elif event.ui_element == standard_info_button:
                show_standard_popup(ui_manager)
            elif event.ui_element == quick_info_button:
                show_quick_popup(ui_manager)
        elif event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element == confirmation_popup:
                proceed_with_lottery()

        
    if countdown_start:  
        remaining_time = 30 - (time.time() - countdown_start)
        if remaining_time <= 0:
            resolve_lottery()
        else:
            result_label.set_text(f"Result in {int(remaining_time)} seconds...")

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return "lottery"

def show_standard_popup(ui_manager):
    global standard_popup
    standard_popup = pygame_gui.windows.UIMessageWindow(
        rect=pygame.Rect((current_width // 2 - 200, current_height // 2 - 200, 400, 400)),
        html_message="<b>Standard Lottery Info:</b><br>$15 per ticket.<br>10% chance to win $15.<br>5% chance to win $50.<br>1% chance for the $1,000 jackpot!<br>Max 25 tickets.",
        manager=ui_manager,
        window_title="Standard Lottery Info"
    )

def show_quick_popup(ui_manager):
    global quick_popup
    quick_popup = pygame_gui.windows.UIMessageWindow(
        rect=pygame.Rect((current_width // 2 - 200, current_height // 2 - 200, 400, 400)),
        html_message="<b>Quick Lottery Info:</b><br>$2 per ticket.<br>20% chance to win $3.<br>5% chance to win $8.<br>1% chance to win $100.<br>Max 50 tickets.",
        manager=ui_manager,
        window_title="Quick Lottery Info"
    )

def start_lottery(ui_manager):
    global countdown_start, net_worth
    global confirmation_popup
    
    selected_lottery = lottery_dropdown.selected_option[0]
    print(selected_lottery)
    try:
        num_tickets = int(ticket_input.get_text())
        if num_tickets <= 0:
            result_label.set_text("Enter a valid number of tickets!")
            return
        total_cost = num_tickets * (STANDARD_LOTTERY_PRICE if "Standard" in selected_lottery else QUICK_LOTTERY_PRICE)
        if ("Standard" in selected_lottery and num_tickets > 25) :
            result_label.set_text("You can only buy 25 tickets for Standard Lottery!")
            return
        if ("Quick" in selected_lottery and num_tickets > 50) :
            result_label.set_text("You can only buy 50 tickets for Quick Lottery!")
            return
        if total_cost > net_worth:
            result_label.set_text("Insufficient funds!")
            return
        
        confirmation_popup = pygame_gui.windows.UIConfirmationDialog(
            rect=pygame.Rect((current_width // 2 - 200, current_height // 2 - 100, 400, 200)),
            manager=ui_manager,
            action_long_desc=f"Buy {num_tickets} {selected_lottery} tickets for ${total_cost}?",
            window_title="Confirm Purchase",
            action_short_name="Confirm",
            blocking=True
        )

    except ValueError:
        result_label.set_text("Invalid ticket amount!")

def resolve_lottery():
    global countdown_start, net_worth
    countdown_start = None

    selected_lottery = lottery_dropdown.selected_option[0]
    num_tickets = int(ticket_input.get_text())

    # Total pool of 100 tickets
    tickets = ["Lose"] * 100

    # Standard Lottery winnings (balanced)
    if selected_lottery == "Standard Lottery":
        winners = random.sample(range(100), 16)  # Pick winners without replacement
        jackpot, mid_winners, small_winners = winners[0], winners[1:6], winners[6:16]

        tickets[jackpot] = 1000  # 1 winner: Jackpot ($1,000)
        for index in mid_winners:
            tickets[index] = 50  # 5 winners: Medium prize ($50 each)
        for index in small_winners:
            tickets[index] = 15  # 10 winners: Small prize ($15 each)

    # Quick Lottery winnings (lower payout)
    elif selected_lottery == "Quick Lottery":
        winners = random.sample(range(100), 26)  # Pick winners without replacement
        big_winners, mid_winners, small_winners = winners[:1], winners[1:6], winners[6:26]

        tickets[big_winners[0]] = 100  # 1 winner: Big prize ($100)
        for index in mid_winners:
            tickets[index] = 8  # 5 winners: Medium prize ($8 each)
        for index in small_winners:
            tickets[index] = 3  # 20 winners: Small prize ($3 each)

    # Select player's tickets **without replacement**
    selected_tickets = random.sample(tickets, num_tickets)
    winnings = sum(selected_tickets) if isinstance(selected_tickets[0], int) else 0
    lost_tickets = num_tickets - sum(1 for ticket in selected_tickets if isinstance(ticket, int))

    net_worth += winnings
    result_label.set_text(f"Lottery Over! {lost_tickets} tickets lost.\nTotal winnings: ${winnings}\nTotal Balance: ${net_worth:.2f}")