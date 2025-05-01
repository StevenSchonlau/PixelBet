import pygame
import pygame_gui
from constants import *
from login import get_user
from user_session import UserSession
BASE_URL = SERVER_URL

btns = {}
networth_min = None
networth_max = None


def send_networth_email(nw, the_min, the_max):
    requests.post(f"{BASE_URL}/send-networth-email", json={"id": get_user(), "nw": nw, "min": the_min, "max": the_max})

def get_user_notification_preferences_networth():
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/get-user-notification-preferences-networth", json={"id": session.get_user()})
    preference = response.json()['preference']
    if preference is not None:
        return preference
    return False

def set_notification_preferences_networth(value):
    session = UserSession()
    requests.post(f"{SERVER_URL}/set-user-notification-preferences-networth", json={"id": session.get_user(), "preference": value})

def get_user_notification_preferences():
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/get-user-notification-preferences", json={"id": session.get_user()})
    preference = response.json()['preference']
    if preference is not None:
        return preference
    return False

def set_notification_preferences(value):
    session = UserSession()
    requests.post(f"{SERVER_URL}/set-user-notification-preferences", json={"id": session.get_user(), "preference": value})

def get_user_notification_preferences_results():
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/get-user-notification-preferences-results", json={"id": session.get_user()})
    preference = response.json()['preference']
    if preference is not None:
        return preference
    return False

def set_notification_preferences_results(value):
    session = UserSession()
    requests.post(f"{SERVER_URL}/set-user-notification-preferences-results", json={"id": session.get_user(), "preference": value})

def get_user_networth_min_max():
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/get-user-networth-min-max", json={"id": session.get_user()})
    try:
        min_max = (float(response.json()['min']), float(response.json()['max']))
        if min_max is not None:
            return min_max
        return (-1, 999)
    except:
        return (-1, 999)

def set_user_networth_min_max(the_min, the_max):
    session = UserSession()
    requests.post(f"{SERVER_URL}/set-user-networth-min-max", json={"id": session.get_user(), "min": the_min, "max": the_max})

min_val, max_val = get_user_networth_min_max()

def set_min_max_networth():
    global networth_min, networth_max, min_val, max_val
    new_min = min_val
    new_max = max_val
    if networth_min.get_text() != "":
        #try:
        new_min = float(networth_min.get_text())
        min_val = new_min
        # except:
        #     if min_val is not None:
        #         networth_min.text = min_val
        #     else:
        #         networth_min.s""
    else:
        new_min = -1
    if networth_max.get_text() != "":
        #try:
        new_max = float(networth_max.get_text())
        max_val = new_max
        # except:
        #     if max_val is not None:
        #         networth_max.text = max_val
        #     else:
        #         networth_max.text = ""
    else:
        new_max = 999
    set_user_networth_min_max(new_min, new_max)
    



def initialize_notification(ui_manager):
    ui_manager.clear_and_reset()
    #render name, button, and price for each 
    global btns,min_val,max_val
    min_val, max_val = get_user_networth_min_max()
    back_button = draw_button("Back", ui_manager, 0, 0)


    notifications_on_networth = get_user_notification_preferences_networth()
    if notifications_on_networth:
        email_notification_networth_btn = draw_button("Turn off networth notifications", ui_manager, 1.3, 2.2)
    else:
        email_notification_networth_btn = draw_button("Turn on networth notifications", ui_manager, 1.3, 2.2)

    btns["email_notification_networth_btn"] = email_notification_networth_btn

    global networth_max
    networth_max = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
        relative_rect=pygame.Rect((screen_width // 8 *5 , screen_height // 2), (screen_width // 8 * 3,50)),
        manager=ui_manager,
        object_id="networth_max",
        placeholder_text="Max"
    )
    print(min_val, max_val)
    networth_max.set_allowed_characters(['1','2','3','4','5','6','7','8','9','0','.'])
    if max_val is not None and max_val != 999:
        networth_max.set_text(f"{max_val:.2f}")

    global networth_min
    networth_min = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
        relative_rect=pygame.Rect((screen_width // 8, screen_height // 2), (screen_width // 8 * 3,50)),
        manager=ui_manager,
        object_id="networth_min",
        placeholder_text="Min"
    )
    networth_min.set_allowed_characters(['1','2','3','4','5','6','7','8','9','0','.'])
    if min_val is not None and min_val != -1:
        networth_min.set_text(f"{min_val:.2f}")

    notifications_on = get_user_notification_preferences()
    if notifications_on:
        email_notification_btn = draw_button("Turn off game start notifications", ui_manager, 1, 7)
    else:
        email_notification_btn = draw_button("Turn on game start notifications", ui_manager, 1, 7)
    btns["email_notification_btn"] = email_notification_btn

    
    notifications_on_results = get_user_notification_preferences_results()
    if notifications_on_results:
        email_notification_results_btn = draw_button("Turn off results notifications", ui_manager, 1.7, 5)
    else:
        email_notification_results_btn = draw_button("Turn on results notifications", ui_manager, 1.7, 5)
    btns["email_notification_results_btn"] = email_notification_results_btn


    btns['back_button'] = back_button






def draw_notification(screen, events, ui_manager):
    draw_background(screen)
    title_text_pixel_bet = FONT.render("Notifications", True, WHITE)
    screen.blit(title_text_pixel_bet, (screen_width // 2 - title_text_pixel_bet.get_width() // 2, 50))
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            global btns
            text = event.ui_element.text
            if text == "Turn off game start notifications":
                set_notification_preferences(False)
                event.ui_element.text = "Turn on game start notifications"
                initialize_notification(ui_manager)
            elif text == "Turn on game start notifications":
                set_notification_preferences(True)
                event.ui_element.text = "Turn off game start notifications"
                initialize_notification(ui_manager)
                
            elif text == "Turn off results notifications":
                set_notification_preferences_results(False)
                event.ui_element.text = "Turn on results notifications"
                initialize_notification(ui_manager)
            elif text == "Turn on results notifications":
                set_notification_preferences_results(True)
                event.ui_element.text = "Turn off results notifications"
                initialize_notification(ui_manager)

            elif text == "Turn off networth notifications":
                set_notification_preferences_networth(False)
                event.ui_element.text = "Turn on networth notifications"
                initialize_notification(ui_manager)
            elif text == "Turn on networth notifications":
                set_notification_preferences_networth(True)
                event.ui_element.text = "Turn off networth notifications"
                initialize_notification(ui_manager)


            elif event.ui_element == btns['back_button']:
                set_min_max_networth()
                return "View Profile"


                
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   
    return "notifications"