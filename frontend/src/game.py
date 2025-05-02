import math
import pygame
import random
import datetime
import pygame_gui
from constants import *
from achievements import check_achievements, set_ach_popup, get_ach_popup
from login import get_user  # Replace 'login' with the actual module name
from settings import is_winning_sound_enabled, is_losing_sound_enabled, is_money_sound_enabled
from notifications import get_user_notification_preferences_results, get_user_networth_min_max, send_networth_email

BASE_URL = SERVER_URL
USER_ID = get_user()
SPONSOR_TIERS = {
    "Bronze": {"cost": 100, "boost": 0.05},
    "Silver": {"cost": 300, "boost": 0.10},
    "Gold": {"cost": 500, "boost": 0.20},
}
TIER_ORDER = {"Bronze": 1, "Silver": 2, "Gold": 3}

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
betting_limit = None
pygame.mixer.init()
winning_sound = pygame.mixer.Sound("./frontend/assets/effects/winning.wav")
winning_sound.set_volume(0.2)
losing_sound = pygame.mixer.Sound("./frontend/assets/effects/losing.wav")
losing_sound.set_volume(0.2)
money_sound = pygame.mixer.Sound("./frontend/assets/effects/money.wav")
money_sound.set_volume(0.2)
play_sound_effects = True
result_notifications = False
current_width, current_height = 0, 0
sponsor_panel = None
sponsor_close_button = None
sponsor_boost = None
sponsor_buttons = {}
sponsor_selection = {}
chance_labels = {}
owned_tiers = {}
streak = 0
max_streak = 0
match_bet_global = None
DEFAULT_BG   = pygame.Color('#CCCCCC')
OWNED_BG  = pygame.Color('#88FF88')
SELECTED_BG   = pygame.Color('#00AA00')

def fetch_net_worth():
    """Fetches the user's net worth from the backend API."""
    global USER_ID, BASE_URL, streak, max_streak
    BASE_URL = SERVER_URL
    USER_ID = get_user()

    #check mining and update based on that

    try:
        response = requests.get(f"{BASE_URL}/game/get-net-worth/{get_user()}")
        if response.status_code == 200:
            data = response.json()
            streak = data.get('streak', 0)
            max_streak = data.get('max_streak', 0)
            return(float(data.get('net_worth', 0.0)))
        else:
            return 0
    except Exception as e:
        return 0

def send_bet_email(win, amount, wh, lh=""):
    """Sends email with win/loss (T/F) and amount"""
    global USER_ID, BASE_URL
    BASE_URL = SERVER_URL
    USER_ID = get_user()
    try:
        data = {
            "win": win,
            "amount": amount,
            "id": USER_ID,
            "wh": wh,
            "lh": lh
        }
        requests.post(f"{BASE_URL}/send-bet-email", json=data)
    except Exception as e:
        return 0

def load_sponsorships():
    """GET /sponsorship/get-sponsorships"""
    resp = requests.get(
        f"{SERVER_URL}/sponsorship/get-sponsorships",
        json={ 'id': USER_ID }
    )
    data = resp.json()
    if resp.status_code == 200 and data['message']=='success':
        return data['sponsorships'], data['net_worth']
    # fallback
    return {}, globals().get('net_worth', 0.0)

def buy_sponsorship(horse, tier):
    """POST /sponsorship/buy-sponsorship"""
    resp = requests.post(
        f"{SERVER_URL}/sponsorship/buy-sponsorship",
        json={ 'id': USER_ID, 'horse_name': horse, 'tier': tier }
    )
    return resp.status_code, resp.json()

def compute_probabilities():
    global sponsor_boost, horses
    # returns {horse_name: probability_float}
    weights = {}
    for h in horses:
        base_w = 1.0 / h["odds"]
        boost = sponsor_boost.get(h["name"], 0.0)
        weights[h["name"]] = base_w + boost
    total = sum(weights.values())
    return {name: w / total for name, w in weights.items()}

