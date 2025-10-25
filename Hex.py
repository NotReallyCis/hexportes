import pygame as pg
import math, data, object_type
from unit import Object, Unit, Usine
from pyaddition import keyboard, Button, is_even, Visible_object


class Hex:

    size = 35  # size of one side of an hex
    width = math.sqrt(3) * size  # pythagorean theorem
    height = 2 * size  # and that comes from a website

    map_width = 15
    map_height = 10
    surface = data.hex_surface
    mask = pg.mask.from_surface(surface, 1)

    all_hexs: list["Hex"] = []

    hex_cursor_is_on = None

    def __init__(self, w: int, h: int, movement_point_needed: int = 1):
        self.w = w
        self.h = h
        self.x, self.y = Hex.get_xy_by_wh(self.w, self.h)

        self.type = data.hex_type

        self.size = Hex.size

        self.width = Hex.width
        self.height = Hex.height
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)

        self.default_movement_point_needed = movement_point_needed

        self.object_on_hex: Unit | None = None

        self.stat = []

        self.is_visible = True

        is_cursor_on_self = Hex.hex_cursor_is_on == self

        self.visible_object = Visible_object(
            data.hex_type.get_hex_image_from_stat(
                self.stat, is_cursor_on_self, self.is_visible
            ),
            self.rect,
            10,
        )

    def on_end_of_turn():
        for line in Hex.all_hexs:
            for hex in line:
                hex: Hex
                hex.is_visible = False

    def step_to_all_hex():
        for line in Hex.all_hexs:
            for hex in line:
                hex: Hex
                hex.step()

        Hex.draw_wh_of_hex_cursor_is_on()

    def step(self):
        if self.is_position_in_hex(keyboard.mouse_position.xy):
            Hex.hex_cursor_is_on = self

        self.draw()
        self.stat = []  # reset each time so it only last one tick

    def draw(self):

        is_cursor_on_self = Hex.hex_cursor_is_on == self
        self.visible_object.change_image(
            data.hex_type.get_hex_image_from_stat(
                self.stat, is_cursor_on_self, self.is_visible
            ),
        )

    def draw_wh_of_hex_cursor_is_on():
        if Hex.hex_cursor_is_on != None:
            import pyaddition

            text_to_draw = pyaddition.draw.text(
                (Hex.hex_cursor_is_on.w, Hex.hex_cursor_is_on.h)
            )
            pyaddition.camera.show(text_to_draw, (0, -text_to_draw.get_height()), True)

    def is_position_in_hex(self, position: tuple[int, int] | pg.Vector2):
        return (
            self.rect.collidepoint(
                position[0], position[1]
            )  # check for collision with the rect so it's optimized
            and (
                Hex.mask.get_at((position[0] - self.x, position[1] - self.y))
            )  # pixel perfect
            and (not Button.is_position_in_zone_covered(position[0], position[1]))
        )

    def clicked(self):
        if data.click_stat.stat == data.click_stat.SELECT_UNIT:
            if self.object_on_hex != None:
                self.object_on_hex.select()
        else:
            Object.object_selected.clicked_somewhere(self)

    def create_hexs_map():
        for w in range(Hex.map_width):
            Hex.all_hexs.append([])
            for h in range(Hex.map_height):
                Hex.all_hexs[w].append(Hex(w, h))
        return Hex.all_hexs[w]

    def get_xy_by_wh(w: int, h: int):
        x = w * Hex.width * 0.75  # idk why it's 0.75, don't ask me ;_;
        if is_even(w):
            y = h * Hex.height
        else:
            y = (h * Hex.height) + (Hex.height / 2)
        return round(x), round(y)

    def get_hex_by_wh(w: int, h: int) -> "Hex":
        if Hex.is_wh_inside_border(w, h):
            output: Hex = Hex.all_hexs[w][h]
            return output
        else:
            raise ValueError("{w},{h} are not inside worlds border")

    def get_movement_point_needed(self):

        if self.object_on_hex == None:
            return self.default_movement_point_needed
        else:
            return (
                self.default_movement_point_needed
                + self.object_on_hex.movement_point_needed
            )

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

    def __str__(self):
        if self.object_on_hex == None:
            return str((self.w, self.h))
        else:
            return str((self.w, self.h, self.object_on_hex))

    def __repr__(self):
        return self.__str__()

    def get_representation(self):
        if self.object_on_hex != None:
            return self.object_on_hex.__tuple__()
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

    def load_hex__str__(w: int, h: int, infos: dict | None):
        hex: Hex = Hex.get_hex_by_wh(w, h)

        if infos is None:
            if hex.object_on_hex != None:
                hex.object_on_hex.destroy()

        else:
            unit_type = object_type.get_class_by_type_name(infos[object_type.TYPE])
            unit_type.create_object_from_infos(w, h, infos)
