import pygame
from settings import *
from damgui import damgui
from damgui import settings as guiconf

class GUI:
    def __init__(self, main):
        self.main = main
        self.display_surface = get_window()
        self.assets = self.main.asset_loader
        self.ui_assets = self.assets["ui"]
        guiconf.create_fonts("assets/fonts/main.ttf",from_file=True,y_padding=4)
        guiconf.set_font_size("m")
        guiconf.builtin_theme("blue")
    
    # damgui
    def frame_start(self): damgui.frame_start()
    def event(self,event): damgui.register_event(event)
    def draw(self): damgui.frame_end(self.display_surface)
    
    # styles
    def btn_style(self):
        guiconf.OUTLINE_ENABLED = False
        guiconf.BG_ENABLED = False
        guiconf.PADDING = 0
    
    def btn_style_end(self):
        guiconf.OUTLINE_ENABLED = True
        guiconf.BG_ENABLED = True
        guiconf.PADDING = guiconf.defaults["PADDING"]
    
    # window
    def center_win(self, id, title, size, can_drag=False,can_scroll=False, offset=(0,0)):
        damgui.begin(id,title,(H_WIDTH-size[0]//2+offset[0],H_HEIGHT-size[1]//2+offset[1]),size,can_drag,can_scroll=can_scroll)
    def centerx_win(self, id, title, size, y_pos, can_drag=False, can_scroll=False, offsetx=0):
        damgui.begin(id,title,(H_WIDTH-size[0]//2+offsetx,y_pos),size,can_drag,can_scroll=can_scroll)
    
    # button
    def get_arrow_btn(self, dir, size):
        scale = 1 if size != "ss" else 0.7
        if size == "ss": size = "s"
        match dir:
            case "up": angle = 0
            case "down": angle = 180
            case "left": angle = 90
            case "right": angle = 270
        return pygame.transform.scale_by(pygame.transform.rotate(self.ui_assets[f"arrow-{size}"],angle),scale)
        
    def get_btn_surf(self, text, color="",small=False, fs="m", text_col = "white", wide=False, small_wide=False):
        text1 = ""
        if "\n" in text: text, text1 = text.split("\n")
        name = (f"btnbg-{color}" if not small else f"btnbg-s-{color}") if color else (f"btnbg" if not small else f"btnbg-s")
        if wide: name = "bg-wide"
        if small_wide: name = "blankbutton"
        bg = self.ui_assets[name].copy()
        txt_surf = self.assets["fonts"][fs].render(text,True,text_col)
        txt_surf = create_soft_outline(txt_surf,3)
        if text1:
            txt1_surf = self.assets["fonts"][fs].render(text1,True,text_col)
            txt1_surf = create_soft_outline(txt1_surf,3)
        bg_rect = bg.get_rect()
        if not text1: txt_rect = txt_surf.get_rect(center=bg_rect.center)
        else:
            txt_rect = txt_surf.get_rect(midbottom=bg_rect.center)
            txt1_rect = txt1_surf.get_rect(midtop=bg_rect.center)
        bg.blit(txt_surf,txt_rect)
        if text1: bg.blit(txt1_surf,txt1_rect)
        return bg
