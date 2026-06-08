from pyg import camera, draw, get_percentage
import pygame as pg
import data, pyg


from typing import TYPE_CHECKING

if TYPE_CHECKING:  # resolve the circular import type hinting issue
    from hex import Hex
else:

    class Hex:  # empty class replaced with the Hex just below
        pass


def get_variable(variable, default):
    """return The variable if it's not none and the default otherwise (similar to git.dict)"""
    if variable is None:
        return default
    else:
        return variable


RANGE = "range"
VIEW_RANGE = "view_range"
MOVEMENT_POINT = "movement_point"
IMAGE = "image"
PV = "pv"
TEST_UNIT = "first_test"
DAMAGE = "damage"
AMMO = "ammo"
FUEL = "fuel"

unit_type = {
    TEST_UNIT: {
        MOVEMENT_POINT: 4,
        RANGE: 5,
        VIEW_RANGE: 5,
        IMAGE: "tile-village.png",
        PV: 10,
        DAMAGE: 5,
        AMMO: 20,
        FUEL: 10,
    },
}


def get_unit_image_by_unit_and_color(unit_name: str, color: str):
    image_name = unit_type[unit_name][IMAGE]
    return pg.image.load(data.directory_unit_team_color + color + "_" + image_name)


class Unit:
    all_units = []
    unit_selected = None

    color_remaining = data.all_colors
    selected_bad_unit_sound = data.selected_bad_unit_sound

    @classmethod
    def init(cls, team: int):
        """create a new team"""
        Unit.team_of_main = team

        Unit.map_teams_to_color = {Unit.team_of_main: Unit.color_remaining[0]}
        Unit.color_remaining.pop(0)

    def set_click_stat_at_go():
        data.click_stat.stat = data.click_stat.SELECT_UNIT_DESTINATION

    go_button = pyg.Button(
        data.go_button,
        set_click_stat_at_go,
        pg.Rect(100, 0, 50, 50),
    )

    def set_click_stat_at_attack():
        data.click_stat.stat = data.click_stat.SELECT_UNIT_ATTACK

    attack_button = pyg.Button(
        data.attack_button,
        set_click_stat_at_attack,
        pg.Rect(50, 0, 50, 50),
    )

    def __init__(
        self,
        w: int,
        h: int,
        name: str,
        team: int,
        pv: int = None,
        ammo: int = None,
        fuel: int = None,
    ):
        self.w = w
        self.h = h

        self.name = name

        self.default_pv = unit_type[name][PV]
        self.pv: int = get_variable(pv, self.default_pv)

        self.default_ammo = unit_type[name][AMMO]
        self.ammo: int = get_variable(ammo, self.default_ammo)

        self.default_fuel = unit_type[name][FUEL]
        self.fuel: int = get_variable(fuel, self.default_fuel)

        self.damage = unit_type[name][DAMAGE]
        self.range = unit_type[name][RANGE]
        self.view_range = unit_type[name][VIEW_RANGE]

        self.movement_point = unit_type[name][MOVEMENT_POINT]
        self.default_movement_point = self.movement_point

        self.team = team
        self.set_color()
        self.set_image()
        if self.get_hex().unit_on_hex != None:
            raise ValueError(
                f"hex({w,h}) is arleady taken by another unit, can't generate here"
            )
        self.get_hex().unit_on_hex = self

        self.get_possible_paths()
        self.get_possible_range()
        self.get_possible_view_range()

        self.is_selected = False

        Unit.all_units.append(self)

    def set_image(self):
        self.image = get_unit_image_by_unit_and_color(self.name, self.color)

    def set_color(self):
        if self.team in Unit.map_teams_to_color.keys():
            self.color = Unit.map_teams_to_color[self.team]
        else:
            Unit.map_teams_to_color[self.team] = Unit.color_remaining[0]
            Unit.color_remaining.pop(0)
            self.color = Unit.map_teams_to_color[self.team]

    def destroy(self):
        if self.is_selected:
            self.unselect()
        self.get_hex().unit_on_hex = None
        Unit.all_units.remove(self)

    @classmethod
    def destroy_all_units(cls):
        for unit in Unit.all_units:
            unit: Unit
            unit.destroy()

    def __str__(self):
        return str((self.name, self.team))

    def __repr__(self):
        return self.__str__()

    def __tuple__(self):
        return (self.name, self.team, self.pv, self.ammo, self.fuel)

    def step(self):
        if self.pv <= 0:
            self.destroy()

        if self.is_selected:
            match data.click_stat.stat:
                case data.click_stat.SELECT_UNIT_DESTINATION:
                    self.draw_possible_paths()
                case data.click_stat.SELECT_UNIT_ATTACK:
                    self.draw_possible_range()
        if self.get_hex().is_visible:
            self.draw()
            self.draw_info()

    @classmethod
    @pyg.Profiler
    def step_all_units(cls):

        for unit in Unit.all_units:
            unit: Unit
            unit.step()

    def draw(self):
        from hex import Hex

        x, y = Hex.get_xy_by_wh(self.w, self.h)
        camera(self.image, (x, y))

    def draw_info(self):
        x, y = self.get_xy()

        life_info = draw.bar_percentage(
            get_percentage(self.pv, self.default_pv),
            width=50,
            height=5,
            border_size=1,
            bar_color=pg.Color(0, 250, 0),
        )
        camera(life_info, (x, y - 5))

        fuel_info = draw.bar_percentage(
            get_percentage(self.fuel, self.default_fuel),
            width=50,
            height=5,
            border_size=1,
            bar_color=pg.Color(250, 123, 0),
        )
        camera(fuel_info, (x, y))

        ammo_info = draw.bar_percentage(
            get_percentage(self.ammo, self.default_ammo),
            width=50,
            height=5,
            border_size=1,
            bar_color=pg.Color(250, 0, 0),
        )
        camera(ammo_info, (x, y + 5))

    def draw_possible_paths(self):
        for hex in self.possible_paths:
            hex.draw_surface_on_top(data.hex_can_go)

    def draw_possible_range(self):
        for hex in self.possible_range:
            hex.draw_surface_on_top(data.hex_can_attack)

    def get_hex(self):
        """Get the hex where the unit is"""
        from hex import Hex

        hex: Hex = Hex.get_hex_by_wh(self.w, self.h)
        return hex

    def get_xy(self):
        return (self.get_hex().x, self.get_hex().y)

    def move_to(self, w: int, h: int):
        from hex import Hex

        hex_to_move: Hex = Hex.get_hex_by_wh(w, h)

        if (
            hex_to_move not in self.possible_paths.keys()
            or not self.have_enough_fuel_to_go_to(hex_to_move)
        ):
            self.unselect()
            return

        self.get_hex().unit_on_hex = None
        hex_to_move.unit_on_hex = self

        self.w = w
        self.h = h

        movement_point_consumed = self.movement_point - self.possible_paths[hex_to_move]
        self.fuel -= movement_point_consumed
        self.movement_point = self.possible_paths[hex_to_move]

        self.get_possible_paths()
        self.get_possible_range()
        self.get_possible_view_range()

    def have_enough_fuel_to_go_to(self, hex: "Hex"):
        if hex not in self.possible_paths.keys():
            raise ValueError("hex is unreacheable")

        movement_point_consumed = self.movement_point - self.possible_paths[hex]
        fuel_left = self.fuel - movement_point_consumed
        return fuel_left >= 0

    def attack(self, unit_to_attack: "Unit"):
        if (
            unit_to_attack.get_hex() in self.possible_range
            and unit_to_attack.team != self.team
        ):
            unit_to_attack.pv -= self.damage
            self.ammo -= 1

    def select(self):
        if self.is_selected:
            raise ValueError(
                "you can't select a unit that is arleady selected, (unit selected:)",
                self.__str__(),
            )
        elif self.team != Unit.team_of_main:
            Unit.selected_bad_unit_sound.play()
        else:
            self.is_selected = True
            Unit.unit_selected = self
            data.click_stat.stat = data.click_stat.SELECT_UNIT_DESTINATION

        Unit.attack_button.is_visible = True
        Unit.go_button.is_visible = True

    def unselect(self):
        if not self.is_selected:
            raise ValueError(
                "you can't unselect a unit that is not selected, (unit unselected:)",
                self.__str__(),
            )
        else:
            self.is_selected = False
            Unit.unit_selected = None
            data.click_stat.stat = data.click_stat.SELECT_UNIT
        Unit.attack_button.is_visible = False
        Unit.go_button.is_visible = False

    def get_possible_paths(self):
        """get all the possible tiles you can go"""
        movement_point = self.movement_point
        self.possible_paths = self.search_hex(self.get_hex(), movement_point, True)

    def get_possible_range(self):
        """get all the possible tiles you can shoot to"""
        self.possible_range = self.search_hex(self.get_hex(), self.range, False)

    def get_possible_view_range(self):
        """get all the possible tiles you can view"""
        visible_hexs = self.search_hex(self.get_hex(), self.view_range, False)
        for hex in visible_hexs:
            hex.remove_fog()

    def search_hex(
        self,
        start_hex: Hex,
        movement_point_possessed: int,
        is_hex_weight_matter: bool,
    ):
        """_summary_

        Args:
            hex (Hex): The hex you start from
            movement_point_possessed (int): _description_
            path (list): input an empty list at beginning
            is_hex_weight_matter (bool): does the weight of the hex you go to are counted
        """
        hexs_to_calculate: list[tuple[Hex, int]] = [
            (start_hex, movement_point_possessed)
        ]

        hexs_calculated: dict[Hex, int] = {}

        while True:
            if hexs_to_calculate == []:  # on end
                return hexs_calculated

            hex_calculating, movement_point = hexs_to_calculate[0]
            hexs_to_calculate.pop(0)

            hexs_calculated[hex_calculating] = movement_point

            for hex_around in hex_calculating.get_hexs_around_hex():
                if hex_around in hexs_calculated:
                    continue

                hex_around_weight: int = 1
                if is_hex_weight_matter:
                    hex_around_weight = hex_around.weight

                movement_point_after_hex_around = movement_point - hex_around_weight
                """number of movement point you have after going to the hex_around"""
                if movement_point_after_hex_around > 0:
                    hexs_to_calculate.append(
                        (hex_around, movement_point_after_hex_around)
                    )
