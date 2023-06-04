import pygame
from settings import *

class GameMenu:
    def __init__(self, game):
        self.game = game
        self.assets = self.game.assets
        self.display_surface = get_window()
        self.black_overlay = pygame.Surface(SIZES,pygame.SRCALPHA)
        self.black_overlay.fill("black")
        self.black_overlay.set_alpha(150)
        self.resume_btn = MenuButton((playimg:=self.assets["ui"]["play-big"]),(H_WIDTH,H_HEIGHT))
        self.back_btn = MenuButton(self.assets["ui"]["goback-big"],(H_WIDTH-playimg.get_width()-SPACING,H_HEIGHT))
        self.restart_btn = MenuButton(pygame.transform.scale_by(self.assets["ui"]["restart"],1.3),(H_WIDTH+playimg.get_width()+SPACING,H_HEIGHT))
        self.refresh_name()
        
    def refresh_name(self):
        self.name_surf = self.assets["fonts"]["xxl"].render(self.game.level.data.level_name,True,"gold")
        self.name_surf = create_soft_outline(self.name_surf,3,(0,0,0,255),3,3)
        self.name_rect = self.name_surf.get_rect(midtop=(H_WIDTH,SPACING+HH_HEIGHT*0.2))
        
    def update(self, dt):
        if self.resume_btn.check():
            self.game.unpause()
        if self.back_btn.check():
            self.game.apply_go_back()
        if self.restart_btn.check():
            self.game.level.player.reset()
            self.game.main.music.restart_music()
            self.game.unpause()
        
    def draw(self):
        self.display_surface.blit(self.black_overlay,(0,0))
        self.display_surface.blit(self.name_surf,self.name_rect)
        self.resume_btn.draw(self.display_surface)
        self.restart_btn.draw(self.display_surface)
        self.back_btn.draw(self.display_surface)
