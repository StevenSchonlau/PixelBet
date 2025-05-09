import os
import pygame
import pygame_gui
import multipleGames
from pygame.locals import *
from game import draw_game_screen, initialize_game
from home import draw_home_screen, initialize_home
from dailyLogin import draw_popup, initialize_popup
from crypto import initialize_crypto, draw_crypto_screen
from roomShop import draw_room_shop, initialize_room_shop
from lottery import initialize_lottery, draw_lottery_screen
from friendsList import init_friends_page, draw_friends_page
from profileView import draw_view_profile, init_profile_view
from shirtShop import draw_shirt_shop, initialize_shirt_shop
from themeShop import draw_theme_shop, initialize_theme_shop
from underDev import initialize_underDev, draw_underDev_screen
from leaderboard import draw_leaderboard_page, init_leaderboard_page
from notifications import initialize_notification, draw_notification
from confirmEmail import initialize_confirming, draw_confirming_screen
from musicShop import draw_music_shop, initialize_music_shop, play_music
from constants import screen_width, screen_height, FPS, BLACK, THEME_PATH
from passwordReset import initialize_password_reset, draw_password_reset_screen
from achievements import initialize_achievement_popup, draw_achievement_popup, get_ach_popup, GLOBAL_ACHIEVEMENTS
from signup import draw_signup_screen, initialize_signup, get_sign_up_success, get_back_to_login, set_back_to_login, get_confirming, set_confirming
from settings import initialize_settings, draw_settings_screen, is_resolution_set, fetch_user_resolution, set_resolution_marker, is_button_sound_enabled
from timeLimits import initialize_time_limit, draw_time_limit, process_time_limit, init_time_limit, initialize_time_limit_reached, draw_time_limit_reached, reset_time
from login import draw_login_screen, initialize_login, get_user, get_sign_up, set_sign_up, set_password_reset, get_password_reset, get_login_reward, set_login_reward, clear_user

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("PixelBet")
icon_path = os.path.join('frontend\\assets\\images', "pixelbet_logo.jpeg")  # Update path if needed
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)
else:
    print("Warning: Icon file not found!")

ui_manager = pygame_gui.UIManager((screen_width, screen_height), THEME_PATH)
ui_manager.clear_and_reset()
initialized = "None"
current_screen = "login"
selected_game = None
login_reward = False
music_playing = False

pygame.mixer.init()
button_click_sound = pygame.mixer.Sound("./frontend/assets/effects/buttonClick.wav")

def main():
    global initialized, current_screen, selected_game, show_achievement_popup ,GLOBAL_ACHIEVEMENTS, screen
    clock = pygame.time.Clock()
    running = True
    print(GLOBAL_ACHIEVEMENTS)

    while running:
        time_delta = clock.tick(FPS) / 1000.0  # pygame_gui needs delta time
        events = pygame.event.get()  # Collect all events
        
        for event in events:
            if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED and is_button_sound_enabled():
                button_click_sound.play()
            if event.type == VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h))
                ui_manager.set_window_resolution((event.w, event.h))
                print("Resized to:", event.w, event.h)
            #print(event)
            if event.type == pygame.QUIT:
                running = False
            ui_manager.process_events(event)
        global music_playing
        
        if get_user() is not None:
            if initialized == "login":
                init_time_limit()
            if not music_playing:
                play_music()
                music_playing = True
            if not is_resolution_set():
                set_resolution_marker(True)
                res = fetch_user_resolution()
                width, height = map(int, res.split('x'))
                new_resolution = (width, height)
                pygame.display.set_mode(new_resolution)
                ui_manager.set_window_resolution((width, height))
            if get_login_reward():
                #show login_reward
                if initialized != "dailyLogin":
                    reset_time()
                    initialize_popup(ui_manager)
                    initialized = "dailyLogin"
                draw_popup(screen, events, ui_manager)
            elif process_time_limit(time_delta) == "time limit reached":
                #draw time up screen
                if initialized != "time limit reached":
                    initialize_time_limit_reached(ui_manager)
                    initialized = "time limit reached"
                if draw_time_limit_reached(screen, events, ui_manager) == "signout":
                    clear_user()
            elif get_ach_popup():
                if initialized != "achievement":
                    print("initializing achievement popup")
                    initialize_achievement_popup(ui_manager)
                    initialized = "achievement"
                draw_achievement_popup(screen, events, ui_manager)
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
                elif selected_game == "notifications":
                    if initialized != "notifications":
                        initialize_notification(ui_manager)
                        initialized = "notifications"
                    selected_game = draw_notification(screen, events, ui_manager)
                elif selected_game == "time limit":
                    if initialized != "time limit":
                        initialize_time_limit(ui_manager)
                        initialized = "time limit"
                    selected_game = draw_time_limit(screen, events, ui_manager)
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
                elif selected_game == "shirt":
                    if initialized != "shirt":
                        initialize_shirt_shop(ui_manager)
                        initialized = "shirt"
                    shirt_result = draw_shirt_shop(screen, events, ui_manager)

                    if shirt_result == "home":  # If "Back" is pressed in crypto, return to home
                        selected_game = None
                        initialize_home(ui_manager)
                        initialized = "home"
                elif selected_game == "room":
                    if initialized != "room":
                        initialize_room_shop(ui_manager)
                        initialized = "room"
                    room_result = draw_room_shop(screen, events, ui_manager)

                    if room_result == "home":  # If "Back" is pressed in crypto, return to home
                        selected_game = None
                        initialize_home(ui_manager)
                        initialized = "home"
                elif selected_game == "theme":
                    if initialized != "theme":
                        initialize_theme_shop(ui_manager)
                        initialized = "theme"
                    theme_result = draw_theme_shop(screen, events, ui_manager)

                    if theme_result == "home":  # If "Back" is pressed in crypto, return to home
                        selected_game = None
                        initialize_home(ui_manager)
                        initialized = "home"
                elif selected_game == "lottery":
                    if initialized != "lottery":
                        initialize_lottery(ui_manager)
                        initialized = "lottery"
                    lottery_result = draw_lottery_screen(screen, events, ui_manager)

                    if lottery_result == "home":  # If "Back" is pressed in lottery, return to home
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

                elif selected_game == "settings":
                    if initialized != "settings":
                        initialize_settings(ui_manager)
                        initialized = "settings"
                    selected_game = draw_settings_screen(screen, events, ui_manager, selected_game)

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
            music_playing = False
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
