import pygame
from settings import *
import game.player
from game.effects import Particles

class Gamemode:
    def __init__(self, player, rotate_speed = 0, ground_rotate=False, trail_center=True):
        self.player: game.player.Player= player
        self.rotate_speed = rotate_speed
        self.ground_rotate = ground_rotate
        self.trail_center = trail_center
        self.display_surface = get_window()
        
    def base_rotate(self):
        if self.player.gravity > 0:
            self.player.image = pygame.transform.rotate(self.player.original_image,self.player.angle)
            self.player.rect = self.player.image.get_rect(center=self.player.rect.center)
        else:
            self.player.flipped_image = pygame.transform.rotate(self.player.original_flipped,self.player.angle)
            self.player.rect = self.player.flipped_image.get_rect(center=self.player.rect.center)
            
    def rotate(self, dt):...
    def move(self):...
    def on_change(self):...
    def input_jump(self):...
    def update(self, dt):...
    def draw(self):...
    def reset(self):...
    
class Cube(Gamemode):
    def __init__(self, player):
        super().__init__(player,-200)
        self.normal_range = ((0,0),(-50,-100))
        self.flip_range = ((0,0),(50,100))
        self.ground_particles = Particles(self.player,True,["white"],True,100,300,self.normal_range)
        
    def rotate(self, dt):
        if not self.player.on_ground: self.player.angle += self.rotate_speed*dt
        self.base_rotate()
        
    def move(self, dt):
        self.player.pos.y += self.player.y_dir*dt
        self.player.y_dir += GRAVITY*dt*self.player.gravity
        
    def on_change(self):
        self.player.set_image_category("cube")
        self.player.level.set_top_border(False)
        
    def update(self, dt):
        self.ground_particles.speed_random_range = self.normal_range if self.player.gravity > 0 else self.flip_range
        if self.player.on_ground: self.ground_particles.generate(self.player.hitbox.bottomleft if self.player.gravity > 0 else self.player.hitbox.topleft,dt)
        
    def draw(self): self.ground_particles.draw()
    def input_jump(self): self.player.jump("normal",True,True)
    def reset(self): self.ground_particles.empty()
        
class Ship(Gamemode):
    def __init__(self, player):
        super().__init__(player,trail_center=False)
        self.normal_particles = Particles(self.player,True,["white"],False,100,300,((0,0),(-100,100)))
        self.fly_particles = Particles(self.player,True,SHIP_TRAIL_COLS,False,100,400,((0,0),(-100,100)),start_radius=6,interval=5)
        
    def move(self, dt):
        if not self.player.key_pressed: self.player.y_dir += SHIP_GRAVITY*dt*self.player.gravity
        self.player.pos.y += self.player.y_dir*dt
    
    def input_jump(self): self.player.y_dir -= SHIP_FLY_SPEED*self.player.gravity
        
    def on_change(self):
        self.player.set_image_category("ship")
        self.player.level.set_top_border(True)
        self.player.angle = 0
        self.rotate(0)
        
    def update(self, dt):
        self.normal_particles.generate(self.player.hitbox.midleft if self.player.gravity > 0 else self.player.hitbox.topleft, dt)
        if self.player.key_pressed: self.fly_particles.generate(self.player.hitbox.midleft, dt)
        
    def draw(self):
        self.normal_particles.draw()
        self.fly_particles.draw()
        
    def reset(self):
        self.normal_particles.empty()
        self.fly_particles.empty()
        
class Ball(Gamemode):
    def __init__(self, player):
        super().__init__(player, -500, True)
        self.normal_range = ((0,0),(-50,-100))
        self.flip_range = ((0,0),(50,100))
        self.ground_particles = Particles(self.player,True,["white"],True,100,300,self.normal_range)
        
    def rotate(self, dt):
        self.player.angle += self.rotate_speed*dt*self.player.gravity
        self.base_rotate()
        
    def move(self, dt):
        self.player.y_dir += BALL_GRAVITY*dt*self.player.gravity
        self.player.pos.y += self.player.y_dir*dt
        
    def input_jump(self):
        if not self.player.was_pressing and self.player.on_ground:
            self.player.gravity *= -1
            self.player.on_ground = False
        
    def on_change(self):
        self.player.set_image_category("ball")
        self.player.level.set_top_border(True)
        self.player.angle = 0
        self.rotate(0)
        
    def update(self, dt):
        self.ground_particles.speed_random_range = self.normal_range if self.player.gravity > 0 else self.flip_range
        if self.player.on_ground: self.ground_particles.generate(self.player.hitbox.midbottom if self.player.gravity > 0 else self.player.hitbox.midtop, dt)
        
    def draw(self): self.ground_particles.draw()
    def reset(self): self.ground_particles.empty()
        