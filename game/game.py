import pygame, sys
from settings import *
from state import GameState
from game.level import Level
from game.menu import GameMenu

class Game(GameState):
    def __init__(self, main):
        super().__init__(main)
        self.assets = main.asset_loader
        self.level = Level(self)
        self.menu = GameMenu(self)
        self.time_scale = 1
        self.paused, self.back_to = False, None
            
    # update
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit_all()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.paused: self.unpause()
                else: self.pause()
            self.level.event(event)
    
    def update(self, dt):
        dt *= self.time_scale
        self.level.update(dt)
        if self.paused: self.menu.update(dt)
        
    def draw(self):
        self.display_surface.fill("black")
        self.level.draw()
        if self.paused: self.menu.draw()
    
    # back
    def go_back_to(self, data): self.back_to = data
    def apply_go_back(self):
        if self.back_to: self.main.level_go_back(self.back_to)
    
    # time
    def resume_time(self): self.time_scale = 1
    def stop_time(self): self.time_scale = 0
    def set_time_scale(self, value): self.time_scale = value
    
    def pause(self):
        self.paused = True
        self.stop_time()
        self.main.music.pause_music()
    
    def unpause(self):
        self.paused = False
        self.resume_time()
        self.main.music.resume_music()
        