import pygame, json, os
from settings import *
from state import GameState
from background import Background
from editor.ui import EditorUI
from editor.sprites import *

class Editor(GameState):
    def __init__(self, main):
        super().__init__(main)
        self.assets = main.asset_loader
        
        self.offset = 0
        self.mode = 0 # 0: build, 1: edit, 2: delete
        self.selected_objects = []
        self.grid_x_amount = range((WIDTH//BLOCK_SIZE)+1)
        self.grid_active = self.snap_grid = True
        self.multiselect_active, self.top_border = False
        self.was_pressing = self.was_pressing_right = False
        self.paused = self.was_paused = False
        self.selected_build = ("blocks","classic")
        self.change_time = pygame.time.get_ticks()
        
        self.visible = CameraGroup(self)
        self.all = pygame.sprite.Group()
        
        self.data = EditorData(self)
        self.background = Background(self.assets["bg"],self.assets["ground"],self,True)
        self.ui = EditorUI(self)
    
    # button actions
    def save(self):
        with open("data/levels.json","r") as levels_file:
            level_list = json.load(levels_file)
            if self.data.level_name not in level_list["levels"]: level_list["levels"].append(self.data.level_name)
        with open("data/levels.json","w") as levels_file: json.dump(level_list,levels_file) 
        level_data = {
            "name":self.data.level_name,
            "description":self.data.level_description,
            "start_gamemode":self.data.start_gamemode,
            "start_speed":self.data.start_speed,
            "bg_color":self.data.bg_color,
            "ground_color":self.data.ground_color,
            "bg_index":self.data.bg_index,
            "ground_index":self.data.ground_index,
            "blocks":[ {
                "pos":block.rect.topleft,
                "category":block.category,
                "name":block.name,
                "data":block.data,
            } for block in self.all]
        }
        with open(f"data/levels/{self.data.level_name}.json","w") as level_file: json.dump(level_data,level_file)
        
    def load(self, name):
        with open(f"data/levels/{name}.json","r") as level_file: level_data = json.load(level_file)
        self.data.level_name = level_data["name"]
        self.data.level_description = level_data["description"]
        self.data.start_speed = level_data["start_speed"]
        self.data.start_gamemode = level_data["start_gamemode"]
        self.data.bg_index = level_data["bg_index"]
        self.data.ground_index = level_data["ground_index"]
        self.data.bg_color = level_data["bg_color"]
        self.data.ground_color = level_data["ground_color"]
        self.data.level_description = level_data["description"]
        self.background.refresh_bg_idx()
        self.background.refresh_gd_idx()
        self.ui.bg_col_surf.fill(self.data.bg_color)
        self.ui.gd_col_surf.fill(self.data.ground_color)
        for block_data in level_data["blocks"]: Object((block_data["category"],block_data["name"]),block_data["pos"],self,[self.all,self.visible])
        
    def exit(self):
        for obj in self.all: obj.kill()
        self.main.editor_exit()
        
    def play(self):
        self.main.game.go_back_to({"state":"editor"})
        self.main.play_level(self.data.level_name)
    
    # build
    def interaction_build(self, obj):
        if (obj.category != self.selected_build[0] and obj.name == self.selected_build[1]) or \
            (obj.category == self.selected_build[0] and obj.name != self.selected_build[1]):
            self.build_selected()
        
    def build_selected(self):
        obj = Object(self.selected_build,(Input.mouse_pos[0]+self.offset,Input.mouse_pos[1]),self,[self.all,self.visible])
        obj.rect.x = int(obj.rect.x-(obj.rect.x%BLOCK_SIZE))
        obj.rect.y = int(obj.rect.y-(obj.rect.y%BLOCK_SIZE))-4
        
    def select_build(self, category, name): self.selected_build = (category,name)
    
    # edit
    def interaction_edit(self, obj):
        if not self.multiselect_active:
            if obj in self.selected_objects and not self.was_pressing: self.selected_objects.clear()
            elif not self.was_pressing:
                self.selected_objects.clear()
                self.selected_objects.append(obj)
        else:
            if obj in self.selected_objects:
                if Input.keys_pressed[pygame.K_LSHIFT]: self.selected_objects.remove(obj)
            elif not Input.keys_pressed[pygame.K_LSHIFT]: self.selected_objects.append(obj)
            
    def move_selected(self, direction, mul):
        for obj in self.selected_objects:
            obj.pos.x += BLOCK_SIZE*direction[0]*mul
            obj.pos.y += BLOCK_SIZE*direction[1]*mul
            obj.rect.center = (round(obj.pos.x),round(obj.pos.y))
            obj.hitbox.center = obj.rect.center
        
    # delete
    def delete_one(self, obj):
        obj.kill()
        
    def delete_selected(self):
        for obj in self.selected_objects: obj.kill()
    
    # move
    def slider_scroll(self, amount):
        if len(self.all) <= 0: return
        far_x = 0
        for obj in self.all:
            if obj.rect.right > far_x: far_x = obj.rect.right
        self.move((far_x*amount-H_WIDTH)-self.offset)
    
    def move(self, dx):
        self.offset += dx
        if self.offset < 0: self.offset = 0; dx = 0
        self.background.ground_position -= dx
        self.background.bg_position -= dx/3
    
    # state
    def on_change(self):
        self.change_time = pygame.time.get_ticks()
        
    # update
    def update(self, dt):
        if Input.mouse_pressed[1] and not self.paused: self.move(-Input.mouse_rel[0])
        self.background.editor_update()
        
        can_interact = self.can_interact()
        if Input.mouse_pressed[0] and can_interact:
            collided = False
            for obj in self.all:
                if obj.offset_rect.collidepoint(Input.mouse_pos):
                    collided = True
                    match self.mode:
                        case 0: self.interaction_build(obj); break
                        case 1: self.interaction_edit(obj); break
                        case 2: self.delete_one(obj); break
            if self.mode == 0 and not collided: self.build_selected()
        else:
            if Input.mouse_pressed[2] and can_interact:
                if self.was_pressing_right:
                    for obj in self.selected_objects:
                        obj.rect.center = vector(Input.mouse_pos)-obj.move_dist
                        if self.snap_grid:
                            obj.rect.x = int(obj.rect.x-(obj.rect.x%BLOCK_SIZE))
                            obj.rect.y = int(obj.rect.y-(obj.rect.y%BLOCK_SIZE))-4
                        obj.pos = vector(obj.rect.center)
                        obj.hitbox.center = obj.rect.center
                else:
                    for obj in self.selected_objects: obj.move_dist = vector(Input.mouse_pos)-vector(obj.rect.center)
        
        if not self.ui.settings_open and not self.paused:
            if Input.keys_pressed[pygame.K_1]: self.mode = 0
            elif Input.keys_pressed[pygame.K_2]: self.mode = 1
            elif Input.keys_pressed[pygame.K_3]: self.mode = 2
            elif Input.keys_pressed[pygame.K_4]: self.mode = 3
                        
        self.was_pressing = Input.mouse_pressed[0]
        self.was_pressing_right = Input.mouse_pressed[2]
        self.was_paused = self.paused
        
    def can_interact(self):
        if self.paused or self.was_paused: return False
        if Input.keys_pressed[pygame.K_LCTRL]: return True
        if self.ui.scrolling: return False
        if self.ui.settings_open and self.ui.settings_win_rect.collidepoint(Input.mouse_pos): return False
        if self.mode == 1:
            if self.ui.edit_m_winrect.collidepoint(Input.mouse_pos): return False
        elif self.ui.mode_win_rect.collidepoint(Input.mouse_pos): return False
        for rect in self.ui.other_win_rects:
            if rect.collidepoint(Input.mouse_pos): return False
        return True
        
    # event
    def event_loop(self):
        self.ui.frame_start()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit_all()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.paused = not self.paused
            self.main.gui.event(event)
    
    # draw
    def draw(self):
        if pygame.time.get_ticks() - self.change_time < WAIT_CD: return
        self.display_surface.fill((0,0,0))
        self.background.draw()
        if self.grid_active: self.draw_grid()
        self.visible.custom_draw()
        self.background.draw_after()
        self.ui.draw()
        
    def draw_grid(self):
        y = GROUND_Y-BLOCK_SIZE
        while True:
            pygame.draw.line(self.display_surface,GRID_COL,(0,y),(WIDTH,y),GRID_THICKNESS)
            y -= BLOCK_SIZE
            if y < 0: break
        pygame.draw.line(self.display_surface,GRID_COL,(0,GRID_THICKNESS//2),(WIDTH,GRID_THICKNESS//2),GRID_THICKNESS)
        o = -self.offset%BLOCK_SIZE
        for i in self.grid_x_amount:
            pygame.draw.line(self.display_surface,GRID_COL,(o+i*BLOCK_SIZE,0),(o+i*BLOCK_SIZE,GROUND_Y),GRID_THICKNESS)
        
class EditorData:
    def __init__(self, editor):
        self.editor = editor
        self.level_name, self.level_description = "Unnamed 0", ""
        self.start_gamemode, self.start_speed = "cube", "1x"
        self.bg_color = self.ground_color = (0,105,255)
        self.bg_index = self.ground_index = 0
        
class CameraGroup(pygame.sprite.Group):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.display_surface = get_window()
    
    def custom_draw(self):
        for sprite in self.spritedict:
            offset_rect = sprite.rect.copy()
            offset_rect.x -= self.editor.offset
            self.display_surface.blit(sprite.image,offset_rect)
            sprite.offset_rect = offset_rect
            if sprite in self.editor.selected_objects: self.display_surface.blit(sprite.selected_mask,offset_rect)
