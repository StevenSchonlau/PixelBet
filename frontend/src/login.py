import pygame_gui.elements.ui_text_entry_line
import requests
from constants import SERVER_URL
from profile import Profile
import json
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, FONT
import pygame
import pygame_gui

BASE_URL = SERVER_URL #where server is running



user = None
def get_user():
    return user

#failed login
error_message = ""

signup_screen = False
def get_sign_up():
    return signup_screen
def set_sign_up(val):
    global signup_screen
    signup_screen = val

def login_server(username, password):
    print("true", username, password)
    response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    print(response.json())
    return response

def attempt_login(username, password):
    global error_message
    if username == "":
        error_message = "Username cannot be blank"
        return None
    if password == "":
        error_message = "Password cannot be blank"
        return None
    if username == "test" and password == "password": #bypass
        print("bypass server")
        error_message = ""
        return "00000000-0000-0000-0000-000000000000"
    else:
        response = login_server(username, password)
        if "denied" in str(response.json()):
            error_message = "Incorrect credentials"
            return None
        return response.json()['user_id']

#global vars for buttons
login_btn = None
username_field = None
password_field = None
sign_up_screen_btn = None


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

def draw_login_screen(screen, events, ui_manager):
    screen.fill(BLACK)
    title_text = FONT.render("Login", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

    global error_message
    fail_text = FONT.render(error_message, True, WHITE)
    screen.blit(fail_text, (SCREEN_WIDTH // 2 - fail_text.get_width() // 2, SCREEN_HEIGHT // 8 * 7))


    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(event.ui_element)
            if event.ui_element == login_btn:
                print("login", username_field.get_text(), password_field.get_text())
                global user
                error_message = "Loading..."
                user = attempt_login(username_field.get_text(), password_field.get_text())
                print(user)
            if event.ui_element == sign_up_screen_btn:
                print("signup")
                global signup_screen
                signup_screen = True

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   

# Example usage:
#register("testuser2", "securepassword123")
#login("testuser", "unsecurepassword")
#get_user("testuser2")