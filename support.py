from os import walk
import pygame


def import_folder(path, size=1):
    surface_list = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            image_surf = pygame.transform.scale(
                image_surf, (int(image_surf.get_width() * size), int(image_surf.get_height() * size)))
            surface_list.append(image_surf)

    return surface_list
