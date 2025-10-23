import sys

sys.path.append("C:/Users/bauma/Documents/GitHub/hexportes")

import os
import pygame as pg

"""
this file is for converting the hex_stat_when_mouse_not_on_it folder to a hex_stat_when_mouse_it folder
"""

directory_str = "assets/hex_stat/hex_stat_when_mouse_not_on_it"
output_directory_str = "assets/hex_stat/hex_stat_when_mouse_on_it"
calc_to_add = pg.image.load("developpement_addon/mouse_on_it_calc.png")


def reset_folder(folder: str = output_directory_str):
    output_directory = os.fsencode(folder)
    for file in os.listdir(output_directory):
        filename = os.fsdecode(file)
        os.remove(folder + "/" + filename)


reset_folder()

directory = os.fsencode(directory_str)


def get_surface_from_file(file: bytes):
    filename = os.fsdecode(file)
    return pg.image.load(directory_str + "/" + filename)


def save_surface(surface: pg.Surface, name: str):

    pg.image.save(
        surface,
        output_directory_str + "/" + name,
    )


from data import hex_type


def set_mouse_on_it_types(image: pg.Surface):
    image = image.copy()
    image = pg.transform.scale(image, (hex_type.width, hex_type.height))
    image.blit(calc_to_add)
    return image


for file in os.listdir(directory):
    filename = os.fsdecode(file)
    surface = get_surface_from_file(file)
    output_surface = set_mouse_on_it_types(surface)
    save_surface(output_surface, filename)
