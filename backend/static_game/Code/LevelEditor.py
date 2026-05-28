import pygame, sys
from pygame.mouse import get_pressed as mouse_buttons
from pygame.mouse import get_pos as mouse_pos
from pygame.math import Vector2 as vector
from pygame.image import load
from timer import Timer
from menu import Menu
from random import choice, randint

from support import *
from Settings import *



class Editor:
    def __init__(self,switch):
        # main setup
        self.display_surface = pygame.display.get_surface()
        self.canvas_data = {}
        self.switch = switch

        #imports
        self.imports()

        #navigation
        self.origin = vector()
        self.pan_offset = vector()

        #support lines
        self.support_line_surf = pygame.Surface((width,height))
        self.support_line_surf.set_colorkey("green")
        self.support_line_surf.set_alpha(20)

        #selection
        self.selection_index = 2
        self.last_selected = None

        #menu
        self.menu = Menu()

        #Objects
        self.canvas_objects = pygame.sprite.Group()
        self.foreground = pygame.sprite.Group()
        self.background = pygame.sprite.Group()
        self.object_drag_active = False
        self.object_timer = Timer(300)

        #Player
        CanvasObject(
            pos = (200,height //2),
            frames = self.animations[0]['frames'],
            tile_id = 0,
            origin = self.origin,
            group = [self.canvas_objects,self.foreground]
        )

    # support
    def get_current_cell(self,obj = None):
        distance_to_origin = (vector(mouse_pos()) - self.origin) // Tile_Size if not obj else (vector(obj.distance_to_origin) - self.origin) // Tile_Size
        return (int(distance_to_origin.x),int(distance_to_origin.y))
    def check_neighbors(self,cell_pos):
        #create local clusters
        cluster_size = 3
        local_cluster = [
            (cell_pos[0] + col - (cluster_size // 2),cell_pos[1] + row - (cluster_size // 2))
            for row in range(cluster_size)
            for col  in range(cluster_size)
        ]

        # check neighbors
        for cell in local_cluster:
            if cell in self.canvas_data:
                self.canvas_data[cell].terrain_neighbors = []
                self.canvas_data[cell].water_on_top = False
                for neighbor, direction in NEIGHBOR_DIRECTIONS.items():
                    neighbor_cell = (cell[0] + direction[0],cell[1] + direction[1])

                    if neighbor_cell in self.canvas_data:

                    # if top neighbor has water and current cell has water, it has water on top
                        if self.canvas_data[neighbor_cell].has_water and neighbor == 'A' and self.canvas_data[cell].has_water:
                            self.canvas_data[cell].water_on_top = True
                    # terrain neighbors
                        if self.canvas_data[neighbor_cell].has_terrain:
                            self.canvas_data[cell].terrain_neighbors.append(neighbor)
    def imports(self):
        self.animations = {}
        for key,value in EDITOR_DATA.items():
            if value['graphics']:
                graphics = import_folder(value['graphics'])
                self.animations[key] = {
                    'frame index': 0,
                    'frames': graphics,
                    'length': len(graphics)
                }

        #preview
        self.preview_surfs = {key: load(value['preview']) for key,value in EDITOR_DATA.items() if value['preview']}

    def animation_updates(self,dt):
        for value in self.animations.values():
            # * dt makes it framerate independent
            value['frame index'] += ANIMATION_SPEED * dt
            if value['frame index'] >= value['length']:
                value['frame index'] = 0
    def mouse_on_object(self):
        for sprite in self.canvas_objects:
            if sprite.rect.collidepoint(mouse_pos()):
                return sprite

    # create grid for level
    def create_grid(self):
        for tile in self.canvas_data.values():
            tile.objects = []
        for obj in self.canvas_objects:
            current_cell = self.get_current_cell(obj)
            offset = vector(obj.distance_to_origin) - vector(current_cell) * Tile_Size
            if current_cell in self.canvas_data: # tile exists already
                self.canvas_data[current_cell].add_id(obj.tile_id,offset)
            else: # no tiles exist
                self.canvas_data[current_cell] = CanvasTile(obj.tile_id,offset)

        # grid offset
        # this returns position of topleftmost canvas tile

        #sorts list, gets first tuple, gets value needed
        left = sorted(self.canvas_data.keys(), key = lambda tile: tile[0])[0][0]
        top = sorted(self.canvas_data.keys(), key = lambda tile: tile[1])[0][1]

        # create empty grid
        # order matters, water is before bg_palms and so on
        layers = {
            'water' : {},
            'bg palms': {},
            'terrain' : {},
            'enemies' : {},
            'coins' : {},
            'fg objects' : {}
        }

        # fill grid
        for tile_pos, tile in self.canvas_data.items():
            x_adjusted = tile_pos[0] - left
            y_adjusted = tile_pos[1] - top

            x = x_adjusted * Tile_Size
            y = y_adjusted * Tile_Size

            if tile.has_terrain:
                layers['terrain'][(x,y)] = 'Terrain1'
            if tile.coin:
                layers['coins'][(x + Tile_Size // 2,y + Tile_Size //2)] = tile.coin
            if tile.enemy:
                layers['enemies'][(x,y)] = tile.enemy

            if tile.objects:  # (obj,offset)
                for obj, offset in tile.objects:
                    if obj in [key for key, value in EDITOR_DATA.items() if value['style'] == 'palm_bg']:
                        layers['bg palms'][(int(x + offset.x),int(y + offset.y))] = obj
                    else:
                        layers['fg objects'][(int(x + offset.x),int(y + offset.y))] = obj

        return layers

    #event loop
    def event_loop(self):
        #event loop
        #close game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.switch(self.create_grid())
                #self.editor_music.stop()
            self.pan_input(event)
            self.selection_hotkeys(event)
            self.menu_click(event)
            self.object_drag(event)

            self.canvas_add()
            self.canvas_remove()

    # input
    def pan_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and (mouse_buttons()[1] or (mouse_buttons()[0] and self.selection_index == 6)):
            self.pan_active = True
            self.pan_offset = vector(mouse_pos()) - self.origin
        if not (mouse_buttons()[0] and self.selection_index == 6):
            self.pan_active = False

        #mousewheel
        if event.type == pygame.MOUSEWHEEL:
            if mouse_buttons()[0]:
                self.origin.x -= event.y * 8
            else:
                self.origin.y -= event.y * 8

            for sprite in self.canvas_objects:
                sprite.pan_pos(self.origin)

        if self.pan_active:
            self.origin = vector(mouse_pos()) - self.pan_offset
            for sprite in self.canvas_objects:
                sprite.pan_pos(self.origin)
    def selection_hotkeys(self,event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.selection_index += 1
            if event.key == pygame.K_LEFT:
                self.selection_index -= 1
            self.selection_index = max(2,min(self.selection_index,6))
    def object_drag(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[0]:
            for sprite in self.canvas_objects:
                if sprite.rect.collidepoint(event.pos):
                    sprite.start_drag()
                    self.object_drag_active = True
        if event.type == pygame.MOUSEBUTTONUP and self.object_drag_active:
            for sprite in self.canvas_objects:
                if sprite.selected:
                    sprite.end_drag(self.origin)
                self.object_drag_active = False
    def menu_click(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(mouse_pos()):
            self.selection_index = self.menu.click(mouse_pos(),mouse_buttons())

    def canvas_add(self):

        if mouse_buttons()[0] and not self.menu.rect.collidepoint(mouse_pos()) and not self.object_drag_active:
            current_cell = self.get_current_cell()
            if EDITOR_DATA[self.selection_index]['type'] == 'tile':
                if current_cell != self.last_selected:
                    if current_cell in self.canvas_data:
                        self.canvas_data[current_cell].add_id(self.selection_index)
                    else:
                        self.canvas_data[current_cell] = CanvasTile(self.selection_index)
                    self.check_neighbors(current_cell)
                    self.last_selected = current_cell
            elif EDITOR_DATA[self.selection_index]['type'] == 'tool':
                x = 4
            else: # object
                if not self.object_timer.active:
                    groups = [self.canvas_objects,self.background] if EDITOR_DATA[self.selection_index]['style'] == 'palm_bg' else [self.canvas_objects,self.foreground]
                    CanvasObject(
                        pos = mouse_pos(),
                        frames = self.animations[self.selection_index]['frames'],
                        tile_id = self.selection_index,
                        origin = self.origin,
                        group = groups
                    )
                    self.object_timer.activate()
    def canvas_remove(self):
        if mouse_buttons()[2] and not self.menu.rect.collidepoint(mouse_pos()):
            #Delete Objects
            selected_object = self.mouse_on_object()
            if selected_object:
                if EDITOR_DATA[selected_object.tile_id]['style'] not in ('player', 'sky'):
                    selected_object.kill()
            #Delete Tiles
            if self.canvas_data:
                current = self.get_current_cell()
                if current in self.canvas_data:
                    self.canvas_data[current].remove_id(self.selection_index)
                    if self.canvas_data[current].is_empty:
                        del self.canvas_data[current]
                    self.check_neighbors(current)

    # drawing
    def draw_grid(self):
        columns = width // Tile_Size
        rows = height // Tile_Size

        self.support_line_surf.fill("green")
        for i in range(columns+1):
            self.ref = self.origin.x % Tile_Size
            x = (self.ref) + i * Tile_Size
            pygame.draw.line(self.support_line_surf,'black',(x,0),(x,height))

        for i in range(rows+1):
            self.ref = self.origin.y % Tile_Size
            y = (self.ref) + i * Tile_Size
            pygame.draw.line(self.support_line_surf,'black',(0,y),(width,y))

        self.display_surface.blit(self.support_line_surf,(0,0))
    def draw_level(self):
        self.background.draw(self.display_surface)
        for cell_pos, tile in self.canvas_data.items():
            pos = self.origin + vector(cell_pos) * Tile_Size

            # coins
            if tile.coin:
                frames = self.animations[tile.coin]['frames']
                index = int(self.animations[tile.coin]['frame index'])
                surf = frames[index]
                surf = pygame.transform.scale_by(surf,0.8)
                rec = surf.get_rect(center = (pos[0] + (Tile_Size // 2),pos[1] + (Tile_Size // 2)))
                self.display_surface.blit(surf, rec)

            # terrain
            if tile.has_terrain:
                self.display_surface.blit(self.animations[1]["frames"][0], pos)

            # enemies
            if tile.enemy:
                frames = self.animations[tile.enemy]['frames']
                index = int(self.animations[tile.enemy]['frame index'])
                if tile.enemy == 11:
                    surf = frames[index]
                    rec = surf.get_rect(midbottom=(pos[0] + (Tile_Size // 2), pos[1] + Tile_Size))
                elif tile.enemy == 10:
                    surf = pygame.transform.scale(frames[index],(32,32))
                    rec = surf.get_rect(midtop = (pos[0] + (Tile_Size // 2),pos[1]))
                elif tile.enemy == 9:
                    surf = frames[index]
                    rec = surf.get_rect(midbottom =(pos[0] + (Tile_Size // 2), pos[1] + Tile_Size))
                elif tile.enemy == 8:
                    surf = pygame.transform.scale(frames[index], (64, 64))
                    rec = surf.get_rect(midbottom=(pos[0] + (Tile_Size // 2), pos[1] + Tile_Size))
                else:
                    surf = pygame.transform.scale(frames[index], (64, 64))
                    rec = surf.get_rect(midbottom=(pos[0] + (Tile_Size // 2), pos[1] + Tile_Size))

                # pygame.draw.rect(self.display_surface,'red', rec, 1)
                self.display_surface.blit(surf, rec)
        self.foreground.draw(self.display_surface)
    def preview(self):
        selected_object = self.mouse_on_object()
        if not self.menu.rect.collidepoint(mouse_pos()):
            if selected_object:
                #why not inflate+copy
                rect = selected_object.rect.inflate(10,10)
                color = 'black'
                linewidth = 1
                size = 10

                surf = EDITOR_DATA[selected_object.tile_id]['preview']
                pygame.draw.lines(self.display_surface,color,False,((rect.left,rect.top + size),rect.topleft,(rect.left + size,rect.top)),linewidth)
                pygame.draw.lines(self.display_surface, color, False, ((rect.right,rect.top + size),rect.topright,(rect.right - size,rect.top)), linewidth)
                pygame.draw.lines(self.display_surface, color, False, ((rect.left,rect.bottom - size),rect.bottomleft,(rect.left + size,rect.bottom)), linewidth)
                pygame.draw.lines(self.display_surface, color, False, ((rect.right,rect.bottom - size),rect.bottomright,(rect.right - size,rect.bottom)), linewidth)
                # draws lines around objects when hovered over
            else:
                type_dict = {key: value['type'] for key,value in EDITOR_DATA.items()}

                # preview of tile/object
                surf = self.preview_surfs[self.selection_index].copy()
                #makes it a little transparent
                surf.set_alpha(50)

                # tile
                if type_dict[self.selection_index] == 'tile':
                    current_cell = self.get_current_cell()
                    rect = surf.get_rect(topleft = self.origin + vector(current_cell) * Tile_Size)
                # object
                else:
                    rect = surf.get_rect(center = mouse_pos())


                self.display_surface.blit(surf,rect)

    #update
    def run(self, dt):
        #event
        self.event_loop()
        # # updating
        self.animation_updates(dt)
        self.canvas_objects.update(dt)
        self.object_timer.update()

        # drawing
        self.display_surface.fill('white')
        self.draw_level()
        self.draw_grid()

        # pygame.draw.rect(self.display_surface,"red", self.menu.rect, 2)
        self.preview()
        self.menu.display(self.selection_index)


# tiles and objects
class CanvasTile:
    def __init__(self,tile_id,offset = vector()):
        # terrain
        self.has_terrain = False
        self.terrain_neighbors = []

        # water
        self.has_water = False
        self.water_on_top = False

        #coin (either 4, 5 or 6)
        self.coin = None

        #enemy
        self.enemy = None

        #objects
        self.objects = []

        self.add_id(tile_id,offset)
        self.is_empty = False
    def add_id(self,tile_id,offset = vector()):
        options = {key: value['style'] for key, value in EDITOR_DATA.items()}
        match options[tile_id]:
            case 'terrain': self.has_terrain = True
            case 'water': self.has_water = True
            case 'coin': self.coin = tile_id
            case 'enemy': self.enemy = tile_id
            case _: # Objects
                if (tile_id,offset) not in self.objects:
                    self.objects.append((tile_id,offset))
    def remove_id(self,tile_id):
        options = {key: value['style'] for key, value in EDITOR_DATA.items()}
        match options[tile_id]:
            case 'terrain': self.has_terrain = False
            case 'water': self.has_water = False
            case 'coin': self.coin = None
            case 'enemy': self.enemy = None
        self.check_content()
    def check_content(self):
        if not self.has_terrain and not self.has_water and not self.coin and not self.enemy:
            self.is_empty = True
    def get_water(self):
        return 'bottom' if self.water_on_top else 'top'
    def get_terrain(self):
        return ''.join(self.terrain_neighbors)
class CanvasObject(pygame.sprite.Sprite):
    def __init__(self,pos,frames,tile_id,origin,group):
        super().__init__(group)
        self.tile_id = tile_id

        # animation
        self.frames = frames
        self.frame_ind = 0

        self.image = self.frames[self.frame_ind]
        self.rect = self.image.get_rect(center = pos)

        # movement
        self.distance_to_origin = vector(self.rect.topleft) - origin
        self.selected = False
        self.mouse_offset = vector()

    def start_drag(self):
        self.selected = True
        self.mouse_offset = vector(mouse_pos()) - vector(self.rect.topleft)
    def drag(self):
        if self.selected:
            self.rect.topleft = mouse_pos() - self.mouse_offset
    def end_drag(self,origin):
        self.selected = False
        self.distance_to_origin = vector(self.rect.topleft) - origin

    def animate(self,dt):
        self.frame_ind += PLAYER_ANIMATION * dt
        if self.frame_ind >= len(self.frames):
            self.frame_ind = 0
        self.image = self.frames[int(self.frame_ind)]
        self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
    def pan_pos(self,origin):
        self.rect.topleft = origin + self.distance_to_origin

    def update(self,dt):
        self.animate(dt)
        self.drag()