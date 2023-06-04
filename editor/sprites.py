import pygame
from settings import *
from sprites import Generic

class Object(Generic):
    def __init__(self, id, pos, editor, groups):
        match id:
            case (category, name): id = get_id(category,name)
            case _: id = id
        self.category, self.name, surface = get_from_id(id)
        self.editor = editor
        super().__init__(pos, surface, groups, False)
        self.offset_rect = self.rect
        mask = pygame.mask.from_surface(self.image,threshold=2)
        self.selected_mask = mask.to_surface(setcolor=(0,255,0))
        self.selected_mask.set_alpha(255//1.5)
        self.move_dist = vector()
        self.pos = vector(self.rect.center)
        self.data = {}
        