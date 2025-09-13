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
        if Hex.is_wh_inside_border(w, h):
            return Hex.all_hexs[w][h]
        else:
            raise ValueError("{w},{h} are not inside worlds border")

    def is_wh_inside_border(w: int, h: int):
        return (w > 0 and w < map_width) and (h > 0 and h < map_height)

    def draw(self):
        camera.show_on_camera(self.image, (self.x, self.y))

    def step(self):
        self.draw()

    def debug_highlight(self):
        Unit(self.w, self.h, placeholder_debug_unit, 0)

    def __str__(self):
        return str(self.w) + "," + str(self.h)

    def __repr__(self):
        return self.__str__()


Hex.all_hexs = []


def create_hexs_map(width: int, height: int):

    map_width = width
    map_height = height

    for w in range(map_width):
        Hex.all_hexs.append([])
        for h in range(map_height):
            Hex.all_hexs[w].append(Hex(w, h, Hex.image_placeholder))


map_width = 30
map_height = 10
create_hexs_map(map_width, map_height)


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

    def destroy(self):
        Unit.all_units.remove(self)

    def draw(self):
        x, y = Hex.get_xy_by_wh(self.w, self.h)
        camera.show_on_camera(self.image, (x, y))

    def step(self):
        self.draw()

    def step_all_units():
        for unit in Unit.all_units:
            unit: Unit
            unit.step()

    def get_hex(self):
        return Hex.get_hex_by_wh(self.w, self.h)

    def get_possible_paths(self):
        self.possible_paths = {}  # format: {hex:(hex_path,point_left)}
        hex_path = [Hex.get_hex_by_wh(self.w, self.h)]
        self.search_hex(self.get_hex(), hex_path, self.movement_point)
        return self.possible_paths

    def get_hexs_around_hex(hex: Hex):
        coordinates_around = [
            (hex.w - 1, hex.h),
            (hex.w - 1, hex.h - 1),
            (hex.w + 1, hex.h),
            (hex.w + 1, hex.h - 1),
            (hex.w, hex.h + 1),
            (hex.w, hex.h - 1),
        ]
        hexs_around = []
        for coordinate in coordinates_around:
            if Hex.is_wh_inside_border(coordinate[0], coordinate[1]):
                hexs_around.append(Hex.get_hex_by_wh(coordinate[0], coordinate[1]))
        return hexs_around

    def search_hex(self, hex: Hex, path: list, movement_point_left: int):

        for hex in Unit.get_hexs_around_hex(hex):
            print(hex, "trying")
            if self.is_capable_going_to_hex(hex, movement_point_left):
                movement_point = movement_point_left - hex.movement_point_needed
                self.search_hex(hex, path, movement_point)
        self.add_to_possible_path(hex, path, movement_point_left)

    def is_capable_going_to_hex(self, hex: Hex, movement_point_left: int):
        return movement_point_left >= hex.movement_point_needed

    def add_to_possible_path(self, hex: Hex, path: list, movement_point_left: int):
        self.possible_paths[hex] = (path, movement_point_left)


test_unit = Unit(4, 4, placeholder_test_unit, 1)

possible_paths = test_unit.get_possible_paths()
print(possible_paths)
for hex in possible_paths:
    hex: Hex
    hex.debug_highlight()

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
