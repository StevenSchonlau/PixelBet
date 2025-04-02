import pygame
import pygame_gui
from constants import *
from user_session import UserSession
from game import fetch_net_worth, update_net_worth

net_worth = 0
room_arr = ["Cozy Room", "Tech Room"]
room_name_arr = ["cozy", "tech"]
room_arr_cost = [20, 20]
owns_room_list = []
back_btn = None
room_buttons = []
error = None

def buy_room(index):
    global error, net_worth
    data = {
        "cost": room_arr_cost[index],
        "room": room_name_arr[index],
    }
    response = requests.post(f"{SERVER_URL}/profile/buyroom/{get_profile()['id']}", json=data)
    if response.status_code == 200:
        error = "Success!"
        net_worth = float(get_profile()['net_worth'])
    else:
        error = "An error occurred"

def initialize_room_shop(ui_manager):
    global net_worth, owns_room_list, back_btn, room_buttons
    ui_manager.clear_and_reset()
    user = get_profile()
    net_worth = float(user['net_worth'])
    owns_room_list = user['owns_room_list']
    print(owns_room_list)
    for index, room in enumerate(room_arr):
        room_buttons.append(pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 200, 100 * index + 200), (400, 40)),
            text=f"${room_arr_cost[index]} {room}",
            manager=ui_manager,
            object_id=f"#room_btn_{index}",
            visible=True
        ))
        back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 4 * 3, 100), (100, 40)),
            text="Back",
            manager=ui_manager,
            object_id="#Back",
            visible=True
        )

def draw_room_shop(screen, events, ui_manager):
    global net_worth, error, room_buttons
    draw_background(screen)
    title_text_pixel_bet = FONT.render("Room Shop", True, WHITE)
    screen.blit(title_text_pixel_bet, (SCREEN_WIDTH // 2 - title_text_pixel_bet.get_width() // 2, 50))
    
    title_text_pixel_bet = FONT.render(f"Money: ${net_worth:.2f}", True, WHITE)
    screen.blit(title_text_pixel_bet, (SCREEN_WIDTH // 2 - title_text_pixel_bet.get_width() // 2, 100))
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_btn:
                room_buttons = []
                error = None
                return "home"
            elif event.ui_element in room_buttons:
                index = room_buttons.index(event.ui_element)
                if room_name_arr[index] in owns_room_list:
                    error = "Room already owned"
                    return
                if net_worth - room_arr_cost[index] >= 0:
                    print(f"buying: {room_arr[index]}")
                    buy_room(index)
                else:
                    error = "Insufficient funds"

    if error:
        error_name = FONT.render(error, True, WHITE)
        screen.blit(error_name, ((SCREEN_WIDTH // 8) * 1, (SCREEN_HEIGHT // 8) * 6))
                
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   
    return "room"
