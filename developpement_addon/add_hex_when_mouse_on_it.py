"""
this file is for converting the hex_stat_when_mouse_not_on_it folder to a hex_stat_when_mouse_it folder
"""

import sys

sys.path.append("C:/Users/bauma/Documents/GitHub/hexportes")
# equal to "cd C:/Users/bauma/Documents/GitHub/hexportes"
import os
import pygame as pg

directory_str = "assets/hex_stat/hex_stat_when_mouse_not_on_it"
output_directory_str = "assets/hex_stat/hex_stat_when_mouse_on_it"


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

mouse_on_it_image = pg.Surface((hex_type.width, hex_type.height))
mouse_on_it_image.fill(
    pg.Color(
        hex_type.luminosity_added_when_mouse_on_hex,
        hex_type.luminosity_added_when_mouse_on_hex,
        hex_type.luminosity_added_when_mouse_on_hex,
    )
)


def set_mouse_on_it_types(image: pg.Surface):
    image = image.copy()
    image = pg.transform.scale(image, (hex_type.width, hex_type.height))
    image.blit(mouse_on_it_image, (0, 0), None, pg.BLEND_RGB_ADD)
    return image


for file in os.listdir(directory):
    filename = os.fsdecode(file)
    surface = get_surface_from_file(file)
    output_surface = set_mouse_on_it_types(surface)
    save_surface(output_surface, filename)
