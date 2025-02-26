import pygame
import pygame_gui
import datetime
import random
from constants import *

# Global variables
back_button = None
history_toggle_button = None
bet_buttons = {}
bet_amount_entry = None
message_label = None
race_timer_label = None
race_start_time = None
racing_phase = False
showing_history = False  
winner_announced = False
bets_placed = []
bet_history = []
user_balance = 1000
horses = []
horse_positions = {}
winning_horse = None
table_elements = {}
horse_bets = {}
pending_bets = {}  


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
    global bet_buttons, table_elements, pending_bets

    y_offset = SCREEN_HEIGHT - 180

    # **Table Headers**
    table_elements["header_name"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((100, SCREEN_HEIGHT - 220, 200, 30)),  # Wider name column
        text="Horse Name",
        manager=ui_manager,
        object_id="#label"
    )
    table_elements["header_color"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((300, SCREEN_HEIGHT - 220, 100, 30)),  # Increased column width
        text="Color",
        manager=ui_manager,
        object_id="#label"
    )
    table_elements["header_odds"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((400, SCREEN_HEIGHT - 220, 100, 30)),  # More space for odds
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
        horse_name = horse["name"]

        table_elements[f"horse_name_{i}"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((100, y_offset, 200, 30)),  # Wider name column
            text=horse["name"],
            manager=ui_manager
        )
        table_elements[f"horse_color_{i}"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((300, y_offset, 100, 30)),
            text=horse["color"],
            manager=ui_manager
        )
        table_elements[f"horse_odds_{i}"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((400, y_offset, 100, 30)),
            text=f"{horse['odds']}x",
            manager=ui_manager
        )
        # **Bet Controls**
        table_elements[f"bet_decrement_{i}"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((500, y_offset, 30, 30)),  # - Button
            text="-",
            manager=ui_manager
        )
        table_elements[f"bet_input_{i}"] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((530, y_offset, 70, 30)),  # Bet amount input
            manager=ui_manager
        )
        table_elements[f"bet_input_{i}"].set_text(str(pending_bets[horse_name]))
        table_elements[f"bet_increment_{i}"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((600, y_offset, 30, 30)),  # + Button
            text="+",
            manager=ui_manager
        )
        table_elements[f"bet_confirm_{i}"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((630, y_offset, 70, 30)),  # Confirm Bet
            text="Confirm",
            manager=ui_manager,
            object_id="confirm-button"
        )
        y_offset += 30  # Space between rows

def place_bet(horse_name, bet_amount, horse_odds):
    """Stores the bet details and deducts from user balance for new bets only."""
    global user_balance, bet_history, bets_placed
    print(bet_amount)
    if bet_amount <= 0:
        return "Error: Bet amount must be greater than 0!"

    # Check if a bet already exists on this horse
    existing_bet = next((bet for bet in bets_placed if bet["horse"] == horse_name), None)
    print("existing_bet:")
    print(existing_bet)

    if existing_bet:
        # **Modify existing bet amount**
        bet_difference = bet_amount - existing_bet["amount"]
        print("bet_difference:")
        print(bet_difference)

        # Ensure the user has enough funds if increasing bet
        if bet_difference > user_balance:
            return "Error: Insufficient funds!"

        user_balance -= bet_difference  # Deduct or refund balance difference
        existing_bet["amount"] = bet_amount  # Update bet amount

        # **Update bet history to reflect changes**
        for bet in bet_history:
            if bet["horse"] == horse_name:
                bet["amount"] = bet_amount  # Update history record
                bet["odds"] = horse_odds
                bet["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return "Bet updated successfully!"
    else:
        # **New bet: Ensure enough funds**
        if bet_amount > user_balance:
            return "Error: Insufficient funds!"

        user_balance -= bet_amount  # Deduct balance

        # Store new bet
        bet_details = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "horse": horse_name,
            "odds": horse_odds,
            "amount": bet_amount
        }

        # Add to active bets and bet history
        bets_placed[:] = [bet for bet in bets_placed if bet["horse"] != horse_name]
        bets_placed.append(bet_details)  # Add updated/new bet

        # **Update bet history in the same way**
        bet_history[:] = [bet for bet in bet_history if bet["horse"] != horse_name]
        bet_history.append(bet_details)  

        print(f"✅ Bet placed: {bet_details}")
        return "Bet placed successfully!"
                              