def show_sponsor_panel(ui_manager):
    global current_width, current_height, sponsor_panel, sponsor_close_button, sponsor_buttons, sponsor_selection, owned_tiers, chance_labels
    panel_rect = pygame.Rect((current_width // 2) - (current_width - 100) // 2, 100, current_width - 100, current_height - 200)
    panel_width = panel_rect.width

    if sponsor_panel is not None:
        sponsor_panel.kill()
        sponsor_panel = None
        sponsor_buttons.clear()
        chance_labels.clear()

    existing_data, nw = load_sponsorships()

    owned_tiers       = {}
    sponsor_selection = {}
    sponsor_boost     = {}

    for h in horses:
        name = h["name"]
        info = existing_data.get(name, {})
        owned_list = info.get("owned", [])
        active_tier = info.get("active")    # might be None

        owned_tiers[name]       = owned_list
        sponsor_selection[name] = active_tier
        sponsor_boost[name]     = (SPONSOR_TIERS[active_tier]["boost"]
                                   if active_tier in SPONSOR_TIERS else 0.0)

    sponsor_panel = pygame_gui.elements.UIPanel(
        relative_rect=panel_rect,
        manager=ui_manager,
        object_id="#sponsor_panel"
    )
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((panel_width // 2 - 100, 10), (200, 30)),
        text="Sponsor a Team (permanent boost)",
        manager=ui_manager,
        container=sponsor_panel
    )
    probs = compute_probabilities()
    x_offset = 0
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((x_offset, 50), (panel_width // 11 * 3, 50)),
        text="Horse Name",
        manager=ui_manager,
        container=sponsor_panel
    )
    x_offset += panel_width // 11 * 3
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((x_offset, 50), (panel_width // 11 * 2, 50)),
        text="Chance to Win",
        manager=ui_manager,
        container=sponsor_panel
    )
    x_offset += panel_width // 11 * 2
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((x_offset, 50), (panel_width // 11 * 2, 50)),
        text="Bronze ($100)",
        manager=ui_manager,
        container=sponsor_panel
    )
    x_offset += panel_width // 11 * 2
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((x_offset, 50), (panel_width // 11 * 2, 50)),
        text="Silver ($300)",
        manager=ui_manager,
        container=sponsor_panel
    )
    x_offset += panel_width // 11 * 2
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((x_offset, 50), (panel_width // 11 * 2, 50)),
        text="Gold ($500)",
        manager=ui_manager,
        container=sponsor_panel
    )
    probs = compute_probabilities()
    y_offset = 100
    for h in horses:
        name = h["name"]
        x_offset = 0
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_offset, y_offset), (panel_width // 11 * 3, 50)),
            text=name,
            manager=ui_manager,
            container=sponsor_panel
        )
        x_offset += panel_width // 11 * 3
        pct = int(probs[name]*100)
        chance_lbl = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_offset, y_offset), (panel_width // 11 * 2, 50)),
            text=f"{pct}%",
            manager=ui_manager,
            container=sponsor_panel
        )
        chance_labels[name] = chance_lbl
        x_offset += panel_width // 11 * 2
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_offset, y_offset), (panel_width // 11 * 2, 50)),
            text="Select",
            manager=ui_manager,
            container=sponsor_panel
        )
        col_w = panel_width // 11 * 2
        row_h = 50
        for tier_key in ["Bronze", "Silver", "Gold"]:
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((x_offset, y_offset), (col_w, row_h)),
                text=tier_key,
                manager=ui_manager,
                container=sponsor_panel
            )
            if tier_key not in owned_tiers[name]:
                btn.colours['normal_bg'] = DEFAULT_BG
            elif sponsor_selection[name] == tier_key:
                # owned & active → green
                btn.colours['normal_bg'] = SELECTED_BG
            else:
                # owned but inactive → light gray
                btn.colours['normal_bg'] = OWNED_BG
            btn.rebuild()

            # remember what this button is
            sponsor_buttons[btn] = (name, tier_key)
            x_offset += col_w
        y_offset += 50

    # Add a close button on the panel
    sponsor_close_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((panel_rect.width - 110, 10), (100, 30)),
        text="Close",
        manager=ui_manager,
        container=sponsor_panel,
        object_id="#close_sponsors"
    )
    
    return sponsor_panel


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
    global show_achievement_popup, new_achievements, streak, max_streak
    BASE_URL = SERVER_URL
    USER_ID = get_user()
    if not USER_ID:
        return

    the_min, the_max = get_user_networth_min_max()
    try:
        # Update the net worth
        response = requests.post(
            f"{BASE_URL}/game/update-net-worth/{USER_ID}",
            json={"net_worth": new_balance}
        )
        if response.status_code == 200:
            data = response.json()
            streak = data['streak']
            max_streak = data['max_streak']
            if new_balance < the_min:
                send_networth_email(new_balance, the_min, -1)
            elif new_balance > the_max:
                send_networth_email(new_balance, -1, the_max)
            '''add achievment check'''
            new_achievements = check_achievements(USER_ID)
            if new_achievements:
                set_ach_popup(True)
            else:
                set_ach_popup(False)
    except Exception as e:
        pass

def fetch_bet_history(user_id):
    """Fetches the user's bet history from the backend API and updates the global bet_history list."""
    global BASE_URL, bet_history
    try:
        response = requests.get(f"{BASE_URL}/game/get-bet-history/{user_id}")
        if response.status_code == 200:
            data = response.json()
            # Assume the response returns a dictionary with a "bet_history" key.
            bet_history = data.get("bet_history", [])
            return bet_history
        else:
            bet_history = []
            return bet_history
    except Exception as e:
        bet_history = []
        return bet_history

def update_bet_history(bets_placed):
    """Sends the current bets_placed list to the backend and then leaves it unchanged (it will be cleared after a successful update)."""
    global BASE_URL, USER_ID
    if not bets_placed:
        return

    try:
        payload = {"bets": bets_placed}  # send current bets
        response = requests.post(f"{BASE_URL}/game/update-bet-history/{USER_ID}", json=payload)
    except Exception as e:
        pass

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
    global bet_history, table_elements, current_height

    date_options = ["All", "30s", "1m", "1h"]
    sort_options = ["None", "Largest", "Smallest"]

    dropdown_y = current_height - 300  # adjust as needed

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
    header_y = current_height - 220
    header_x = (current_width - 600) // 2

    # Create and store header elements in table_elements.
    table_elements["header_date"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((header_x, header_y, 200, header_height)),
        text="Date",
        manager=ui_manager,
        object_id="#label"
    )
    header_x += 200  # Move to the next column
    table_elements["header_horse"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((header_x, header_y, 150, header_height)),
        text="Horse",
        manager=ui_manager,
        object_id="#label"
    )
    header_x += 150  # Move to the next column
    table_elements["header_odds"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((header_x, header_y, 75, header_height)),
        text="Odds",
        manager=ui_manager,
        object_id="#label"
    )
    header_x += 75  # Move to the next column
    table_elements["header_amount"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((header_x, header_y, 100, header_height)),
        text="Amount",
        manager=ui_manager,
        object_id="#label"
    )
    header_x += 100  # Move to the next column
    table_elements["header_outcome"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((header_x, header_y, 75, header_height)),
        text="Outcome",
        manager=ui_manager,
        object_id="#label"
    )

    # Create a scrolling container for just the bet rows.
    scroll_container_rect = pygame.Rect(0, header_y + header_height, current_width * .9 , container_height)
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
        x_offset = (current_width - 600) // 2
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_offset, y_offset, 200, row_height)),
            text=bet["date"],
            manager=ui_manager,
            container=scroll_container
        )
        x_offset += 200  # Move to the next column
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_offset, y_offset, 150, row_height)),
            text=bet["horse"],
            manager=ui_manager,
            container=scroll_container
        )
        x_offset += 150  # Move to the next column
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_offset, y_offset, 75, row_height)),
            text=f"{bet['odds']}x",
            manager=ui_manager,
            container=scroll_container
        )
        x_offset += 75  # Move to the next column
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_offset, y_offset, 100, row_height)),
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
        x_offset += 100  # Move to the next column
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_offset, y_offset, 75, row_height)),
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
    global bet_buttons, table_elements, pending_bets, current_height

    y_offset = current_height - 180
    x_offset = (current_width- 600) // 2

    # **Table Headers**
    table_elements["header_name"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((x_offset, current_height - 220, 200, 30)),  # Wider name column
        text="Horse Name",
        manager=ui_manager,
        object_id="#label"
    )
    x_offset += 200  # Move to the next column
    table_elements["header_color"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((x_offset, current_height - 220, 100, 30)),  # Increased column width
        text="Color",
        manager=ui_manager,
        object_id="#label"
    )
    x_offset += 100  # Move to the next column
    table_elements["header_odds"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((x_offset, current_height - 220, 100, 30)),  # More space for odds
        text="Odds",
        manager=ui_manager,
        object_id="#label"
    )
    x_offset += 100  # Move to the next column
    table_elements["header_bet"] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((x_offset, current_height - 220, 200, 30)),  # Wider column for betting
        text="Bet",
        manager=ui_manager,
        object_id="#label"
    )

    # **Generate Full-Width Table Rows**
    for i, horse in enumerate(horses):
        x_offset = (current_width- 600) // 2
        horse_name = horse["name"]

        table_elements[f"horse_name_{i}"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_offset, y_offset, 200, 30)),  # Wider name column
            text=horse["name"],
            manager=ui_manager
        )
        x_offset += 200  # Move to the next column
        table_elements[f"horse_color_{i}"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_offset, y_offset, 100, 30)),
            text=horse["color"],
            manager=ui_manager
        )
        x_offset += 100  # Move to the next column
        table_elements[f"horse_odds_{i}"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_offset, y_offset, 100, 30)),
            text=f"{horse['odds']}x",
            manager=ui_manager
        )
        # **Bet Controls**
        x_offset += 100  # Move to the next column
        table_elements[f"bet_decrement_{i}"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_offset, y_offset, 30, 30)),  # - Button
            text="-",
            manager=ui_manager
        )
        x_offset += 30  # Move to the next column
        table_elements[f"bet_input_{i}"] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((x_offset, y_offset, 70, 30)),  # Bet amount input
            manager=ui_manager
        )
        x_offset += 70  # Move to the next column
        table_elements[f"bet_input_{i}"].set_text(str(pending_bets[horse_name]))
        table_elements[f"bet_increment_{i}"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_offset, y_offset, 30, 30)),  # + Button
            text="+",
            manager=ui_manager
        )
        x_offset += 30  # Move to the next column
        table_elements[f"bet_confirm_{i}"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_offset, y_offset, 70, 30)),  # Confirm Bet
            text="Confirm",
            manager=ui_manager,
            object_id="confirm-button"
        )
        y_offset += 30  # Space between rows

