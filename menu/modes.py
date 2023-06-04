import pygame, json, os
from settings import *
from damgui import damgui
from damgui import settings as guiconf

class MenuMode:
    def __init__(self, menu):
        self.menu = menu
        self.display_surface = get_window()
        self.assets = self.menu.assets
        self.ui_assets = self.assets["ui"]
        self.gui = self.menu.main.gui
        self.change_time = pygame.time.get_ticks()
        
    def update(self, dt):...
    def event(self, event):...
    def draw(self):...
    def on_change(self): self.change_time = pygame.time.get_ticks()
    
class MenuMainScreen(MenuMode):
    def __init__(self, menu):
        super().__init__(menu)
        
        self.logo_surf = self.ui_assets["logo"];self.logo_rect = self.logo_surf.get_rect(center=(H_WIDTH,H_HEIGHT-HH_HEIGHT*1.2))
        self.play_btn = MenuButton(self.ui_assets["play-main"],(H_WIDTH,H_HEIGHT))
        self.edit_btn = MenuButton(self.ui_assets["edit-main"],(H_WIDTH+HH_WIDTH//(2.3*WIN_SCALE_X),H_HEIGHT))
        self.icon_btn = MenuButton(self.ui_assets["icon-main"],(H_WIDTH-HH_WIDTH//(2.3*WIN_SCALE_X),H_HEIGHT))
        self.close_btn = MenuButton(self.ui_assets["close"],(WIDTH-self.ui_assets["close"].get_width()-SPACING,SPACING),True)
        
    def update(self, dt):
        if pygame.time.get_ticks() - self.change_time < WAIT_CD: return
        if self.play_btn.check(): self.menu.change_mode("play")
        if self.icon_btn.check(): self.menu.change_mode("iconkit")
        if self.edit_btn.check(): self.menu.change_mode("levels")
        if self.close_btn.check(): quit_all()
        
    def draw(self):
        if pygame.time.get_ticks() - self.change_time < WAIT_CD: return
        self.display_surface.blit(self.logo_surf,self.logo_rect)
        self.play_btn.draw(self.display_surface)
        self.icon_btn.draw(self.display_surface)
        self.edit_btn.draw(self.display_surface)
        self.close_btn.draw(self.display_surface)
        
    def on_change(self): self.change_time = pygame.time.get_ticks()
        
class MenuIconkit(MenuMode):
    def __init__(self, menu):
        super().__init__(menu)
        self.back_button = MenuButton(self.ui_assets["back"],(SPACING,SPACING),True)
        
    def draw(self):
        if pygame.time.get_ticks() - self.change_time < WAIT_CD: return
        self.back_button.draw(self.display_surface)
        
    def update(self, dt):
        if pygame.time.get_ticks() - self.change_time < WAIT_CD: return
        if self.back_button.check(): self.menu.change_mode("main")
        
    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.menu.change_mode("main")
            
    def on_change(self): self.change_time = pygame.time.get_ticks()
        
class MenuLevelList(MenuMode):
    def __init__(self, menu):
        super().__init__(menu)
        self.back_button = MenuButton(self.ui_assets["back"],(SPACING,SPACING),True)
        self.plus_button = MenuButton(self.ui_assets["plus-big"],(WIDTH-(wdth:=self.ui_assets["plus-big"].get_width())-SPACING,HEIGHT-wdth-SPACING),True)
        self.frame_surf = pygame.transform.scale_by(self.ui_assets["frame-big"],(1*WIN_SCALE_X,0.85*WIN_SCALE_Y))
        self.frame_rect = self.frame_surf.get_rect(center=(H_WIDTH,H_HEIGHT))
        self.cont_rect = self.frame_rect.inflate(-110*WIN_SCALE_X,-160*WIN_SCALE_Y)
        self.title_surf = self.ui_assets["levels-title"]; self.title_rect = self.title_surf.get_rect(midbottom=self.frame_rect.midtop)
        self.Stack = damgui.stack
        self.viewbtn_surf = self.gui.get_btn_surf("VIEW",small_wide=True,fs="l")
        self.viewbtn_w = self.viewbtn_surf.get_width()
        self.on_change()
        
    def new_level(self):
        already_existing = []
        for l_name in self.level_names:
            if l_name.startswith("Unnamed"):
                num = l_name.split(" ")[1].strip()
                if num.isdecimal():
                    num = int(num)
                    if num not in already_existing: already_existing.append(num)
        level_num = max(already_existing) +1
        name = f"Unnamed {level_num}"
        self.level_names = [name,*self.level_names]
        with open("data/levels.json","w") as levels_file: json.dump({"levels":self.level_names},levels_file) 
        level_data = {
            "name":name,
            "description":"No description",
            "start_gamemode":"cube",
            "start_speed":"1x",
            "bg_color":(0,105,255),
            "ground_color":(0,105,255),
            "bg_index":0,
            "ground_index":0,
            "blocks":[]
        }
        with open(f"data/levels/{name}.json","w") as level_file: json.dump(level_data,level_file)
        
    def on_change(self):
        self.level_names = []
        with open("data/levels.json","r") as levels_file: self.level_names = json.load(levels_file)["levels"]
        self.change_time = pygame.time.get_ticks()
        
    def draw(self):
        if pygame.time.get_ticks() - self.change_time < WAIT_CD: return
        self.back_button.draw(self.display_surface)
        self.plus_button.draw(self.display_surface)
        self.display_surface.blit(self.frame_surf,self.frame_rect)
        self.display_surface.blit(self.title_surf,self.title_rect)
        # damgui
        guiconf.set_font_size("xxl")
        damgui.begin("levellist_win","",self.cont_rect.topleft,self.cont_rect.size,False,False,False,True)
        (win:=self.Stack.memory["levellist_win"])["bg"] = False; win["outline"] = False
        for level_name in self.level_names:
            self.gui.btn_style()
            damgui.label(f"{level_name}_label",f" {level_name}")
            damgui.place_side().separator((self.cont_rect.w-30-self.viewbtn_w-self.Stack.last_element["sx"],10))
            if damgui.place_side().image_button(f"{level_name}_viewbtn",self.viewbtn_surf):
                self.menu.set_level(level_name)
                self.menu.change_mode("details")
            self.gui.btn_style_end()
            damgui.line(self.cont_rect.w-10,2,10)
        guiconf.reset_font_size()
        damgui.end()
        
    def update(self, dt):
        if pygame.time.get_ticks() - self.change_time < WAIT_CD: return
        if self.back_button.check(): self.menu.change_mode("main")
        if self.plus_button.check(): self.new_level()
    
    def event(self, event):
        self.Stack.mouserel = Input.mouse_rel
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.menu.change_mode("main")

class MenuLevelDetails(MenuMode):
    def __init__(self, menu):
        super().__init__(menu)
        self.name_entry_id = "levelname_entryline"
        self.description_entry_id = "leveldescr_entryline"
        self.l_name = ""
        self.old_name = self.l_name
        self.l_data = None
        self.l_description = ""
        self.name_surf=self.name_rect = None
        imgsz = self.ui_assets["play-big"].get_width()
        
        self.back_button = MenuButton(self.ui_assets["back"],(SPACING,SPACING),True)
        self.play_btn = MenuButton(self.ui_assets["play-big"],(H_WIDTH+SPACING,H_HEIGHT-imgsz//1.5),True)
        self.edit_btn = MenuButton(self.ui_assets["edit-big"],(H_WIDTH-imgsz-SPACING,H_HEIGHT-imgsz//1.5),True)
        self.del_btn = MenuButton(self.ui_assets["trash"],(WIDTH-self.ui_assets["trash"].get_width()-SPACING,SPACING),True)
        
    def play(self):
        self.menu.main.game.go_back_to({"state":"menu","mode":"details"})
        self.menu.main.play_level(self.l_name)
        
    def edit(self): self.menu.main.editor_edit(self.l_name)
        
    def delete(self):
        self.save()
        with open("data/levels.json","r") as levels_file:
            levels_list = json.load(levels_file)
            levels_list["levels"].remove(self.l_name)
        with open("data/levels.json","w") as levels_file: json.dump(levels_list,levels_file)
        os.remove(f"data/levels/{self.old_name}.json")
        self.menu.change_mode("levels")
        
    def refresh_name_img(self):
        self.name_surf = self.assets["fonts"]["xxl"].render(self.l_name,True,"gold")
        self.name_surf = create_soft_outline(self.name_surf,3,(0,0,0,255),3,3)
        self.name_rect = self.name_surf.get_rect(midtop=(H_WIDTH,SPACING+HH_HEIGHT*0.2))
        
    def load(self, name):
        self.old_name = name
        self.l_name = name
        with open(f"data/levels/{name}.json","r") as level_file:
            self.l_data = json.load(level_file)
            self.l_description = self.l_data["description"]
        if damgui.id_exists(self.name_entry_id):
            damgui.entryline_set_text(self.name_entry_id,self.l_name)
        if damgui.id_exists(self.description_entry_id):
            damgui.entryline_set_text(self.description_entry_id,self.l_description)
        self.refresh_name_img()
        
    def save(self):
        if self.old_name != self.l_name:
            with open("data/levels.json","r") as levels_file:
                levels_list = json.load(levels_file)
                idx = levels_list["levels"].index(self.old_name)
                levels_list["levels"].pop(idx)
                levels_list["levels"].insert(idx,self.l_name)
            with open("data/levels.json","w") as levels_file:
                json.dump(levels_list,levels_file)
            os.remove(f"data/levels/{self.old_name}.json")
            self.old_name = self.l_name
        self.l_data["name"] = self.l_name
        self.l_data["description"] = self.l_description
        with open(f"data/levels/{self.l_name}.json","w") as level_file:
            json.dump(self.l_data,level_file)
        
    def on_change(self):
        self.load(self.menu.data.level_name)
        self.change_time = pygame.time.get_ticks()
        
    def draw(self):
        if pygame.time.get_ticks() - self.change_time < WAIT_CD: return
        self.back_button.draw(self.display_surface)
        self.display_surface.blit(self.name_surf,self.name_rect)
        self.play_btn.draw(self.display_surface)
        self.edit_btn.draw(self.display_surface)
        self.del_btn.draw(self.display_surface)
        # damgui
        guiconf.OUTLINE_ENABLED = False
        guiconf.BG_ENABLED = False
        self.gui.centerx_win("leveldetails_win","",(H_WIDTH,HH_HEIGHT),H_HEIGHT+HH_HEIGHT)
        guiconf.OUTLINE_ENABLED = True
        guiconf.BG_ENABLED = True
        damgui.place_centerx().label("leveldetail_info","Edit name and description:")
        cur_name = damgui.place_centerx().entry_line(self.name_entry_id,(HH_WIDTH,40),placeholder="Insert name...",start_text=self.l_name)
        if cur_name != self.l_name and len(cur_name) > 0:
            self.l_name = cur_name
            self.menu.set_level(self.l_name)
            self.refresh_name_img()
        self.l_description = damgui.place_centerx().entry_line(self.description_entry_id,(H_WIDTH,40),placeholder="Insert description...",start_text=self.l_description)
        damgui.end()
        
    def update(self, dt):
        if pygame.time.get_ticks() - self.change_time < WAIT_CD: return
        if self.back_button.check(): self.save();self.menu.change_mode("levels")
        if self.play_btn.check(): self.play()
        if self.edit_btn.check(): self.edit()
        if self.del_btn.check(): self.delete()
        
    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.save();self.menu.change_mode("levels")
        
class MenuPlayLevels(MenuMode):
    def __init__(self, menu):
        super().__init__(menu)
        self.back_button = MenuButton(self.ui_assets["back"],(SPACING,SPACING),True)
        
    def draw(self):
        if pygame.time.get_ticks() - self.change_time < WAIT_CD: return
        self.back_button.draw(self.display_surface)
        
    def update(self, dt):
        if pygame.time.get_ticks() - self.change_time < WAIT_CD: return
        if self.back_button.check(): self.menu.change_mode("main")
        
    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.menu.change_mode("main")
            
    def on_change(self): self.change_time = pygame.time.get_ticks()
        
class MenuButton:
    def __init__(self, image, pos, topleft=False):
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        if topleft: self.rect.topleft = pos
        self.clicking = False
        
    def draw(self, screen): screen.blit(self.image,self.rect)
        
    def check(self):
        if Input.mouse_pressed[0]:
            if not self.clicking:
                self.clicking = True
                if self.rect.collidepoint(Input.mouse_pos): return True
        else: self.clicking = False
        return False
