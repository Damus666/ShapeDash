import pygame, math, sys
from pygame.math import Vector2 as vector
from os import walk
from os.path import join
from random import randint, choice, uniform

# window
TEST_WIN = False
SIZES = WIDTH, HEIGHT = 1920,1080
if TEST_WIN: SIZES = WIDTH, HEIGHT = 1200,800
H_WIDTH, H_HEIGHT = WIDTH//2, HEIGHT//2
HH_WIDTH, HH_HEIGHT = H_WIDTH//2, H_HEIGHT//2
FPS = 0 
TITLE = "Shape Dash"
WIN_SCALE_X = WIDTH/1920
WIN_SCALE_Y = HEIGHT/1080

# CONSTANTS

# level
ANIMATION_SPEED = 8
BLOCK_SIZE = 64
REAL_BLOCK_SIZE = 120
SCALE_FACTOR = BLOCK_SIZE/REAL_BLOCK_SIZE

GROUND_Y = HEIGHT-(HEIGHT//4.5)+BLOCK_SIZE-(BLOCK_SIZE//5)
LOW_GROUND_Y = HEIGHT-(HEIGHT//6.5)+BLOCK_SIZE-(BLOCK_SIZE//5)
TOP_Y = HEIGHT-GROUND_Y
LOW_TOP_Y = HEIGHT-LOW_GROUND_Y
Y_DIFF = GROUND_Y-LOW_GROUND_Y

# player
GRAVITY = 8500
UP_GRAVITY = GRAVITY
PLAYER_X = WIDTH//3.5

# ship
SHIP_FLY_SPEED = 3.5
SHIP_GRAVITY = 3000

# ball
BALL_GRAVITY = 12000

# paths
MAIN_FONT = "assets/fonts/main.ttf"

# DATA
# speed
JUMP_SPEEDS = {
    "normal":1550,
    "pink_orb":1450,
    "yellow_orb":1800,
    "red_orb":2200,
    "green_orb":2200,
}
SPEEDS = {
    "1x":600,
    "-1x":350,
    "2x":750,
    "3x":900,
    "4x":1100
}
# id
PLAYER_IDS = {
    "cube":[],
    "ship":[],
    "ball":[],
    "ufo":[],
    "wave":[],
    "robot":[],
    "spider":[],
}
IDS_LOOKUP = {
    "orbs":{},
    "blocks":{},
    "objects":{},
    "portals":{},
    "triggers":{}
}
LEVEL_IDS = {}
# object
DAMAGING = [
    "spike","saw","monster"
]
# trail
TRAILS = list(range(1,16)); TRAILS.remove(6); TRAILS.remove(9)

# colors
GRID_COL = (180,180,180)
SHIP_TRAIL_COLS = [
    (255,50,0),
    (255,200,0),
    (200,0,0),
    (150,0,0),
    (200,200,0),
    (100,100,0),
    (255,150,0),
    (200,150,0),
]
COLORS = [(125, 255, 0), (0, 255, 0), (0, 255, 125), (0, 255, 255),
          (0, 125, 255), (0, 0, 255), (125, 0, 255), (255, 0, 255),
          (255, 0, 125), (255, 0, 0), (255, 125, 0), (255, 255, 0),
          (255, 255, 255), (185, 0, 255), (255, 185, 0), (0, 0, 0),
          (0, 200, 255), (175, 175, 175), (90, 90, 90), (255, 125, 125),
          (0, 175, 75), (0, 125, 125), (0, 75, 175), (75, 0, 175),
          (125, 0, 125), (175, 0, 75), (175, 75, 0), (125, 125, 0),
          (75, 175, 0), (255, 75, 0), (150, 50, 0), (150, 100, 0),
          (100, 150, 0), (0, 150, 100), (0, 100, 150), (100, 0, 150),
          (150, 0, 100), (150, 0, 0), (0, 150, 0), (0, 0, 150),
          (125, 255, 175), (125, 125, 255)]
PORTAL_COLORS = {
    "ship":["pink","purple","magenta"],
    "ball":["red","orange","dark red"],
    "cube":["green", "dark green", "lime"]
}
GAMEMODES = [
    "cube","ship","ball"
]
SPEED_NAMES = list(SPEEDS.keys())
GAMEMODES_SPEEDS = [*GAMEMODES,*SPEED_NAMES]
ORBS_COLORS = {
    "blue":["blue","cyan","cyan"],
    "green":["green","lime","lime"],
    "pink":["purple","magenta","magenta"],
    "yellow":["light orange","yellow","yellow"],
    "red":["dark orange","red","red"],
}

# EDITOR
GRID_THICKNESS = 1
SPACING = 10
CONTS_HEIGHT = 300
MODE_CONT_W = int(H_WIDTH*1.5)
OTHER_CONT_W = (WIDTH-MODE_CONT_W)//2-SPACING*4
MOVE_MULS = [1,5,10,0.1]
MUL_IMG_LOOKUP = {
    1:"s",
    5:"d",
    10:"t",
    0.1:"ss",
}
EDIT_MODE_W, EDIT_MODE_H = (120*8+10+2*8, 120*2+2*2)
BUILD_CATEGORIES = list(IDS_LOOKUP.keys())
BUILD_CARD_H = 80

# menu
MENU_SPEED = 200
WAIT_CD = 70

# numeric
ONE_OVER_1000 = 1/1000
IDEAL_DEW = 280

# SUPPORT

# generic
def quit_all(): pygame.quit(); sys.exit()
def get_window(): return pygame.display.get_surface()

def list_remove_cond(iterable, condition):
    toremove = [el for el in iterable if condition(el)]
    for e in toremove: iterable.remove(e)
    
# input
class Input:
    mouse_pos = (0,0)
    mouse_rel = (0,0)
    mouse_pressed = None
    keys_pressed = None
    
    @classmethod
    def update(cls):
        cls.mouse_pos = pygame.mouse.get_pos()
        cls.mouse_rel = pygame.mouse.get_rel()
        cls.mouse_pressed = pygame.mouse.get_pressed()
        cls.keys_pressed = pygame.key.get_pressed()
        
# level
def get_id(category, name): return IDS_LOOKUP[category][name]

def get_from_id(id):
    data = LEVEL_IDS[id]
    return data["category"],data["name"],data["image"]

def blocks(num=1): return BLOCK_SIZE*num
def blocks_g(num=1): return GROUND_Y-BLOCK_SIZE*num
def block_p(block_x=0,block_y=1): return (BLOCK_SIZE*block_x,GROUND_Y-BLOCK_SIZE*block_y)

# import
def load(path,convert_alpha = True,scale_factor=True):
    image = pygame.image.load("assets/graphics/"+path+".png").convert_alpha() if convert_alpha else pygame.image.load("assets/graphics/"+path+".png").convert()
    if scale_factor: return pygame.transform.scale_by(image,SCALE_FACTOR)
    return image

def load_scale(path,scale_factor,convert_alpha = True):
    return pygame.transform.scale_by(pygame.image.load("assets/graphics/"+path+".png").convert_alpha() if convert_alpha \
        else pygame.image.load("assets/graphics/"+path+".png").convert() ,scale_factor)
    
def import_folder(path,convert_alpha = True, scale_factor=True):
    images = []
    for _, _, image_names in walk("assets/graphics/"+path):
        for image_name in image_names:
            full_path = "assets/graphics/"+join(path,image_name)
            image = pygame.image.load(full_path).convert_alpha() if convert_alpha else pygame.image.load(full_path).convert()
            if scale_factor: image = pygame.transform.scale_by(image,SCALE_FACTOR)
            images.append(image)
        break
    return images

def import_bgs(path, convert_alpha=True):
    images = import_folder(path,convert_alpha,False)
    new_images = []
    for image in images:
        new_images.append(pygame.transform.scale(image,(int(image.get_width()*(WIN_SCALE_X+0.1)),int(image.get_height()*(WIN_SCALE_Y+0.1)))))
    return new_images

def import_assets(path,convert_alpha = True, scale_factor=True, custom_scale=None):
    images = {}
    for _, sub_f, image_names in walk("assets/graphics/"+path):
        for image_name in image_names:
            full_path = "assets/graphics/"+join(path,image_name)
            scale_factor_ = SCALE_FACTOR if not "ship_" in image_name else SCALE_FACTOR*1.5
            if custom_scale: scale_factor_ = custom_scale
            image = pygame.image.load(full_path).convert_alpha() if convert_alpha else pygame.image.load(full_path).convert()
            if scale_factor or custom_scale: image = pygame.transform.scale_by(image,scale_factor_)
            images[image_name.split(".")[0]] = image
        break
    return images

def count_pngs(path):
    count = 0
    for _, sub_f, files in walk(path):
        for sub_n in sub_f: count += count_pngs(path+"/"+sub_n)
        for f in files:
            if f.endswith("png"): count += 1
    return count 

# math
def angle_to_vec(angle):
    return vector(math.cos(math.radians(angle)),-math.sin(math.radians(angle)))

def weighted_choice(sequence,weights):
    weightssum = sum(weights)
    chosen = randint(0,weightssum)
    cweight = 0; i = 0
    for w in weights:
        if inside_range(chosen,cweight,cweight+w): return sequence[i]
        cweight += w; i += 1
        
def weighted_choice_combined(sequence_and_weights):
    sequence = [s_a_w[0] for s_a_w in sequence_and_weights]
    weights = [saw[1] for saw in sequence_and_weights]
    weightssum = sum(weights)
    chosen = randint(0,weightssum)
    cweight = 0; i = 0
    for w in weights:
        if inside_range(chosen,cweight,cweight+w): return sequence[i]
        cweight += w; i += 1
        
def lerp(start, end, t): return start * (1 - t) + end * t
def inside_range(number:float|int,rangeStart:float|int,rangeEnd:float|int)->bool:
    return number >= min(rangeStart,rangeEnd) and number <= max(rangeStart,rangeEnd)

# color
def color_to_01(color):
    if len(color) == 4: color = (color[0],color[1],color[2])
    r, g, b = color
    return r/255.0, g/255.0, b/255.0

def color_to_255(color):
    if len(color) == 4: color = (color[0],color[1],color[2])
    r, g, b = color
    return int(r*255), int(g*255), int(b*255)

def parse_color(red:str, green:str, blue:str):
    r, g, b = 0,0,0
    if red.isdecimal(): r = pygame.math.clamp(int(red),0,255)
    if green.isdecimal(): g = pygame.math.clamp(int(green),0,255)
    if blue.isdecimal(): b = pygame.math.clamp(int(blue),0,255)
    return r,g,b

# big boi
def create_soft_outline(
    surface: pygame.Surface,
    radius: int,
    color: pygame.Color | list[int] | tuple[int, ...] = (0, 0, 0, 255),
    border_inflate_x: int = 0,
    border_inflate_y: int = 0,
    mask_threshold=127,
    sharpness_passes: int = 0,
) -> pygame.Surface:
    """
    Parameters
    ----------
    surface : pygame.Surface
        The input surface.
    radius : int
        The outline radius.
    color : pygame.Color | tuple[int, ...], optional
        The outline color, by default (0, 0, 0, 255).
    border_inflate_x : int, optional
        Extra padding to add to the outline on the x-axis, to prevent atrifacts, by default 0.
    border_inflate_y : int, optional
        Extra padding to add to the outline on the y-axis, to prevent atrifacts, by default 0.
    mask_threshold : int, optional
        The opacity threshold to use for silouhette generation, by default 127.
    sharpness_passes : int, optional
        The amount of extra sharpness passes to perform on the outline, by default 0.
    """
    surf_size = surface.get_size()
    backdrop_surf_size = (
        surf_size[0] + radius + border_inflate_x,
        surf_size[1] + radius + border_inflate_y,
    )

    silhouette = pygame.mask.from_surface(surface, threshold=mask_threshold).to_surface(
        setcolor=color, unsetcolor=(0, 0, 0, 0)
    )
    backdrop = pygame.Surface((backdrop_surf_size), pygame.SRCALPHA)
    blit_topleft = (
        backdrop_surf_size[0] / 2 - surf_size[0] / 2,
        backdrop_surf_size[1] / 2 - surf_size[1] / 2,
    )
    backdrop.blit(silhouette, blit_topleft)
    backdrop_blurred = pygame.transform.gaussian_blur(backdrop, radius=radius)
    for _ in range(sharpness_passes):
        backdrop_blurred.blit(backdrop_blurred, (0, 0))
        
    backdrop_blurred.blit(surface, blit_topleft)
    return backdrop_blurred

def create_outline(
    surface: pygame.Surface,
    radius: int,
    color: pygame.Color | list[int] | tuple[int, ...] = (0, 0, 0, 255),
    rounded: bool = False,
    border_inflate_x: int = 0,
    border_inflate_y: int = 0,
    mask_threshold=127,
    sharpness_passes: int = 4,
) -> pygame.Surface:
    surf_size = surface.get_size()
    backdrop_surf_size = (
        surf_size[0] + radius + border_inflate_x,
        surf_size[1] + radius + border_inflate_y,
    )

    silhouette = pygame.mask.from_surface(surface, threshold=mask_threshold).to_surface(
        setcolor=color, unsetcolor=(0, 0, 0, 0)
    )
    backdrop = pygame.Surface((backdrop_surf_size), pygame.SRCALPHA)
    blit_topleft = (
        backdrop_surf_size[0] / 2 - surf_size[0] / 2,
        backdrop_surf_size[1] / 2 - surf_size[1] / 2,
    )
    backdrop.blit(silhouette, blit_topleft)
    backdrop_blurred = (
        pygame.transform.gaussian_blur(backdrop, radius=radius)
        if rounded
        else pygame.transform.box_blur(backdrop, radius=radius)
    )
    for _ in range(sharpness_passes):
        backdrop_blurred.blit(
            backdrop_blurred, (0, 0), special_flags=pygame.BLEND_RGBA_ADD
        )

    backdrop_blurred.blit(surface, blit_topleft)
    return backdrop_blurred
