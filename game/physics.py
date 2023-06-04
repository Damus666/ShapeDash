import pygame
from settings import *
from game.sprites import *

class Physics:
    def __init__(self, level):
        self.level = level
        
    def collisions(self, player, direction):
        for sprite in self.level.collidable:
            if sprite.hitbox.colliderect(player.hitbox):
                if direction == "horizontal":
                    player.hitbox.right = sprite.hitbox.left
                    player.rect.centerx, player.pos.x = player.hitbox.centerx, player.hitbox.centerx
                    player.die()
                else:
                    player.hitbox.top = sprite.hitbox.bottom if player.y_dir < 0 else player.hitbox.top
                    player.hitbox.bottom = sprite.hitbox.top if player.y_dir > 0 else player.hitbox.bottom
                    player.rect.centery, player.pos.y = player.hitbox.centery-player.hitbox_offset, player.hitbox.centery-player.hitbox_offset
                    player.touch_ground()
                    
    def border_collisions(self, player):
        bottom_pos = GROUND_Y# if not self.level.top_border else LOW_GROUND_Y
        if player.hitbox.bottom > bottom_pos:
            player.hitbox.bottom = bottom_pos
            player.rect.centery, player.pos.y = player.hitbox.centery,player.hitbox.centery
            player.touch_ground()
            
        if not self.level.top_border: return
        if player.hitbox.top < LOW_TOP_Y+self.level.offset.y:
            player.hitbox.top = LOW_TOP_Y+self.level.offset.y
            player.rect.centery, player.pos.y = player.hitbox.centery,player.hitbox.centery
            player.touch_ground()
            
    def special_collisions(self, player):
        hitbox = player.hitbox
        for orb in self.level.orbs:
            if hitbox.colliderect(orb.hitbox): player.orb_collision(orb.name)
        for portal in self.level.portals:
            if hitbox.colliderect(portal.hitbox): player.portal_collision(portal.name)
        for damage in self.level.damaging:
            if hitbox.colliderect(damage.hitbox): player.damage_collision()
        for trigger in self.level.triggers:
            if not trigger.activated and trigger.rect.centerx <= hitbox.centerx: player.trigger_trigger(trigger)
        