def place_bet(horse_name, bet_amount, horse_odds):
    """Stores the bet details and deducts from user balance for new bets only."""
    global bet_history, bets_placed, net_worth
    if bet_amount <= 0:
        return "Error: Bet amount must be greater than 0!"

    # Check if a bet already exists on this horse
    existing_bet = next((bet for bet in bets_placed if bet["horse"] == horse_name), None)


    if betting_limit is not None:
        total_bets = sum(bet["amount"] for bet in bets_placed) + bet_amount
        if total_bets > betting_limit:
            return(f"Bet exceeds your set limit of ${betting_limit}!")



    if existing_bet:
        # **Modify existing bet amount**
        bet_difference = bet_amount - existing_bet["amount"]

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
            "outcome": "undecided",
        }

        # Add to active bets and bet history
        bets_placed[:] = [bet for bet in bets_placed if bet["horse"] != horse_name]
        bets_placed.append(bet_details)  # Add updated/new bet

        # **Update bet history in the same way**
        bet_history.append(bet_details)  

        return "Bet placed successfully!"

def initialize_game(ui_manager):
    """Initializes the game screen UI elements for horse derby betting."""
    global back_button, history_toggle_button, bet_buttons, bet_amount_entry
    global message_label, race_timer_label, race_start_time, horses
    global horse_positions, racing_phase, winning_horse, showing_history, horse_bets, pending_bets, USER_ID
    global net_worth, bet_history, user
    global set_limit_button, remove_limit_button, limit_entry, limit_toggle_button
    global sponsor_button, sponsor_boost
    global rumor_button, insider_button, sound_toggle_button, current_width, current_height, insight_toggle_button
    current_width, current_height = pygame.display.get_window_size()
    global result_notifications
    result_notifications = get_user_notification_preferences_results()
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

    import profileView
    if profileView.match_bet:
        match_bet = profileView.match_bet
        pending_bets[match_bet.get("horse")] = match_bet.get("amount")
        profileView.match_bet = None


    existing_data, net_worth = load_sponsorships()
    sponsor_boost = {}
    for h in horses:
        info = existing_data.get(h["name"], {})        # info is { "owned":[…], "active":tier_str }
        tier = info.get("active")                      # tier_str or None
        if tier and tier in SPONSOR_TIERS:
            sponsor_boost[h["name"]] = SPONSOR_TIERS[tier]["boost"]
        else:
            sponsor_boost[h["name"]] = 0.0

    weights = []
    for h in horses:
        base_w = 1.0 / h["odds"]
        bonus  = sponsor_boost[h["name"]]
        weights.append(base_w + bonus)

    # RIGGED FOR DEBUGING STREAK
    # winning_horse = random.choices(horse_names, weights=weights, k=1)[0]
    winning_horse = "Lightning Bolt"

    # Reset horse positions
    horse_positions = {horse["name"]: 120 for horse in horses}

    # Reset betting phase
    racing_phase = False

    # Create "Back" button to return to home
    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 0, 100, 40)),  
        text="Back",
        manager=ui_manager,
        object_id="#back_button"
    )

    sound_toggle_button = draw_button(
        text="Turn Sound Effects Off",  # Default text
        ui_manager=ui_manager,
        x=1,  # Place to the right of the "Back" button
        y=0,  # Same vertical position as "Back" button
        object_id="#sound_toggle_button",
        size="sm"  # Small button size
    )


    # Timer label to show countdown to next race
    race_timer_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((current_width // 2 - 100, 20, 200, 30)),
        text="Next Race: 60s",
        manager=ui_manager,
        object_id="#timer_label"
    )

    #message label
    message_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((current_width // 2 - 250, 260, 500, 30)),
        text="",
        manager=ui_manager,
        object_id="#label"
    )

    set_limit_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width - 230, current_height - 280, 100, 30)),
        text="Set",
        manager=ui_manager,
        object_id="set-limit-button"
    )
    set_limit_button.hide()

    remove_limit_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width - 120, current_height - 280, 100, 30)),  
        text="Remove",
        manager=ui_manager,
        object_id="remove-limit-button"
    )
    remove_limit_button.hide()


    limit_entry = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((current_width - 230, current_height - 320, 210, 30)),  
        manager=ui_manager,
        object_id="limit-entry"
    )
    limit_entry.hide()

    limit_toggle_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width - 170, current_height - 240, 150, 30)),  
        text="Set Limit",
        manager=ui_manager,
        object_id="limit-toggle-button",
    )


    history_toggle_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, current_height - 40, 200, 40)),
        text="View Bet History",
        manager=ui_manager,
        object_id="toggle-button"
    )

    insider_cost = max(math.floor((net_worth * 0.6) / 5) * 5, 60)  #dynamic, or 60

    insider_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width - 360, current_height - 40, 200, 40)),  # Positioned close to the bottom-right
        text=f"Insider ${insider_cost}",
        manager=ui_manager,
        object_id="insider-button",
        visible = False
    )
    insider_button.hide()


    rumor_cost = max(math.floor((net_worth * 0.3) / 5) * 5, 30)  #dynamic, or 30

    rumor_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width - 560, current_height - 40, 200, 40)),  # Positioned next to Insider Message
        text=f"Rumor ${rumor_cost}",
        manager=ui_manager,
        object_id="rumor-button",
        visible = False
    )
    rumor_button.hide()

    insight_toggle_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width - 150, current_height - 40, 150, 40)),  # Positioned where insider_button was
        text="Insights",
        manager=ui_manager,
        object_id="insight-toggle-button",
    )

    sponsor_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((current_width - 600, current_height - 40, 200, 40)),
        text="Sponsor Teams",
        manager=ui_manager,
        object_id="#sponsor-button"
    )

    draw_betting_table(ui_manager)
    # Start the race timer
    race_start_time = datetime.datetime.now()

