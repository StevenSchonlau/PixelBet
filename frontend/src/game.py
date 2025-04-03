import pygame
import pygame_gui
import datetime
import random
from constants import *
from login import get_user  # Replace 'login' with the actual module name
from achievements import check_achievements, set_ach_popup, get_ach_popup
BASE_URL = SERVER_URL
USER_ID = get_user()

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
net_worth = None
horses = []
horse_positions = {}
winning_horse = None
table_elements = {}
horse_bets = {}
pending_bets = {}
current_date_filter = "All"  # Options: "30s", "1m", "1h" or None for no filter
current_sort_order = "None"  # Options: "none", "desc" (largest first), "asc" (smallest first)
theme_btn_dict = {}
user = None

def fetch_net_worth():
    """Fetches the user's net worth from the backend API."""
    global USER_ID, BASE_URL
    BASE_URL = SERVER_URL
    USER_ID = get_user()
    try:
        response = requests.get(f"{BASE_URL}/game/get-net-worth/{get_user()}")
        if response.status_code == 200:
            data = response.json()
            print(f"🔄 Fetched net worth: ${data['net_worth']}")

            return(float(data.get('net_worth', 0.0)))
        else:
            print(f"⚠️ Failed to fetch net worth: {response.json()}")
            return 0
    except Exception as e:
        print(f"❌ Error fetching net worth: {str(e)}")
        return 0

def draw_game_background(surface):
    """Draws background as a gradient"""
    global user
    gradient_presets = {
        'default': (PRIMARY, SECONDARY),  # pastel red, less pink
        'red': ((255, 120, 100), (240, 80, 60)),  # pastel red, less pink
        'green': ((102, 255, 178), (0, 102, 51)),   # mint to forest
        'purple': ((204, 153, 255), (102, 0, 204)), # lavender to royal
        'gold': ((255, 215, 0), (184, 134, 11)),    # gold to goldenrod
    }

    if user:
        active_background_index = user['active_theme']
        owns_themes = user['owns_themes']
        gradient_key = owns_themes[active_background_index]
    else:
        gradient_key = 'default'

    top_color, bottom_color = gradient_presets.get(
        gradient_key, ((186, 48, 48), (223, 27, 27))
    )

    width, height = surface.get_size()
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

def update_net_worth(new_balance):
    """Updates the user's net worth on the backend API."""
    global show_achievement_popup, new_achievements
    BASE_URL = SERVER_URL
    USER_ID = get_user()
    if not USER_ID:
        print("❌ No user logged in!")
        return

    try:
        response = requests.post(
            f"{BASE_URL}/game/update-net-worth/{USER_ID}",
            json={"net_worth": new_balance}
        )
        if response.status_code == 200:
            print(f"✅ Net worth updated successfully: ${new_balance}")
            '''add achievment check'''
            new_achievements = check_achievements(USER_ID)
            if new_achievements:
                print("set popup to true")
                set_ach_popup(True)
            else:
                set_ach_popup(False)
                print("no new achievement")
        else:
            print(f"⚠️ Failed to update net worth: {response.json()}")
    except Exception as e:
        print(f"❌ Error updating net worth: {str(e)}")

def fetch_bet_history(user_id):
    """Fetches the user's bet history from the backend API and updates the global bet_history list."""
    global BASE_URL, bet_history
    try:
        response = requests.get(f"{BASE_URL}/game/get-bet-history/{user_id}")
        if response.status_code == 200:
            data = response.json()
            print("🔄 Fetched bet history:", data)
            # Assume the response returns a dictionary with a "bet_history" key.
            bet_history = data.get("bet_history", [])
            return bet_history
        else:
            print("⚠️ Failed to fetch bet history:", response.status_code, response.json())
            bet_history = []
            return bet_history
    except Exception as e:
        print("❌ Error fetching bet history:", str(e))
        bet_history = []
        return bet_history

def update_bet_history(bets_placed):
    """Sends the current bets_placed list to the backend and then leaves it unchanged (it will be cleared after a successful update)."""
    global BASE_URL, USER_ID
    if not bets_placed:
        print("No bets to update.")
        return

    try:
        payload = {"bets": bets_placed}  # send current bets
        response = requests.post(f"{BASE_URL}/game/update-bet-history/{USER_ID}", json=payload)
        if response.status_code == 200:
            print("✅ Bet history updated successfully.")
        else:
            print("⚠️ Failed to update bet history:", response.status_code, response.json())
    except Exception as e:
        print("❌ Error updating bet history:", str(e))

def filter_and_sort_bets(bets, date_filter, sort_order):
    from datetime import datetime, timedelta
    now = datetime.now()
    filtered_bets = bets

    # Date filtering based on a time delta
    if date_filter:
        if date_filter == "30s":
            delta = timedelta(seconds=30)
        elif date_filter == "1m":
            delta = timedelta(minutes=1)
        elif date_filter == "1h":
            delta = timedelta(hours=1)
        else:
            delta = None

        if delta is not None:
            filtered_bets = [
                bet for bet in bets
                if datetime.strptime(bet["date"], "%Y-%m-%d %H:%M:%S") >= (now - delta)
            ]

    # Sorting by wager amount
    if sort_order == "Largest":
        # Largest amounts on top
        filtered_bets.sort(key=lambda bet: bet["amount"], reverse=True)
    elif sort_order == "Smallest":
        # Smallest amounts on top
        filtered_bets.sort(key=lambda bet: bet["amount"])
    # If sort_order is "none", leave the order as is.

    return filtered_bets

