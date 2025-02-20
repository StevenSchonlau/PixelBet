import pygame
import pygame_gui
import datetime
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, FONT

button_mapping = {}

def draw_game_screen(screen, events, ui_manager, selected_game):
    global current_screen
    current_screen = "game"
    screen.fill(BLACK)
    
    game_text = FONT.render(f"Now Playing: {selected_game}", True, WHITE)
    screen.blit(game_text, (SCREEN_WIDTH // 2 - game_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    
    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 100, 100, 50)),
        text="Back",
        manager=ui_manager,
        object_id="#button"
    )
    button_mapping[back_button] = "Back"
    
    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(event.ui_element)
            if event.ui_element in button_mapping:
                current_screen = "home"
                for button in button_mapping.keys():
                    button.kill()
        ui_manager.process_events(event)
    
    ui_manager.update(1 / 60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()
    return current_screen
