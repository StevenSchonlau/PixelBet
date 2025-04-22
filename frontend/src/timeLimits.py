import pygame
import pygame_gui
from constants import *
from user_session import UserSession
BASE_URL = SERVER_URL

btns = {}
has_time_limit = None
time_limit = None
total_day_time = None


def get_user_has_time_limit():
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/get-user-has-time-limit", json={"id": session.get_user()})
    preference = bool(response.json()['preference'])
    if preference is not None:
        has_time_limit = preference
        return preference
    return False

def set_user_has_time_limit(value):
    session = UserSession()
    requests.post(f"{SERVER_URL}/set-user-has-time-limit", json={"id": session.get_user(), "preference": value})

def get_user_time_limit():
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/get-user-time-limit", json={"id": session.get_user()})
    try:
        new_time = int(response.json()['time limit'])
        if new_time is not None:
            return new_time
        return 99999
    except:
        return 99999

def set_user_time_limit(new_time):
    session = UserSession()
    requests.post(f"{SERVER_URL}/set-user-time-limit", json={"id": session.get_user(), "time limit": new_time})

time_limit = get_user_time_limit()

def set_time_limit():
    global time_limit
    new_time = time_limit
    if time_limit_field.get_text() != "":
        #try:
        new_time = int(time_limit_field.get_text())
        time_limit = new_time
    else:
        new_time = 99999
    set_user_time_limit(new_time)
    

def set_user_total_time_day(new_time):
    session = UserSession()
    requests.post(f"{SERVER_URL}/set-user-total-time-day", json={"id": session.get_user(), "total time": int(new_time)})

def get_user_total_time_day():
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/get-user-total-time-day", json={"id": session.get_user()})
    try:
        new_time = float(response.json()['total time'])
        print(new_time)
        if new_time is not None:
            return new_time
        return -1
    except:
        return -1

def init_time_limit():
    global total_day_time, has_time_limit, time_limit
    total_day_time = get_user_total_time_day()
    time_limit = get_user_time_limit()
    has_time_limit = get_user_has_time_limit()

def process_time_limit(time_delta):
    global total_day_time, time_limit, has_time_limit
    if has_time_limit and total_day_time + time_delta > time_limit *60:
        #time is up
        print(f"TIME LIMIT REACHED of {total_day_time} seconds {time_limit} minutes and {has_time_limit} for has time limit value")
        return "time limit reached"
    else:
        print(f"TIME LIMIT not REACHED of {total_day_time} seconds {time_limit} minutes and {has_time_limit} for has time limit value")
        total_day_time += time_delta
        return "time limit not reached"

def end_time_limit():
    global total_day_time
    set_user_total_time_day(total_day_time)


def initialize_time_limit(ui_manager):
    ui_manager.clear_and_reset()
    #render name, button, and price for each 
    global btns,time_limit
    time_limit = get_user_time_limit()
    back_button = draw_button("Back", ui_manager, 0, 0)


    has_time_limit = get_user_has_time_limit()
    if has_time_limit:
        time_limit_btn = draw_button("Turn off time limit", ui_manager, 2.1, 3)
    else:
        time_limit_btn = draw_button("Turn on time limit", ui_manager, 2.1, 3)

    btns["email_notification_networth_btn"] = time_limit_btn

    global time_limit_field
    time_limit_field = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 8 *2 , SCREEN_HEIGHT // 8 * 3.8), (SCREEN_WIDTH // 8 * 4,50)),
        manager=ui_manager,
        object_id="time_limit",
        placeholder_text="Limit (minutes)"
    )
    time_limit_field.set_allowed_characters(['1','2','3','4','5','6','7','8','9','0'])
    if time_limit is not None and time_limit != 99999:
        time_limit_field.set_text(f"{time_limit}")

    btns['back_button'] = back_button






def draw_time_limit(screen, events, ui_manager):
    draw_background(screen)
    global btns, has_time_limit
    title_text_pixel_bet = FONT.render("Time Limit", True, WHITE)
    screen.blit(title_text_pixel_bet, (SCREEN_WIDTH // 2 - title_text_pixel_bet.get_width() // 2, SCREEN_HEIGHT //8 * 1))
    if has_time_limit:
        time_left_txt = FONT.render(f"Time Left: {(time_limit * 60 - total_day_time):.2f}", True, WHITE)
        screen.blit(time_left_txt, (SCREEN_WIDTH // 2 - time_left_txt.get_width() // 2, SCREEN_HEIGHT // 8 * 2))
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            text = event.ui_element.text
            if text == "Turn off time limit":
                set_user_has_time_limit(False)
                event.ui_element.text = "Turn on time limit"
                set_time_limit()
                has_time_limit = False
                initialize_time_limit(ui_manager)
            elif text == "Turn on time limit":
                set_user_has_time_limit(True)
                event.ui_element.text = "Turn off time limit"
                set_time_limit()
                has_time_limit = True
                initialize_time_limit(ui_manager)
                

            elif event.ui_element == btns['back_button']:
                set_time_limit()
                return "View Profile"


                
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   
    return "time limit"



def add_time(minutes):
    global time_limit
    time_limit = get_user_time_limit() + minutes
    set_user_time_limit(time_limit)


def initialize_time_limit_reached(ui_manager):
    ui_manager.clear_and_reset()
    #render name, button, and price for each 
    global btns,time_limit
    time_limit = get_user_time_limit()
    ok_button = draw_button("Ok", ui_manager, 0, 0)


    add_10_btn = draw_button("Add 10 Minutes", ui_manager, 2, 2.2)

    btns["add_10_button"] = add_10_btn

    btns['ok_button'] = ok_button






def draw_time_limit_reached(screen, events, ui_manager):
    draw_background(screen)
    title_text_pixel_bet = FONT.render("Time Limit Reached", True, WHITE)
    screen.blit(title_text_pixel_bet, (SCREEN_WIDTH // 2 - title_text_pixel_bet.get_width() // 2, 50))
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            global btns
            text = event.ui_element.text
            if text == "Add 10 Minutes":
                add_time(10)
                return "home"                
            elif event.ui_element == btns['ok_button']:
                end_time_limit() #push time spent to backend
                return "signout"


                
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   
    return "time limit"


def reset_time():
    global total_day_time
    total_day_time = 0
    set_user_total_time_day(total_day_time)