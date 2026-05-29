import pygame
import sys
import math
from pygame.math import Vector2 as vector
from Settings import *
from timer import *
from random import choice,randint
import time

# basic prepared image and rect sprite parent class
class Generic(pygame.sprite.Sprite):
    def __init__(self,pos,surf,group,z = LEVEL_LAYERS['main'],type = 'terrain'):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        self.type = type

# Blocks
class Block(Generic):
    def __init__(self, pos, size, group,type = 'tree'):
        surf = pygame.Surface(size)
        super().__init__(pos,surf,group)
        self.type = type


# simple animated objects
class Animated(Generic):
    def __init__(self,assets,pos,group,z = LEVEL_LAYERS['main']):
        self.animation_frames = assets
        self.frame_index = 0
        super().__init__(pos,self.animation_frames[0],group,z)
    def animate(self,dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index >= len(self.animation_frames):
            self.frame_index = 0
        self.image = self.animation_frames[int(self.frame_index)]
    def update(self,dt):
        self.animate(dt)

class Particle(Animated):
    def __init__(self,assets,pos,group):
        super().__init__(assets,pos,group)
        self.rect = self.image.get_rect(center = pos)
    def animate(self,dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.animation_frames):
            self.image = self.animation_frames[int(self.frame_index)]
        else:
            self.kill()

# Enemies
class Enemy(Generic):
    def __init__(self,assets,pos,group,collision_sprites):
        super().__init__(pos,assets[0],group)
        self.frames = assets
        self.frame_index = 0
        self.pos = vector(pos)
        self.direction = vector(1,0)

        self.collision_sprites = collision_sprites

        self.mask = pygame.mask.from_surface(self.image)
        self.hit_timer = Timer(400)
        self.speed = 50

        self.health_bar = HealthBar(self.rect.width,3,self.rect.topleft,self.groups()[0])


    def hit(self):
        if not self.hit_timer.active:
            self.health_bar.reduce(10)
            self.hit_timer.activate()

        if not self.health_bar.exists:
            self.kill()
    def check_collisions(self,type):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if type == 'horizontal':
                    if self.direction.x > 0:
                        self.rect.right = sprite.rect.left
                        self.direction.x = -1
                    elif self.direction.x < 0:
                        self.rect.left = sprite.rect.right
                        self.direction.x = 1
                self.pos.x = self.rect.x


    def move(self,dt):
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.check_collisions('horizontal')

        d = {-1: self.rect.bottomleft, 1: self.rect.bottomright}
        if not [sprite for sprite in self.collision_sprites if (sprite.rect.collidepoint(d[self.direction.x] + vector(0, 10)))]:
            self.direction.x *= -1
            self.orientation = 'right' if self.direction.x == 1 else 'left'

        self.health_bar.move(pos = (self.rect.x,self.rect.y))


    def animate(self,dt):
        self.frame_index += 10 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        if self.hit_timer.active:
            surf = self.mask.to_surface()
            surf.set_colorkey('black')
            self.image = surf
        if self.direction.x < 0:
            self.image = pygame.transform.flip(self.image, True,False)
    def update(self,dt):
        self.hit_timer.update()
        self.move(dt)
        self.animate(dt)

# player
class Player(Generic):
    def __init__(self,pos,assets,group,collision_sprites,z):
        # animation
        self.frames = assets
        self.frame_index = 0
        self.status = 'idle'
        self.orientation = 'right'
        surf = self.frames[f'{self.status}'][self.frame_index]
        super().__init__(pos, surf, group,z)
        self.mask = pygame.mask.from_surface(self.image)


        # movement
        self.way = 1
        self.direction = vector()
        self.pos = vector(self.rect.center)
        self.speed = 500
        self.gravity = 4
        self.on_floor = False

        # collision
        self.collision_sprites = collision_sprites
        self.hitbox = self.rect.inflate(-10,0)
        self.last_tile = None
        self.count = 0
        # timer
        self.hit_timer = Timer(400)

        self.jump_timer = Timer(50)
        self.was_active = False

        self.attack = False
        self.attack_rect = None

    # called in update
    def apply_gravity(self, dt):
        self.direction.y += self.gravity * dt
    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.orientation = 'right'
            self.way = 0
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.orientation = 'left'
            self.way = 140
        else:
            self.direction.x = 0
        # jump
        if keys[pygame.K_SPACE] and not self.jump_timer.active and self.on_floor:
            self.direction.y = -2
            self.jump_timer.activate()
        # attack
        if keys[pygame.K_RETURN]:
            self.frame_index = 0
            self.attack = True


    def check_on_floor(self):
        floor_rect = pygame.Rect((self.hitbox.left + 3, self.hitbox.bottom), (self.hitbox.width - 6, 2))
        floor_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.colliderect(floor_rect)]
        self.on_floor = True if floor_sprites else False

    def move(self, dt):
        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')
    def get_status(self):
        if self.on_floor and self.direction.x == 0:
            self.status = 'idle'
        elif self.on_floor:
            self.status = 'run'
        elif self.direction.y < 0:
            self.status = 'jump'
        else:
            self.status = 'fall'

        if self.attack:
            self.status = 'attack'
    def animate(self,dt):
        current_animation = self.frames[f'{self.status}']

        if self.status == 'run':
            self.frame_index += RUN_ANIMATION * dt
        elif self.status == 'attack':
            self.frame_index += 10 * dt
            self.attack_rect = pygame.Rect(self.hitbox.right - self.way,self.hitbox.top,110,64)
        elif self.jump_timer.active:
            self.frame_index += JUMP_ANIMATION * dt
        else:
            self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index >= len(current_animation)-0.5:
            self.frame_index = 0
            self.attack = False
            self.attack_rect = None

        self.image = current_animation[int(self.frame_index)]
        if self.orientation == "left":
            self.image = pygame.transform.flip(self.image,True, False)
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)

        if self.hit_timer.active:
            surf = self.mask.to_surface()
            surf.set_colorkey("black")
            self.image = surf

    # called in level
    def damage(self):
        if not self.hit_timer.active:
            self.hit_timer.activate()
            self.direction.y -= 1.5
    # called in move
    def collision(self,direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.rect.right
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx
                else:
                    self.hitbox.top = sprite.rect.bottom if self.direction.y < 0 else self.hitbox.top
                    self.hitbox.bottom = sprite.rect.top if self.direction.y > 0 else self.hitbox.bottom
                    self.rect.centery, self.pos.y = self.hitbox.centery, self.hitbox.centery
                    self.direction.y = 0
                self.last_tile = sprite.type

    def update(self,dt):
        self.apply_gravity(dt)

        self.input()
        self.check_on_floor()
        self.move(dt)
        self.hit_timer.update()
        self.jump_timer.update()

        self.get_status()
        self.animate(dt)


#Enemy Health
class HealthBar(pygame.sprite.Sprite):
    def __init__(self,w,h,pos,group,z = 0):
        super().__init__(group)
        self.image = pygame.Surface((w,h))
        #self.image.fill('black')
        self.rect = self.image.get_rect(midleft = pos)
        self.z = z
        self.w = w
        self.h = h
        self.pos = pos
        self.exists = True
    def move(self,pos,centered = False):
        self.rect.left = pos[0]
        self.rect.top = pos[1]
        if centered:
            self.rect = self.image.get_rect(center=pos)
        self.pos = pos
    def reduce(self,amount):
        self.w -= amount
        if self.w > 0:
            self.image = pygame.Surface((self.w, self.h))
            self.rect = self.image.get_rect(midleft = self.pos)
        else:
            self.exists = False
            self.kill()
