import pygame
import sys


# Function to draw text
def draw_text(screen, text, font, color, x, y):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))
