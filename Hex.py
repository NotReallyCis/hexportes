import pygame as pg
import math, json, unit_type
import Unit
from pyaddition import keyboard, camera, is_even

placeholder_hex_highlight = pg.image.load(
    "essentials-4xgames-tileset/tile-farm-sown.png"
)


class Hex:

    size = 35  # size of one side of an hex
    width = math.sqrt(3) * size  # pythagorean theorem
    height = 2 * size  # and that comes from a website
    vertical_spacing = height
    horizontal_spacing = width * 0.75  # idk why it's 0.75, don't ask me ;_;

    map_width = 15
    map_height = 10

    image_placeholder = pg.image.load("hex_placeholder.png")
    image_placeholder = pg.transform.scale(image_placeholder, (width, height))

    image_placeholder_cursor_on_hex = image_placeholder

    mask = pg.mask.from_surface(image_placeholder, 1)

    all_hexs = []

    hex_cursor_is_on = None

    def __init__(
        self, w: int, h: int, image: pg.Surface, movement_point_needed: int = 1
    ):
        self.w = w
        self.h = h
        self.x, self.y = Hex.get_xy_by_wh(self.w, self.h)

        self.size = Hex.size

        self.width = Hex.width
        self.height = Hex.height
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)

        self.image = image

        self.movement_point_needed = movement_point_needed

        self.is_cursor_on_hex = False

        self.unit_on_hex: Unit.Unit | None = None

    def step_to_all_hex():
        for w in range(len(Hex.all_hexs)):
            for hex in Hex.all_hexs[w]:
                hex: Hex
                hex.step()

    def step(self):
        if self.is_position_in_hex(keyboard.mouse_position.xy):
            self.is_cursor_on_hex = True
            Hex.hex_cursor_is_on = self

        else:
            self.is_cursor_on_hex = False

        self.draw()

    def draw(self):
        camera.show_on_camera(self.image, (self.x, self.y))
        if self.is_cursor_on_hex:
            camera.show_on_camera(
                self.image_placeholder_cursor_on_hex, (self.x, self.y)
            )

    def clicked(self):
        if self.unit_on_hex != None:
            self.unit_on_hex.clicked()

        elif Unit.Unit.unit_selected != None:
            Unit.Unit.unit_selected.move_to(self.w, self.h)
            Unit.Unit.unit_selected.is_selected = False
            Unit.Unit.unit_selected = None

    def create_hexs_map():
        for w in range(Hex.map_width):
            Hex.all_hexs.append([])
            for h in range(Hex.map_height):
                Hex.all_hexs[w].append(Hex(w, h, Hex.image_placeholder))

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

    def get_hexs_around_hex(self):
        hexs_around = []
        if is_even(self.w):
            wh_hexs_around = [
                (self.w - 1, self.h),
                (self.w - 1, self.h - 1),
                (self.w + 1, self.h),
                (self.w + 1, self.h - 1),  # top right
                (self.w, self.h + 1),  # bottom
                (self.w, self.h - 1),  # top
            ]
        else:
            wh_hexs_around = [
                (self.w - 1, self.h),
                (self.w + 1, self.h),
                (self.w, self.h - 1),
                (self.w, self.h + 1),
                (self.w + 1, self.h + 1),
                (self.w - 1, self.h + 1),
            ]

        for wh_of_hex_around in wh_hexs_around:
            if Hex.is_wh_inside_border(wh_of_hex_around[0], wh_of_hex_around[1]):

                hexs_around.append(
                    Hex.get_hex_by_wh(wh_of_hex_around[0], wh_of_hex_around[1])
                )

        return hexs_around

    def is_wh_inside_border(w: int, h: int):
        return (w >= 0 and w < Hex.map_width) and (h >= 0 and h < Hex.map_height)

    def debug_highlight(self, highlight_image: pg.Surface = placeholder_hex_highlight):
        Unit.Unit(self.w, self.h, highlight_image, 0)

    def is_position_in_hex(self, position: tuple[int, int] | pg.Vector2):
        return self.rect.collidepoint(  # check for collision with the rect so it's optimized
            position[0], position[1]
        ) and (
            Hex.mask.get_at((position[0] - self.x, position[1] - self.y))
        )  # really precised

    def __str__(self):
        if self.unit_on_hex == None:
            return str((self.w, self.h))
        else:
            return str((self.w, self.h, self.unit_on_hex))

    def __repr__(self):
        return self.__str__()

    def get_representation(self):
        if self.unit_on_hex != None:
            return self.unit_on_hex.__tuple__()
        else:
            return None

    def get_all_hexs__str__():
        output = []
        for w in range(len(Hex.all_hexs)):
            output.append([])
            for hex in Hex.all_hexs[w]:
                hex: Hex
                output[w].append(hex.get_representation())
        return output

    def load_all_hexs__str__(all_hexs__str__: list[list]):
        for w in range(len(all_hexs__str__)):
            for h, hex__str__ in enumerate(all_hexs__str__[w]):
                Hex.load_hex__str__(w, h, hex__str__)

    def load_hex__str__(w: int, h: int, string_to_load: tuple | str):
        hex: Hex = Hex.get_hex_by_wh(w, h)

        unit_name: str = string_to_load[0]
        unt_team: int = string_to_load[1]

        if string_to_load == "None":
            if hex.unit_on_hex != None:
                hex.unit_on_hex.destroy()

        elif unit_name in unit_type.unit_type.keys():
            print("unit", unit_name, unt_team, w, h)
            hex.unit_on_hex = Unit.Unit(w, h, string_to_load, unt_team)

        else:
            raise ValueError(
                string_to_load,
                type(string_to_load),
                "in hex",
                hex,
                "has not been understood,most likely due that it is incorrect",
            )
