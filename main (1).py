import pygame as pg
import math


pg.init()
screen = pg.display.set_mode((800, 600))
clock = pg.time.Clock()  # Limit to 60 frames per second
fps = 60

from pyaddition import *

placeholder_debug_unit = pg.image.load("essentials-4xgames-tileset/tile-village.png")
placeholder_test_unit = pg.image.load("essentials-4xgames-tileset/tile-pineforest.png")


def is_even(numb: int):
    return numb % 2 == 0


class Hex:

    size = 30
    border_size = 2
    image_placeholder = pg.image.load("essentials-4xgames-tileset/base_baren.png")
    image_placeholder = pg.transform.scale(
        image_placeholder, (size * 2 - border_size, size * 2 - border_size)
    )
    vertical_spacing = math.sqrt(3) * size
    horizontal_spacing = 1.5 * size
    all_hexs = []

    def __init__(
        self, w: int, h: int, image: pg.Surface, movement_point_needed: int = 1
    ):
        self.w = w
        self.h = h
        self.x, self.y = Hex.get_xy_by_wh(self.w, self.h)

        self.size = Hex.size

        self.image = image

        self.movement_point_needed = movement_point_needed

    def step_to_all_hex():
        for width in range(len(Hex.all_hexs)):
            for hex in Hex.all_hexs[width]:
                hex: Hex
                hex.step()

    def get_xy_by_wh(w: int, h: int):
        x = w * Hex.horizontal_spacing
        if is_even(w):
            y = h * Hex.vertical_spacing
        else:
            y = (h * Hex.vertical_spacing) + (Hex.vertical_spacing / 2)
        return round(x), round(y)

    def get_hex_by_wh(w: int, h: int):
        return Hex.all_hexs[w][h]

    def draw(self):
        camera.show_on_camera(self.image, (self.x, self.y))

    def step(self):
        self.draw()

    def debug_highlight(self):
        Unit(self.w, self.h, placeholder_debug_unit, 0)


Hex.all_hexs = []


def create_hexs_map(width: int, height: int):
    map_width = width
    map_height = height

    for w in range(map_width):
        Hex.all_hexs.append([])
        for h in range(map_height):
            Hex.all_hexs[w].append(Hex(w, h, Hex.image_placeholder))


create_hexs_map(30, 10)


class Unit:
    all_units = []

    def __init__(
        self,
        w: int,
        h: int,
        image: pg.Surface,
        movement_point: int,
    ):
        self.w = w
        self.h = h
        self.movement_point = movement_point
        self.image = image
        Unit.all_units.append(self)

    def step_all_units():
        for unit in Unit.all_units:
            unit: Unit
            unit.step()

    def draw(self):
        x, y = Hex.get_xy_by_wh(self.w, self.h)
        camera.show_on_camera(self.image, (x, y))

    def step(self):
        self.draw()

    def destroy(self):
        Unit.all_units.remove(self)

    def get_hexs_around(self):
        coordinates_around = [
            (self.w - 1, self.h),
            (self.w - 1, self.h - 1),
            (self.w + 1, self.h),
            (self.w + 1, self.h - 1),
            (self.w, self.h + 1),
            (self.w, self.h - 1),
        ]
        hexs_around = []
        for coordinate in coordinates_around:
            hexs_around.append(Hex.get_hex_by_wh(coordinate[0], coordinate[1]))

        return hexs_around

    
    def is_capable_going_to_hex(self, hex: Hex):
        return self.movement_point >= hex.movement_point_needed
    
    def get_possible_paths(self):
        possible_paths = {}  # format: {hex:(hex_path,point_left)}
        for hex in self.get_hexs_around():
            
            if self.is_capable_going_to_hex(hex):
                

        return possible_paths



test_unit = Unit(4, 4, placeholder_test_unit, 0)


running = True
while running:

    Hex.step_to_all_hex()
    Unit.step_all_units()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    pg.display.flip()
    screen.fill((0, 0, 0))
    clock.tick(fps)

pg.quit()
