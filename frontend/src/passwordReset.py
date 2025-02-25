import pygame_gui.elements.ui_text_entry_line
import requests
from constants import SERVER_URL
from profile import Profile
import json
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, FONT
import pygame
import pygame_gui
from signup import get_user, set_back_to_login
from login import set_password_reset
from http_client import session
from datetime import datetime


BASE_URL = SERVER_URL #where server is running

error_message = ""


#TODO - create field to enter email and send button that calls /reset-password in auth.py server side


back_to_login_btn = None
email_txt_field =None
send_btn = None
sent = False

#initialize buttons
def initialize_password_reset(ui_manager):
    ui_manager.clear_and_reset()
    global back_to_login_btn 
    back_to_login_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 6), (SCREEN_WIDTH // 2,50)),
        text="Back to Login",
        manager=ui_manager,
        object_id="back_to_login",
    )
    global email_txt_field
    email_txt_field = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 4), (SCREEN_WIDTH // 2,50)),
        manager=ui_manager,
        object_id="email_txt",
        placeholder_text="email@somewhere.com"
    )
    global send_btn
    send_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 5), (SCREEN_WIDTH // 2,50)),
        text="Send Email",
        manager=ui_manager,
        object_id="back_to_login",
    )

def send_reset_email(email):
    response = requests.post(f"{BASE_URL}/reset-password", json={"email": email})
    return response

def draw_password_reset_screen(screen, events, ui_manager):
    screen.fill(BLACK)
    title_text = FONT.render("Password Reset", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

    instruction1 = FONT.render("Go to your email and", True, WHITE)
    screen.blit(instruction1, (SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 2))
    instruction2 = FONT.render("click on the link!", True, WHITE)
    screen.blit(instruction2, (SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 3))

    global error_message
    
    error_message_text = FONT.render(error_message, True, WHITE)
    screen.blit(error_message_text, (SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 7))
    global sent
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(event.ui_element)
            if event.ui_element == back_to_login_btn:
                print("back")
                error_message = ""
                set_password_reset(False)
                set_back_to_login(True) 
            if event.ui_element == send_btn and not sent:
                print("sending")
                error_message = "Loading..."
                screen.fill(BLACK) #to cover last error message
                title_text = FONT.render("Password Reset", True, WHITE)
                screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

                instruction1 = FONT.render("Go to your email and", True, WHITE)
                screen.blit(instruction1, (SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 2))
                instruction2 = FONT.render("click on the link!", True, WHITE)
                screen.blit(instruction2, (SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 3))
                error_message_text = FONT.render(error_message, True, WHITE)
                screen.blit(error_message_text, (SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 7))
                ui_manager.update(1 / 60)
                ui_manager.draw_ui(screen)

                pygame.display.flip() 
                response = send_reset_email(email_txt_field.get_text())
                if "invalid" in str(response.json()):
                    if email_txt_field.get_text() == "":
                        error_message = "Email cannot be empty"
                    elif "@" not in email_txt_field.get_text() or "." not in email_txt_field.get_text():
                        error_message = "Email not formatted correctly"
                elif "Non-Existent" in str(response.json()):
                    error_message = "Account doesn't exist"
                else:
                    error_message = "Sent! Go back to login"
                    sent = True
          
    

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   
