import pygame
from settings import *
from state import GameState
from game.game import Game
from editor.editor import Editor
from menu.menu import Menu
from assetloader import AssetLoader
from menu.loading import LoadingScreen
from gui import GUI

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SIZES,pygame.FULLSCREEN if not TEST_WIN else 0)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        self.asset_loader = AssetLoader()
        self.asset_loader.pre_load()
        self.loading_screen = LoadingScreen(self)
        self.asset_loader.load()
        self.gui = GUI(self)
        self.game = Game(self)
        self.editor = Editor(self)
        self.menu = Menu(self)
        self.game_state:GameState = self.menu
        
    def play_level(self, name):
        self.game.level.load(name)
        self.game_state = self.game
        
    def editor_exit(self):
        self.game_state = self.menu
        self.menu.change_mode("details")
        
    def editor_edit(self, name):
        self.game_state = self.editor
        self.editor.on_change()
        self.editor.load(name)
        
    def level_go_back(self, data):
        match data["state"]:
            case "editor": self.game_state = self.editor
            case "menu":
                self.game_state = self.menu
                self.menu.change_mode(data["mode"])
        
    def run(self):
        while True: 
            Input.update()
            
            self.gui.frame_start()
            self.game_state.event_loop()
            self.game_state.update(pygame.math.clamp(self.clock.tick(FPS)*ONE_OVER_1000,0,1))
            self.game_state.draw()
            self.gui.draw()
            
            pygame.display.update()
            
if __name__ == "__main__":
    main = Main()
    main.run()
