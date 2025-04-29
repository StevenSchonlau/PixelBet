import pygame
import pygame_gui
import datetime
import random
import requests
from constants import *
from user_session import UserSession
from profileView import init_profile_view, draw_view_profile

error = None
players = []
friends = []
sent_pending = []
rec_pending = []
curr_player = None
selected_player = None
initialized = False
y_off = 0
current_width, current_height = 0, 0
chat_panel        = None
chat_close_button = None
chat_scroll       = None
chat_input_line   = None
chat_send_button  = None
chat_labels       = []
current_chat_with = None
USER_ID = None

def fetch_chat_history(other_id, since=None):
    """
    Pull the full chat history between the current user and other_id.
    Returns: list of { id, sender, receiver, body, timestamp }
    """
    profile = get_profile()
    user_id = profile["id"]

    payload = {
        "user_id":  user_id,
        "other_id": other_id
    }
    if since:
        payload["since"] = since

    try:
        # <-- use GET, not POST
        resp = requests.get(f"{SERVER_URL}/chat/get-messages", json=payload)

        if resp.status_code != 200:
            print("💬 fetch_chat_history failed:", resp.status_code, resp.text)
            return []

        data = resp.json()
        if data.get("message") != "success":
            print("💬 fetch_chat_history failed:", data)
            return []

        return data.get("messages", [])
    except ValueError:
        print("💬 fetch_chat_history: server returned invalid JSON")
        return []
    except Exception as e:
        print("💬 Error fetching chat history:", e)
        return []


def send_chat_message(recipient_id, body):
    """
    POST a new chat message to the backend.
    Returns (status_code, json_data)
    """
    profile = get_profile()
    sender_id = profile["id"]

    payload = {
        "sender_id":   sender_id,
        "receiver_id": recipient_id,
        "body":        body
    }

    resp = requests.post(
        f"{SERVER_URL}/chat/send-message",
        json=payload
    )
    return resp.status_code, resp.json()


def show_chat_panel(ui_manager, recipient_id, recipient_username):
    global chat_panel, chat_close_button, chat_scroll, y_off
    global chat_input_line, chat_send_button, chat_labels, current_chat_with

    # remember who we're talking to
    current_chat_with = recipient_id

    # kill any existing panel
    if chat_panel:
        chat_panel.kill()
        for lbl in chat_labels:
            lbl.kill()
        chat_labels.clear()

    # panel dims
    chat_panel = pygame_gui.elements.UIPanel(
        relative_rect= pygame.Rect((current_width // 2) - (current_width - 100) // 2, 100, current_width - 100, current_height - 200),
        manager=ui_manager,
        object_id="#chat_panel",
        starting_height=100000,
    )
    panel_width, panel_height = current_width - 100, current_height - 200
    title_text = f"Chat with {recipient_username}"
    text_surf = FONT.render(title_text, True, (0, 0, 0))
    text_w = text_surf.get_width()

    # Title
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(((current_width - text_w)// 2, 10), (200, 30)),
        text=title_text,
        manager=ui_manager,
        container=chat_panel
    )

    # Scrolling container for messages
    chat_scroll = pygame_gui.elements.UIScrollingContainer(
        relative_rect=pygame.Rect((10, 50), (panel_width - 10, panel_height - 50)),
        manager=ui_manager,
        container=chat_panel,
        allow_scroll_x=False,
        object_id="#chat_scroll"
    )

    # Load history from backend
    history = fetch_chat_history(recipient_id)   # implement this to GET your /chat/messages
    y_off = 0
    half_w = panel_width // 2
    for msg in history:
        is_mine = (msg['sender_id'] == USER_ID)
        if is_mine:
            x = half_w                        # start at mid-point
            width = half_w - 10               # leave a little padding
            text = msg['body']                # or include “[me]: …”
            bubble_surf = pygame.Surface((width + 10, 24), pygame.SRCALPHA)
            bubble_surf.fill((0, 122, 204, 200))  # RGBA, last is alpha
            pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect((x - 5, y_off - 2), (width + 10, 24)),
                image_surface=bubble_surf,
                manager=ui_manager,
                container=chat_scroll.scrollable_container,
                starting_height=0  # make sure it sits underneath the label
            )
        else:
            x = 0
            width = half_w - 10
            text = f"{msg['sender_username']}: {msg['body']}"
        lbl = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x, y_off), (width, 20)),
            text=text,
            manager=ui_manager,
            container=chat_scroll.scrollable_container
        )
        chat_labels.append(lbl)
        y_off += 24
    chat_scroll.set_scrollable_area_dimensions((panel_width - 20, y_off))

    # Input box
    chat_input_line = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((10, panel_height - 40), (panel_width - 120, 30)),
        manager=ui_manager,
        container=chat_panel,
        object_id="#chat_input"
    )

    # Send button
    chat_send_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((panel_width - 110, panel_height - 50), (100, 40)),
        text="Send",
        manager=ui_manager,
        container=chat_panel,
        object_id="#chat_send"
    )

    # Close button
    chat_close_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((panel_width - 110, 10), (100, 40)),
        text="Close",
        manager=ui_manager,
        container=chat_panel,
        object_id="#close_chat"
    )

