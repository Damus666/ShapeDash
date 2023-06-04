import pygame
from settings import *
from pygame.sprite import Sprite
from random import randint, uniform, choice

class Generic(Sprite):
    def __init__(self, pos, surf, groups, pos_center=False):
        super().__init__(groups)
        self.image = surf
        if pos_center: self.rect:pygame.Rect = self.image.get_rect(center=pos)
        else: self.rect:pygame.Rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()
        
    def draw(self):...
        
class Animated(Generic):
    def __init__(self, pos, frames, groups, pos_center=False, speed_mul=1):
        self.frames = frames
        self.frame_index = uniform(0.0,0.5)
        self.animation_speed = ANIMATION_SPEED*speed_mul
        super().__init__(pos,self.frames[int(self.frame_index)],groups,pos_center)
    
    def animate(self,dt):
        old_frame = int(self.frame_index)
        self.frame_index += self.animation_speed*dt
        if self.frame_index >= len(self.frames): self.frame_index = 0
        if old_frame != int(self.frame_index):
            self.image = self.frames[int(self.frame_index)]
            self.rect = self.image.get_rect(center=self.rect.center)
    
    def update(self,dt): self.animate(dt)
        
class AnimatedStatus(Animated):
    def __init__(self, pos, animations, status, groups, pos_center=False):
        self.animations = animations
        self.status = status
        super().__init__(pos,self.animations[self.status],groups,pos_center)

    def set_status(self,status,force=False):
        if self.status != status or force: self.status = status; self.frames = self.animations[self.status]
