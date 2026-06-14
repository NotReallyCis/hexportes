import pygame as pg
import math, data, random
from unit import Unit
import pyg


class Hex:

    width = 64
    height = 64
    vertical_spacing = 56
    horizontal_spacing = 48

    map_width = 100
    map_height = 100

    hex_image = data.hex_image
    fog = data.fog

    all_hexs_surface = pg.Surface(
        (width * map_width, height * map_height + (height / 2))
    )
    all_hexs_fog_surface = pg.Surface(
        (width * map_width, height * map_height + (height / 2)), pg.SRCALPHA
    )

    mask = pg.mask.from_surface(hex_image, 1)

    all_hexs: list[list["Hex"]] = []

    hex_cursor_is_on = None

    BAREN = "baren terrain"
    GREEN = "green terrain"
    ROCKY = "rocky terrain"
    WATER = "water terrain"

    SURFACE = "surface"
    WEIGHT = "weight"
    terrain_types: dict[str] = {
        BAREN: {SURFACE: data.baren, WEIGHT: 1},
        GREEN: {SURFACE: data.green, WEIGHT: 1},
        ROCKY: {SURFACE: data.rocky, WEIGHT: 3},
        WATER: {SURFACE: data.water, WEIGHT: 0},
    }
    """If the weight is 0 then the tile is impassable"""

    def __init__(self, w: int, h: int, type: str):
        if type not in Hex.terrain_types:
            raise ValueError(f"Type {type} is not recognised")

        self.w = w
        self.h = h
        self.x, self.y = Hex.get_xy_by_wh(self.w, self.h)

        self.rect = pg.Rect(self.x, self.y, self.width, self.height)

        self.type = type
        self.surface = Hex.terrain_types[type][Hex.SURFACE]
        Hex.all_hexs_surface.blit(self.surface, self.get_xy_by_wh(self.w, self.h))

        self.weight = Hex.terrain_types[type][Hex.WEIGHT]
        """the amount of movement point needed"""
        if self.weight == 0:
            self.weight = 999  # a really high value

        self.unit_on_hex: Unit | None = None

        self.is_visible = (
            True  # set to True first because add_fog won't add fog if it's False
        )
        self.add_fog()

    @classmethod
    def create_hexs_map(cls):
        for w in range(Hex.map_width):
            Hex.all_hexs.append([])
            for h in range(Hex.map_height):
                type = random.choice(list(Hex.terrain_types.keys()))
                Hex.all_hexs[w].append(Hex(w, h, type))
        return Hex.all_hexs[w]

    @classmethod
    def on_end_of_turn(cls):
        for line in Hex.all_hexs:
            for hex in line:
                hex: Hex
                hex.add_fog()

    @classmethod
    @pyg.Profiler
    def step_to_all_hex(cls):
        Hex.draw_all()
        Hex.hex_cursor_is_on = Hex.get_hex_by_xy(pyg.keyboard.mouse_position.xy)

    @classmethod
    def draw_all(cls):
        pyg.camera(Hex.all_hexs_surface, (0, 0), 1)
        pyg.camera(
            Hex.all_hexs_fog_surface,
            (0, 0),
            2,
        )

    def add_fog(self):
        if self.is_visible == False:
            return
        Hex.all_hexs_fog_surface.blit(Hex.fog, (self.x, self.y))
        self.is_visible = False

    def remove_fog(self):
        if self.is_visible == True:
            return
        Hex.mask.to_surface(
            Hex.all_hexs_fog_surface,
            setcolor=(0, 0, 0, 0),  # put on white becuse I use BLEND_RGBA_MULT
            unsetcolor=None,
            dest=(self.x, self.y),
        )
        self.is_visible = True

    def draw_surface_on_top(self, surface: pg.Surface, special_flags: int = 0):
        """blit a custom surface on top of the hex (eg: can_go_tile)"""
        pyg.camera(surface, (self.x, self.y), -101, False, False, special_flags)

    def is_position_in_hex(self, position: tuple[int, int] | pg.Vector2) -> bool:
        return (
            self.rect.collidepoint(
                position[0], position[1]
            )  # check for collision with the rect first for optimisation
            and (
                Hex.mask.get_at((position[0] - self.x, position[1] - self.y))
            )  # pixel perfect
            and (not pyg.Button.is_position_in_zone_covered(position[0], position[1]))
        )

    @staticmethod
    @pyg.keyboard.execute_on_click
    def click_hex_selected():
        if Hex.hex_cursor_is_on is None:
            return
        if not pyg.Button.is_position_in_zone_covered(*pyg.keyboard.mouse_position.xy):
            Hex.hex_cursor_is_on.clicked()

    def clicked(self):
        if data.current_state == data.click_stat.SELECT_UNIT:
            if self.unit_on_hex != None:
                self.unit_on_hex.select()
        else:
            Unit.unit_selected.on_click(self)

    @classmethod
    def get_xy_by_wh(cls, w: int, h: int):
        x = w * Hex.horizontal_spacing
        if pyg.is_even(w):
            y = h * Hex.vertical_spacing
        else:
            y = (h * Hex.vertical_spacing) + (Hex.vertical_spacing / 2)
        return round(x), round(y)

    @classmethod
    def get_hex_by_wh(cls, w: int, h: int) -> "Hex":
        if Hex.is_wh_inside_border(w, h):
            output: Hex = Hex.all_hexs[w][h]
            return output
        else:
            raise ValueError(f"{w},{h} are not inside worlds border")

    @classmethod
    def get_hex_by_xy(cls, pos: tuple[int, int]):
        x, y = pos
        w = math.floor(x / Hex.horizontal_spacing)
        h = math.floor(y / Hex.vertical_spacing)

        if not Hex.is_wh_inside_border(w, h):
            return None

        hex = Hex.get_hex_by_wh(w, h)
        if hex.is_position_in_hex(pos):
            return hex

        for hex_around in hex.get_hexs_around_hex():
            if hex_around.is_position_in_hex(pos):
                return hex_around
        # okay well i know it doesn't look good but at least it works

    def get_hexs_around_hex(self):
        hexs_around: list[Hex] = []
        if pyg.is_even(self.w):
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

    @classmethod
    def is_wh_inside_border(cls, w: int, h: int):
        return (w >= 0 and w < Hex.map_width) and (h >= 0 and h < Hex.map_height)

    def __str__(self):
        if self.unit_on_hex == None:
            return str((self.w, self.h))
        else:
            return str((self.w, self.h, self.unit_on_hex))

    def __repr__(self):
        return self.__str__()

    def get_representation(self):
        if self.unit_on_hex != None:
            return self.unit_on_hex.get_info()
        else:
            return None

    @classmethod
    def get_all_hexs__str__(cls):
        output: list[list] = []
        for w in range(len(Hex.all_hexs)):
            output.append([])
            for hex in Hex.all_hexs[w]:
                hex: Hex
                output[w].append(hex.get_representation())
        return output

    @classmethod
    def load_all_hexs__str__(cls, all_hexs__str__: list[list]):
        for w in range(len(all_hexs__str__)):
            for h, hex__str__ in enumerate(all_hexs__str__[w]):
                Hex.load_hex__str__(w, h, hex__str__)

    @classmethod
    def load_hex__str__(cls, w: int, h: int, info: dict[str] | None):
        import unit

        hex: Hex = Hex.get_hex_by_wh(w, h)

        if info is None:
            return
        else:
            Unit(hex.w, hex.h, info)

    def search_hex(
        self,
        movement_point_possessed: int,
        is_hex_weight_matter: bool,
    ):
        """_summary_

        Args:
            movement_point_possessed (int): _description_
            is_hex_weight_matter (bool): does the weight of the hex you go to are counted
        """

        hexs_to_calculate: list[tuple[Hex, int]] = [(self, movement_point_possessed)]

        hexs_calculated: dict[Hex, int] = {}
        movement_point_possessed += 1  # off by one error
        while True:
            if hexs_to_calculate == []:  # on end
                return hexs_calculated

            hex_calculating, movement_point = hexs_to_calculate[0]
            hexs_to_calculate.pop(0)

            hexs_calculated[hex_calculating] = movement_point

            for hex_around in hex_calculating.get_hexs_around_hex():

                hex_around_weight: int = 1
                if is_hex_weight_matter:
                    hex_around_weight = hex_around.weight

                movement_point_after_hex_around = movement_point - hex_around_weight
                """number of movement point you have after going to the hex_around"""
                if (
                    hex_around in hexs_calculated
                    and movement_point_after_hex_around > hexs_calculated[hex_around]
                ):
                    continue
                if movement_point_after_hex_around <= 0:
                    continue

                hexs_to_calculate.append((hex_around, movement_point_after_hex_around))
