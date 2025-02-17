import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, BLUE, BUTTON_COLOR, HOVER_COLOR
def draw_home_screen(screen, font):
    screen.fill(BLACK)

    # Draw title
    title_text = font.render("PixelBet", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 50))

    # Draw game options

    pygame.display.flip()