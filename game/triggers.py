import pygame
from settings import *

def get_trigger(id, trigger, data):
    match id:
        case "Color": return ColorTrigger(trigger, data)
        case "HidePlayer": return HidePlayerTrigger(trigger, data)
        case "ShowPlayer": return ShowPlayerTrigger(trigger, data)
    raise Exception(f"No trigger class for '{id}'")

class ColorTrigger:
    def __init__(self, trigger, data): self.trigger, self.data = trigger, data
        
    def apply(self):
        if self.data["type"] == "bg": self.trigger.level.data.bg_color = self.data["color"]
        else: self.trigger.level.data.ground_color = self.data["color"]
        self.trigger.level.background.refresh_colors()
    
class HidePlayerTrigger:
    def __init__(self, trigger, data): self.trigger, self.data = trigger, data
    def apply(self): self.trigger.level.data.player_visible = False
        
class ShowPlayerTrigger:
    def __init__(self, trigger, data): self.trigger, self.data = trigger, data   
    def apply(self): self.trigger.level.data.player_visible = True
