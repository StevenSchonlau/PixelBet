import pygame
import pygame_gui
from constants import *
from user_session import UserSession
from game import fetch_net_worth, update_net_worth

net_worth = 0
music_arr = ["Country Jam", "Funky Rock", "Arcade"]
music_arr_path_name = ["country-fun.mp3", "out-on-the-farm.mp3", "arcade-kid.mp3"]
music_arr_cost = [10, 20, 100]
btns = [] #holds buttons for each to buy/select if (un)owned
music_owned = [] #1's and 0's for owning or not owning music respectively
the_net_worth = 0
selected_btn = -1

def get_music_owned():
    #get the music owned and append 0 to music_owned if unowned, 1 if owned
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/get-music-owned", json={"id": session.get_user()})
    print(response)
    print(response.json())
    music_list = response.json()['music'].split(',')
    global music_owned
    music_owned = []
    for m in music_arr:
        if m in music_list:
            music_owned.append(1)
        else:
            music_owned.append(0)
    return music_owned

def buy_music(index):
    global the_net_worth, music_arr_cost, music_owned, btns
    if the_net_worth - music_arr_cost[index] >= 0:
        the_net_worth -= music_arr_cost[index]
        update_net_worth(the_net_worth)
        music_owned[index] = 1
        session = UserSession()
        response = requests.get(f"{SERVER_URL}/get-music-owned", json={"id": session.get_user()})
        music_list = response.json()["music"].split(',')
        music_list.append(music_arr[index])
        print(music_list, response.json()['music'].split(','))  
        requests.post(f"{SERVER_URL}/set-music-owned", json={"id": session.get_user(), "music": ','.join(music_list)})
        return True
    return False

def set_music(index):
    session = UserSession()
    if index == -1:
        requests.post(f"{SERVER_URL}/set-music-selected", json={"id": session.get_user(), "music": None})
        pygame.mixer.music.unload()
    else:
        requests.post(f"{SERVER_URL}/set-music-selected", json={"id": session.get_user(), "music": music_arr[index]})
        pygame.mixer.music.unload()
        play_music()


def get_selected_music():
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/get-music-selected", json={"id": session.get_user()})
    data = response.json()
    return data['music']


def initialize_music_shop(ui_manager):
    ui_manager.clear_and_reset()
    get_music_owned()
    global the_net_worth
    the_net_worth = fetch_net_worth()
    selected_music = get_selected_music()
    #render name, button, and price for each 
    global btns, music_arr
    btns=[]
    for m in range(0, len(music_arr)):
        if music_arr[m] == selected_music:
            btns.append(pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 200, 100 * m + 200), (400, 40)),
            text="Selected " + music_arr[m],
            manager=ui_manager,
            object_id="#Selected" + str(m),
            visible=True
            ))
        elif music_owned[m] == 0:
            btns.append(pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 200, 100 * m + 200), (400, 40)),
            text="Buy " + music_arr[m] + " for $" + str(music_arr_cost[m]),
            manager=ui_manager,
            object_id="#Buy" + str(m),
            visible=True
            )) #add new button per music_arr
        else:
            btns.append(pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 200, 100 * m + 200), (400, 40)),
            text="Select " + music_arr[m],
            manager=ui_manager,
            object_id="#Select" + str(m),
            visible=True
            )) #add new button per music_arr
    global back_btn
    back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 4 * 3, 100), (100, 40)),
            text="Back",
            manager=ui_manager,
            object_id="#Back",
            visible=True
            )






def draw_music_shop(screen, events, ui_manager):
    draw_background(screen)
    title_text_pixel_bet = FONT.render("Music Shop", True, WHITE)
    screen.blit(title_text_pixel_bet, (SCREEN_WIDTH // 2 - title_text_pixel_bet.get_width() // 2, 50))
    
    title_text_pixel_bet = FONT.render(f"Money: ${the_net_worth:.2f}", True, WHITE)
    screen.blit(title_text_pixel_bet, (SCREEN_WIDTH // 2 - title_text_pixel_bet.get_width() // 2, 100))
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            global btns, music_arr, music_owned
            for b in range(0, len(btns)):
                if event.ui_element == btns[b]:
                    print(b, len(btns), music_arr, music_owned)
                    if music_owned[b] == 0:
                        #buy music
                        val = buy_music(b)
                        if val:
                            btns[b] = pygame_gui.elements.UIButton(
                            relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 200, 100 * b + 200), (400, 40)),
                            text="Select " + music_arr[b],
                            manager=ui_manager,
                            object_id="#Select" + str(b),
                            visible=True
                            )
                    else:
                        #select music
                        global selected_btn
                        if b == selected_btn:
                            b = -1
                        selected_btn = b
                        set_music(b)
                        initialize_music_shop(ui_manager)
                elif event.ui_element == back_btn:
                    return "home"


                
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)

    pygame.display.flip()   
    return "music"

def play_music():
    name = get_selected_music()
    if name is not None and name != "":
        idx = music_arr.index(name)
        pygame.mixer.music.load("frontend/assets/music/" + music_arr_path_name[idx])
        pygame.mixer.music.play(loops=-1)

