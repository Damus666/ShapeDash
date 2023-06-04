import pygame, sys
from settings import *
from state import GameState
from game.level import Level

class Game(GameState):
    def __init__(self, main):
        super().__init__(main)
        self.assets = main.asset_loader
        self.level = Level(self)
        self.time_scale = 1
        self.back_to = None
    
    # update
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit_all()
            self.level.event(event)
    
    def update(self, dt):
        dt *= self.time_scale
        self.level.update(dt)
        
    def draw(self):
        self.display_surface.fill("black")
        self.level.draw()
    
    # back
    def go_back_to(self, data): self.back_to = data
    def apply_go_back(self):
        if self.back_to: self.main.level_go_back(self.back_to)
    
    # time
    def resume_time(self): self.time_scale = 1
    def stop_time(self): self.time_scale = 0
    def set_time_scale(self, value): self.time_scale = value
        