def clear_table_elements():
    """Removes all UI elements related to the betting table or history."""
    for element in table_elements.values():
        element.kill()

def draw_bet_history(ui_manager):
    """Displays the bet history table."""
    global bet_history, table_elements

    date_options = ["All", "30s", "1m", "1h"]
    sort_options = ["None", "Largest", "Smallest"]

    dropdown_y = SCREEN_HEIGHT - 300  # adjust as needed

    # Create drop-down for date filter.
    dropdown_date = pygame_gui.elements.UIDropDownMenu(
        options_list=date_options,
        starting_option=current_date_filter,
        relative_rect=pygame.Rect((10, dropdown_y, 150, 30)),
        manager=ui_manager,
        container=None,
        object_id="#date_dropdown"
    )
    table_elements["date_dropdown"] = dropdown_date

    # Create drop-down for sort order.
    dropdown_sort = pygame_gui.elements.UIDropDownMenu(
        options_list=sort_options,
        starting_option=current_sort_order,
        relative_rect=pygame.Rect((170, dropdown_y, 150, 30)),
        manager=ui_manager,
        container=None,
        object_id="#sort_dropdown"
    )
    table_elements["sort_dropdown"] = dropdown_sort

    display_bets = filter_and_sort_bets(bet_history, current_date_filter, current_sort_order)

    header_height = 40
    container_total_height = 180  # total height for the bet history section
    container_height = container_total_height - header_height

    # Y-position for the headers (absolute on the screen)
    header_y = SCREEN_HEIGHT - 220

    # Create and store header elements in table_elements.
    table_elements["header_date"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((100, header_y, 200, header_height)),
        text="Date",
        manager=ui_manager,
        object_id="#label"
    )
    table_elements["header_horse"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((300, header_y, 150, header_height)),
        text="Horse",
        manager=ui_manager,
        object_id="#label"
    )
    table_elements["header_odds"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((450, header_y, 75, header_height)),
        text="Odds",
        manager=ui_manager,
        object_id="#label"
    )
    table_elements["header_amount"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((525, header_y, 100, header_height)),
        text="Amount",
        manager=ui_manager,
        object_id="#label"
    )
    table_elements["header_outcome"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((625, header_y, 75, header_height)),
        text="Outcome",
        manager=ui_manager,
        object_id="#label"
    )

    # Create a scrolling container for just the bet rows.
    scroll_container_rect = pygame.Rect(0, header_y + header_height, 700, container_height)
    row_height = 40
    content_height = row_height * len(bet_history)
    scroll_container = pygame_gui.elements.UIScrollingContainer(
        relative_rect=scroll_container_rect,
        manager=ui_manager,
        starting_height=content_height,
        allow_scroll_x=False,
        container=None,
        object_id="#bet_history_scroll_container"
    )
    table_elements["bet_history_container"] = scroll_container

    # Add bet rows inside the scrolling container.
    y_offset = 0  # container-relative coordinates
    for bet in display_bets:
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((100, y_offset, 200, row_height)),
            text=bet["date"],
            manager=ui_manager,
            container=scroll_container
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((300, y_offset, 150, row_height)),
            text=bet["horse"],
            manager=ui_manager,
            container=scroll_container
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((450, y_offset, 75, row_height)),
            text=f"{bet['odds']}x",
            manager=ui_manager,
            container=scroll_container
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((525, y_offset, 100, row_height)),
            text=f"${bet['amount']}",
            manager=ui_manager,
            container=scroll_container
        )
        outcome = bet.get("outcome", "undecided")
        if outcome == "win":
            outcome_text = "W"
        elif outcome == "loss":
            outcome_text = "L"
        else:
            outcome_text = "~"
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((625, y_offset, 75, row_height)),
            text=outcome_text,
            manager=ui_manager,
            container=scroll_container
        )
        y_offset += row_height

    # Update the scrollable area dimensions so the container knows the full content height.
    scroll_container.set_scrollable_area_dimensions(
        (scroll_container.relative_rect.width, y_offset)
    )


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
    global bet_history, bets_placed, net_worth
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
        if bet_difference > net_worth:
            return "Error: Insufficient funds!"

        net_worth -= bet_difference  # Deduct or refund balance difference
        existing_bet["amount"] = bet_amount  # Update bet amount

        # **Update bet history to reflect changes**
        for bet in bets_placed:
            if bet["horse"] == horse_name:
                bet["amount"] = bet_amount  # Update history record
                bet["odds"] = horse_odds
                bet["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return "Bet updated successfully!"
    else:
        # **New bet: Ensure enough funds**
        if bet_amount > net_worth:
            return "Error: Insufficient funds!"

        net_worth -= bet_amount # Deduct balance

        # Store new bet
        bet_details = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "horse": horse_name,
            "odds": horse_odds,
            "amount": bet_amount,
            "outcome": "undecided"
        }
        print(bet_details)

        # Add to active bets and bet history
        bets_placed[:] = [bet for bet in bets_placed if bet["horse"] != horse_name]
        bets_placed.append(bet_details)  # Add updated/new bet

        # **Update bet history in the same way**
        bet_history.append(bet_details)  

        print(f"✅ Bet placed: {bet_details}")
        return "Bet placed successfully!"