def initialize_game(ui_manager):
    """Initializes the game screen UI elements for horse derby betting."""
    global back_button, history_toggle_button, bet_buttons, bet_amount_entry
    global message_label, race_timer_label, race_start_time, horses
    global horse_positions, racing_phase, winning_horse, showing_history, horse_bets, pending_bets
    # Clear old UI elements
    ui_manager.clear_and_reset()

    # List of horses with colors and odds
    horses = [
        {"name": "Lightning Bolt", "color": "Yellow", "odds": 2.0},
        {"name": "Thunder Hoof", "color": "Blue", "odds": 3.5},
        {"name": "Midnight Runner", "color": "Red", "odds": 5.0},
        {"name": "Golden Mane", "color": "Gold", "odds": 1.8},
    ]

    horse_bets = {horse["name"]: 0 for horse in horses}

    horse_names = [horse["name"] for horse in horses]
    pending_bets = {horse["name"]: 0 for horse in horses}
    horse_weights = [1 / horse["odds"] for horse in horses]  # Lower odds → higher chance of winning
    winning_horse = random.choices(horse_names, weights=horse_weights, k=1)[0]
    print(f"🏆 Predetermined Winner: {winning_horse}")

    # Reset horse positions
    horse_positions = {horse["name"]: 120 for horse in horses}

    # Reset betting phase
    racing_phase = False

    # Create "Back" button to return to home
    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 0, 100, 40)),  # Position: Top Right
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

    #message label
    message_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 150, 260, 300, 30)),
        text="",
        manager=ui_manager,
        object_id="#label"
    )

    history_toggle_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, SCREEN_HEIGHT - 40, 180, 40)),
        text="View Bet History",
        manager=ui_manager,
        object_id="toggle-button"
    )
    draw_betting_table(ui_manager)
    # Start the race timer
    race_start_time = datetime.datetime.now()

