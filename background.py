import pygame, time
from settings import *
from game.effects import Particles

class Background:
    def __init__(self, bg_assets:list[pygame.Surface], ground_assets:list[pygame.Surface], level, is_editor=False):
        self.display_surface = get_window()
        self.level = level
        self.is_editor = is_editor
        self.bg_assets, self.ground_assets = bg_assets, ground_assets
        self.set_bg(self.level.data.bg_index)
        self.set_ground(self.level.data.ground_index)
        self.set_bg_color(self.level.data.bg_color)
        self.set_ground_color(self.level.data.ground_color)
        self.bg_position = self.ground_position = 0
        self.bottom_gpos, self.lowbottom_gpos = GROUND_Y, LOW_GROUND_Y
        if not self.is_editor:
            self.ambient_particles = Particles(self.level.player,True,[self.level.player.main_color,self.level.player.secondary_color],
                                               False, 0,1000, ((-1000,-500),(0,0)),start_radius=5,interval=32)
        
    def set_background_color(self, new_color):
        self.set_bg_color(new_color)
        self.set_ground_color(new_color)
        
    def refresh_colors(self):
        self.set_bg_color(self.level.data.bg_color)
        self.set_ground_color(self.level.data.ground_color)
        
    def refresh_bg_color(self):
        self.set_bg_color(self.level.data.bg_color)
        
    def refresh_gd_color(self):
        self.set_ground_color(self.level.data.ground_color)
        
    def refresh_bg_idx(self):
        self.set_bg(self.level.data.bg_index)
        self.refresh_bg_color()
        
    def refresh_gd_idx(self):
        self.set_ground(self.level.data.ground_index)
        self.refresh_gd_color()
        
    def set_bg_color(self, new_color):
        self.current_bg = self.original_bg.copy()
        self.bg_colored.fill(new_color)
        self.current_bg.blit(self.bg_colored,(0,0),special_flags=pygame.BLEND_RGB_MULT)
        #pygame.image.save(self.current_bg,"assets/graphics/other/loading_bg.png")
                
    def set_ground_color(self, new_color):
        self.current_ground = self.original_ground.copy()
        self.ground_colored.fill(new_color)
        self.current_ground.blit(self.ground_colored,(0,0),special_flags=pygame.BLEND_RGB_MULT)
        self.flipped_ground = pygame.transform.rotate(self.current_ground,180)
        
    def set_background(self, index):
        self.set_bg(index)
        if index > len(self.ground_assets)-1: index = len(self.ground_assets)-1
        self.set_ground(index)
        
    def set_bg(self, index):
        self.current_bg:pygame.Surface = self.bg_assets[index]
        self.original_bg = self.current_bg
        self.bg_width = self.current_bg.get_width()
        self.bg_amount = range((WIDTH//self.bg_width)+2)
        self.bg_colored = pygame.Surface((self.bg_width,self.current_bg.get_height()))
        
    def set_ground(self, index):
        self.current_ground:pygame.Surface = self.ground_assets[index]
        self.flipped_ground:pygame.Surface = pygame.transform.rotate(self.current_ground,180)
        self.original_ground = self.current_ground
        self.ground_width = self.current_ground.get_width()
        self.ground_amount = range((WIDTH//self.ground_width)+2)
        self.top_gpos = HEIGHT-LOW_GROUND_Y
        self.top_gdrawpos = self.top_gpos-self.current_ground.get_height()
        self.ground_colored = pygame.Surface((self.ground_width,self.current_ground.get_height()))
        
    def update(self, dt):
        self.ambient_particles.start_radius = randint(3,6)
        if self.level.player.deatheffect_obj: return
        self.bg_position -= (dx:=self.level.speed*dt)/3
        if self.bg_position <= -self.bg_width: self.bg_position = 0
        self.ground_position -= dx
        if self.ground_position <= -self.ground_width: self.ground_position = 0
        self.ambient_particles.generate((randint(0,WIDTH),randint(0,HEIGHT)),dt)
        
    def editor_update(self):
        if self.bg_position <= -self.bg_width: self.bg_position = 0
        if self.ground_position <= -self.ground_width: self.ground_position = 0
        if self.bg_position > 0: self.bg_position = -self.bg_width+self.bg_position
        if self.ground_position > 0: self.ground_position = -self.ground_width+self.ground_position
        
    def draw(self):
        for i in self.bg_amount: self.display_surface.blit(self.current_bg,(self.bg_position+self.bg_width*i,0))
        if not self.is_editor: self.ambient_particles.draw(False)
            
    def draw_after(self):
        bottom_pos = self.bottom_gpos if not self.level.top_border else self.lowbottom_gpos
        for i in self.ground_amount: self.display_surface.blit(self.current_ground,(self.ground_position+self.ground_width*i,bottom_pos))
        pygame.draw.line(self.display_surface,"white",(0,bottom_pos),(WIDTH,bottom_pos),2)
        if self.level.top_border:
            for i in self.ground_amount: self.display_surface.blit(self.flipped_ground,(self.ground_position+self.ground_width*i,self.top_gdrawpos))
            pygame.draw.line(self.display_surface,"white",(0,self.top_gpos),(WIDTH,self.top_gpos),2)
