import pygame
import pygame_gui
from constants import *
from notifications import get_user_networth_min_max, send_networth_email

net_worth = 0
shirt_arr = ["Red Shirt", "Pixel Shirt"]
shirt_dict = {"Red Shirt": "redShirt", "Pixel Shirt": "pixelShirt"}
shirt_arr_cost = [10, 10]
owns_shirts_list = []
back_btn = None
shirt_buttons = []
error = None
current_width, current_height = 0,0

def buy_shirt(index):
    global error, net_worth
    data = {
        "cost": shirt_arr_cost[index],
        "shirt": shirt_dict[shirt_arr[index]],
    }
    the_min, the_max = get_user_networth_min_max()
    new_nw = net_worth - shirt_arr_cost[index]
    response = requests.post(f"{SERVER_URL}/profile/buyshirt/{get_profile()['id']}", json=data)
    if response.status_code == 200:
        if new_nw < the_min:
            send_networth_email(new_nw, the_min, -1)
        elif new_nw > the_max:
            send_networth_email(new_nw, -1, the_max)
        error = "Success!"
        net_worth = float(get_profile()['net_worth'])
    else:
        error = "An error occurred"

def initialize_shirt_shop(ui_manager):
    global net_worth, owns_shirts_list, back_btn, shirt_buttons, current_width, current_height
    current_width, current_height = pygame.display.get_window_size()
    ui_manager.clear_and_reset()
    user = get_profile()
    net_worth = float(user['net_worth'])
    owns_shirts_list = user['owns_shirts_list']
    print(owns_shirts_list)
    for index, shirt in enumerate(shirt_arr):
        shirt_buttons.append(pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((current_width // 2 - 200, 100 * index + 200), (400, 40)),
            text=f"${shirt_arr_cost[index]} {shirt}",
            manager=ui_manager,
            object_id=f"#shirt_btn_{index}",
            visible=True
        ))
        back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((current_width // 4 * 3, 100), (100, 40)),
            text="Back",
            manager=ui_manager,
            object_id="#Back",
            visible=True
        )

def draw_shirt_shop(screen, events, ui_manager):
    global net_worth, error, shirt_buttons, current_width, current_height
    draw_background(screen)
    title_text_pixel_bet = FONT.render("Shirt Shop", True, WHITE)
    screen.blit(title_text_pixel_bet, (current_width // 2 - title_text_pixel_bet.get_width() // 2, 50))
    
    title_text_pixel_bet = FONT.render(f"Money: ${net_worth:.2f}", True, WHITE)
    screen.blit(title_text_pixel_bet, (current_width // 2 - title_text_pixel_bet.get_width() // 2, 100))
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_btn:
                shirt_buttons = []
                error = None
                return "home"
            elif event.ui_element in shirt_buttons:
                index = shirt_buttons.index(event.ui_element)
                if shirt_dict[shirt_arr[index]] in owns_shirts_list:
                    error = "Shirt already owned"
                    return
                if net_worth - shirt_arr_cost[index] >= 0:
                    print(f"buying: {shirt_arr[index]}")
                    buy_shirt(index)
                else:
                    error = "Insufficient funds"

    if error:
        error_name = FONT.render(error, True, WHITE)
        screen.blit(error_name, ((current_width // 8) * 1, (current_height // 8) * 6))
                
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   
    return "shirt"