def refresh_data(ui_manager):
    get_all_players()
    get_friends(ui_manager)
    get_rec(ui_manager)

def draw_search_panel(ui_manager):
    global ui_dict, current_width, current_height
    search_panel_rect = pygame.Rect(
        (current_width * 0.55, current_height * 0.65),
        (current_width * 0.4, current_height * 0.2)
    )
    search_panel = pygame_gui.elements.UIPanel(
        relative_rect=search_panel_rect,
        starting_height=1,
        manager=ui_manager,
        object_id="#search_panel"
    )
    search_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((10, 5), (search_panel_rect.width - 20, 20)),
        text="Search Friends",
        manager=ui_manager,
        container=search_panel,
        object_id="#panel_label"
    )
    search_box_rect = pygame.Rect(
        (search_panel_rect.width * 0.05, search_panel_rect.height * 0.3),
        (search_panel_rect.width * 0.9, search_panel_rect.height * 0.3)
    )
    search_box = pygame_gui.elements.UITextEntryLine(
        relative_rect=search_box_rect,
        manager=ui_manager,
        container=search_panel,
        placeholder_text="username",
        object_id="#search_box"
    )
    ui_dict["search_box"] = search_box
    return search_panel

def draw_requests_panel(ui_manager):
    global current_width, current_height
    requests_panel_rect = pygame.Rect(
        (current_width * 0.05, current_height * 0.65),
        (current_width * 0.4, current_height * 0.3)
    )
    requests_panel = pygame_gui.elements.UIPanel(
        relative_rect=requests_panel_rect,
        starting_height=1,
        manager=ui_manager,
        object_id="#requests_panel"
    )
    scroll_container_rect = pygame.Rect(0, 40, requests_panel_rect.width, requests_panel_rect.height - 40)
    requests_scroll = pygame_gui.elements.UIScrollingContainer(
        relative_rect=scroll_container_rect,
        starting_height=1,
        manager=ui_manager,
        container=requests_panel,
        allow_scroll_x=False,
        object_id="#requests_scroll"
    )
    requests_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((10, 10), (requests_panel_rect.width - 20, 30)),
        text="Friend Requests",
        manager=ui_manager,
        container=requests_panel,
        object_id="#panel_label"
    )
    ui_dict["requests_scroll"] = requests_scroll
    return requests_panel

def draw_friends_panel(ui_manager):
    global current_width, current_height
    friends_list_panel_rect = pygame.Rect(
        (current_width * 0.05, current_height * 0.2),
        (current_width * 0.9, current_height * 0.4)
    )
    friends_list_panel = pygame_gui.elements.UIPanel(
        relative_rect=friends_list_panel_rect,
        starting_height=1,
        manager=ui_manager,
        object_id="#friends_list_panel"
    )
    scroll_container_rect = pygame.Rect(0, 40, friends_list_panel_rect.width, friends_list_panel_rect.height - 40)
    friends_list_scroll = pygame_gui.elements.UIScrollingContainer(
        relative_rect=scroll_container_rect,
        manager=ui_manager,
        container=friends_list_panel,
        allow_scroll_x=False,
        object_id="#friends_list_scroll"
    )
    friends_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((10, 10), (friends_list_panel_rect.width - 20, 30)),
        text="Friends List",
        manager=ui_manager,
        container=friends_list_panel,
        object_id="#panel_label"
    )
    ui_dict["friends_list_scroll"] = friends_list_scroll
    return friends_list_panel



