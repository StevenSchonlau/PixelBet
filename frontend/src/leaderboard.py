import pygame
import pygame_gui
import datetime
import random
import requests
from constants import *
from user_session import UserSession
from profileView import init_profile_view, draw_view_profile

error = None
ui_dict = {}
selected_player = None
initialized = False
curr_player = None

def refresh_data(ui_manager):
    get_players(ui_manager)


def clean_buttons(key):
    for button in ui_dict[key]:
        button.kill()
    ui_dict[key] = []
    return ui_dict[key]


def add_friend(friend_id):
    global curr_player, error
    response = requests.post(f"{SERVER_URL}/friend-request/{curr_player.id}/{friend_id}")
    if response.status_code == 200:
        print("success")
        error = "Sent!"
        return True
    else:
        error = response.json()["message"]
        return False

def get_players(ui_manager):
    global error
    players = []

    response = requests.get(f"{SERVER_URL}/game/all-net")
    if response.status_code == 200:
        users = response.json()
        for user in users:
            player_obj = User(user["username"], user["id"], net_worth=float(user["net_worth"]))
            players.append(player_obj)
        error = None
    else:
        print("Error:", response.status_code, response.json())
        error = "An error occurred"

    players.sort(key=lambda player: player.net_worth, reverse=True)

    ui_dict["players"] = clean_buttons("players")
    ui_dict["add_friends"] = clean_buttons("add_friends")
    ui_dict["view_profile_buttons"] = clean_buttons("view_profile_buttons")
    ui_dict["nets"] = clean_buttons("nets")

    button_height = 40
    start_y = 0
    container = ui_dict["board_scroll"].scrollable_container
    container_width = container.get_size()[0]
    for i, player in enumerate(players):
        y = start_y + i * (button_height + 10)
        result_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((100, y), (container_width - 600, button_height)),
            text=f"{player.username}",
            manager=ui_manager,
            container=container,
            object_id="#friend_result"
        )
        net_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((100, y), (container_width - 400, button_height)),
            text=f"${player.net_worth}",
            manager=ui_manager,
            container=container,
            object_id="#friend_result"
        )
        add_friend = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 270 + 130, y), (120, button_height)),
            text="Add Friend",
            manager=ui_manager,
            container=container,
            object_id="#accept-button"
        )
        view_profile_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 270 + 10, y), (120, button_height)),
            text="View Profile",
            manager=ui_manager,
            container=container,
            object_id="#decline-button"
        )
        view_profile_button.user = player
        add_friend.user = player
        ui_dict["players"].append(result_label)
        ui_dict["nets"].append(net_label)
        ui_dict["view_profile_buttons"].append(view_profile_button)
        ui_dict["add_friends"].append(add_friend)

    total_height = start_y + len(players) * (button_height + 10)
    ui_dict["board_scroll"].set_scrollable_area_dimensions((container_width, total_height)) 



def draw_leaderboard_button(ui_manager, profile_button):
    text = "Leaderboard"
    text_surface = FONT.render(text, True, WHITE)
    button_width = text_surface.get_width() + 40
    button_height = text_surface.get_height() + 20
    button_x = 0
    button_y = profile_button.rect.height + 10
    
    button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((button_x, button_y), (button_width, button_height)),
        text=text,
        manager=ui_manager,
        object_id="#friends",
    )

def draw_leaderboard(ui_manager):
    board_panel_rect = pygame.Rect(
        (SCREEN_WIDTH * 0.05, SCREEN_HEIGHT * 0.2),
        (SCREEN_WIDTH * 0.9, SCREEN_HEIGHT * 0.7)
    )
    board_panel = pygame_gui.elements.UIPanel(
        relative_rect=board_panel_rect,
        starting_height=1,
        manager=ui_manager,
        object_id="#board_panel"
    )
    scroll_container_rect = pygame.Rect(0, 40, board_panel_rect.width, board_panel_rect.height - 80)
    board_scroll = pygame_gui.elements.UIScrollingContainer(
        relative_rect=scroll_container_rect,
        manager=ui_manager,
        container=board_panel,
        allow_scroll_x=False,
        object_id="#board_scroll"
    )
    leaderboard_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((10, 10), (board_panel_rect.width - 20, 30)),
        text="Leaderboard",
        manager=ui_manager,
        container=board_panel,
        object_id="#panel_label"
    )
    ui_dict["board_scroll"] = board_scroll
    ui_dict["board_panel"] = board_panel
    refresh_data(ui_manager)

def init_leaderboard_page(ui_manager):
    global ui_dict, curr_player
    ui_manager.clear_and_reset()
    profile = get_profile()
    curr_player = User(profile["username"], profile["id"])

    ui_dict["board_scroll"] = None
    ui_dict["board_panel"] = None
    ui_dict["players"] = []
    ui_dict["view_profile_buttons"] = []
    ui_dict["add_friends"] = []
    ui_dict["nets"] = []

    back_button = draw_button("Back", ui_manager, 0, 0)
    refresh_button = draw_button("Refresh", ui_manager, 0, .8)
    ui_dict["refresh"] = refresh_button

    draw_leaderboard(ui_manager)

def draw_leaderboard_page(screen, events, ui_manager, selected_game):
    global error, selected_player, initialized

    if selected_player:
        if not initialized:
            init_profile_view(ui_manager, selected_player=selected_player)
            initialized = True
        selected_game = draw_view_profile(screen, events, ui_manager, selected_game)
        if selected_game == None:
            selected_game = "Leaderboard"
            selected_player = None
            initialized = False
            init_leaderboard_page(ui_manager)
        return selected_game

    draw_background(screen)

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            text = event.ui_element.text
            print(text)
            if text == "Back":
                selected_game = None
            elif event.ui_element in ui_dict["view_profile_buttons"]:
                selected_player = event.ui_element.user
            elif event.ui_element in ui_dict["add_friends"]:
                if curr_player.id == event.ui_element.user.id:
                    error = "You can't friend yourself!"
                else:
                    add_friend(event.ui_element.user.id)
            elif event.ui_element == ui_dict["refresh"]:
                refresh_data(ui_manager)

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    if error:
        error_name = FONT.render(error, True, WHITE)
        screen.blit(error_name, ((SCREEN_WIDTH // 8) * 2, (SCREEN_HEIGHT // 8) * 0))


    pygame.display.flip()
    return selected_game