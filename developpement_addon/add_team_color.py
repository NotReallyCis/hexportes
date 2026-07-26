import sys

sys.path.append("/home/louane/git/hexportes")

import os, data
import pygame as pg

"""
this file is for converting the assets/unit folder to a assets/unit_with_team_color folder
"""

directory_str = "assets/unit"
output_directory_str = "assets/unit_with_team_color"


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


def save_surface(surface: pg.Surface, color: tuple[int, int, int], name: str):
    pg.image.save(
        surface,
        output_directory_str + "/" + data.color_of_teams[color] + "_" + name,
    )


def add_border(surface: pg.Surface, color: tuple, size: int = 1):
    surface = surface.copy()
    surface_border = pg.Surface(surface.get_size(), pg.SRCALPHA)
    surface_border.fill((0, 0, 0, 0))

    surface_mask = pg.mask.from_surface(surface)
    surface_filled = surface_mask.to_surface(setcolor=color)
    surface_filled.set_colorkey((0, 0, 0))
    for position_offset in [
        (1 * size, 0),
        (-1 * size, 0),
        (0, 1 * size),
        (0, -1 * size),
    ]:
        surface_border.blit(surface_filled, position_offset)
    surface_border.blit(surface, (0, 0))
    return surface_border


def change_color(
    surface: pg.Surface,
    color_start: tuple[int, int, int],
    color_end: tuple[int, int, int],
    threshold: int = 30,
):
    surface = surface.copy()
    color_start: pg.Color = pg.Color(color_start)
    color_end: pg.Color = pg.Color(color_end)
    color_offset_start_to_end = (
        color_end.r - color_start.r,
        color_end.g - color_start.g,
        color_end.b - color_start.b,
    )
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            color = surface.get_at((x, y))
            color_change_to_color_start = (
                color.r - color_start[0],
                color.g - color_start[1],
                color.b - color_start[2],
            )
            change_to_color_start = (
                abs(color_change_to_color_start[0])
                + abs(color_change_to_color_start[1])
                + abs(color_change_to_color_start[2])
            )
            if change_to_color_start > threshold:
                continue

            color_changed = (
                color.r + color_offset_start_to_end[0],
                color.g + color_offset_start_to_end[1],
                color.b + color_offset_start_to_end[2],
            )
            surface.set_at((x, y), normalize_color_tuple(color_changed))
    return surface


def normalize_color_tuple(color: tuple[int, int, int]):
    color = (
        pg.math.clamp(color[0], 0, 255),
        pg.math.clamp(color[1], 0, 255),
        pg.math.clamp(color[2], 0, 255),
    )
    return color


start_color = (64, 106, 150)
border_size = 1
for file in os.listdir(directory):
    filename = os.fsdecode(file)

    surface = get_surface_from_file(file)

    for color in data.color_of_teams:
        colored_surface = change_color(surface, start_color, color, 160)
        colored_surface = add_border(colored_surface, color, border_size)
        save_surface(colored_surface, color, filename)
