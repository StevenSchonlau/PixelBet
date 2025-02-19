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

signup_success = False
def get_sign_up_success():
    return signup_success

back_to_login = False
def get_back_to_login():
    return back_to_login
def set_back_to_login(val):
    global back_to_login
    back_to_login = val


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


#global vars for buttons
username_field = None
password_field = None
sign_up_btn = None
back_to_login_btn = None

#initialize buttons
def initialize_signup(ui_manager):
    ui_manager.clear_and_reset()
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
    global sign_up_btn 
    sign_up_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 5), (SCREEN_WIDTH // 2,50)),
        text="Sign Up",
        manager=ui_manager,
        object_id="sign_up",
    )
    global back_to_login_btn 
    back_to_login_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 4 , SCREEN_HEIGHT // 8 * 6), (SCREEN_WIDTH // 2,50)),
        text="Back to Login",
        manager=ui_manager,
        object_id="back_to_login",
    )

def draw_signup_screen(screen, events, ui_manager):
    screen.fill(BLACK)
    title_text = FONT.render("Sign Up", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

    

    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(event.ui_element)
            if event.ui_element == back_to_login_btn:
                print("back")
                global back_to_login
                back_to_login = True
            if event.ui_element == sign_up_btn:
                print("signup")
            

    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   

# Example usage:
#register("testuser2", "securepassword123")
#login("testuser", "unsecurepassword")
#get_user("testuser2")