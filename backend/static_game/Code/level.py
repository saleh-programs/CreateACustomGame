import pygame, sys
from pygame.math import Vector2 as vector
from random import choice,randint
from sprites import Generic, Block, Animated, Particle, Player, Enemy

from Settings import *
from support import *
from pygame.image import load

from controls import Controls, ControlButton

class Level:
    def __init__(self,grid,switch,asset_dict):
        self.display_surface = pygame.display.get_surface()
        self.switch = switch

        # groups
        self.all_sprites = CameraGroup()
        self.coin_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.shell_sprites = pygame.sprite.Group()


        self.false_keys = {
            "K_RIGHT": False,
            "K_LEFT": False,
            "K_UP": False,
            "K_DOWN": False,
            "K_SPACE": False,
            "K_RETURN": False
        }
        self.controls = Controls(self.false_keys)
        font = pygame.font.Font("fixed_graphics/PressStart2P-Regular.ttf", 15)
        self.exit_surf = font.render("Back to editor", True, "white").convert_alpha()
        size = 90
        margin = 6
        exit_rect = pygame.Rect((margin, margin), (size * 3, size * .75 )).move(0,0)
        self.exit = ControlButton(exit_rect, (), self.exit_surf, None)

        self.build_level(grid,asset_dict)


        # other support
        self.particle = asset_dict['particle']
        self.background = asset_dict['background']



    def build_level(self,grid,asset_dict):#,jump_sound):
        for layer_name, layer in grid.items():
            for pos, data in layer.items():
                if layer_name == 'terrain':
                    Generic(pos,asset_dict['terrain'],[self.all_sprites,self.collision_sprites])


                match data:
                    case 0:
                        self.player = Player(pos,asset_dict['player'],self.all_sprites, self.collision_sprites,LEVEL_LAYERS['player'])
                        self.player.false_keys = self.false_keys

                    #coins
                    case 2: Generic(pos - vector(Tile_Size//2,Tile_Size//2),asset_dict['coin'],[self.all_sprites,self.coin_sprites])
                    # enemies
                    case 3:
                        Enemy(asset_dict['enemy'],pos,[self.all_sprites,self.damage_sprites],self.collision_sprites)
                    # foreground trees
                    case 4:
                        Block((pos[0]+10,pos[1]+5),(36,25), self.collision_sprites)
                        Animated([asset_dict['tree']], pos, self.all_sprites)

                    # background trees
                    case 5: Animated([asset_dict['tree']], pos, self.all_sprites,LEVEL_LAYERS['bg']) # straight bg palm

        for sprite in self.shell_sprites:
            sprite.player = self.player
        for sprite in self.damage_sprites:
            sprite.player = self.player

    def get_coins(self):
        collided_coins = pygame.sprite.spritecollide(self.player,self.coin_sprites,True)
        for sprite in collided_coins:
            Particle([self.particle], sprite.rect.center,self.all_sprites)
    def get_damage(self):
        collision_sprites = [sprite for sprite in self.damage_sprites if self.player.hitbox.colliderect(sprite)]
        if collision_sprites:
            #self.hit_sound.play()
            self.player.damage()
    def give_damage(self):
        if self.player.attack_rect:
            for sprite in self.damage_sprites:
                if self.player.attack_rect.colliderect(sprite):
                    sprite.hit()


    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch()

            if event.type == pygame.MOUSEBUTTONDOWN and self.exit.rect.collidepoint(pygame.mouse.get_pos()):
                self.switch()
            self.controls.click_controls(event)

    def run(self,dt):
        #update
        self.event_loop()
        self.all_sprites.update(dt)
        self.exit.update()
        self.get_coins()
        self.get_damage()
        self.give_damage()

        self.display_surface.fill("white")
        self.all_sprites.custom_draw(self.player,self.background)
        self.display_surface.blit(self.exit.image, self.exit.rect)
        self.controls.display()

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # until here, above is exact copy of a regular sprite group

        self.display_surface = pygame.display.get_surface()
        self.offset = vector()

        self.left_margin = 800
        self.right_margin = width - 800

        self.top_margin = 350
        self.bottom_margin = height - 250

        self.leftwall = 0
        self.topwall = 0
        self.hor_center = width / 2
        self.ver_center = height / 2

        self.alt_height = height/2 + 20

    def custom_draw(self, player,back):
        # box camera
        if player.rect.centerx <= self.leftwall + self.left_margin:
            self.leftwall = player.rect.centerx - self.left_margin
            self.hor_center = self.leftwall + width/2

            self.offset.x = player.rect.centerx - self.left_margin
        elif player.rect.centerx >= self.leftwall + self.right_margin:
            self.leftwall = player.rect.centerx - self.right_margin
            self.hor_center = self.leftwall + width/2

            self.offset.x = player.rect.centerx - self.right_margin
        else:
            self.offset.x = self.hor_center - width / 2
        if player.rect.centery <= self.topwall + self.top_margin:
            self.topwall = player.rect.centery - self.top_margin
            self.ver_center = self.topwall + height/2

            self.offset.y = player.rect.centery - self.top_margin
        elif player.rect.centery >= self.topwall + self.bottom_margin:
            self.topwall = player.rect.centery - self.bottom_margin
            self.ver_center = self.topwall + height/2

            self.offset.y = player.rect.centery - self.bottom_margin
        else:
            self.offset.y = self.ver_center - height / 2



        self.display_surface.blit(back, (0, 0))

        all_sprites = [(sprite.image, sprite.rect.topleft - self.offset, sprite.z) for sprite in self if vector(player.rect.center).distance_to(vector(sprite.rect.center)) < 1800]

        all_sprites.sort(key = lambda sprite: sprite[2])
        all_sprites = [(sprite[0],sprite[1]) for sprite in all_sprites]

        if player.attack_rect:
            r = player.attack_rect.copy()
            r.x -= self.offset.x
            r.y -= self.offset.y
            pygame.draw.rect(self.display_surface, "red", r,2)
        for sprite in all_sprites:
            self.display_surface.blit(sprite[0],sprite[1])

            rect = sprite[0].get_rect(topleft=sprite[1])
            pygame.draw.rect(self.display_surface, "red", rect, 2)


