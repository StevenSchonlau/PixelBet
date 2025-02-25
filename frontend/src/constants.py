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

SPRITE_SIZE = 128

THEME_PATH = "frontend/assets/ui/theme.json"

FONT_PATH = "frontend/assets/fonts/PixelEmulator-xq08.ttf"
FONT = pygame.font.Font(FONT_PATH, 24)
SERVER_URL="http://localhost:5000/"
