import pygame
from settings import *

class Music:
    def __init__(self, main):
        self.main = main
        self.assets = self.main.asset_loader

        pygame.mixer_music.load("assets/audio/menu/menuLoop.mp3")
        pygame.mixer_music.play(-1)
    
    def enter_level(self, music_name):
        pygame.mixer_music.unload()
        pygame.mixer_music.load(f"assets/audio/levels/{music_name.replace(' ','')}.mp3")
        pygame.mixer_music.play(1,fade_ms=5000)
        
    def restart_music(self, loops=1):
        pygame.mixer_music.rewind()
        pygame.mixer_music.play(loops)
        
    def pause_music(self):
        pygame.mixer_music.pause()
        
    def resume_music(self):
        pygame.mixer_music.unpause()
        
    def stop_music(self):
        pygame.mixer_music.stop()
        
    def play_fx(self, name):
        self.assets["fx-sounds"][name].play()
        
    def enter_menu(self):
        pygame.mixer_music.unload()
        pygame.mixer_music.load("assets/audio/menu/menuLoop.mp3")
        pygame.mixer_music.play(-1)
        
    def enter_editor(self):
        self.stop_music()