def init_friends_page(ui_manager):
    global ui_dict, curr_player, current_height, current_width, USER_ID
    ui_manager.clear_and_reset()
    current_width, current_height = pygame.display.get_window_size()
    profile = get_profile()
    curr_player = User(profile["username"], profile["id"])
    USER_ID = profile["id"]  
    ui_dict = {}

    back_button = draw_button("Back", ui_manager, 0, 0)
    refresh_button = draw_button("Refresh", ui_manager, 0, .8)

    requests_panel = draw_requests_panel(ui_manager)
    search_panel = draw_search_panel(ui_manager)
    friends_list_panel = draw_friends_panel(ui_manager)

    ui_dict["requests_panel"] = requests_panel
    ui_dict["search_panel"] = search_panel
    ui_dict["friends_list_panel"] = friends_list_panel
    ui_dict["friends"] = []
    ui_dict["request_labels"] = []
    ui_dict["request_accept"] = []
    ui_dict["request_decline"] = []
    ui_dict["view_profile_buttons"] = []
    ui_dict["message_buttons"] = []
    ui_dict["remove_buttons"] = []
    refresh_data(ui_manager)


def get_all_players():
    global error, players
    response = requests.get(f"{SERVER_URL}/users")
    if response.status_code == 200:
        users = response.json()
        for user in users:
            player_obj = User(user["username"], user["id"])
            players.append(player_obj)

        error = None
    else:
        print("Error:", response.status_code, response.json())
        error = "An error occurred"

def get_friends(ui_manager):
    global error, friends, ui_dict
    user_id = get_profile()['id']
    response = requests.get(f"{SERVER_URL}/friends/{user_id}")
    friends.clear()
    if response.status_code == 200:
        for friend in response.json():
            friend_obj = User(friend["username"], friend["id"])
            friends.append(friend_obj)
        error = None
    elif response.status_code == 201:
        error = None
    else:
        print("Error:", response.status_code, response.json())
        error = "An error occurred"

    for button in ui_dict["friends"]:
        button.kill()
    ui_dict["friends"] = []
    for button in ui_dict["remove_buttons"]:
        button.kill()
    ui_dict["remove_buttons"] = []
    for button in ui_dict["view_profile_buttons"]:
        button.kill()
    ui_dict["view_profile_buttons"] = []
    for btn in ui_dict["message_buttons"]:
        btn.kill()
    ui_dict["message_buttons"] = []

    button_height = 40
    start_y = 0
    container = ui_dict["friends_list_scroll"].scrollable_container
    container_width = container.get_size()[0]

    for i, friend in enumerate(friends):
        y = start_y + i * (button_height + 10)
        result_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, y), (container_width - 600, button_height)),
            text=f"{friend.username}",
            manager=ui_manager,
            container=container,
            object_id="#friend_result"
        )
        remove_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 220 + 130, y), (70, button_height)),
            text="Remove",
            manager=ui_manager,
            container=container,
            object_id="#accept-button"
        )
        view_profile_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 220 + 10, y), (120, button_height)),
            text="View Profile",
            manager=ui_manager,
            container=container,
            object_id="#decline-button"
        )
        message_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 280, y), (70, button_height)),
            text="Message",
            manager=ui_manager,
            container=container,
            object_id="#message-button"
        )
        view_profile_button.user = friend
        remove_button.user_id = friend.id
        message_button.username = friend.username
        message_button.user_id  = friend.id
        ui_dict["message_buttons"].append(message_button)
        ui_dict["friends"].append(result_label)
        ui_dict["view_profile_buttons"].append(view_profile_button)
        ui_dict["remove_buttons"].append(remove_button)


    total_height = start_y + len(friends) * (button_height + 10)
    ui_dict["friends_list_scroll"].set_scrollable_area_dimensions((container_width, total_height)) 