def draw_game_screen(screen, events, ui_manager, selected_game):
    """Handles the horse derby game betting screen with a table and race visualization."""
    global user_balance, bet_history, race_start_time, bets_placed, message_label, winner_announced
    global horses, horse_positions, racing_phase, winning_horse, showing_history, horse_bets, pending_bets
    draw_background(screen)

    # Show game and balance info
    game_text = FONT.render(f"Bet on: {selected_game}", True, WHITE)
    balance_text = FONT.render(f"Balance: ${user_balance:.2f}", True, WHITE)
    screen.blit(game_text, (SCREEN_WIDTH // 2 - game_text.get_width() // 2, 50))
    screen.blit(balance_text, (500, 10))

    # Time logic
    now = datetime.datetime.now()
    time_elapsed = (now - race_start_time).seconds
    time_remaining = max(0, 30 - time_elapsed)
    

    # Update race phase logic
    if time_elapsed < 20:  # Betting Phase (0-19s)
        time_remaining = 20 - time_elapsed
        race_timer_label.set_text(f"Next Race: {time_remaining}s")
        
    if time_elapsed >= 20 and not racing_phase:
        print("🏇 Race Starting!")
        time_remaining = 30
        racing_phase = True  # Enter racing phase
        #winning_horse = random.choice(horses)["name"]  # Select winner

    if time_elapsed == 25 and not winner_announced:
        print(f"🏆 Winning Horse: {winning_horse}")
        message_label.set_text(f"Winning Horse: {winning_horse}")

        # Process bets
        for bet in bets_placed:
            if bet["horse"] == winning_horse:
                winnings = bet["amount"] * bet["odds"]
                user_balance += winnings
                print(f"🎉 Winner! Won ${winnings} on {winning_horse}")
                message_label.set_text(f"Winner! Won ${winnings} on {winning_horse}")

        bets_placed.clear()  # Clear bets only after processing

        # Set flag to prevent rerunning
        winner_announced = True
    if time_elapsed >= 30:
        # Reset for next race
        race_start_time = datetime.datetime.now()
        racing_phase = False  # Return to betting phase
        winner_announced = False
        initialize_game(ui_manager)  # Reset horses
    if racing_phase == False:
        race_timer_label.set_text(f"Next Race: {time_remaining}s")
    else:
        race_timer_label.set_text(f"Next Derby: {time_remaining}s")

    # Draw race box
    pygame.draw.rect(screen, WHITE, (50, 100, SCREEN_WIDTH - 100, 150), 2)  # White border
    y_offset = 120

    # Handle race animation inside the box
    for horse in horses:
        horse_name = horse["name"]
        horse_odds = horse["odds"]
        if racing_phase:
            if horse_name == winning_horse:
                speed = random.randint(1, 10) / 2  # Fastest movement for winner
            else:
                speed = random.randint(1, 10 - int(horse_odds)) / 2 # Higher odds → slower movement

            horse_positions[horse_name] += speed
            if horse_positions[horse_name] >= SCREEN_WIDTH - 150:
                horse_positions[horse_name] = SCREEN_WIDTH - 150
        pygame.draw.rect(screen, pygame.Color(horse["color"]), (horse_positions[horse_name], y_offset, 16, 16))
        y_offset += 20

    for event in events:
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                for i, horse in enumerate(horses):
                    horse_name = horse["name"]
                    input_field = table_elements[f"bet_input_{i}"]

                    # Ensure the text input is numeric
                    bet_amount = input_field.get_text()

                    if bet_amount == "":
                        pending_bets[horse_name] = 0
                    elif bet_amount.isdigit():
                        bet_amount = int(bet_amount)

                        # Ensure bet does not exceed balance + existing bet
                        max_possible_bet = user_balance + horse_bets.get(horse_name, 0)
                        if bet_amount > max_possible_bet:
                            input_field.set_text(str(pending_bets[horse_name]))  # Reset input
                            message_label.set_text("Error: Insufficient funds!")
                        else:
                            pending_bets[horse_name] = bet_amount  # Store in pending bets
                            input_field.set_text(str(pending_bets[horse_name]))
                    else:
                        input_field.set_text(str(pending_bets[horse_name]))
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_button:
                print("Returning to home screen")
                return None  # Go back to home
            
            if event.ui_element == history_toggle_button:
                showing_history = not showing_history
                clear_table_elements()
                if showing_history:
                    history_toggle_button.set_text("View Betting Table")
                    draw_bet_history(ui_manager)
                else:
                    history_toggle_button.set_text("View Bet History")
                    draw_betting_table(ui_manager)

            for i, horse in enumerate(horses):
                horse_name = horse["name"]
                horse_odds = horse["odds"]
                if event.ui_element == table_elements[f"bet_decrement_{i}"]:
                    if pending_bets[horse_name] > 0 and not racing_phase:
                        pending_bets[horse_name] -= 1
                        table_elements[f"bet_input_{i}"].set_text(str(pending_bets[horse_name]))

                if event.ui_element == table_elements[f"bet_increment_{i}"]:
                    if not racing_phase:
                        max_possible_bet = user_balance + horse_bets.get(horse_name, 0)
                        if pending_bets[horse_name] < max_possible_bet:
                            pending_bets[horse_name] += 1
                            table_elements[f"bet_input_{i}"].set_text(str(pending_bets[horse_name]))
                        else:
                            message_label.set_text("Error: Insufficient funds!")

                if event.ui_element == table_elements[f"bet_confirm_{i}"]:
                    if racing_phase:
                        message_label.set_text("Betting is closed!")
                    else:
                        bet_amount = pending_bets[horse_name]
                        message_label.set_text(place_bet(horse_name, bet_amount, horse_odds))

            
            
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return selected_game