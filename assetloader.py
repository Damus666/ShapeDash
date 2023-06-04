import pygame, plistlib
from settings import *

class AssetLoader:
    def __init__(self):
        self.assets = {}
    
    def pre_load(self):
        self.assets["other"] = {
            "loading_bg" : pygame.transform.scale(load("other/loading_bg",False,False),(HEIGHT,HEIGHT))
        }
        self.assets["ui"] = {
            "logo": load_scale("ui/logo",1.3*WIN_SCALE_X)
        }
        self.assets["fonts"] = {
            "m":pygame.font.Font(MAIN_FONT,22),
            "l":pygame.font.Font(MAIN_FONT,30),
            "xl":pygame.font.Font(MAIN_FONT,50),
            "xxl":pygame.font.Font(MAIN_FONT,80),
            "xxxxl":pygame.font.Font(MAIN_FONT,100),
        }
        
    def load(self):
        self.load_all()
        self.load_audio()
        self.load_player()
        self.load_ids()
        self.load_deatheffects()
        
    def load_audio(self):
        self.assets["fx-sounds"] = load_sounds("fx")
        
    def load_all(self):
        self.assets["bg"] = import_bgs("bg",False)
        self.assets["ground"] = import_bgs("ground",False)
        self.assets["achievements"] = import_assets("achievements",True,False)
        self.assets["gauntlets"] = import_assets("gauntlets",True,False)
        self.assets["trails"] = import_assets("trails",True,False)
        self.assets["ui"] = import_assets("ui",True,False,0.5)
        self.assets["ui"]["logo"] = load_scale("ui/logo",1.15*WIN_SCALE_X)
        self.assets["ui"].update( import_assets("ui-copied",True,False,1))
        self.assets["player"] = import_assets("player",True,True)
        self.assets["deatheffects"] = {
            "icons":import_assets("deatheffects/icons",True,False),
            "sheets":import_assets("deatheffects/sheets/png",True,False),
        }
        self.assets["level"] = {
            "orbs":import_assets("level/orbs",True,True),
            "blocks":import_assets("level/blocks",True,True),
            "objects":import_assets("level/objects",True,True),
            "portals":import_assets("level/portals",True,True),
            "triggers":import_assets("level/triggers",True,True),
        }
        
    def load_deatheffects(self):
        animations = {}
        for name, image in self.assets["deatheffects"]["sheets"].items():
            image_size, plist, frames = image.get_size(), None, []
            with open(f"assets/graphics/deatheffects/sheets/plist/{name}.plist","rb") as plistfile: plist = plistlib.load(plistfile)
            if not plist: raise Exception("PLIST error")
            new_name = int(name.replace("-hd","").replace("PlayerExplosion_",""))
            for f_data in plist["frames"].values():
                pos_str, size_str = f_data["textureRect"].split("},{")
                pos_x, pos_y = [int(v) for v in pos_str.replace("{{","").split(",")]
                size_x, size_y = [int(v) for v in size_str.replace("}}","").split(",")]
                if pos_x+size_x > image_size[0]: size_x -= (pos_x+size_x)-image_size[0]
                if pos_y+size_y > image_size[1]: size_y -= (pos_y+size_y)-image_size[1]
                frames.append(image.subsurface((pos_x,pos_y,size_x,size_y)))
            biggest, biggest_size, new_frames = None, (0,0), []
            for frame in frames:
                if vector((frame_size:=frame.get_size())).magnitude() > vector(biggest_size).magnitude():
                    biggest = frame; biggest_size = frame_size
            old_size = biggest.get_size()
            w_factor = IDEAL_DEW/old_size[0]; h_factor = int(old_size[0]*w_factor)/old_size[0]
            for frame in frames: new_frames.append(pygame.transform.scale(frame,(int(frame.get_width()*w_factor),int(frame.get_height()*h_factor))))
            animations[new_name] = new_frames
        self.assets["deatheffects"]["animations"] = animations
        
    def load_ids(self):
        index = 0
        for category, dictionary in self.assets["level"].items():
            for name, image in dictionary.items():
                LEVEL_IDS[index] = {
                    "category":category,
                    "name":name,
                    "image":image,
                }
                IDS_LOOKUP[category][name] = index
                index += 1
                
    def load_player(self):
        player = {
            "cube":{},
            "ship":{},
            "ball":{},
            "ufo":{},
            "wave":{},
            "robot":{},
            "spider":{},
        }
        
        for name, image in self.assets["player"].items():
            category, index = name.split("_")
            category = self.map_category(category)
            player[category][int(index)] = image
            PLAYER_IDS[category].append(int(index))
            
        del self.assets["player"]
        self.assets["player"] = player
        
    def get_player(self, category, index, main_color, secondary_color):
        surface:pygame.Surface = self.assets["player"][category][index]
        increase = 0.3
        for i in range(surface.get_width()):
            for j in range(surface.get_height()):
                color = surface.get_at((i,j))
                color = (color[0],color[1],color[2])
                if color == (0,0,0): continue
                if color == (255,255,255): color = secondary_color
                else:
                    if self.white_pixel_around(surface,i,j): color = secondary_color
                    else:
                        if color == (175,175,175): color = main_color
                        else:
                            col01 = color_to_01(color)
                            seccol01 = color_to_01(main_color)
                            newcolor = (pygame.math.clamp(seccol01[0]+increase,0,1)*col01[0],
                                        pygame.math.clamp(seccol01[1]+increase,0,1)*col01[1],
                                        pygame.math.clamp(seccol01[2]+increase,0,1)*col01[2])
                            color = color_to_255(newcolor)
                surface.set_at((i,j),color)
        return surface
    
    def white_pixel_around(self, surface, x, y):
        dirs = [(x-1,y),(x+1,y),(x-1,y-1),(x+1,y-1),(x,y-1),(x,y+1),(x-1,y+1),(x+1,y+1)]
        for dir in dirs:
            try:
                color = surface.get_at((dir[0],dir[1]))
                color = (color[0],color[1],color[2])
                if color == (255,255,255): return True
            except: pass
        return False
                
    def map_category(self, category):
        if category == "icon": return "cube"
        return category
        
    def __getitem__(self, name): return self.assets[name]
