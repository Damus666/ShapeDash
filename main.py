import pygame, os, platform
from settings import *
from state import GameState
from game.game import Game
from editor.editor import Editor
from menu.menu import Menu
from assetloader import AssetLoader
from menu.loading import LoadingScreen
from gui import GUI
from debugger import Debugger
from music import Music

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SIZES,pygame.FULLSCREEN if not TEST_WIN else 0)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        self.debugger = Debugger()
        self.asset_loader = AssetLoader()
        self.asset_loader.pre_load()
        self.loading_screen = LoadingScreen(self)
        self.asset_loader.load()
        self.music = Music(self)
        self.gui = GUI(self)
        self.game = Game(self)
        self.editor = Editor(self)
        self.menu = Menu(self)
        self.game_state:GameState = self.menu
        
    def play_level(self, name):
        self.game_state = self.game
        self.game.level.load(name)
        self.game.menu.refresh_name()
        self.game.unpause()
        self.music.enter_level(self.game.level.data.level_music)
        self.music.play_fx("playSound_01")
        self.debugger.change_state("Game")
        self.debugger.playing(name)
        
    def editor_exit(self):
        self.game_state = self.menu
        self.music.enter_menu()
        self.debugger.change_state("Menu")
        self.menu.change_mode("details")
        
    def editor_edit(self, name):
        self.game_state = self.editor
        self.debugger.change_state("Editor")
        self.debugger.editing(name)
        self.editor.on_change()
        self.editor.load(name)
        self.music.enter_editor()
        
    def level_go_back(self, data):
        match data["state"]:
            case "editor":
                self.game_state = self.editor
                self.editor.on_change()
                self.music.enter_editor()
                self.debugger.change_state("Editor")
            case "menu":
                self.game_state = self.menu
                self.debugger.change_state("Menu")
                self.menu.change_mode(data["mode"])
                self.music.enter_menu()
        
    def run(self):
        self.debugger.start()
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
