Tile_Size = 64
width = 1800
height = 950
ANIMATION_SPEED = 5
PLAYER_ANIMATION = 5
RUN_ANIMATION = 15
JUMP_ANIMATION = 15

SKY_COLOR = "#ffc57d"
SEA_COLOR = "#63a1c9"


EDITOR_DATA = {
    0: {'style':'player','type':'object','menu':None,'menu_surf':None,'preview':None,'graphics':'custom_graphics/player/idle'},

    1: {'style':'terrain','type':'tile','menu':'terrain','menu_surf':'custom_graphics/terrain/0.png','preview':'custom_graphics/terrain/0.png','graphics': "custom_graphics/terrain"},

    2: {'style':'coin','type':'tile','menu':'coin','menu_surf':'custom_graphics/coin/0.png','preview':'custom_graphics/coin/0.png','graphics': "custom_graphics/coin"},

    3: {'style':'enemy','type':'tile','menu':'enemy','menu_surf':'custom_graphics/enemy/0.png','preview':'custom_graphics/enemy/0.png','graphics':'custom_graphics/enemy'},

    4: {'style':'palm_fg','type':'object','menu':'palm_fg','menu_surf':'custom_graphics/tree/0.png','preview':'custom_graphics/tree/0.png','graphics':'custom_graphics/tree'},

    5: {'style':'palm_bg','type':'object','menu':'palm_bg','menu_surf':'custom_graphics/tree/0.png','preview':'custom_graphics/tree/0.png','graphics':'custom_graphics/tree'},

    6: {'style': 'navigate', 'type': 'tool', 'menu': 'navigate', 'menu_surf': 'fixed_graphics/navigate.png','preview': 'fixed_graphics/navigate.png', 'graphics': None}

}

NEIGHBOR_DIRECTIONS = {
    'A': (0,-1),
    'B': (1,-1),
    'C': (1,0),
    'D': (1,1),
    'E': (0,1),
    'F': (-1,1),
    'G': (-1,0),
    'H': (-1,-1)
}

LEVEL_LAYERS = {
    'clouds': 1,
    'bg': 200,
    'player': 201,
    'water': 202,
    'main': 203
}

