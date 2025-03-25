import pygame
import pygame_gui
import os
from pygame.locals import *
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, THEME_PATH
from home import draw_home_screen, initialize_home
from game import draw_game_screen, initialize_game
from login import draw_login_screen, initialize_login, get_user, get_sign_up, set_sign_up, set_password_reset, get_password_reset, get_login_reward, set_login_reward
from signup import draw_signup_screen, initialize_signup, get_sign_up_success, get_back_to_login, set_back_to_login, get_confirming, set_confirming
from confirmEmail import initialize_confirming, draw_confirming_screen
from passwordReset import initialize_password_reset, draw_password_reset_screen
from profileView import draw_view_profile, init_profile_view
from crypto import initialize_crypto, draw_crypto_screen
from underDev import initialize_underDev, draw_underDev_screen
from friendsList import init_friends_page, draw_friends_page
from leaderboard import draw_leaderboard_page, init_leaderboard_page
from dailyLogin import draw_popup, initialize_popup
from musicShop import draw_music_shop, initialize_music_shop
import multipleGames

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
initialized = "None"
current_screen = "login"
selected_game = None
login_reward = False
def main():
    global initialized, current_screen, selected_game
    clock = pygame.time.Clock()
    running = True


    while running:
        time_delta = clock.tick(FPS) / 1000.0  # pygame_gui needs delta time
        events = pygame.event.get()  # Collect all events
        
        for event in events:
            #print(event)
            if event.type == pygame.QUIT:
                print ("main quit")
                running = False
            ui_manager.process_events(event)

        screen.fill(BLACK)  # Clear screen
        
        if get_user() is not None:
            if get_login_reward():
                #show login_reward
                if initialized != "dailyLogin":
                    initialize_popup(ui_manager)
                    initialized = "dailyLogin"
                draw_popup(screen, events, ui_manager)
            else:
                if selected_game is None:  # Home screen logic
                    if initialized != "home":
                        initialize_home(ui_manager)
                        initialized = "home"
                    selected_game = draw_home_screen(screen, events, ui_manager)  # If a game is selected, it will return a value

                elif selected_game == "View Profile":
                    if initialized != "profile-view":
                        init_profile_view(ui_manager)
                        initialized = "profile-view"
                    selected_game = draw_view_profile(screen, events, ui_manager, selected_game)
                elif selected_game == "Friends":
                    if initialized != "friends":
                        init_friends_page(ui_manager)
                        initialized = "friends"
                    selected_game = draw_friends_page(screen, events, ui_manager, selected_game)
                elif selected_game == "Leaderboard":
                    if initialized != "leaderboard":
                        init_leaderboard_page(ui_manager)
                        initialized = "leaderboard"
                    selected_game = draw_leaderboard_page(screen, events, ui_manager, selected_game)
                elif selected_game == "crypto":
                    if initialized != "crypto":
                        initialize_crypto(ui_manager)
                        initialized = "crypto"
                    crypto_result = draw_crypto_screen(screen, events, ui_manager)

                    if crypto_result == "home":  # If "Back" is pressed in crypto, return to home
                        selected_game = None
                        initialize_home(ui_manager)
                        initialized = "home"
                elif selected_game == "music":
                    if initialized != "music":
                        initialize_music_shop(ui_manager)
                        initialized = "music"
                    music_result = draw_music_shop(screen, events, ui_manager)

                    if music_result == "home":  # If "Back" is pressed in crypto, return to home
                        selected_game = None
                        initialize_home(ui_manager)
                        initialized = "home"
                elif selected_game == "underDev":
                    if initialized != "underDev":
                        initialize_underDev(ui_manager)
                        initialized = "underDev"
                    selected_game = draw_underDev_screen(screen, events, ui_manager, selected_game)

                    if selected_game == "home":  # If "Back" is pressed in crypto, return to home
                        selected_game = None
                        initialize_home(ui_manager)
                        initialized = "home"

                elif selected_game == "multiple_games":
                    if initialized != "multiple_games":
                        multipleGames.prompt_user_for_derbies(ui_manager)
                        initialized = "multiple_games"
                    multiple_games_result = multipleGames.draw_multiple_games_screen(screen, events, ui_manager)
                    
                    if multiple_games_result == "home":  # If "Back" is pressed in multiple games, return to home
                        selected_game = None
                        initialize_home(ui_manager)
                        initialized = "home"

                else:  # A game is selected, display game screen
                    if initialized != "game":
                        initialize_game(ui_manager)
                        initialized = "game"
                    game_result = draw_game_screen(screen, events, ui_manager, selected_game)

                    if game_result is None:  # If "Back" is pressed in game, return to home
                        selected_game = None
                        initialize_home(ui_manager)
                        initialized = "home"
        else:
            if not get_password_reset():
                if not get_sign_up():
                    if get_back_to_login(): #reset when back at login
                        set_back_to_login(False)
                        set_confirming(False)
                        set_password_reset(False)
                    if initialized != "login":
                        initialize_login(ui_manager)
                        initialized = "login"
                    draw_login_screen(screen, events, ui_manager)
                else:
                    if get_back_to_login():
                        set_sign_up(False)
                    if get_confirming():
                        if initialized != "confirming":
                            initialize_confirming(ui_manager)
                            initialized = "confirming"
                        draw_confirming_screen(screen, events, ui_manager)
                    else: 
                        if initialized != "signup":
                            initialize_signup(ui_manager)
                            initialized = "signup"
                        draw_signup_screen(screen, events, ui_manager)
            else: #password reset
                if initialized != "password_reset":
                    initialize_password_reset(ui_manager)
                    initialized = "password_reset"
                draw_password_reset_screen(screen, events, ui_manager)

        ui_manager.update(time_delta)  # Update pygame_gui
        ui_manager.draw_ui(screen)  # Draw UI elements
        
        pygame.display.flip()


if __name__ == "__main__":
    main()