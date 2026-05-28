import pygame
# import cProfile,pstats
from os import walk

def import_folder(path):
    surface_list = []
    for folder_name, sub_folders, img_files in walk(path):
        for image_name in img_files:
            full_path = path + '/' + image_name
            image_surf = pygame.image.load(full_path).convert_alpha()
            # add image surface to surface list
            surface_list.append(image_surf)
    return surface_list

def import_folder_dict(path):
    surface_dict = {}
    for folder_name, sub_folders, img_files in walk(path):
        for image_name in img_files:
            full_path = path + '/' + image_name
            image_surf = pygame.image.load(full_path).convert_alpha()
            # add image surface to surface list
            surface_dict[image_name.split('.')[0]] = image_surf
    return surface_dict

# def profile(function):
#     with cProfile.Profile() as profile:
#         function()
#     results = pstats.Stats(profile)
#     results.sort_stats(pstats.SortKey.TIME)
#     results.print_stats()

