import pygame
from settings import *
import game.player

# TYPES
# 2 - continuos
# 3 - dotted
# 1 - decreasing
# 4 - decreasing normal

class Trail:
    def __init__(self, player):
        self.display_surface = get_window()
        self.player:game.player.Player = player
        self.reset()
        
    def reset(self):
        self.positions, self.particles = [], []
        self.skipping, self.skip_count = False, 0
        
    def update(self, dt):
        match self.player.trail_type:
            case 2 | 3:
                self.positions.append([self.player.hitbox.midleft if not self.player.gamemode.trail_center else self.player.hitbox.center,self.skipping])
                self.skip_count += 1
                if self.skip_count >= 20: self.skip_count, self.skipping = 0, not self.skipping
            case 1 | 4:
                self.particles.append({"pos":self.player.hitbox.midleft if not self.player.gamemode.trail_center else self.player.hitbox.center,"size":15 if self.player.trail_type == 4 else 8})
                toremove = []
                for p in self.particles:
                    p["size"] -= (30 if self.player.trail_type == 4 else 25)*dt
                    if p["size"] <= 0: toremove.append(p)
                for p in toremove: self.particles.remove(p)
                
    def draw(self):
        toremove, toremovep, last = [], [], None
        match self.player.trail_type:
            case 2 | 3:
                for data in self.positions:
                    pos, skipping = data
                    if not last: last = pos
                    else:
                        pos_o = (pos[0]-self.player.level.offset.x,pos[1]-self.player.level.offset.y)
                        last_o = (last[0]-self.player.level.offset.x,last[1]-self.player.level.offset.y)
                        last = pos
                        if self.player.trail_type == 3: pygame.draw.line(self.display_surface,self.player.trail_color,pos_o,last_o,4)
                        elif self.player.trail_type == 1 and not skipping:
                            pygame.draw.line(self.display_surface,self.player.trail_color,pos_o,last_o,4)
                        if pos_o[0] < 0: toremove.append(data)
            case 1 | 4:
                for particle in self.particles:
                    if not last: last = particle; continue
                    pos_o = (particle["pos"][0]-self.player.level.offset.x,particle["pos"][1]-self.player.level.offset.y)
                    last_o = (last["pos"][0]-self.player.level.offset.x,last["pos"][1]-self.player.level.offset.y)
                    last = particle
                    pygame.draw.line(self.display_surface,self.player.trail_color,pos_o,last_o,int(particle["size"]))
                    if pos_o[0] < 0: toremovep.append(particle)
        for p in toremove: self.positions.remove(p)
        for p in toremovep: self.particles.remove(p)
        
class Particles():
    def __init__(self,
                 player, active = True, colors = ["white"], use_gravity = True, gravity_speed: float = 100, cooldown: int = 1000,
                 speed_random_range = ( (-1.0, 1.0), (-1.0, 1.0)), change_over_time: bool = True, change_multiplier: int = -1, start_radius: int = 5, 
                 interval=20, destroy_or_hide_cooldown: int = 9999, destroy_after_time: bool = False,hide_after_time: bool = False, square=True):
        
        self.player = player
        self.display_surface = get_window()
        self.particles = []
        self.use_gravity, self.gravity_speed = use_gravity, gravity_speed
        self._cooldown, self._start_scale = cooldown, start_radius if not square else start_radius*2
        self.speed_random_range = speed_random_range
        self.change_over_time, self.change_multiplier = change_over_time, change_multiplier
        self.destroy_or_hide_cooldown = destroy_or_hide_cooldown
        self.destroy_after_time, self.hide_after_time = destroy_after_time, hide_after_time
        self.active, self.colors = active, colors
        self.scaleMinuser = self._start_scale/self._cooldown
        self.interval = interval
        self.last_spawn = self.lastTime = self.lastHide = pygame.time.get_ticks()
        self.square = square
        
    @property
    def cooldown(self): return self._cooldown

    @cooldown.setter
    def cooldown(self, value):
        self._cooldown = value
        self.scaleMinuser = self._start_scale/self._cooldown

    @property
    def start_radius(self) : return self._start_scale

    @start_radius.setter
    def start_radius(self, value: int):
        self._start_scale = value
        self.scaleMinuser = self._start_scale/self._cooldown

    def empty(self):self.particles.clear()

    def generate(self, position , dt):
        if self.active:
            if pygame.time.get_ticks()-self.last_spawn >= self.interval:
                self.particles.append({"color": choice(self.colors), "pos": list(position), "speed": [uniform(self.speed_random_range[0][0], self.speed_random_range[0][1]), 
                    uniform( self.speed_random_range[1][0], self.speed_random_range[1][1])], "time": self._cooldown, "scale": self._start_scale})
                self.last_spawn = pygame.time.get_ticks()
        self.dt = dt

    def draw(self, move=True) -> None:
        current = pygame.time.get_ticks()
        toRemove = []

        for particle in self.particles:
            particle["pos"][0] += particle["speed"][0]*self.dt
            particle["pos"][1] += particle["speed"][1]*self.dt

            dt = current-self.lastTime
            particle["time"] -= dt

            if self.use_gravity: particle["speed"][1] += self.gravity_speed*self.dt
            if particle["time"] <= 0: toRemove.append(particle)

            if self.change_over_time:
                preview = particle["scale"] + ((dt*self.scaleMinuser) * self.change_multiplier)
                if round(preview) > 0: particle["scale"] = preview

            pos = (int(particle["pos"][0]), int(particle["pos"][1])-self.player.level.offset.y)
            if move: pos = (pos[0]-self.player.level.offset.x,pos[1])
            if pos[0] > 0: 
                if not self.square: pygame.draw.circle(self.display_surface, particle["color"], pos, round(particle["scale"]))
                else: pygame.draw.rect(self.display_surface,particle["color"],(pos,(particle["scale"],particle["scale"])))

        for particle in toRemove: self.particles.remove(particle)

        if self.destroy_after_time or self.hide_after_time:
            if current-self.lastHide >= self.destroy_or_hide_cooldown:
                if self.destroy_after_time: self.kill()
                elif self.hide_after_time: self.active = False; self.empty()
                self.lastHide = current
        self.lastTime = current

    def kill(self): del self
