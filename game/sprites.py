import pygame
from settings import *
from sprites import *
from game.effects import Particles
from game.triggers import *

class Object(Generic):
    def __init__(self, id, pos, level, groups):
        match id:
            case (category, name): id = get_id(category,name)
            case _: id = id
        self.category, self.name, surface = get_from_id(id)
        self.level = level
        super().__init__(pos, surface, groups, False)

class Block(Object):
    def __init__(self, id, pos, level):
        if isinstance(id, str): id = ("blocks",id)
        super().__init__(id, pos, level, [level.all, level.visible,level.collidable])
        
class Trigger(Object):
    def __init__(self, id, pos, level, data):
        self.action = get_trigger(id, self, data)
        if isinstance(id, str): id = ("triggers",id)
        super().__init__(id, pos, level, [level.all, level.triggers])
        self.activated = False
        
    def activate(self):
        self.activated = True
        self.action.apply()
        
class Portal(Object):
    def __init__(self, id, pos, level):
        if isinstance(id, str): id = ("portals",id)
        super().__init__(id, pos, level, [level.all, level.visible_top, level.portals, level.updates, level.draws])
        self.has_particles = self.name in PORTAL_COLORS.keys()
        if self.has_particles: self.particles = Particles(self.level.player,True,PORTAL_COLORS[self.name],False,100,600,((-150,150),(-150,150)),interval=10)
            
    def update(self, dt):
        if self.has_particles: self.particles.generate(self.hitbox.center,dt)
            
    def draw(self):
        if self.has_particles: self.particles.draw()
        
class Orb(Object):
    def __init__(self, id, pos, level):
        if isinstance(id, str): id = ("orbs",id)
        super().__init__(id, pos, level, [level.all, level.visible, level.orbs, level.updates, level.draws])
        self.hitbox.inflate_ip(BLOCK_SIZE,BLOCK_SIZE)
        self.has_particles = self.name in ORBS_COLORS.keys()
        if self.has_particles: self.particles = Particles(self.level.player,True,ORBS_COLORS[self.name],False,100,500,((-150,150),(-150,150)),interval=10)
            
    def update(self, dt):
        if self.has_particles: self.particles.generate(self.hitbox.center,dt)
            
    def draw(self):
        if self.has_particles: self.particles.draw()
        
class ExtraObject(Object):
    def __init__(self, id, pos, level):
        if isinstance(id, str): id = ("objects",id)
        super().__init__(id, pos, level, [level.all, level.visible])
        
class Damaging(ExtraObject):
    def __init__(self, id, pos, level):
        super().__init__(id, pos, level, [level.all, level.visible, level.damaging])
        
class DeathEffect(Animated):
    def __init__(self, index, pos, level):
        frames = level.assets["deatheffects"]["animations"][index]
        super().__init__(pos, frames, [level.all, level.visible_top,level.updates],True,len(frames)/3.5)
        self.level = level
        
    def animate(self,dt):
        old_frame = int(self.frame_index)
        self.frame_index += self.animation_speed*dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
            self.level.player.finalize_death()
            self.kill()
        if old_frame != int(self.frame_index):
            self.image = self.frames[int(self.frame_index)]
            self.rect = self.image.get_rect(center=self.rect.center)