def search_player(username):
    global error
    response = requests.get(f"{SERVER_URL}/search/{username}")
    if response.status_code == 200:
        friend = response.json()
        friend_obj = User(friend["username"], friend["id"])
        error = None
        return friend_obj
    else:
        print("Error:", response.status_code, response.json())
        error = None
        return None


def add_friend(username):
    global curr_player, players, error
    friend = None
    for player in players:
        if player.username == username:
            friend = player
    if friend:
        response = requests.post(f"{SERVER_URL}/friend-request/{curr_player.id}/{friend.id}")
        if response.status_code == 200:
            print("success")
            error = "Sent!"
            return True
        else:
            print("Error:", response.status_code, response.json())
            error = response.json()["message"]
            return False
    else:
        error = "An error has occurred"
        return False


def remove_friend(friend_id):
    global curr_player, error
    response = requests.post(f"{SERVER_URL}/remove-friend/{curr_player.id}/{friend_id}")
    if response.status_code == 200:
        print("Removed!")
        error = None
        return True
    else:
        print("Error:", response.status_code, response.json())
        error = response.json()["message"]
        return False


def get_sent():
    global error, sent_pending, curr_player
    response = requests.get(f"{SERVER_URL}/pending-sent/{curr_player.id}")
    if response.status_code == 200:
        for player in response.json():
            player_obj = User(player["username"], player["id"])
            sent_pending.append(player_obj)
        error = None
        return True
    elif response.status_code == 201:
        error = None
    else:
        print("Error:", response.status_code, response.json())
        error = response.json()["message"]
        return False

def get_rec(ui_manager):
    global error, rec_pending, curr_player
    rec_pending.clear()
    response = requests.get(f"{SERVER_URL}/pending-received/{curr_player.id}")
    if response.status_code == 200:
        for player in response.json():
            player_obj = User(player["username"], player["id"])
            rec_pending.append(player_obj)
        error = None
    elif response.status_code == 201:
        error = None
    else:
        print("Error:", response.status_code, response.json())
        error = response.json()["message"]
        return

    for button in ui_dict["request_labels"]:
        button.kill()
    ui_dict["request_labels"] = []
    for button in ui_dict["request_accept"]:
        button.kill()
    ui_dict["request_accept"] = []
    for button in ui_dict["request_decline"]:
        button.kill()
    ui_dict["request_decline"] = []
    
    start_y = 10
    button_height = 40
    padding = 10
    scroll_container = ui_dict["requests_scroll"].scrollable_container
    container_width = scroll_container.get_size()[0]
    
    for i, user in enumerate(rec_pending):
        y = start_y + i * (button_height + padding)
        user_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y), (container_width - 200, button_height)),
            text=user.username,
            manager=ui_manager,
            container=scroll_container,
            object_id="#requests_label"
        )
        accept_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 200 + 10, y), (70, button_height)),
            text="Accept",
            manager=ui_manager,
            container=scroll_container,
            object_id="#accept-button"
        )
        decline_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 200 + 80, y), (70, button_height)),
            text="Decline",
            manager=ui_manager,
            container=scroll_container,
            object_id="#decline-button"
        )
        accept_button.user_id, decline_button.user_id = user.id, user.id
        ui_dict["request_labels"].append(user_label)
        ui_dict["request_accept"].append(accept_button)
        ui_dict["request_decline"].append(decline_button)

    total_height = start_y + len(rec_pending) * (button_height + padding)
    ui_dict["requests_scroll"].set_scrollable_area_dimensions((container_width, total_height)) 

def reject_request(user_id):
    global error
    response = requests.post(f"{SERVER_URL}/reject-request/{curr_player.id}/{user_id}")
    if response.status_code == 200:
        error = None
    else:
        print("Error:", response.status_code, response.json())
        error = response.json()["message"]

def accept_request(user_id):
    global error
    response = requests.post(f"{SERVER_URL}/accept-request/{curr_player.id}/{user_id}")
    if response.status_code == 200:
        error = None
    else:
        print("Error:", response.status_code, response.json())
        error = response.json()["message"]

