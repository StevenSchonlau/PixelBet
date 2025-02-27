import pygame
import pygame_gui
import datetime
import random
import requests
from constants import *
from user_session import UserSession

error = None
players = []
friends = []
sent_pending = []
rec_pending = []
curr_player = None

def refresh_data(ui_manager):
    get_all_players()
    get_friends(ui_manager)
    get_rec(ui_manager)


def draw_home_friends_button(ui_manager):
    text_surface = FONT.render("Friends", True, WHITE)
    button_width = text_surface.get_width() + 40
    button_height = text_surface.get_height() + 20
    button_x = SCREEN_WIDTH - button_width
    button_y = SCREEN_HEIGHT - button_height
    
    button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((button_x, button_y), (button_width, button_height)),
        text="Friends",
        manager=ui_manager,
        object_id="#friends",
    )

def draw_search_panel(ui_manager):
    global ui_dict
    search_panel_rect = pygame.Rect(
        (SCREEN_WIDTH * 0.55, SCREEN_HEIGHT * 0.65),
        (SCREEN_WIDTH * 0.4, SCREEN_HEIGHT * 0.2)
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
    requests_panel_rect = pygame.Rect(
        (SCREEN_WIDTH * 0.05, SCREEN_HEIGHT * 0.65),
        (SCREEN_WIDTH * 0.4, SCREEN_HEIGHT * 0.3)
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
    friends_list_panel_rect = pygame.Rect(
        (SCREEN_WIDTH * 0.05, SCREEN_HEIGHT * 0.2),
        (SCREEN_WIDTH * 0.9, SCREEN_HEIGHT * 0.4)
    )
    friends_list_scroll_rect = pygame.Rect(
        (SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.2),
        (SCREEN_WIDTH*0.9, SCREEN_HEIGHT*0.2)
    )
    friends_list_panel = pygame_gui.elements.UIPanel(
        relative_rect=friends_list_panel_rect,
        starting_height=1,
        manager=ui_manager,
        object_id="#friends_list_panel"
    )
    friends_list_scroll = pygame_gui.elements.UIScrollingContainer(
        relative_rect=friends_list_panel_rect,
        starting_height=1,
        manager=ui_manager,
        container=friends_list_panel,
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
    global ui_dict, curr_player
    ui_manager.clear_and_reset()
    profile = get_profile()
    curr_player = User(profile["username"], profile["id"])
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
    if response.status_code == 200:
        friends.clear()
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

    container_width = SCREEN_WIDTH * .7
    button_height = 40
    start_y = 0

    for i, friend in enumerate(friends):
        y = start_y + i * (button_height + 10)
        result_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, y), (container_width, button_height)),
            text=f"{friend.username}",
            manager=ui_manager,
            container=ui_dict["friends_list_scroll"].scrollable_container,
            object_id="#friend_button"
        )
        ui_dict["friends"].append(result_button)



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
            error = None
            return True
        else:
            print("Error:", response.status_code, response.json())
            error = response.json()["message"]
            return False
    else:
        error = "An error has occurred"
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
    global error
    draw_background(screen)

    for event in events:
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == ui_dict["search_box"]:
                search_text = event.text  # The text entered by the user
                print("User pressed Enter in the search box:", search_text)
                friend = search_player(search_text)
                if "search_result" in ui_dict:
                    ui_dict["search_result"].kill()
                else:
                    ui_dict["search_result"] = None
                if friend:
                    result_button = pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((SCREEN_WIDTH*0.4*.05, SCREEN_HEIGHT*0.2*.6), (SCREEN_WIDTH*0.4*.9, SCREEN_HEIGHT*0.2*.3)),
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

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    if error:
        error_name = FONT.render(error, True, WHITE)
        screen.blit(error_name, ((SCREEN_WIDTH // 8) * 2, (SCREEN_HEIGHT // 8) * 0))


    pygame.display.flip()
    return selected_game