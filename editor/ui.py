import pygame
from settings import *
from damgui import damgui
from damgui import settings as guiconf

class EditorUI:
    def __init__(self, editor):
        self.editor = editor
        self.assets = self.editor.assets
        self.ui_assets = self.assets["ui"]
        self.display_surface = get_window()
        self.gui = self.editor.main.gui
        self.Stack = damgui.stack
        
        # images
        self.small_bg_imgs = [pygame.transform.scale_by(img,0.1261) for img in self.editor.background.bg_assets]
        self.small_gd_imgs = [pygame.transform.scale_by(img,0.5) for img in self.editor.background.ground_assets]
        self.bg_col_surf = pygame.Surface((180,100))
        self.gd_col_surf = pygame.Surface((180,100))
        self.bg_col_surf.fill(self.editor.data.bg_color)
        self.gd_col_surf.fill(self.editor.data.ground_color)
        # rects
        self.settings_win_rect = pygame.Rect(H_WIDTH-H_WIDTH//2,H_HEIGHT-H_HEIGHT//2-100,H_WIDTH,H_HEIGHT)
        self.mode_win_rect = pygame.Rect(H_WIDTH-MODE_CONT_W//2,HEIGHT-SPACING-CONTS_HEIGHT,MODE_CONT_W,CONTS_HEIGHT)
        self.edit_m_winrect = pygame.Rect(H_WIDTH-EDIT_MODE_W//2,HEIGHT-SPACING-CONTS_HEIGHT,EDIT_MODE_W,EDIT_MODE_H)
        self.other_win_rects = [
            pygame.Rect(SPACING,SPACING,80,80),
            pygame.Rect(WIDTH-SPACING-80,SPACING,80,80),
            pygame.Rect(H_WIDTH-HH_WIDTH,SPACING,H_WIDTH,100),
            pygame.Rect(SPACING,HEIGHT-SPACING-CONTS_HEIGHT,OTHER_CONT_W,CONTS_HEIGHT),
            pygame.Rect(WIDTH-SPACING-OTHER_CONT_W,HEIGHT-SPACING-CONTS_HEIGHT,OTHER_CONT_W,CONTS_HEIGHT),
        ]
        # assets
        self.blank_button = pygame.transform.scale_by(self.ui_assets["blankbutton"],0.66)
        self.dark_surf = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        self.dark_surf.fill("black"); self.dark_surf.set_alpha(120)
        self.make_buttons()
        self.make_assets()
        self.gamemode_portals = {name:pygame.transform.scale_by(self.level_assets["portals_ui"][name],0.8) for name in GAMEMODES}
        self.speed_portals = {name:pygame.transform.scale_by(self.level_assets["portals_ui"][name],0.8)for name in GAMEMODES_SPEEDS}
        
        self.win_cache = {}
        self.settings_open = self.scrolling = False
        self.build_category = "orbs"
        
    def make_buttons(self):
        self.ui_buttons = {
            "grid":self.gui.get_btn_surf("Grid"),
            "grid-on":self.gui.get_btn_surf("Grid","blue"),
            "snap":self.gui.get_btn_surf("Snap"),
            "snap-on":self.gui.get_btn_surf("Snap","blue"),
            "mulsel":self.gui.get_btn_surf("Mult.\nsel."),
            "mulsel-on":self.gui.get_btn_surf("Mult.\nsel.","blue"),
            "save":self.gui.get_btn_surf("Save",wide=True,fs="l"),
            "save-play":self.gui.get_btn_surf("Save & Play",wide=True,fs="l"),
            "save-exit":self.gui.get_btn_surf("Save & Exit",wide=True,fs="l"),
            "exit":self.gui.get_btn_surf("Exit",wide=True,fs="l"),
        }
        for dir in ["up","down","left","right"]:
            for size in ["s","d","t","ss"]: self.ui_buttons[f"{dir}-{size}"] = self.gui.get_arrow_btn(dir, size)
            
    def make_assets(self):
        self.level_assets = {}
        for category in BUILD_CATEGORIES:
            self.level_assets[category] = {}
            for name, image in self.assets["level"][category].items():
                height = image.get_height()
                factor_h = BUILD_CARD_H/height
                factor_w = (height*factor_h)/height
                self.level_assets[category][name] = pygame.transform.scale_by(image,(factor_w,factor_h))
        self.level_assets["portals_ui"] = {}
        for name, image in self.assets["level"]["portals"].items():
            height = image.get_height()
            factor_h = (BUILD_CARD_H*2)/height
            factor_w = (height*factor_h)/height
            self.level_assets["portals_ui"][name] = pygame.transform.scale_by(image,(factor_w,factor_h))
        
    def draw(self):
        if Input.keys_pressed[pygame.K_LCTRL]: return
        if self.editor.paused:
            self.gui_pause()
            return
        self.gui_mode()
        match self.editor.mode:
            case 0: self.gui_m_build()
            case 1: self.gui_m_edit()
            case 2: self.gui_m_delete()
        self.gui_options()
        self.gui_scroll()
        self.gui_settings()
        
    def gui_pause(self):
        self.display_surface.blit(self.dark_surf,(0,0))
        self.transparent_win("pause_win",(H_WIDTH-HH_WIDTH,H_HEIGHT-HH_HEIGHT),(H_WIDTH,H_HEIGHT))
        self.gui.btn_style()
        if damgui.place_centerx().image_button("unpause_btn",self.ui_assets["pause"]): self.editor.paused = False
        damgui.separator((10,20))
        if damgui.place_centerx().image_button("save_btn",self.ui_buttons["save"]): self.editor.save()
        if damgui.place_centerx().image_button("saveplay_btn",self.ui_buttons["save-play"]):
            self.editor.save()
            self.editor.play()
        if damgui.place_centerx().image_button("saveexit_btn",self.ui_buttons["save-exit"]):
            self.editor.save()
            self.editor.exit()
        if damgui.place_centerx().image_button("exit_btn",self.ui_buttons["exit"]): self.editor.exit()
        self.gui.btn_style_end()
        damgui.end()
        
    def gui_mode(self):
        self.transparent_win("mode_sel_win",(SPACING,HEIGHT-SPACING-CONTS_HEIGHT),(OTHER_CONT_W,10))
        self.gui.btn_style()
        # build, edit, delete
        if damgui.place_centerx().image_button("buildmode_btn",self.ui_assets["build-on" if self.editor.mode == 0 else "build-off"]): self.editor.mode = 0
        if damgui.place_centerx().image_button("editmode_btn",self.ui_assets["edit-on" if self.editor.mode == 1 else "edit-off"]): self.editor.mode = 1
        if damgui.place_centerx().image_button("deletemode_btn",self.ui_assets["delete-on" if self.editor.mode == 2 else "delete-off"]): self.editor.mode = 2
        self.gui.btn_style_end()
        damgui.end()
    
    def gui_options(self):
        self.transparent_win("options_win",(WIDTH-SPACING-OTHER_CONT_W,HEIGHT-SPACING-CONTS_HEIGHT),(OTHER_CONT_W,10))
        self.gui.btn_style()
        # grid toggle
        if damgui.image_button("grid_btn",self.ui_buttons["grid-on" if self.editor.grid_active else "grid"]):
            self.editor.grid_active = not self.editor.grid_active
        # multiselect toggle
        if damgui.place_side().image_button("grid_btn",self.ui_buttons["mulsel-on" if self.editor.multiselect_active else "mulsel"]):
            self.editor.multiselect_active = not self.editor.multiselect_active
        # snap toggle
        if damgui.image_button("snap_btn",self.ui_buttons["snap-on" if self.editor.snap_grid else "snap"]):
            self.editor.snap_grid = not self.editor.snap_grid
        # delete btn
        if damgui.place_side().image_button("quickdel_btn",self.ui_assets["trash"]):
            self.editor.delete_selected()
        self.gui.btn_style_end()
        damgui.end()
        
    def gui_m_build(self):
        self.centerx_win("build_m_win","Select Building",(MODE_CONT_W,CONTS_HEIGHT),HEIGHT-SPACING-CONTS_HEIGHT,False,True)
        for i, category in enumerate(BUILD_CATEGORIES):
            if i > 0: damgui.place_side()
            if damgui.button(f"{category}_build_btn",category.title()): self.build_category = category
        damgui.place_side().label("selected_b_il",f"Selected: {self.editor.selected_build[0].title()}, {self.editor.selected_build[1].title()}")
        x = 0
        for i,(name, image) in enumerate(self.level_assets[self.build_category].items()):
            if i > 0:
                if x < MODE_CONT_W-120: damgui.place_side()
                else: x = 0
            if damgui.image_button(f"{name}_build_btn",image): self.editor.select_build(self.build_category,name)
            x += self.Stack.last_element["sx"]+guiconf.MARGIN
        damgui.end()
        
    def gui_m_edit(self):
        self.centerx_win("edit_m_win","Edit Options",(EDIT_MODE_W,EDIT_MODE_H),HEIGHT-SPACING-CONTS_HEIGHT,False,True)
        # up
        for i,mul in enumerate(MOVE_MULS):
            if i > 0: damgui.place_side()
            if damgui.image_button(f"up_e{mul}_btn",self.ui_buttons["up-"+MUL_IMG_LOOKUP[mul]],(120,120)):
                self.editor.move_selected((0,-1),mul)
        # left
        damgui.place_side().separator((10,10))
        for mul in MOVE_MULS:
            if damgui.place_side().image_button(f"left_e{mul}_btn",self.ui_buttons["left-"+MUL_IMG_LOOKUP[mul]],(120,120)):
                self.editor.move_selected((-1,0),mul)
        # down
        for i,mul in enumerate(MOVE_MULS):
            if i > 0: damgui.place_side()
            if damgui.image_button(f"down_e{mul}_btn",self.ui_buttons["down-"+MUL_IMG_LOOKUP[mul]],(120,120)):
                self.editor.move_selected((0,1),mul)
        # right
        damgui.place_side().separator((10,10))
        for mul in MOVE_MULS:
            if damgui.place_side().image_button(f"right_e{mul}_btn",self.ui_buttons["right-"+MUL_IMG_LOOKUP[mul]],(120,120)):
                self.editor.move_selected((1,0),mul)
        damgui.end()
    
    def gui_m_delete(self): pass
        
    def gui_settings(self):
        self.transparent_win("settings_btn_win",(SPACING,SPACING),(100,100))
        self.gui.btn_style()
        if damgui.image_button("settings_btn",self.assets["ui"]["settings-gear"]): self.settings_open = not self.settings_open
        self.gui.btn_style_end()
        damgui.end()
        if not self.settings_open: return
        self.center_win("settings_win","Settings",(H_WIDTH,H_HEIGHT),offset=(0,-100))
        damgui.container("bggdimgcol_cont",(10,10),False,True,False,True)
        # bg gd image
        damgui.label("bggdindex_l","Background and ground image:")
        _, bg_index = damgui.slideshow("bg_idx_slides",self.small_bg_imgs,False,self.editor.data.bg_index)
        _, ground_index = damgui.place_side().slideshow("gd_idx_slides",self.small_gd_imgs,False,self.editor.data.ground_index)
        if bg_index != self.editor.data.bg_index:
            self.editor.data.bg_index = bg_index
            self.editor.background.refresh_bg_idx()
        if ground_index != self.editor.data.ground_index:
            self.editor.data.ground_index = ground_index
            self.editor.background.refresh_gd_idx()
        # bg gd color
        damgui.label("bgcols_l","Background and ground color:")
        bghardcode = not self.win_cache.get("bgcol_picker",{"open":False})["open"]
        gdhardcode = not self.win_cache.get("gdcol_picker",{"open":False})["open"]
        if damgui.image_button("bgcol_btn",self.bg_col_surf):
            if not "bgcol_picker" in self.win_cache: self.win_cache["bgcol_picker"] = {"open":True,"sliders":False}
            self.win_cache["bgcol_picker"]["open"] = True
        if damgui.place_side().image_button("gdcol_btn",self.gd_col_surf):
            if not "gdcol_picker" in self.win_cache: self.win_cache["gdcol_picker"] = {"open":True,"sliders":False}
            self.win_cache["gdcol_picker"]["open"] = True
        if self.win_cache.get("bgcol_picker",{"open":False})["open"]:
            newcolor = parse_color(*self.color_picker(self.editor.data.bg_color,"bgcol_picker",bghardcode))
            if newcolor != self.editor.data.bg_color:
                self.editor.data.bg_color = newcolor
                self.editor.background.refresh_bg_color()
                self.bg_col_surf.fill(newcolor)
        if self.win_cache.get("gdcol_picker",{"open":False})["open"]:
            newcolor = parse_color(*self.color_picker(self.editor.data.ground_color,"gdcol_picker",gdhardcode))
            if newcolor != self.editor.data.ground_color:
                self.editor.data.ground_color = newcolor
                self.editor.background.refresh_gd_color()
                self.gd_col_surf.fill(newcolor)
        damgui.end()
        # music
        cont_h= self.Stack.memory["bggdimgcol_cont"]["sy"]
        damgui.place_side().container("musicsel_cont",(350,cont_h),False,False,False,True)
        damgui.label("musicsel_l","Level music:")
        cont_h -= self.Stack.memory["musicsel_l"]["sy"]+guiconf.Y_MARGIN*3
        if cont_h < 10: cont_h = 10
        sel_music = damgui.selection_list("musicsel_sl",LEVEL_MUSICS,False,(340,cont_h),False)
        if sel_music:
            if sel_music != self.editor.data.level_music: self.editor.data.level_music = sel_music
        damgui.end()
        # start gamemode speed
        damgui.label("gamemode_l",f"Start gamemode and speed (Selected: {self.editor.data.start_gamemode.title()}, {self.editor.data.start_speed}):")
        for i,name in enumerate(GAMEMODES_SPEEDS):
            if i > 0: damgui.place_side()
            if damgui.image_button(f"{name}_portal",self.gamemode_portals[name] if name in GAMEMODES else self.speed_portals[name]):
                if name in GAMEMODES: self.editor.data.start_gamemode = name
                elif name in SPEED_NAMES: self.editor.data.start_speed = name
        damgui.end()
        
    def gui_scroll(self):
        # scroll
        self.transparent_win("scroll_win",(H_WIDTH-(scroll_w:=H_WIDTH)//2+25,SPACING),(scroll_w,100))
        amount = damgui.slider("scroll_slider",scroll_w-50)
        if self.Stack.last_element["unhover_press"]: 
            self.editor.slider_scroll(amount)
            self.scrolling = True
        else: self.scrolling = False
        damgui.end()
        # pause
        self.transparent_win("pause_btn_win",(WIDTH-SPACING-80,SPACING),(80,80))
        self.gui.btn_style()
        if damgui.image_button("pause_btn",self.assets["ui"]["pause"]): self.editor.paused = True
        self.gui.btn_style_end()
        damgui.end()
    
    # helpers
    def transparent_win(self, id, pos, size):
        guiconf.OUTLINE_ENABLED = False
        damgui.begin(id,"",pos,size,False)
        self.Stack.last_element["bg"] = False
        guiconf.OUTLINE_ENABLED = True
        
    def center_win(self, id, title, size, can_drag=False,can_scroll=False, offset=(0,0)):
        damgui.begin(id,title,(H_WIDTH-size[0]//2+offset[0],H_HEIGHT-size[1]//2+offset[1]),size,can_drag,can_scroll=can_scroll)
        
    def centerx_win(self, id, title, size, y_pos, can_drag=False, can_scroll=False, offsetx=0):
        damgui.begin(id,title,(H_WIDTH-size[0]//2+offsetx,y_pos),size,can_drag,can_scroll=can_scroll)
        
    def color_picker(self, current, id, hardcode=False):
        self.center_win(f"{id}","Choose a color",(250,150),True)
        damgui.label(f"{id}_sliders_l","Use sliders")
        was = self.win_cache.get(id,False)["sliders"]
        use_sliders = damgui.place_side().checkbox(f"{id}_sliders_check",(25,25))
        if use_sliders != was: hardcode = True
        if id in self.win_cache: self.win_cache[id]["sliders"] = use_sliders
        damgui.label(f"{id}_redl","R:",(30,0))
        if not use_sliders: red = damgui.place_side().entry_line(f"{id}_redel",(200,40),placeholder="Insert color (0-255)")
        else: red = int(damgui.place_side().slider(f"{id}_redels",180)*255)
        damgui.label(f"{id}_greenl","G:",(30,0))
        if not use_sliders: green = damgui.place_side().entry_line(f"{id}_greenel",(200,40),placeholder="Insert color (0-255)")
        else: green = int(damgui.place_side().slider(f"{id}_greenels",180)*255)
        damgui.label(f"{id}_bluel","B:",(30,0))
        if not use_sliders: blue = damgui.place_side().entry_line(f"{id}_blueel",(200,40),placeholder="Insert color (0-255)")
        else: blue = int(damgui.place_side().slider(f"{id}_blueels",180)*255)
        if hardcode:
            red, green, blue = current
            if not use_sliders:
                damgui.entryline_set_text(f"{id}_redel",str(red))
                damgui.entryline_set_text(f"{id}_greenel",str(green))
                damgui.entryline_set_text(f"{id}_blueel",str(blue))
            else:
                self.Stack.memory[f"{id}_redels"]["handle_pos"] = (red/255)*180-15
                self.Stack.memory[f"{id}_greenels"]["handle_pos"] = (green/255)*180-15
                self.Stack.memory[f"{id}_blueels"]["handle_pos"] = (blue/255)*180-15
        if damgui.button(f"{id}_quit_btn","Ok",(250,0)): self.win_cache[id] = {"open":False,"sliders":use_sliders}
        damgui.end()
        return str(red),str(green), str(blue)

    # state    
    def frame_start(self): self.Stack.mouserel = Input.mouse_rel
        