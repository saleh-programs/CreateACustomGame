import pygame
from Settings import *
from pygame.image import load
from pygame.math import Vector2 as vector

from sprites import Generic

class Controls:
    def __init__(self, keys):
        self.display_surface = pygame.display.get_surface()
        font = pygame.font.Font("fixed_graphics/PressStart2P-Regular.ttf", 15)

        self.left_surf = load("fixed_graphics/left.png").convert_alpha()
        self.right_surf = load("fixed_graphics/right.png").convert_alpha()
        self.up_surf = load("fixed_graphics/up.png").convert_alpha()
        self.down_surf = load("fixed_graphics/down.png").convert_alpha()
        self.jump_surf = load("fixed_graphics/jump.png").convert_alpha()
        self.attack_surf = font.render("Attack", True, "white").convert_alpha()

        self.create_data()
        self.Create_ControlButtons()

        self.false_keys = keys

    def create_data(self):
        # Make dictionary of keys and associated menu surfaces
        self.menu_surfs = {}
        for key, value in EDITOR_DATA.items():
            if value['menu']:
                if not value['menu'] in self.menu_surfs:
                    self.menu_surfs[value['menu']] = [(key, load(value['menu_surf']))]
                else:
                    self.menu_surfs[value['menu']].append((key, load(value['menu_surf'])))

    def Create_ControlButtons(self):
        size = 90
        margin = 6
        topleft = (margin + size, height - (size) - margin)


        # Menu Tiles
        general_button_rect = pygame.Rect(topleft, (size , size ))
        button_margin = 5

        self.left = general_button_rect.move(-size, 0).inflate(-button_margin, -button_margin)
        self.right = general_button_rect.move(size, 0).inflate(-button_margin, -button_margin)
        self.up = general_button_rect.move(0, -size).inflate(-button_margin, -button_margin)
        self.down = general_button_rect.move(0, size).inflate(-button_margin, -button_margin)
        self.jump = general_button_rect.move(0, 0).inflate(-button_margin, -button_margin)

        self.attack =  pygame.Rect((margin, (height - margin - (size * 2))), (size * 3, size )).inflate(-button_margin * 15, -button_margin* 4)


        #create buttons
        self.control_buttons = pygame.sprite.Group()
        ControlButton(self.left, self.control_buttons, self.left_surf, "K_LEFT")
        ControlButton(self.right,self.control_buttons, self.right_surf, "K_RIGHT")
        # ControlButton(self.up, self.control_buttons, self.up_surf, "K_UP")
        # ControlButton(self.down, self.control_buttons, self.down_surf, "K_DOWN")
        ControlButton(self.jump, self.control_buttons, self.jump_surf, "K_SPACE")

        ControlButton(self.attack, self.control_buttons, self.attack_surf, "K_RETURN")
    def click_controls(self, event):
        for s in self.control_buttons:
            if s.control:
                self.false_keys[s.control] = s.mouse_click(event)
    def display(self):
        self.control_buttons.update()
        self.control_buttons.draw(self.display_surface)

class ControlButton(pygame.sprite.Sprite):
    def __init__(self, rect, group, surf, control):
        super().__init__(group)
        self.image = pygame.Surface(rect.size, pygame.SRCALPHA)
        self.rect = rect
        self.surf = surf
        self.pressed = False

        self.control = control
    def mouse_click(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed = False

        return self.pressed

    def update(self):
        self.image.fill('#80808080') if self.pressed else self.image.fill('#80808040')
        rect = self.surf.get_rect(center = (self.rect.width / 2, self.rect.height / 2))
        self.image.blit(self.surf, rect)
