from pyaddition import camera, draw, get_percentage
import pygame as pg
import data, unit_type


class Hex:
    """this is only a class to not depends on hex_file.py for type hints"""


class Unit:
    all_units = []
    unit_selected = None

    color_remaining = data.all_colors
    selected_bad_unit_sound = data.selected_bad_unit_sound

    def init(team: int):
        Unit.team_of_main = team

        Unit.map_teams_to_color = {Unit.team_of_main: Unit.color_remaining[0]}
        Unit.color_remaining.pop(0)

    def __init__(
        self,
        w: int,
        h: int,
        name: str,
        team: int,
        pv_of_unit: int = None,
        ammo: int = None,
        fuel: int = None,
    ):
        self.w = w
        self.h = h

        self.name = name

        self.default_pv = unit_type.unit_type[name][unit_type.PV]

        if pv_of_unit == None:
            self.pv = self.default_pv
        else:
            self.pv = pv_of_unit

        self.default_ammo = unit_type.unit_type[name][unit_type.AMMO]
        if ammo == None:
            self.ammo = self.default_ammo
        else:
            self.ammo = ammo

        self.default_fuel = unit_type.unit_type[name][unit_type.FUEL]
        if fuel == None:
            self.fuel = self.default_fuel
        else:
            self.fuel = fuel

        self.damage = unit_type.unit_type[name][unit_type.DAMAGE]

        self.range = unit_type.unit_type[name][unit_type.RANGE]

        self.view_range = unit_type.unit_type[name][unit_type.VIEW_RANGE]

        self.movement_point = unit_type.unit_type[name][unit_type.MOVEMENT_POINT]
        self.default_movement_point = self.movement_point

        self.team = team
        self.set_color()
        self.set_image()

        self.get_hex().unit_on_hex = self

        self.get_possible_paths()
        self.get_possible_range()
        self.get_possible_view_range()

        self.is_selected = False

        Unit.all_units.append(self)

    def set_image(self):
        self.image = unit_type.get_unit_image_by_unit_and_color(self.name, self.color)

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

    def destroy_all_units():
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

    def step_all_units():

        for unit in Unit.all_units:
            unit: Unit
            unit.step()

    def draw(self):
        from Hex import Hex

        x, y = Hex.get_xy_by_wh(self.w, self.h)
        camera.show(self.image, (x, y))

    def draw_info(self):
        x, y = self.get_xy()

        life_info = draw.bar_percentage(
            get_percentage(self.pv, self.default_pv),
            width=50,
            height=5,
            border_size=1,
            bar_color=pg.Color(0, 250, 0),
        )
        camera.show(life_info, (x, y - 5))

        fuel_info = draw.bar_percentage(
            get_percentage(self.fuel, self.default_fuel),
            width=50,
            height=5,
            border_size=1,
            bar_color=pg.Color(250, 123, 0),
        )
        camera.show(fuel_info, (x, y))

        ammo_info = draw.bar_percentage(
            get_percentage(self.ammo, self.default_ammo),
            width=50,
            height=5,
            border_size=1,
            bar_color=pg.Color(250, 0, 0),
        )
        camera.show(ammo_info, (x, y + 5))

    def draw_possible_paths(self):
        from Hex import Hex

        for hex in self.possible_paths:
            hex: Hex
            hex.stat.append(data.hex_type.UNIT_CAN_GO)

    def draw_possible_range(self):
        from Hex import Hex

        for hex in self.possible_range:
            hex: Hex
            hex.stat.append(data.hex_type.UNIT_CAN_ATTACK)

    def get_hex(self):
        from Hex import Hex

        hex: Hex = Hex.get_hex_by_wh(self.w, self.h)
        return hex

    def get_xy(self):
        return (self.get_hex().x, self.get_hex().y)

    def move_to(self, w: int, h: int):
        from Hex import Hex

        hex_to_move: Hex = Hex.get_hex_by_wh(w, h)

        if (
            hex_to_move not in self.possible_paths.keys()
            or not self.have_enough_fuel_to_go_to(hex_to_move)
        ):
            self.unselect()

        else:

            self.get_hex().unit_on_hex = None
            hex_to_move.unit_on_hex = self

            self.w = w
            self.h = h

            movement_point_consumed = (
                self.movement_point - self.possible_paths[hex_to_move][1]
            )
            self.fuel -= movement_point_consumed
            self.movement_point = self.possible_paths[hex_to_move][1]

            self.get_possible_paths()
            self.get_possible_range()
            self.get_possible_view_range()

    def have_enough_fuel_to_go_to(self, hex: "Hex"):
        if hex not in self.possible_paths.keys():
            raise ValueError("hex is unreacheable")
        movement_point_consumed = self.movement_point - self.possible_paths[hex][1]
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

    def get_possible_paths(self):
        self.possible_paths = {}  # tile_to_go:(path,movement_point_left)
        start_path = []
        self.search_hex(self.get_hex(), self.movement_point, start_path, True, False)

    def get_possible_range(self):
        self.possible_range = []
        start_path = []
        self.search_hex(self.get_hex(), self.range, start_path, False, False)

    def get_possible_view_range(self):
        start_path = []
        self.search_hex(self.get_hex(), self.view_range, start_path, False, True)

    def search_hex(
        self,
        hex: Hex,
        movement_point_possessed: int,
        path: list,
        is_calculating_movement: bool,
        is_calculating_view_range: bool,
    ):
        from Hex import Hex

        hex: Hex = hex  # he's visibly happy if you reassing the value with equal

        path = path.copy()
        path.append(hex)

        for hex_around in hex.get_hexs_around_hex():
            hex_around: Hex
            if is_calculating_movement:
                movement_point_needed = hex_around.movement_point_needed
            else:
                movement_point_needed = 1  # default value for range

            if (
                movement_point_possessed >= movement_point_needed
                and self.is_path_from_node_have_not_been_calculated(
                    hex_around, movement_point_possessed - movement_point_needed
                )
            ):
                self.search_hex(
                    hex_around,
                    movement_point_possessed - movement_point_needed,
                    path,
                    is_calculating_movement,
                    is_calculating_view_range,
                )

        if is_calculating_movement:
            self.possible_paths[hex] = (path, movement_point_possessed)
        else:
            if is_calculating_view_range:

                hex.is_visible = True

            elif hex not in self.possible_range:
                self.possible_range.append(hex)

    def is_path_from_node_have_not_been_calculated(self, hex: Hex, movement_point: int):
        """it checks if the coordinate has been calculated arlready with a better path"""
        return (hex not in self.possible_paths.keys()) or (
            self.possible_paths[hex][1] < movement_point
        )