def draw_friends_page(screen, events, ui_manager, selected_game):
    global error, selected_player, initialized, current_width, current_height, chat_panel, chat_close_button, chat_scroll
    global y_off, chat_input_line, chat_send_button, chat_labels, current_chat_with

    if selected_player:
        if not initialized:
            init_profile_view(ui_manager, selected_player=selected_player)
            initialized = True
        selected_game = draw_view_profile(screen, events, ui_manager, selected_game)
        if selected_game == None:
            selected_game = "Friends"
            selected_player = None
            initialized = False
            init_friends_page(ui_manager)
        return selected_game

    draw_background(screen)

    for event in events:
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == ui_dict["search_box"]:
                search_text = event.text  # The text entered by the user
                friend = search_player(search_text)
                if "search_result" in ui_dict:
                    ui_dict["search_result"].kill()
                else:
                    ui_dict["search_result"] = None
                if friend:
                    result_button = pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((current_width*0.4*.05, current_height*0.2*.6), (current_width*0.4*.9, current_height*0.2*.3)),
                        text=f"{friend.username}",
                        manager=ui_manager,
                        container=ui_dict["search_panel"],
                        object_id="#friend_result_button"
                    )
                    ui_dict["search_result"] = result_button
                else:
                    error = "Friend not found"
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            text = event.ui_element.text
            print(text)
            if text == "Back":
                error = None
                selected_game = None
            elif text == "Refresh":
                refresh_data(ui_manager)
            if "search_result" in ui_dict:
                if event.ui_element == ui_dict["search_result"]:
                    if text == curr_player.username:
                        error = "Can't friend yourself!"
                    else:
                        add_friend(text)
            if event.ui_element in ui_dict["request_accept"]:
                accept_request(event.ui_element.user_id)
                refresh_data(ui_manager)
            elif event.ui_element in ui_dict["request_decline"]:
                reject_request(event.ui_element.user_id)
                refresh_data(ui_manager)
            elif event.ui_element in ui_dict["view_profile_buttons"]:
                selected_player = event.ui_element.user
            elif event.ui_element in ui_dict["remove_buttons"]:
                remove_friend(event.ui_element.user_id)
                refresh_data(ui_manager)
            elif event.ui_element in ui_dict["message_buttons"]:
                # grab the friend object
                friend_id = event.ui_element.user_id
                friend_username = event.ui_element.username
                show_chat_panel(ui_manager, friend_id, friend_username)
                # switch to your chat screen, or popup a chat panel
            elif event.ui_element == chat_send_button:
                text = chat_input_line.get_text().strip()
                if not text:
                    break  # or show “cannot send empty” feedback

                status, data = send_chat_message(current_chat_with, text)
                if status == 201 and data.get("message") == "success":
                    # append it immediately to the scroll container:
                    panel_width = current_width - 100
                    bubble_surf = pygame.Surface((panel_width + 10, 24), pygame.SRCALPHA)
                    bubble_surf.fill((0, 122, 204, 200))  # RGBA, last is alpha
                    pygame_gui.elements.UIImage(
                        relative_rect=pygame.Rect(((panel_width // 2) - 5, y_off-2), ((panel_width // 2 - 5) +10, 24)),
                        image_surface=bubble_surf,
                        manager=ui_manager,
                        container=chat_scroll.scrollable_container,
                        starting_height=0  # make sure it sits underneath the label
                    )
                    new_lbl = pygame_gui.elements.UILabel(
                        relative_rect=pygame.Rect((panel_width // 2, y_off), (panel_width // 2, 20)),
                        text=text,
                        manager=ui_manager,
                        container=chat_scroll.scrollable_container
                    )
                    chat_labels.append(new_lbl)
                    y_off += 24
                    chat_scroll.set_scrollable_area_dimensions((current_width - 20, y_off))

                    chat_input_line.set_text("")  # clear input
                else:
                    print("💬 send failed:", data)
            elif chat_panel and event.ui_element == chat_close_button:
                chat_panel.kill()
                for lbl in chat_labels:
                    lbl.kill()
                chat_labels.clear()
                chat_panel        = None
                chat_close_button = None
                chat_scroll       = None
                chat_input_line   = None
                chat_send_button  = None
                current_chat_with = None

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    if error:
        error_name = FONT.render(error, True, WHITE)
        screen.blit(error_name, ((current_width // 8) * 2, (current_height // 8) * 0))


    pygame.display.flip()
    return selected_game