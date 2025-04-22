import pygame
import pygame_gui
from constants import *
from notifications import get_user_networth_min_max, send_networth_email

net_worth = 0
themes = ["Red", "Green", "Purple", "Gold"]
theme_dict = {"Red": "red", "Green": "green", "Purple": "purple", "Gold": "gold"}
theme_cost = [10, 10, 10, 50]
owns_themes = []
back_btn = None
theme_buttons = []
error = None
current_width, current_height = 0, 0

def buy_theme(index):
    global error, net_worth, theme_dict, theme_cost, themes
    data = {
        "cost": theme_cost[index],
        "theme": theme_dict[themes[index]],
    }
    the_min, the_max = get_user_networth_min_max()
    new_nw = net_worth - theme_cost[index]
    response = requests.post(f"{SERVER_URL}/profile/buytheme/{get_profile()['id']}", json=data)
    if response.status_code == 200:
        if new_nw < the_min:
            send_networth_email(new_nw, the_min, -1)
        elif new_nw > the_max:
            send_networth_email(new_nw, -1, the_max)
        error = "Success!"
        net_worth = float(get_profile()['net_worth'])
    else:
        error = "An error occurred"

def initialize_theme_shop(ui_manager):
    global net_worth, owns_themes, back_btn, theme_buttons, current_width, current_height
    current_width, current_height = pygame.display.get_window_size()
    ui_manager.clear_and_reset()
    user = get_profile()
    net_worth = float(user['net_worth'])
    owns_themes = user['owns_themes']
    print(owns_themes)
    for index, theme in enumerate(themes):
        theme_buttons.append(pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((current_width // 2 - 200, 50 * index + 200), (400, 40)),
            text=f"${theme_cost[index]} {theme}",
            manager=ui_manager,
            object_id=f"#theme_btn_{index}",
            visible=True
        ))
        back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((current_width // 4 * 3, 100), (100, 40)),
            text="Back",
            manager=ui_manager,
            object_id="#Back",
            visible=True
        )

def draw_theme_shop(screen, events, ui_manager):
    global net_worth, error, theme_buttons, current_width, current_height
    draw_background(screen)
    title_text_pixel_bet = FONT.render("Theme Shop", True, WHITE)
    screen.blit(title_text_pixel_bet, (current_width // 2 - title_text_pixel_bet.get_width() // 2, 50))
    
    title_text_pixel_bet = FONT.render(f"Money: ${net_worth:.2f}", True, WHITE)
    screen.blit(title_text_pixel_bet, (current_width // 2 - title_text_pixel_bet.get_width() // 2, 100))
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == back_btn:
                theme_buttons = []
                error = None
                return "home"
            elif event.ui_element in theme_buttons:
                index = theme_buttons.index(event.ui_element)
                if theme_dict[themes[index]] in owns_themes:
                    error = "Theme already owned"
                    return
                if net_worth - theme_cost[index] >= 0:
                    print(f"buying: {themes[index]}")
                    buy_theme(index)
                else:
                    error = "Insufficient funds"

    if error:
        error_name = FONT.render(error, True, WHITE)
        screen.blit(error_name, ((current_width // 8) * 1, (current_height // 8) * 6))
                
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   
    return "theme"
