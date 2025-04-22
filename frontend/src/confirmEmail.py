import pygame_gui.elements.ui_text_entry_line
import requests
from constants import SERVER_URL
from profile import Profile
import json
from constants import *
import pygame
import pygame_gui
from signup import get_user, set_back_to_login
from http_client import session
from datetime import datetime


BASE_URL = SERVER_URL #where server is running

signup_success = False
def get_sign_up_success():
    return signup_success

# back_to_login = False
# def get_back_to_login_from_confirm():
#     return back_to_login
# def set_back_to_login_from_confirm(val):
#     global back_to_login
#     back_to_login = val

error_message = ""

last_email_check = datetime.utcnow()

future = None

not_confirmed = True

def check_email():
    print("running")
    try:
        response = session.get(f"{BASE_URL}/check-confirmation", json={"id": get_user()})
        #response.result()
        return response
    except:
        return None
    #     print("still")
    #     data = response.json()
    #     print(data)
    #     confirm = data.get("message")
    #     if confirm == "confirmed":
    #         return True
    #     print(confirm)
    #     return False
    # except:
    #     print('error')
    #     return False
    

def resend_email():
    response = requests.post(f"{BASE_URL}/reset-time", json={"id": get_user()})
    return response

#global vars for buttons
resend_btn = None
back_to_login_btn = None

#initialize buttons
def initialize_confirming(ui_manager):
    ui_manager.clear_and_reset()
    global resend_btn 
    resend_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((screen_width // 4 , screen_height // 8 * 5), (screen_width // 2,50)),
        text="Resend",
        manager=ui_manager,
        object_id="resend_btn",
    )
    global back_to_login_btn 
    back_to_login_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((screen_width // 4 , screen_height // 8 * 6), (screen_width // 2,50)),
        text="Back to Login",
        manager=ui_manager,
        object_id="back_to_login",
    )

def draw_confirming_screen(screen, events, ui_manager):
    draw_background(screen)
    title_text = FONT.render("Email Confirmation", True, WHITE)
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))

    instruction1 = FONT.render("Go to your email and", True, WHITE)
    screen.blit(instruction1, (screen_width // 4 , screen_height // 8 * 3))
    instruction2 = FONT.render("click on the link!", True, WHITE)
    screen.blit(instruction2, (screen_width // 4 , screen_height // 8 * 4))

    global error_message
    
    error_message_text = FONT.render(error_message, True, WHITE)
    screen.blit(error_message_text, (screen_width // 4 , screen_height // 8 * 7))

    global resend_btn
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(event.ui_element)
            if event.ui_element == back_to_login_btn:
                print("back")
                error_message = ""
                set_back_to_login(True)
            if event.ui_element == resend_btn:
                response = resend_email()           
    global future
    global last_email_check
    global not_confirmed
    if (datetime.utcnow() - last_email_check).seconds > 2 and not_confirmed:
        if future and future.done():
            response = future.result()
            data = response.json()
            print(data)
            confirm = data.get("message")
            if confirm == "confirmed":
                print("Email confirmed!")
                error_message = "Confirmed, go back to login"
                resend_btn.visible = False
                not_confirmed = False
        print(future)
        last_email_check = datetime.utcnow()
        future = check_email()
          
    

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   
