import pygame
from Settings import *
from pygame.image import load
from pygame.math import Vector2 as vector

from sprites import Generic

class Menu:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.navigate_surf = load("fixed_graphics/navigate.png").convert_alpha()

        self.create_data()
        self.Create_Buttons()

    def create_data(self):
        # Make dictionary of keys and associated menu surfaces
        self.menu_surfs = {}
        for key, value in EDITOR_DATA.items():
            if value['menu']:
                if not value['menu'] in self.menu_surfs:
                    self.menu_surfs[value['menu']] = [(key, load(value['menu_surf']))]
                else:
                    self.menu_surfs[value['menu']].append((key, load(value['menu_surf'])))

    def Create_Buttons(self):
        # Menu Box
        size = 180
        margin = 6
        topleft = (width - size - margin, height - size - margin)
        self.rect = pygame.Rect(topleft, (size, size))

        # Menu Tiles
        general_button_rect = pygame.Rect(topleft, (size / 2, size / 2))
        button_margin = 5

        self.navigate_rect = general_button_rect.move(+(size / 4), -(size/2)).inflate(-button_margin, -button_margin)
        self.tile_rect = general_button_rect.copy().inflate(-button_margin, -button_margin)
        self.coin_rect = general_button_rect.move(+(size / 2), 0).inflate(-button_margin, -button_margin)
        self.enemy_rect = general_button_rect.move(+(size / 2), +(size / 2)).inflate(-button_margin, -button_margin)
        self.tree_rect = general_button_rect.move(0, +(size / 2)).inflate(-button_margin, -button_margin)

        #create buttons
        self.buttons = pygame.sprite.Group()
        Button(self.navigate_rect, self.buttons, self.menu_surfs["navigate"])
        Button(self.tile_rect,self.buttons,self.menu_surfs['terrain'])
        Button(self.coin_rect, self.buttons, self.menu_surfs['coin'])
        Button(self.enemy_rect, self.buttons, self.menu_surfs['enemy'])
        Button(self.tree_rect, self.buttons, self.menu_surfs['palm_fg'],self.menu_surfs['palm_bg'])

        bottomleft = (width - size - margin, height - (size + size / 2) - margin)
        self.rect = pygame.Rect(bottomleft, (size, size + size/2))

    def click(self,mouse_pos,mouse_button):
        for sprite in self.buttons:
            if sprite.rect.collidepoint(mouse_pos):
                if mouse_button[1]:
                    #toggle fg and bg
                    sprite.main_active = not sprite.main_active if sprite.items['alt'] else True
                if mouse_button[2]:
                    sprite.switch()

                return sprite.get_id()
        return sprite.get_id()
    def highlight_indicator(self,index):
        if EDITOR_DATA[index]['menu'] == 'terrain':
            pygame.draw.rect(self.display_surface,'black',self.tile_rect.inflate(4,4),5,6)
        if EDITOR_DATA[index]['menu'] == 'coin':
            pygame.draw.rect(self.display_surface,'black',self.coin_rect.inflate(4,4),5,6)
        if EDITOR_DATA[index]['menu'] == 'enemy':
            pygame.draw.rect(self.display_surface,'black',self.enemy_rect.inflate(4,4),5,6)
        if EDITOR_DATA[index]['menu'] in ('palm_fg','palm_bg'):
            pygame.draw.rect(self.display_surface,'black',self.tree_rect.inflate(4,4),5,6)
        if EDITOR_DATA[index]['menu'] == 'navigate':
            pygame.draw.rect(self.display_surface,'black',self.navigate_rect.inflate(4,4),5,6)
    def display(self,index):
        self.buttons.update()
        self.buttons.draw(self.display_surface)
        self.highlight_indicator(index)

class Button(pygame.sprite.Sprite):
    def __init__(self, rect, group, items, items_alt=None):
        super().__init__(group)
        self.image = pygame.Surface(rect.size)
        self.rect = rect

        # items
        self.items = {'main': items, 'alt': items_alt}
        self.index = 0
        self.main_active = True
    def get_id(self):
        return self.items['main' if self.main_active else 'alt'][self.index][0]
    def switch(self):
        self.index += 1
        self.index = 0 if self.index >= len(self.items['main' if self.main_active  else 'alt']) else self.index
    def update(self):
        self.image.fill('#ffd4a6')
        surf1 = self.items['main' if self.main_active else 'alt'][self.index][1].convert_alpha()
        surf = surf1#pygame.transform.smoothscale(surf1, (64,64))
        rect = surf.get_rect(center = (self.rect.width / 2, self.rect.height / 2))
        if rect.height > 70:
            # surf = pygame.transform.smoothscale(surf1, (65,90))
            rect = surf.get_rect(midbottom=(self.rect.width / 2, self.rect.height))
        elif rect.height < 40:
            rect = surf.get_rect(midbottom=(self.rect.width / 2, self.rect.height))

        self.image.blit(surf,rect)
