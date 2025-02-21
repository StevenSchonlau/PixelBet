import pygame
import pygame_gui
import datetime
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, FONT

# Global variables
back_button = None
history_toggle_button = None
bet_buttons = {}
bet_amount_entry = None
error_label = None
race_timer_label = None
race_start_time = None
racing_phase = False
showing_history = False  
bets_placed = []
bet_history = []
user_balance = 1000
horses = []
horse_positions = {}
winning_horse = None
table_elements = {}

def clear_table_elements():
    """Removes all UI elements related to the betting table or history."""
    for element in table_elements.values():
        element.kill()

def draw_bet_history(ui_manager):
    """Displays the bet history table."""
    global bet_history, table_elements

    y_offset = SCREEN_HEIGHT - 180

    # Table Headers
    table_elements["header_date"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((50, y_offset - 30, 200, 30)),
        text="Date",
        manager=ui_manager,
        object_id="#label"
    )
    table_elements["header_horse"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((260, y_offset - 30, 200, 30)),
        text="Horse",
        manager=ui_manager,
        object_id="#label"
    )
    table_elements["header_odds"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((470, y_offset - 30, 100, 30)),
        text="Odds",
        manager=ui_manager,
        object_id="#label"
    )
    table_elements["header_amount"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((580, y_offset - 30, 150, 30)),
        text="Amount",
        manager=ui_manager,
        object_id="#label"
    )

    # Show last 3 bets
    for i, bet in enumerate(bet_history[-3:]):  # Display the last 3 bets
        table_elements[f"bet_date_{i}"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((50, y_offset, 200, 30)),
            text=bet["date"],
            manager=ui_manager
        )
        table_elements[f"bet_horse_{i}"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((260, y_offset, 200, 30)),
            text=bet["horse"],
            manager=ui_manager
        )
        table_elements[f"bet_odds_{i}"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((470, y_offset, 100, 30)),
            text=f"{bet['odds']}x",
            manager=ui_manager
        )
        table_elements[f"bet_amount_{i}"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((580, y_offset, 150, 30)),
            text=f"${bet['amount']}",
            manager=ui_manager
        )

        y_offset += 40  # Space between rows


def draw_betting_table(ui_manager):
    """Displays the betting table with available horses and tracks elements for clearing."""
    global bet_buttons, table_elements

    y_offset = SCREEN_HEIGHT - 180

    # **Table Headers**
    table_elements["header_name"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((100, SCREEN_HEIGHT - 220, 200, 30)),  # Wider name column
        text="Horse Name",
        manager=ui_manager,
        object_id="#label"
    )
    table_elements["header_color"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((300, SCREEN_HEIGHT - 220, 50, 30)),  # Increased column width
        text="Color",
        manager=ui_manager,
        object_id="#label"
    )
    table_elements["header_odds"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((400, SCREEN_HEIGHT - 220, 50, 30)),  # More space for odds
        text="Odds",
        manager=ui_manager,
        object_id="#label"
    )
    table_elements["header_bet"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((500, SCREEN_HEIGHT - 220, 200, 30)),  # Wider column for betting
        text="Bet",
        manager=ui_manager,
        object_id="#label"
    )

    # **Generate Full-Width Table Rows**
    for i, horse in enumerate(horses):
        table_elements[f"horse_name_{i}"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((100, y_offset, 200, 30)),  # Wider name column
            text=horse["name"],
            manager=ui_manager
        )
        table_elements[f"horse_color_{i}"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((300, y_offset, 50, 30)),
            text=horse["color"],
            manager=ui_manager
        )
        table_elements[f"horse_odds_{i}"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((400, y_offset, 50, 30)),
            text=f"{horse['odds']}x",
            manager=ui_manager
        )
        table_elements[f"bet_button_{i}"] = bet_buttons[horse["name"]] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((500, y_offset, 200, 30)),  # Wider bet button column
            text="Bet",
            manager=ui_manager
        )
        y_offset += 30  # Space between rows



def place_bet(horse_name, bet_amount, horse_odds):
    """Stores the bet details and deducts from user balance."""
    global user_balance, bet_history, bets_placed

    # Check if user has enough balance
    if bet_amount > user_balance:
        print("❌ Insufficient balance!")
        return "Insufficient funds"

    # Deduct balance and store bet
    user_balance -= bet_amount
    bet_details = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "horse": horse_name,
        "odds": horse_odds,
        "amount": bet_amount
    }
    
    # **Add to bets placed for race processing**
    bets_placed.append(bet_details)
    bet_history.append(bet_details)

    print(f"✅ Bet placed: {bet_details}")
    return "Bet placed successfully!"

                              
