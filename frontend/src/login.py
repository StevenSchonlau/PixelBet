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

signup_screen = False
def get_sign_up():
    return signup_screen
def set_sign_up(val):
    global signup_screen
    signup_screen = val

def register_server(username, password):
    response = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    print(response.json())

def login_server(username, password):
    response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    print(response.json())

def get_user_server(username):
    response = requests.get(f"{BASE_URL}/get-user", json={"username": username})
    print(response.json())
    print(Profile(**json.loads(str(response.json()).replace("\'","\""))).id)

def attempt_login(username, password):
    if username == "":
        return None
    if password == "":
        return None
    print(username, password)
    if username == "test" and password == "password":
        print("returned")
        return Profile("test", -1)

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
        object_id="username"
    )
    global password_field
    password_field = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 4), (SCREEN_WIDTH // 2,50)),
        manager=ui_manager,
        object_id="password"
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

    

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(event.ui_element)
            if event.ui_element == login_btn:
                print("login", username_field.get_text(), password_field.get_text())
                global user
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