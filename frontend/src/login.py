import pygame_gui.elements.ui_text_entry_line
import requests
from constants import SERVER_URL
from profile import Profile
import json
from constants import *
import pygame
import pygame_gui
from user_session import UserSession
from timeLimits import end_time_limit

BASE_URL = SERVER_URL #where server is running

login_reward = False
def get_login_reward():
    return login_reward
def set_login_reward(val):
    global login_reward
    login_reward = val

user = None
def get_user():
    return user

#failed login
error_message = ""
def clear_user():
    end_time_limit()
    global user
    user = None
    global error_message
    error_message = ""

signup_screen = False
def get_sign_up():
    return signup_screen
def set_sign_up(val):
    global signup_screen
    signup_screen = val

password_reset_screen = False
def get_password_reset():
    return password_reset_screen
def set_password_reset(val):
    global password_reset_screen
    password_reset_screen = val

def login_server(username, password):
    print("true", username, password)
    response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    print(response.json())
    return response

def attempt_login(username, password):
    print("Attempted login")
    global error_message
    session = UserSession()

    if username == "":
        error_message = "Username cannot be blank"
        return None
    if password == "":
        error_message = "Password cannot be blank"
        return None
    if username == "test" and password == "password": #bypass
        print("bypass server")
        error_message = ""
        session.set_user("00000000-0000-0000-0000-000000000000")
        return session.get_user()
    else:
        response = login_server(username, password)
        if "denied" in str(response.json()):
            error_message = "Incorrect credentials"
            return None
        print(response.json())
        if "True" in response.json()["updated_streak"]:
            global login_reward
            login_reward = True
        session.set_user(response.json()['user_id'])
        #Start music https://www.pygame.org/docs/ref/music.html#pygame.mixer.music.play based on users preference
        return session.get_user()

#global vars for buttons
login_btn = None
username_field = None
password_field = None
sign_up_screen_btn = None
reset_password_btn = None



#initialize buttons
def initialize_login(ui_manager):
    ui_manager.clear_and_reset()
    text_surface = FONT.render("Login", True, WHITE)
    global login_btn 
    login_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 5), (SCREEN_WIDTH // 2,50)),
        text="Login",
        manager=ui_manager,
        object_id="login",
    )
    global username_field
    username_field = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 3), (SCREEN_WIDTH // 2,50)),
        manager=ui_manager,
        object_id="username",
        placeholder_text="username"
    )
    global password_field
    password_field = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 4), (SCREEN_WIDTH // 2,50)),
        manager=ui_manager,
        object_id="password",
        placeholder_text="password"
    )
    global sign_up_screen_btn 
    sign_up_screen_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 6), (SCREEN_WIDTH // 2,50)),
        text="Sign Up",
        manager=ui_manager,
        object_id="sign_up_screen",
    )
    global reset_password_btn 
    reset_password_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 7), (SCREEN_WIDTH // 2,50)),
        text="Reset Password",
        manager=ui_manager,
        object_id="password_reset",
    )

def draw_login_screen(screen, events, ui_manager):
    draw_background(screen)
    title_text = FONT.render("Login", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

    title_text_pixel_bet = FONT.render("PixelBet", True, GREEN)
    screen.blit(title_text_pixel_bet, (SCREEN_WIDTH // 2 - title_text_pixel_bet.get_width() // 2, 50))
    global error_message
    fail_text = FONT.render(error_message, True, WHITE)
    screen.blit(fail_text, (SCREEN_WIDTH // 2 - fail_text.get_width() // 2, SCREEN_HEIGHT // 8 * 2))


    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(event.ui_element)
            if event.ui_element == login_btn:
                print("login", username_field.get_text(), password_field.get_text())
                global user
                error_message = "Loading..."
                draw_background(screen)
                title_text = FONT.render("Login", True, WHITE)
                screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
                error_message_text = FONT.render(error_message, True, WHITE)
                screen.blit(error_message_text, (SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 2))
                ui_manager.update(1 / 60)
                ui_manager.draw_ui(screen)

                pygame.display.flip() 
                user = attempt_login(username_field.get_text(), password_field.get_text())
                print(user)
            if event.ui_element == sign_up_screen_btn:
                print("signup")
                global signup_screen
                signup_screen = True
                error_message = ""
            if event.ui_element == reset_password_btn:
                print("reset password")
                global password_reset_screen
                password_reset_screen = True
                error_message = ""

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   

# Example usage:
#register("testuser2", "securepassword123")
#login("testuser", "unsecurepassword")
#get_user("testuser2")