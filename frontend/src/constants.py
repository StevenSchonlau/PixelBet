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


def load_sprites(sheet, num_frames, row=0, scale=2):
    frame_width = SPRITE_SIZE
    frame_height = SPRITE_SIZE
    frames = []
    for i in range(num_frames):
        frame = sheet.subsurface(pygame.Rect(i * frame_width, row * frame_height, frame_width, frame_height))
        scaled_frame = pygame.transform.scale(frame, (frame_width * scale, frame_height * scale))
        frames.append(scaled_frame)
    return frames


class Sprite(pygame.sprite.Sprite):
    def __init__(self, name="", sprite_sheet=None):
        super().__init__()
        self.name = name
        self.frames = load_sprites(sprite_sheet, 8)
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 8 * 3))
        self.animation_speed = 5
        self.frame_counter = 0
    
    def update(self):
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]
            self.frame_counter = 0