def initialize_game(ui_manager):
    """Initializes the game screen UI elements for horse derby betting."""
    global back_button, history_toggle_button, bet_buttons, bet_amount_entry
    global error_label, race_timer_label, race_start_time, horses
    global horse_positions, racing_phase, winning_horse, showing_history
    # Clear old UI elements
    ui_manager.clear_and_reset()

    # List of horses with colors and odds
    horses = [
        {"name": "Lightning Bolt", "color": "Yellow", "odds": 2.0},
        {"name": "Thunder Hoof", "color": "Blue", "odds": 3.5},
        {"name": "Midnight Runner", "color": "Red", "odds": 5.0},
        {"name": "Golden Mane", "color": "Gold", "odds": 1.8},
    ]

    horse_names = [horse["name"] for horse in horses]
    horse_weights = [1 / horse["odds"] for horse in horses]  # Lower odds → higher chance of winning
    winning_horse = random.choices(horse_names, weights=horse_weights, k=1)[0]
    print(f"🏆 Predetermined Winner: {winning_horse}")

    # Reset horse positions
    horse_positions = {horse["name"]: 120 for horse in horses}

    # Reset betting phase
    racing_phase = False

    # Create "Back" button to return to home
    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH - 150, 20, 100, 40)),  # Position: Top Right
        text="Back",
        manager=ui_manager,
        object_id="#back_button"
    )

    # Timer label to show countdown to next race
    race_timer_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 20, 200, 30)),
        text="Next Race: 60s",
        manager=ui_manager,
        object_id="#timer_label"
    )

    # Text entry for bet amount
    bet_amount_entry = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 200, 200, 30)),
        manager=ui_manager
    )

    # Error message label
    error_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 150, 240, 300, 30)),
        text="",
        manager=ui_manager,
        object_id="#label"
    )

    history_toggle_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250, 180, 40)),
        text="View Bet History",
        manager=ui_manager,
        object_id="#toggle_button"
    )
    draw_betting_table(ui_manager)
    # Start the race timer
    race_start_time = datetime.datetime.now()




def draw_game_screen(screen, events, ui_manager, selected_game):
    """Handles the horse derby game betting screen with a table and race visualization."""
    global user_balance, bet_history, race_start_time, bets_placed
    global horses, horse_positions, racing_phase, winning_horse, showing_history
    screen.fill(BLACK)

    # Show game and balance info
    game_text = FONT.render(f"Bet on: {selected_game}", True, WHITE)
    balance_text = FONT.render(f"Balance: ${user_balance}", True, WHITE)
    screen.blit(game_text, (SCREEN_WIDTH // 2 - game_text.get_width() // 2, 50))
    screen.blit(balance_text, (50, 20))

    # Time logic
    now = datetime.datetime.now()
    time_elapsed = (now - race_start_time).seconds
    time_remaining = max(0, 60 - time_elapsed)

    # Update race phase logic
    if time_elapsed >= 20 and not racing_phase:
        print("🏇 Race Starting!")
        racing_phase = True  # Enter racing phase
        #winning_horse = random.choice(horses)["name"]  # Select winner

    if time_elapsed >= 60:
        print(f"🏆 Winning Horse: {winning_horse}")

        # Process bets
        for bet in bets_placed:
            if bet["horse"] == winning_horse:
                winnings = bet["amount"] * bet["odds"]
                user_balance += winnings
                print(f"🎉 Winner! Won ${winnings} on {winning_horse}")

        # Reset for next race
        bets_placed.clear()
        race_start_time = datetime.datetime.now()
        racing_phase = False  # Return to betting phase
        initialize_game(ui_manager)  # Reset horses

    race_timer_label.set_text(f"Next Race: {time_remaining}s")

    # Draw race box
    pygame.draw.rect(screen, WHITE, (50, 100, SCREEN_WIDTH - 100, 150), 2)  # White border
    y_offset = 120

    # Handle race animation inside the box
    for horse in horses:
        horse_name = horse["name"]
        horse_odds = horse["odds"]
        if racing_phase:
            if horse_name == winning_horse:
                speed = random.randint(1, 10)  # Fastest movement for winner
            else:
                speed = random.randint(1, 10 - int(horse_odds))  # Higher odds → slower movement

            horse_positions[horse_name] += speed
            if horse_positions[horse_name] >= SCREEN_WIDTH - 150:
                horse_positions[horse_name] = SCREEN_WIDTH - 150
        pygame.draw.rect(screen, pygame.Color(horse["color"]), (horse_positions[horse_name], y_offset, 16, 16))
        y_offset += 20

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_button:
                print("Returning to home screen")
                return None  # Go back to home
        
            if event.ui_element == history_toggle_button:
                showing_history = not showing_history
                if showing_history:
                    history_toggle_button.set_text("View Betting Table")
                else:
                    history_toggle_button.set_text("View Bet History")

            for horse_name, button in bet_buttons.items():
                if event.ui_element == button:
                    bet_amount = bet_amount_entry.get_text()

                    if not bet_amount.isdigit():
                        error_label.set_text("Error: Enter a valid amount!")
                    else:
                        bet_amount = int(bet_amount)
                        horse_odds = next(h["odds"] for h in horses if h["name"] == horse_name)

                        result = place_bet(horse_name, bet_amount, horse_odds)
                        error_label.set_text(result)
                if event.ui_element == history_toggle_button:
                    showing_history = not showing_history
                    clear_table_elements()
                    if showing_history:
                        history_toggle_button.set_text("View Betting Table")
                        draw_bet_history(ui_manager)
                    else:
                        history_toggle_button.set_text("View Bet History")
                        draw_betting_table(ui_manager)
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return selected_game