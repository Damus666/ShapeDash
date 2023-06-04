import pygame, sys
from settings import *

class GameState:
    def __init__(self, main):
        self.main = main
        self.display_surface = get_window()
    
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit_all()
    
    def update(self, dt): ...
    def draw(self): ...
