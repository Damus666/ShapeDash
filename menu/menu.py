import pygame
from settings import *
from state import GameState
from background import Background
from menu.modes import *

class Menu(GameState):
    def __init__(self, main):
        super().__init__(main)
        self.assets = main.asset_loader
        self.data = MenuData(self)
        self.top_border = False
        self.background = Background(self.assets["bg"],self.assets["ground"],self,True)
        
        self.modes = {
            "main":MenuMainScreen(self),
            "play":MenuPlayLevels(self),
            "levels":MenuLevelList(self),
            "details":MenuLevelDetails(self),
            "iconkit":MenuIconkit(self),
        }
        self.mode:MenuMode = self.modes["main"]
        
    def move_background(self, dx):
        self.background.ground_position -= dx
        self.background.bg_position -= dx/3
    
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit_all()
            self.mode.event(event)
            self.main.gui.event(event)
    
    def update(self, dt):
        self.move_background(MENU_SPEED*dt)
        self.background.editor_update()
        self.mode.update(dt)
                
    def change_mode(self, name):
        self.mode = self.modes[name]
        self.mode.on_change()
        
    def draw(self):
        self.display_surface.fill("black")
        self.background.draw()
        self.background.draw_after()
        self.mode.draw()
        
    def set_level(self, name): self.data.level_name = name
        
class MenuData:
    def __init__(self, menu):
        self.menu = menu
        self.level_name = ""
        self.bg_color = self.ground_color = (0,105,255)
        self.bg_index = self.ground_index = 0
