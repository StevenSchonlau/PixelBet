import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BUTTON_COLOR = (200, 200, 200)
HOVER_COLOR = (170, 170, 170)
PRIMARY = (0, 55, 126) 
SECONDARY = (0, 30, 69) 

SPRITE_SIZE = 128

THEME_PATH = "frontend/assets/ui/theme.json"

FONT_PATH = "frontend/assets/fonts/PixelEmulator-xq08.ttf"
FONT = pygame.font.Font(FONT_PATH, 24)
SERVER_URL="http://localhost:5000/"

def draw_background(surface):
    """Draws background as a gradient"""
    top_color = PRIMARY
    bottom_color = SECONDARY
    width, height = surface.get_size()
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))