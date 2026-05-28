import random

import pygame
import sys
import asyncio

from Settings import *
from pygame.image import load
from pygame.math import Vector2 as vector

from LevelEditor import Editor
from support import *
from level import Level

from os import walk
from timer import Timer

class  Main:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        #data
        self.imports()

        self.editor_active = True
        self.transition = Transition(self.toggle)
        self.editor = Editor(self.switch)

        #cursor
        CursorSurf = load('fixed_graphics/cursor.png').convert_alpha()
        Cursor = pygame.cursors.Cursor((0,0),CursorSurf)
        pygame.mouse.set_cursor(Cursor)

        self.times = []
        self.count = 0
    def imports(self):
        self.terrain = load('custom_graphics/terrain/0.png').convert_alpha()
        self.coin = load('custom_graphics/coin/0.png').convert_alpha()
        self.tree = load("custom_graphics/tree/0.png").convert_alpha()
        self.particle = load("fixed_graphics/particle.png")
        self.enemy = import_folder('custom_graphics/enemy/')
        self.background = load("custom_graphics/background/0.png").convert_alpha()

        # player
        self.playergraphics = {folder: import_folder(f'custom_graphics/player/{folder}') for folder in list(walk(
            'custom_graphics/player'))[0][1]}

    def toggle(self):
        self.editor_active = not self.editor_active

    def switch(self,grid = None):
        asset_dict = {
            'terrain': self.terrain,
            'coin':self.coin,
            'tree': self.tree,
            'enemy':self.enemy,
            'player': self.playergraphics,
            "particle": self.particle,
            'background': self.background
            }

        if grid and not self.transition.active:
            self.level = Level(grid,self.switch,asset_dict)


        self.transition.active = True
    async def run(self):
        while True:
            dt = self.clock.tick() / 1000

            if dt > .1:
                dt = .1

            if self.editor_active:
                self.editor.run(dt)
            else:
                self.level.run(dt)

            self.transition.display(dt)
            pygame.display.update()
            await asyncio.sleep(0)


class Transition:
    def __init__(self,toggle):
        self.display_surface = pygame.display.get_surface()
        self.toggle = toggle
        self.active = False

        self.border_width = 0
        self.direction = 1
        self.center = (width / 2, height / 2)
        self.radius = vector(self.center).magnitude()
        self.threshold = self.radius + 200
    def display(self,dt):
        if self.active:
            self.border_width += 800 * dt * self.direction
            if self.border_width > self.threshold:
                self.border_width = self.threshold
                self.direction = -1
                self.toggle()
            if self.border_width < 0:
                self.active = False
                self.border_width = 1
                self.direction = 1
            pygame.draw.circle(self.display_surface,'black',self.center,self.radius,int(self.border_width))

if __name__ == '__main__':
    main = Main()
    asyncio.run(main.run())

