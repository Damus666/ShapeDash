import pygame
from settings import *
from sprites import Generic
from game.sprites import DeathEffect
from game.physics import Physics
from game.effects import *
from game.gamemodes import *

class Player(Generic):
    def __init__(self, level):
        self.level = level
        self.main_color = (115,0,255)
        self.secondary_color = (0,255,0)
        self.trail_color = (255,255,255)
        self.deatheffect = 0
        self.trail_type = 1
        self.images = {
            "cube":level.assets.get_player("cube",choice(PLAYER_IDS["cube"]),self.main_color,self.secondary_color),
            "ship":level.assets.get_player("ship",choice(PLAYER_IDS["ship"]),self.main_color,self.secondary_color),
            "ball":level.assets.get_player("ball",choice(PLAYER_IDS["ball"]),self.main_color,self.secondary_color),
        }
        super().__init__((-1500,GROUND_Y),self.images["cube"],[],False)
        self.deatheffect_obj = None
        self.display_surface = get_window()
        self.physics:Physics = level.physics
        self.pos = vector(self.rect.center)
        self.y_dir = self.hitbox_offset = self.angle = 0
        self.on_ground = False
        self.gravity = 1
        self.key_pressed = self.was_pressing = False
        self.gamemodes = {
            "cube":Cube(self),
            "ship":Ship(self),
            "ball":Ball(self),
        }
        self.gamemode = None
        self.set_gamemode(self.level.data.start_gamemode)
        self.trail = Trail(self)
        
    def set_gamemode(self, name):
        old = self.gamemode
        self.gamemode:Gamemode = self.gamemodes[name]
        if self.gamemode != old: self.gamemode.on_change()
        
    def set_image_category(self, name):
        self.image = self.images[name]
        self.original_image = self.image
        self.flipped_image = pygame.transform.flip(self.image,False,True)
        self.original_flipped = self.flipped_image
        self.rect = self.image.get_rect(center=self.rect.center)
        self.hitbox = self.rect.copy()
        if name == "ship":
            self.secondary_image = pygame.transform.scale_by(self.images["cube"],0.75)
            self.flipped_secondary = pygame.transform.flip(self.secondary_image,False,True)
            self.secondary_rect = self.secondary_image.get_rect()
        else: self.secondary_image = self.secondary_rect = None
        
    def orb_collision(self, name):
        if not self.key_pressed or (self.key_pressed and self.was_pressing): return
        match name:
            case "black":...
            case "pink" | "red" | "yellow": self.jump(f"{name}_orb")
            case "blue": self.gravity *= -1
            case "green": self.gravity *= -1; self.jump("green_orb",)
        
    def portal_collision(self, name):
        match name:
            case "cube" | "ship" | "ball": self.set_gamemode(name)
            case "invert": self.gravity = -1
            case "revert": self.gravity = 1
            case _: self.level.change_speed(name)
        
    def trigger_trigger(self, trigger): trigger.activate()
    def finalize_death(self):
        self.reset()
        self.level.game.main.music.restart_music()
    def damage_collision(self): self.die()
        
    def die(self):
        deatheffect = self.deatheffect if self.deatheffect != 0 else choice(TRAILS)
        if not self.deatheffect_obj: self.deatheffect_obj = DeathEffect(deatheffect,self.rect.center,self.level)
        self.level.game.main.music.stop_music()
        self.level.game.main.music.play_fx("explode_11")
        
    def reset(self):
        self.pos.x = -1200
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = self.rect.centerx
        self.angle, self.deatheffect_obj = 0, None
        self.snap_angle()
        self.trail.reset()
        self.gamemode.reset()
        
    def snap_angle(self):
        remainder = self.angle % 360
        multiples_90 = remainder / 90
        rounded_multiples = round(multiples_90)
        self.angle = rounded_multiples * 90
        if self.angle >= 360: self.angle = 0
        
    def touch_ground(self):
        self.y_dir = 0
        self.on_ground = True
        if not self.gamemode.ground_rotate:
            self.snap_angle()
            self.gamemode.rotate(0)
        
    def input(self):
        self.key_pressed = Input.keys_pressed[pygame.K_SPACE] or Input.keys_pressed[pygame.K_w] or Input.keys_pressed[pygame.K_UP] or Input.mouse_pressed[0]
        if self.key_pressed: self.gamemode.input_jump()
                
    def jump(self, speed_name, reset_ground=True, check_ground=False):
        if self.on_ground or not check_ground:
            self.y_dir = -JUMP_SPEEDS[speed_name]*self.gravity
            if reset_ground: self.on_ground = False
        
    def move(self, dt):
        if not self.deatheffect_obj: self.pos.x += self.level.speed*dt
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = self.rect.centerx
        self.physics.collisions(self,"horizontal")
        
        self.gamemode.move(dt)
        self.rect.centery = round(self.pos.y)
        self.hitbox.centery = self.rect.centery
        self.physics.collisions(self, "vertical")
        self.physics.border_collisions(self)
        
    def update(self, dt):
        self.input()
        self.move(dt)
        self.gamemode.rotate(dt)
        self.physics.special_collisions(self)
        self.trail.update(dt)
        self.gamemode.update(dt)
        self.was_pressing = self.key_pressed
        
    def draw(self):
        if self.deatheffect_obj: return
        if self.level.data.player_visible: self.trail.draw()
        self.gamemode.draw()
        if not self.level.data.player_visible: return
        offset_rect = self.rect.copy()
        offset_rect.centerx = PLAYER_X
        offset_rect.y -= self.level.offset.y
        if self.secondary_image:
            secondary_offset = self.secondary_rect.copy()
            if self.gravity > 0: secondary_offset.midbottom = offset_rect.center
            else: secondary_offset.midtop = offset_rect.center
            self.display_surface.blit(self.secondary_image if self.gravity > 0 else self.flipped_secondary,secondary_offset)
        self.display_surface.blit(self.image if self.gravity > 0 else self.flipped_image,offset_rect)
        