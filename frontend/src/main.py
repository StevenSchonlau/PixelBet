import pygame
import pygame_gui
import os
from pygame.locals import *
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, THEME_PATH
from home import draw_home_screen
from login import draw_login_screen, initialize_login, get_user, get_sign_up, set_sign_up, set_password_reset, get_password_reset
from signup import draw_signup_screen, initialize_signup, get_sign_up_success, get_back_to_login, set_back_to_login, get_confirming, set_confirming
from confirmEmail import initialize_confirming, draw_confirming_screen
from passwordReset import initialize_password_reset, draw_password_reset_screen

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PixelBet")
icon_path = os.path.join('frontend\\assets\\images', "pixelbet_logo.jpeg")  # Update path if needed
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)
else:
    print("Warning: Icon file not found!")

ui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), THEME_PATH)
ui_manager.clear_and_reset()
intialized = "None"
def main():
    clock = pygame.time.Clock()
    running = True


    while running:
        time_delta = clock.tick(FPS) / 1000.0  # pygame_gui needs delta time
        events = pygame.event.get()  # Collect all events
        
        for event in events:
            #print(event)
            if event.type == pygame.QUIT:
                running = False
            ui_manager.process_events(event)

        screen.fill(BLACK)  # Clear screen
        global intialized
        if get_user() is not None:
            draw_home_screen(screen, events, ui_manager)  # Pass events and ui_manager
        else:
            if not get_password_reset():
                if not get_sign_up():
                    if get_back_to_login(): #reset when back at login
                        set_back_to_login(False)
                        set_confirming(False)
                        set_password_reset(False)
                    if intialized != "login":
                        initialize_login(ui_manager)
                        intialized = "login"
                    draw_login_screen(screen, events, ui_manager)
                else:
                    if get_back_to_login():
                        set_sign_up(False)
                    if get_confirming():
                        if intialized != "confirming":
                            initialize_confirming(ui_manager)
                            intialized = "confirming"
                        draw_confirming_screen(screen, events, ui_manager)
                    else: 
                        if intialized != "signup":
                            initialize_signup(ui_manager)
                            intialized = "signup"
                        draw_signup_screen(screen, events, ui_manager)
            else: #password reset
                if intialized != "password_reset":
                    initialize_password_reset(ui_manager)
                    intialized = "password_reset"
                draw_password_reset_screen(screen, events, ui_manager)

        ui_manager.update(time_delta)  # Update pygame_gui
        ui_manager.draw_ui(screen)  # Draw UI elements
        
        pygame.display.flip()


if __name__ == "__main__":
    main()