def initialize_game(ui_manager):
    """Initializes the game screen UI elements for horse derby betting."""
    global back_button, history_toggle_button, bet_buttons, bet_amount_entry
    global message_label, race_timer_label, race_start_time, horses
    global horse_positions, racing_phase, winning_horse, showing_history, horse_bets, pending_bets, USER_ID
    global net_worth, bet_history, user
    user = get_profile()
    net_worth = fetch_net_worth()
    bet_history = fetch_bet_history(USER_ID)
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
        relative_rect=pygame.Rect((0, SCREEN_HEIGHT - 40, 200, 40)),
        text="View Bet History",
        manager=ui_manager,
        object_id="toggle-button"
    )
    draw_betting_table(ui_manager)
    # Start the race timer
    race_start_time = datetime.datetime.now()

def draw_game_screen(screen, events, ui_manager, selected_game):
    """Handles the horse derby game betting screen with a table and race visualization."""
    global bet_history, race_start_time, bets_placed, message_label, winner_announced, net_worth
    global horses, horse_positions, racing_phase, winning_horse, showing_history, horse_bets, pending_bets, current_date_filter, current_sort_order
    draw_game_background(screen)

    # Show game and balance info
    game_text = FONT.render(f"Bet on: {selected_game}", True, WHITE)
    balance_text = FONT.render(f"Balance: ${net_worth:.2f}", True, WHITE)
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
                bet["outcome"] = "win"
                winnings = bet["amount"] * bet["odds"]
                net_worth += winnings
                print(f"🎉 Winner! Won ${winnings} on {winning_horse}")
                message_label.set_text(f"Winner! Won ${winnings} on {winning_horse}")
            else:
                bet["outcome"] = "loss"


        
        # Set flag to prevent rerunning
        winner_announced = True
    if time_elapsed >= 30:
        # Reset for next race
        race_start_time = datetime.datetime.now()
        racing_phase = False  # Return to betting phase
        winner_announced = False
        update_net_worth(net_worth)
        update_bet_history(bets_placed)
        bets_placed.clear()
        initialize_game(ui_manager)  # Reset horses
    if racing_phase == False:
        race_timer_label.set_text(f"Next Race: {time_remaining}s")

        note = FONT.render(f"Not available until race starts", True, WHITE)
        text_rect = note.get_rect(center=(SCREEN_WIDTH // 2, 225))  # Center in the white box
    
        # Render the text inside the box
        screen.blit(note, text_rect)
    else:
        race_timer_label.set_text(f"Race beginned: {time_elapsed - 20}s")

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

                # Get user input
                bet_amount = input_field.get_text()

                # ✅ Allow empty input (reset bet)
                if bet_amount == "":
                    pending_bets[horse_name] = 0.0
                    continue

                # ✅ Check if input is a valid number (integer or float)
                try:
                    float_bet_amount = float(bet_amount)  # Convert input to float
                except ValueError:
                    input_field.set_text(str(pending_bets[horse_name]))  # Reset input
                    continue  # Skip invalid input

                # ✅ Ensure bet does not exceed available balance
                max_possible_bet = net_worth + sum(bet['amount'] for bet in bets_placed)
                if float_bet_amount > max_possible_bet:
                    input_field.set_text(str(pending_bets[horse_name]))  # Reset input
                    message_label.set_text("Error: Insufficient funds!")
                else:
                    # ✅ Only update input if necessary to prevent cursor jumping
                    if str(pending_bets[horse_name]) != bet_amount:
                        pending_bets[horse_name] = float_bet_amount  # Store the valid float bet


        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            print("drop down changed")
            if event.ui_element == table_elements.get("date_dropdown"):
                selected = event.text  # e.g. "Past 30s", "Past 1m", "Past 1h", or "All"
                print(selected)
                current_date_filter = selected # "30s", "1m", or "1h"
                clear_table_elements()
                draw_bet_history(ui_manager)  # Redraw history with the new filter
            elif event.ui_element == table_elements.get("sort_dropdown"):
                selected = event.text  # "None", "Largest amounts", or "Smallest amounts"
                print(selected)
                current_sort_order = selected
                clear_table_elements()
                draw_bet_history(ui_manager)


        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_button:
                print("Returning to home screen")
                update_net_worth(net_worth)
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
                        max_possible_bet = net_worth + sum(bet['amount'] for bet in bets_placed)
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