def handle_sound_toggle():
    global play_sound_effects

    play_sound_effects = not play_sound_effects  # Toggle the sound effects state

    if play_sound_effects:
        sound_toggle_button.set_text("Turn Sound Effects Off")
    else:
        sound_toggle_button.set_text("Turn Sound Effects On")

def handle_rumor_button():
    global net_worth  
    rumor_cost = max(math.floor((net_worth * 0.3) / 5) * 5, 30)  #dynamic, or 30

    if net_worth >= rumor_cost:
        net_worth -= rumor_cost  # Deduct the cost from net_worth
        non_winning_horses = [horse["name"] for horse in horses if horse["name"] != winning_horse]
        revealed_horse = random.choice(non_winning_horses)

        rumor_options = [
                f"{revealed_horse} did not sleep well last night...",
                f"{revealed_horse} looked a bit sluggish during practice.",
                f"{revealed_horse} was seen eating way too much before the race!",
                f"{revealed_horse} seems distracted.",
                f"{revealed_horse} was overheard complaining about the weather."
        ]

        # Select a random rumor style
        message_label.set_text(random.choice(rumor_options))

    else:
        message_label.set_text("Not enough resources to purchase a rumor!")
    
def handle_insider_button():
    global net_worth
    insider_cost = max(math.floor((net_worth * 0.6) / 5) * 5, 60)  #dynamic, or 60

    if net_worth >= insider_cost:
        net_worth -= insider_cost  # Deduct the cost from net_worth

        # Select the winning horse
        horse_one = winning_horse

        # Randomly select a non-winning horse
        non_winning_horses = [horse["name"] for horse in horses if horse["name"] != winning_horse]
        horse_two = random.choice(non_winning_horses)

        # Generate positive insights for both horses
        insider_options = [
            f"{horse_one} and {horse_two} are favorites among trainers.",
            f"{horse_one} and {horse_two} looked strongest during practice.",
            f"{horse_one} and {horse_two} are in their best form.",
            f"{horse_one} and {horse_two} have impressed everyone this week."
        ]


        # Select a random insider insight
        message_label.set_text(random.choice(insider_options))
    else:
        message_label.set_text("Not enough resources to purchase insider information!")

