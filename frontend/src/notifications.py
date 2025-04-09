import pygame
import pygame_gui
from constants import *
from user_session import UserSession

btns = {}

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



def initialize_notification(ui_manager):
    ui_manager.clear_and_reset()
    #render name, button, and price for each 
    global btns, music_arr
    back_button = draw_button("Back", ui_manager, 0, 0)

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
    screen.blit(title_text_pixel_bet, (SCREEN_WIDTH // 2 - title_text_pixel_bet.get_width() // 2, 50))
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            global btns, music_arr, music_owned
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

            elif event.ui_element == btns['back_button']:
                return "View Profile"


                
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   
    return "notifications"