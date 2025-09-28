import pygame as pg
import math, socket

pg.init()
screen = pg.display.set_mode((1280, 750))
clock = pg.time.Clock()
fps = 120

import Unit as unit
import Hex as hex

from pyaddition import *

placeholder_test_unit1 = pg.image.load("essentials-4xgames-tileset/tile-village.png")
placeholder_test_unit2 = pg.image.load("essentials-4xgames-tileset/tile-pineforest.png")
placeholder_test_unit3 = pg.image.load("essentials-4xgames-tileset/tile-orchard.png")
placeholder_test_unit4 = pg.image.load("essentials-4xgames-tileset/tile-lumberjack.png")
confirm_sound_placeholder = pg.mixer.Sound("confirm_style_4_004.wav")


hex.Hex.create_hexs_map()


def debug_path_finding():
    test_unit = unit.Unit(4, 4, placeholder_test_unit2, 4)
    test_unit.get_possible_paths()
    print(
        "number_of_case:",
        test_unit.possible_paths.__len__(),
    )
    for hex in test_unit.possible_paths:
        hex: hex.Hex
        hex.debug_highlight(placeholder_test_unit4)
    return 1


test_unit = Unit.Unit(4, 4, placeholder_test_unit2, 4)


@keyboard.execute_on_clik
def executed_on_clik():
    Hex.hex_cursor_is_on.clicked()


running = True
while running:
    keyboard.step()

    Hex.step_to_all_hex()
    Unit.step_all_units()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    pg.display.flip()
    screen.fill((0, 0, 0))
    clock.tick(fps)

pg.quit()