def handle_set_limit_button():
    global betting_limit
    try:
        new_limit = float(limit_entry.get_text())  # Get user input from the entry field
        if new_limit <= 0:  # Validate that the limit is positive
            raise ValueError
        betting_limit = new_limit  # Update the betting limit
        message_label.set_text(f"Betting limit set to ${betting_limit:.2f}")
        limit_entry.set_text("") 
    except ValueError:
        # Display an error message if input is invalid
        message_label.set_text("Error: Please enter a valid positive number!")
    
def handle_remove_limit_button():
    global betting_limit
    betting_limit = None  # Clear the betting limit
    message_label.set_text("Betting limit removed.")  # Notify the user
    limit_entry.set_text("") 

def draw_game_screen(screen, events, ui_manager, selected_game):
    """Handles the horse derby game betting screen with a table and race visualization."""
    global bet_history, race_start_time, bets_placed, message_label, winner_announced, net_worth
    global horses, horse_positions, racing_phase, winning_horse, showing_history, horse_bets, pending_bets, current_date_filter, current_sort_order
    global current_width, current_height, sponsor_button, sponsor_panel, sponsor_close_button, streak, max_streak
    draw_game_background(screen)

    # Show game and balance info
    game_text = FONT.render(f"{selected_game}", True, WHITE)
    balance_text = FONT.render(f"Balance: ${net_worth:.2f}", True, WHITE)
    streak_text = FONT.render(f"Streak: {streak}", True, WHITE)
    max_streak_text = SMALL_FONT.render(f"Max Streak: {max_streak}", True, WHITE)

    padding = 10
    line_spacing = 5

    balance_x = current_width - balance_text.get_width() - padding
    balance_y = padding

    streak_x = current_width - streak_text.get_width() - padding
    streak_y = balance_y + balance_text.get_height() + line_spacing

    max_streak_x = current_width - max_streak_text.get_width() - padding
    max_streak_y = streak_y + streak_text.get_height() + line_spacing

    screen.blit(game_text, (current_width // 2 - game_text.get_width() // 2, 50))
    screen.blit(balance_text, (balance_x, balance_y))
    screen.blit(streak_text, (streak_x, streak_y))
    screen.blit(max_streak_text, (max_streak_x, max_streak_y))


    # Time logic
    now = datetime.datetime.now()
    time_elapsed = (now - race_start_time).seconds
    time_remaining = max(0, 30 - time_elapsed)
    

    # Update race phase logic
    if time_elapsed < 20:  # Betting Phase (0-19s)
        time_remaining = 20 - time_elapsed
        race_timer_label.set_text(f"Next Race: {time_remaining}s")
        
    if time_elapsed >= 20 and not racing_phase:
        time_remaining = 30
        racing_phase = True  # Enter racing phase
        #winning_horse = random.choice(horses)["name"]  # Select winner

    if time_elapsed == 25 and not winner_announced:
        message_label.set_text(f"Winning Horse: {winning_horse}")
        global result_notifications
        # Process bets
        for bet in bets_placed:
            if bet["horse"] == winning_horse:
                bet["outcome"] = "win"
                winnings = bet["amount"] * bet["odds"]
                if result_notifications:
                    send_bet_email(True, winnings, winning_horse)
                net_worth += winnings
                message_label.set_text(f"Winner! Won ${winnings} on {winning_horse}")
                if (play_sound_effects) and (is_winning_sound_enabled()):
                    winning_sound.play()
            else:
                bet["outcome"] = "loss"
                message_label.set_text(f"Lost ${bet['amount']}. Better luck next time!")
                if result_notifications:
                    send_bet_email(False, bet["amount"], winning_horse, bet["horse"])
                if (play_sound_effects) and (is_losing_sound_enabled()):
                    losing_sound.play()

        # Set flag to prevent rerunning
        winner_announced = True
    if time_elapsed >= 30:
        # Reset for next race
        race_start_time = datetime.datetime.now()
        racing_phase = False  # Return to betting phase
        winner_announced = False
        update_net_worth(net_worth)
        update_bet_history(bets_placed)
        streak_flag = None
        for bet in bets_placed:
            if bet["outcome"] == "loss":
                streak_flag = 1
                break
            elif bet["outcome"] == "win":
                streak_flag = 0
        if streak_flag is not None:
            response = requests.post(
                f"{BASE_URL}/game/update-streak/{USER_ID}",
                json={"streak": 0 if streak_flag == 1 else 1}
            )
        bets_placed.clear()
        initialize_game(ui_manager)  # Reset horses
    if racing_phase == False:
        race_timer_label.set_text(f"Next Race: {time_remaining}s")

        note = FONT.render(f"Not available until race starts", True, WHITE)
        text_rect = note.get_rect(center=(current_width // 2, 225))  # Center in the white box
    
        # Render the text inside the box
        screen.blit(note, text_rect)
    else:
        race_timer_label.set_text(f"Race beginned: {time_elapsed - 20}s")

    # Draw race box
    pygame.draw.rect(screen, WHITE, (50, 100, current_width - 100, 150), 2)  # White border
    y_offset = 120
    probs = compute_probabilities()
    max_p = max(probs.values()) or 1.0
    min_speed, max_speed = 1.0, 6.0  # tune these to taste
    # Handle race animation inside the box
    for horse in horses:
        
        horse_name = horse["name"]
        p = probs[horse_name]
        if racing_phase:
            if horse_name == winning_horse:
                speed = random.randint(1, 10) / 2  # Fastest movement for winner
            else:
                speed = random.randint(1, 10 - int(1/p *.5)) / 2 # Higher odds → slower movement

            horse_positions[horse_name] += speed
            if horse_positions[horse_name] >= current_width - 150:
                horse_positions[horse_name] = current_width - 150
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
            if event.ui_element == table_elements.get("date_dropdown"):
                selected = event.text  # e.g. "Past 30s", "Past 1m", "Past 1h", or "All"
                current_date_filter = selected # "30s", "1m", or "1h"
                clear_table_elements()
                draw_bet_history(ui_manager)  # Redraw history with the new filter
            elif event.ui_element == table_elements.get("sort_dropdown"):
                selected = event.text  # "None", "Largest amounts", or "Smallest amounts"
                current_sort_order = selected
                clear_table_elements()
                draw_bet_history(ui_manager)


        if event.type == pygame_gui.UI_BUTTON_PRESSED:

            if event.ui_element == sound_toggle_button:
                handle_sound_toggle()

            if event.ui_element == rumor_button:
                handle_rumor_button()
            
            if event.ui_element == insider_button:
                handle_insider_button()

            if event.ui_element == set_limit_button:
                handle_set_limit_button()  # Call the set limit function

            if event.ui_element == remove_limit_button:
                handle_remove_limit_button()  # Call the remove limit function
            
            if event.ui_element == sponsor_button:
                show_sponsor_panel(ui_manager)
            elif sponsor_panel is not None and event.ui_element == sponsor_close_button:
                sponsor_panel.kill()
                sponsor_panel = None
                sponsor_close_button = None
            if event.ui_element in sponsor_buttons:
                horse, tier = sponsor_buttons[event.ui_element]
                owned = owned_tiers[horse]
                active = sponsor_selection[horse]
                # ── 1) Buying a brand‐new tier ───────────────────────────────
                if tier not in owned:
                    status, data = buy_sponsorship(horse, tier)
                    if status == 200 and data['message'] == 'success':
                        # record ownership + auto‐activate
                        owned.append(tier)
                        sponsor_selection[horse] = tier
                        sponsor_boost[horse]     = SPONSOR_TIERS[tier]['boost']
                        net_worth                = data['net_worth']
                        message_label.set_text(
                            f"Purchased {tier} for {horse}! New balance: ${net_worth:.2f}"
                        )
                    elif status == 402 and data['message']=='insufficient_funds':
                        message_label.set_text("Insufficient funds to purchase sponsorship!")
                    else:
                        message_label.set_text("Error purchasing sponsorship.")

                # ── 2) Activating an already‐owned tier ──────────────────────
                else:
                    active = sponsor_selection[horse]
                    #  ─── Deactivate if already active ───────────────────────
                    if active == tier:
                        resp = requests.post(
                            f"{SERVER_URL}/sponsorship/deactivate-sponsorship",
                            json={'id': USER_ID, 'horse_name': horse}
                        )
                        if resp.status_code == 200 and resp.json().get('message')=='deactivated':
                            sponsor_selection[horse] = None
                            sponsor_boost[horse]     = 0.0
                        else:
                            message_label.set_text("Error deactivating sponsorship.")
                    #  ─── Activate if it wasn’t active ──────────────────────
                    else:
                        resp = requests.post(
                            f"{SERVER_URL}/sponsorship/activate-sponsorship",
                            json={'id': USER_ID, 'horse_name': horse, 'tier': tier}
                        )
                        if resp.status_code == 200 and resp.json().get('message')=='activated':
                            sponsor_selection[horse] = tier
                            sponsor_boost[horse]     = SPONSOR_TIERS[tier]['boost']
                        else:
                            message_label.set_text("Error activating sponsorship.")

                # ── 3) Recolor this horse’s row ──────────────────────────────
                for btn, (h2, t2) in sponsor_buttons.items():
                    if h2 == horse:
                        if t2 not in owned:
                            # un‐owned → maybe dim/disable
                            btn.colours['normal_bg'] = DEFAULT_BG
                        elif sponsor_selection[horse] == t2:
                            # owned & active
                            btn.colours['normal_bg'] = SELECTED_BG
                        else:
                            # owned but inactive
                            btn.colours['normal_bg'] = OWNED_BG
                        btn.rebuild()

                # ── 4) Update all chance labels ──────────────────────────────
                probs = compute_probabilities()
                for hn, lbl in chance_labels.items():
                    lbl.set_text(f"{int(probs[hn] * 100)}%")
            
            if event.ui_element == back_button:
                update_net_worth(net_worth)
                return None  # Go back to home
            
            if event.ui_element == limit_toggle_button:
                if limit_toggle_button.text == "Close":
                    limit_entry.hide()
                    set_limit_button.hide()
                    remove_limit_button.hide()
                    limit_toggle_button.set_text("Set Limit")
                else:
                    limit_entry.show()
                    set_limit_button.show()
                    remove_limit_button.show()
                    limit_toggle_button.set_text("Close")
            
            if event.ui_element == insight_toggle_button:
                if insight_toggle_button.text == "Insights":
                # Show insider and rumor buttons, update text
                    insider_button.show()
                    rumor_button.show()
                    sponsor_button.hide()
                    insight_toggle_button.set_text("Close")
                else:
                # Hide insider and rumor buttons, revert text
                    insider_button.hide()
                    rumor_button.hide()
                    sponsor_button.show()
                    insight_toggle_button.set_text("Insights")

            
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
                        if (play_sound_effects) and (is_money_sound_enabled()):
                            money_sound.play()

            
            
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return selected_game
