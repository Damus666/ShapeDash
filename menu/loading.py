import pygame
from settings import *

class LoadingScreen:
    def __init__(self, main):
        self.main = main
        self.assets = main.asset_loader
        self.render()
    
    def render(self):
        bg_width = (bg_image:=self.assets["other"]["loading_bg"]).get_width()
        for i in range(int(WIDTH/bg_width)+1): self.main.screen.blit(bg_image,(bg_width*i,0))
        logo_rect = (logo_image:=self.assets["ui"]["logo"]).get_rect(center=(H_WIDTH,H_HEIGHT-HEIGHT//6))
        self.main.screen.blit(logo_image,logo_rect)
        loading_rect = (loading_surf:=create_soft_outline(self.assets["fonts"]["xxl"].render("Loading...",True,"gold"),10,(0,0,0,255),2,2,57,0)).get_rect(center=(H_WIDTH,H_HEIGHT+HEIGHT//6))
        
        self.main.screen.blit(loading_surf,loading_rect)
        pygame.display.update()
        