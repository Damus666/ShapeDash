import pygame, json
from pygame.sprite import AbstractGroup
from settings import *
from game.player import Player
from game.physics import Physics
from game.sprites import *
from background import Background
from assetloader import AssetLoader

class Level:
    def __init__(self, game):
        self.game = game
        self.display_surface = get_window()
        
        self.all = pygame.sprite.Group()
        self.collidable = pygame.sprite.Group()
        self.updates = pygame.sprite.Group()
        self.orbs = pygame.sprite.Group()
        self.portals = pygame.sprite.Group()
        self.triggers = pygame.sprite.Group()
        self.damaging = pygame.sprite.Group()
        
        self.data = LevelData(self)
        self.assets:AssetLoader = game.assets
        self.physics = Physics(self)
        self.player = Player(self)
        self.background = Background(self.assets["bg"],self.assets["ground"],self)
        self.offset = vector()
        
        self.visible_top = CameraGroup(self.player)
        self.visible = CameraGroup(self.player)
        self.draws = DrawGroup()
        
        self.speed = SPEEDS[self.data.start_speed]
        self.pause_btn = MenuButton(self.assets["ui"]["pause"],(WIDTH-SPACING-self.assets["ui"]["pause"].get_width(),SPACING),True)
        self.player.reset()
        
    def exit(self):
        for obj in self.all: obj.kill()
        self.game.apply_go_back()
        
    def load(self, name):
        with open(f"data/levels/{name}.json","r") as level_file:
            level_data = json.load(level_file)
        # set data
        self.data.level_name = level_data["name"]
        self.data.level_description = level_data["description"]
        self.data.start_speed = level_data["start_speed"]
        self.data.start_gamemode = level_data["start_gamemode"]
        self.data.bg_index = level_data["bg_index"]
        self.data.ground_index = level_data["ground_index"]
        self.data.bg_color = level_data["bg_color"]
        self.data.ground_color = level_data["ground_color"]
        self.data.level_description = level_data["description"]
        self.data.level_music = level_data["music"]
        # apply data
        self.change_speed(self.data.start_speed)
        self.player.set_gamemode(self.data.start_gamemode)
        self.background.refresh_bg_idx()
        self.background.refresh_gd_idx()
        for block_data in level_data["blocks"]:
            match block_data["category"]:
                case "blocks": Block(block_data["name"],block_data["pos"],self)
                case "triggers": Trigger(block_data["name"],block_data["pos"],self,block_data["data"])
                case "orbs": Orb(block_data["name"],block_data["pos"],self)
                case "portals": Portal(block_data["name"],block_data["pos"],self)
                case "objects":
                    if block_data["name"] in DAMAGING: Damaging(block_data["name"],block_data["pos"],self)
                    else: Object(("objects",block_data["name"]),block_data["pos"],self,[self.all,self.visible])
        self.player.reset()
        menu_data = self.game.main.menu.data
        menu_data.bg_index = self.data.bg_index
        menu_data.ground_index = self.data.ground_index
        menu_data.bg_color = self.data.bg_color
        menu_data.ground_color = self.data.ground_color
        menu_data.menu.background.refresh_bg_idx()
        menu_data.menu.background.refresh_gd_idx()
        
    def set_top_border(self, value): self.top_border = value
    def change_speed(self, speed_name): self.speed = SPEEDS[speed_name]
    
    # update
    def event(self, event): pass
        
    def update(self, dt):
        self.offset.x = self.player.rect.centerx - PLAYER_X
        if self.top_border: self.offset.y = Y_DIFF
        self.background.update(dt)
        self.player.update(dt)
        self.updates.update(dt)
        if self.pause_btn.check(): self.game.pause()
        
    def draw(self):
        self.background.draw()
        self.draws.custom_draw()
        self.visible.custom_draw(self.offset)
        self.player.draw()
        self.visible_top.custom_draw(self.offset)
        self.background.draw_after()
        if not self.game.paused: self.pause_btn.draw(self.display_surface)
        
class LevelData:
    def __init__(self, level):
        self.level = level
        self.level_name, self.level_description = "Unnamed 0", ""
        self.level_music = "Stereo Madness"
        self.start_gamemode, self.start_speed = "cube", "1x"
        self.bg_color = self.ground_color = (0,105,255)
        self.bg_index = self.ground_index = 0
        self.player_visible = True
        
class DrawGroup(pygame.sprite.Group):
    def __init__(self): super().__init__()
    
    def custom_draw(self):
        for sprite in self.spritedict: sprite.draw()
        
class CameraGroup(pygame.sprite.Group):
    def __init__(self, player):
        super().__init__()
        self.display_surface = get_window()
        self.player = player
    
    def custom_draw(self, offset):
        for sprite in self.spritedict:
            offset_rect = sprite.rect.copy()
            offset_rect.center -= offset
            self.display_surface.blit(sprite.image,offset_rect)
        