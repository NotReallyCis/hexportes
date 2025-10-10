import os, time,color_teams_map
import pygame as pg

"""
this file is for converting the unit folder to a unit_with_team_color folder
the unit_with_team_color folder image's border is depending on the color
"""

output_directory_str = "unit_with_team_color"


def reset_folder(folder: str = output_directory_str):
    output_directory = os.fsencode(folder)
    for file in os.listdir(output_directory):
        filename = os.fsdecode(file)
        os.remove(folder + "/" + filename)


reset_folder()

directory_str = "unit"
directory = os.fsencode(directory_str)

import 


def get_surface_from_file(file: bytes):
    filename = os.fsdecode(file)
    return pg.image.load(directory_str + "/" + filename)


def save_surface(surface: pg.Surface, color: tuple[int, int, int], name: str):

    pg.image.save(
        surface,
        output_directory_str + "/" + color_teams_map.color_of_teams[color] + "_" + name,
    )


def fill_only_visible_part(surface: pg.Surface, color: tuple):
    width, height = surface.get_size()

    for x in range(width):
        for y in range(height):
            alpha: int = surface.get_at((x, y)).a
            surface.set_at((x, y), pg.Color(color[0], color[1], color[2], alpha))


border_size = 2
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    surface = get_surface_from_file(file)
    output_surface = pg.transform.scale(
        surface,
        (surface.get_width() + border_size * 2, surface.get_height() + border_size * 2),
    )
    for color in color_teams_map.color_of_teams:
        fill_only_visible_part(output_surface, color)
        output_surface.blit(surface, (border_size, border_size))
        save_surface(output_surface, color, filename)
