import os, platform
from settings import *

class Debugger:
    def __init__(self):...
    
    def start(self):
        os.system("cls" if platform.system() == "Windows" else "clear")
        print(f"{TITLE} is running")
        print("[info] Python 3.11.3, pygame-ce 2.2.1, SDL 2.26.4")
        self.change_state("Menu")
    
    def change_state(self, name): print(f"[info] State changed to: {name}")
    def playing(self, name): print(f"[info] Playing level: {name}")
    def editing(self, name): print(f"[info] Editing level: {name}")
    def level_created(self, name): print(f"[info] Level created: {name}")
    def level_deleted(self, name): print(f"[info] Level deleted: {name}")
