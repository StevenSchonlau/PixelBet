import pygame
import pygame_gui
from constants import *
from user_session import UserSession
from login import set_login_reward

pop_up_button = None
streak = 0

def get_streak():
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/get-login-streak", json={"id": session.get_user()})
    print(response)
    print(response.json())
    return response.json()['counter']

def initialize_popup(ui_manager):
    ui_manager.clear_and_reset()
    text = "Daily Login Streak"
    text_surface = FONT.render(text, True, WHITE)
    button_width = text_surface.get_width() + 40
    button_height = text_surface.get_height() + 20
    button_x = screen_height//2
    button_y = screen_height*3//4
    global pop_up_button
    pop_up_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((button_x, button_y), (button_width, button_height)),
        text="OK",
        manager=ui_manager,
        object_id="#reward",
    )
    global streak
    streak = get_streak()





def draw_popup(screen, events, ui_manager):
    draw_background(screen)
    reward = 10*(int(float(streak))+1)
    title_text = FONT.render(f"You received ${reward}!", True, WHITE)
    title_text2 = FONT.render(f"You have logged in {int(float(streak))} days in a row!", True, WHITE)
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 200))
    screen.blit(title_text2, (screen_width // 2 - title_text2.get_width() // 2, 250))
    
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == pop_up_button:
                print("accepted")
                #update money
                set_login_reward(False)


                
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   
