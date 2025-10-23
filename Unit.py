from pyaddition import camera, draw, get_percentage, Button
import pygame as pg
import data, object_type
from typing import overload


class Object:
    all_objects = []
    object_selected: type["Object"] | type["Unit"] | type["Usine"] = None

    color_remaining = data.all_colors
    selected_bad_unit_sound = data.selected_bad_unit_sound

    def init(team: int):
        Object.team_of_main = team

        Object.map_teams_to_color = {Object.team_of_main: Object.color_remaining[0]}
        Object.color_remaining.pop(0)
        Unit.init(team)

    def __init__(
        self,
        w: int,
        h: int,
        name: str,
        team: int,
        pv_of_object: int = None,
    ):
        self.type: str = object_type.TYPE_OBJECT
        self.stat_when_selected: str

        self.w = w
        self.h = h

        self.name = name

        self.cost = object_type.object_type[name][object_type.COST]

        self.view_range = object_type.object_type[name][object_type.VIEW_RANGE]

        self.movement_point_needed = object_type.object_type[name][
            object_type.MOVEMENT_POINT_NEEDED
        ]
        self.get_hex().object_on_hex = self

        self.default_pv = object_type.object_type[name][object_type.PV]
        if pv_of_object == None:
            self.pv = self.default_pv
        else:
            self.pv = pv_of_object

        self.team = team
        self.set_color()
        self.set_image()

        self.is_selected = False
        if self.team == Object.team_of_main:
            self.get_hex_in_view_range()

        Object.all_objects.append(self)

    def set_image(self):
        self.image = object_type.get_object_image_by_name_and_color(
            self.name, self.color
        )

    def set_color(self):
        if self.team in Object.map_teams_to_color.keys():
            self.color = Object.map_teams_to_color[self.team]
        else:
            Object.map_teams_to_color[self.team] = Object.color_remaining[0]
            Object.color_remaining.pop(0)
            self.color = Object.map_teams_to_color[self.team]

    def destroy(self) -> None:
        if self.is_selected:
            Object.unselect()
        self.get_hex().object_on_hex = None
        Object.all_objects.remove(self)

    def destroy_all_units():
        for _ in range(Object.all_objects.__len__()):
            unit: Unit = Object.all_objects[0]
            unit.destroy()
            # this weird thing with range because destroy remove the unit from all_objects
            # so you can't make a for unit in all_objects

    def __str__(self):
        return str(
            (
                (self.w, self.h),
                self.name,
                self.team,
            )
        )

    def __repr__(self):
        return self.__str__()

    def get_infos(self):
        return {
            object_type.TYPE: self.type,
            object_type.NAME: self.name,
            object_type.TEAM: self.team,
            object_type.PV: self.pv,
        }

    def create_object_from_infos(w: int, h: int, infos: dict):
        """function return type,name,team and pv"""
        type_of_object = object_type.get_class_by_type_name(infos[object_type.TYPE])
        name: str = infos[object_type.NAME]
        team: int = infos[object_type.TEAM]
        pv: int = infos[object_type.PV]

        if type_of_object == Object:
            Object(w, h, name, team, pv)
        else:
            return type_of_object, name, team, pv

    def step(self):
        if self.pv <= 0:
            self.destroy()

        if self.get_hex().is_visible:
            self.draw()

        if self.get_hex().is_visible and self.team == Unit.team_of_main:
            self.draw_info()

        self.view_hex_in_visible_hex()

    def step_all_objects():

        for unit in Object.all_objects:
            unit: Object
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

    def view_hex_in_visible_hex(self):
        if self.team == Object.team_of_main:
            from Hex import Hex

            for hex in self.hex_in_view_range:
                hex: Hex
                hex.is_visible = True

    def get_hex(self):
        from Hex import Hex

        hex: Hex = Hex.get_hex_by_wh(self.w, self.h)
        return hex

    def get_xy(self):
        return (self.get_hex().x, self.get_hex().y)

    def clicked_somewhere(self, hex):
        """this is a class for subclass to add things"""

    def select(self):
        if Object.object_selected != None:
            Object.object_selected.unselect()
        if self.team != Object.team_of_main:
            Object.selected_bad_unit_sound.play()
        else:
            self.is_selected = True
            Object.object_selected = self
            data.click_stat.stat = self.stat_when_selected

    def unselect(self):
        if Object.object_selected != None:
            Object.object_selected.is_selected = False
            Object.object_selected = None
            data.click_stat.stat = data.click_stat.SELECT_UNIT

    def unselect_unit_selected():
        if Object.object_selected != None:
            Object.object_selected.unselect()

    def get_hex_in_view_range(self):

        if self.team == Object.team_of_main:
            self.hex_in_view_range = []
            start_path = []
            dict_hex_in_view_range = {}
            self.search_hex(
                self.get_hex(),
                self.view_range,
                start_path,
                dict_hex_in_view_range,
                False,
            )
            self.hex_in_view_range = list(dict_hex_in_view_range)

    def search_hex(
        self,
        hex,
        movement_point_possessed: int,
        path: list,
        dict_to_add: dict,
        is_caring_about_hex_weight: bool,
    ):
        from Hex import Hex

        hex: Hex = (
            hex  # he's happy if you reassing the value with equal to add a type hint
        )

        path = path.copy()
        path.append(hex)

        for hex_around in hex.get_hexs_around_hex():
            hex_around: Hex
            if is_caring_about_hex_weight:
                movement_point_needed = hex_around.get_movement_point_needed()
            else:
                movement_point_needed = 1  # default value for range

            if (
                movement_point_possessed
                >= movement_point_needed  # if he can go the tile
                and (
                    (hex_around not in dict_to_add.keys())
                    or (
                        dict_to_add[hex_around][1]
                        < movement_point_possessed - movement_point_needed
                    )
                )
            ):
                self.search_hex(
                    hex_around,
                    movement_point_possessed - movement_point_needed,
                    path,
                    dict_to_add,
                    is_caring_about_hex_weight,
                )

        dict_to_add[hex] = (path, movement_point_possessed)


class Unit(Object):
    go_button: Button
    attack_button: Button

    def init(team):
        def set_click_stat_at_attack():
            data.click_stat.stat = data.click_stat.SELECT_UNIT_ATTACK

        Unit.attack_button = Button(
            data.attack_button,
            set_click_stat_at_attack,
            50,
            0,
            50,
            50,
            False,
        )

        def set_click_stat_at_go():
            data.click_stat.stat = data.click_stat.SELECT_UNIT_MOVEMENT

        Unit.go_button = Button(
            data.go_button,
            set_click_stat_at_go,
            100,
            0,
            50,
            50,
            False,
        )

    def __init__(
        self,
        w,
        h,
        name,
        team,
        pv_of_unit=None,
        ammo: int = None,
        fuel: int = None,
    ):
        super().__init__(w, h, name, team, pv_of_unit)

        self.type = object_type.TYPE_UNIT
        self.stat_when_selected = data.click_stat.SELECT_UNIT_MOVEMENT

        self.default_ammo = object_type.object_type[name][object_type.AMMO]
        if ammo == None:
            self.ammo = self.default_ammo
        else:
            self.ammo = ammo

        self.default_fuel = object_type.object_type[name][object_type.FUEL]
        if fuel == None:
            self.fuel = self.default_fuel
        else:
            self.fuel = fuel

        self.damage = object_type.object_type[name][object_type.DAMAGE]

        self.range = object_type.object_type[name][object_type.RANGE]

        self.movement_point = object_type.object_type[name][object_type.MOVEMENT_POINT]
        self.default_movement_point = self.movement_point

    def step(self):
        super().step()

        if self.is_selected:
            match data.click_stat.stat:
                case data.click_stat.SELECT_UNIT_MOVEMENT:
                    self.draw_possible_paths()
                case data.click_stat.SELECT_UNIT_ATTACK:
                    self.draw_possible_range()

        if self.get_hex().is_visible and self.team == Unit.team_of_main:
            self.draw_info()

    def clicked_somewhere(self, hex):
        from Hex import Hex

        hex: Hex = hex

        match data.click_stat.stat:
            case data.click_stat.SELECT_UNIT_MOVEMENT:
                self.move_to(hex.w, hex.h)
                if (
                    Object.object_selected == self
                ):  # unit unselect when a he want to go to an unreachable destination
                    if self.movement_point == 0:
                        self.unselect()

            case data.click_stat.SELECT_UNIT_ATTACK:
                if self != None and hex.object_on_hex != None:
                    self.attack(hex.object_on_hex)
                    data.click_stat.stat = data.click_stat.SELECT_UNIT_MOVEMENT

    def select(self):

        super().select()
        self.get_possible_range_and_path()
        Unit.attack_button.is_alive = True
        Unit.go_button.is_alive = True

    def unselect(self):
        super().unselect()
        Unit.attack_button.is_alive = False
        Unit.go_button.is_alive = False

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

    def get_infos(self):
        return super().get_infos() | {
            object_type.AMMO: self.ammo,
            object_type.FUEL: self.fuel,
        }

    def create_object_from_infos(w: int, h: int, infos: dict):
        """function return type, name, team, pv, ammo and fuel"""
        type, name, team, pv = __class__.__base__.create_object_from_infos(w, h, infos)
        ammo = infos[object_type.AMMO]
        fuel = infos[object_type.FUEL]
        if type == Unit:
            Unit(w, h, name, team, pv, ammo, fuel)
        else:
            return type, name, team, pv, ammo, fuel

    def get_possible_paths(self):
        if self.team == Object.team_of_main:
            self.possible_paths = {}  # tile_to_go:(path,movement_point_left)
            start_path = []
            self.search_hex(
                self.get_hex(),
                min(self.movement_point, self.fuel),
                start_path,
                self.possible_paths,
                True,
            )

    def get_possible_range(self):

        if self.team == Object.team_of_main:
            self.possible_range = []
            start_path = []
            dict_possible_range = {}
            self.search_hex(
                self.get_hex(), self.range, start_path, dict_possible_range, False
            )
            self.possible_range = list(dict_possible_range)

    def get_possible_range_and_path(self):
        self.get_possible_paths()
        self.get_possible_range()

    def move_to(self, w: int, h: int):
        from Hex import Hex

        hex_to_move: Hex = Hex.get_hex_by_wh(w, h)

        if (
            hex_to_move not in self.possible_paths.keys()
            or hex_to_move.object_on_hex != None
        ):
            self.unselect()

        else:

            self.get_hex().object_on_hex = None
            hex_to_move.object_on_hex = self

            self.w = w
            self.h = h

            movement_point_consumed = (
                self.movement_point - self.possible_paths[hex_to_move][1]
            )
            self.fuel -= movement_point_consumed
            self.movement_point = self.possible_paths[hex_to_move][1]

            self.get_possible_range_and_path()
            self.get_hex_in_view_range()

    def attack(self, unit_to_attack: "Object"):
        if (
            unit_to_attack.get_hex() in self.possible_range
            and unit_to_attack.team != self.team
        ):
            unit_to_attack.pv -= self.damage
            self.ammo -= 1

    def draw_info(self):
        super().draw_info()

        x, y = self.get_xy()

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


class Usine(Object):
    def __init__(self, w, h, name, team, pv_of_unit=None, material: int = None):
        super().__init__(w, h, name, team, pv_of_unit)

        self.default_material = object_type.object_type[name][object_type.MATERIAL]
        if material == None:
            self.material = self.default_material
        else:
            self.material = material

        self.creatable_units = object_type.object_type[name][object_type.CREATABLE_UNIT]

        self.type = object_type.TYPE_USINE
        self.stat_when_selected = data.click_stat.SELECT_UNIT_TO_CREATE
        self.create_buttons_for_units()
        self.creatable_range = self.get_hex().get_hexs_around_hex()

    def create_buttons_for_units(self):
        self.creatable_units_buttons = []
        rect_to_create_buttons = pg.Rect(0, 50, 100, 800)
        height_of_button = 50
        width_of_button = rect_to_create_buttons.width
        y = rect_to_create_buttons.y

        for creatable_unit_name in self.creatable_units:
            self.creatable_units_buttons.append(
                Button(
                    object_type.object_type[creatable_unit_name][
                        object_type.BUTTON_IMAGE
                    ],
                    self.set_stat_to_create_unit,
                    rect_to_create_buttons.x,
                    y,
                    width_of_button,
                    height_of_button,
                    False,
                    creatable_unit_name,
                )
            )
            y += height_of_button

    def show_buttons_to_chose_unit(self):
        for button in self.creatable_units_buttons:
            button: Button
            button.is_alive = True

    def hide_buttons_to_chose_unit(self):
        for button in self.creatable_units_buttons:
            button: Button
            button.is_alive = False

    def set_stat_to_create_unit(self, unit_name: str):

        if unit_name not in object_type.object_type.keys():
            raise ValueError("unit name: ", unit_name, " is not recognized")
        if object_type.object_type[unit_name][object_type.COST] <= self.material:
            data.click_stat.stat = data.click_stat.SELECT_UNIT_CREATION
            data.click_stat.unit_name_to_create = unit_name
            self.hide_buttons_to_chose_unit()

    def select(self):
        super().select()
        self.show_buttons_to_chose_unit()

    def unselect(self):
        super().unselect()
        self.hide_buttons_to_chose_unit()

    def step(self):
        super().step()
        if (
            self.is_selected
            and data.click_stat.stat == data.click_stat.SELECT_UNIT_CREATION
        ):
            self.draw_creatable_range()

    def get_infos(self):
        return super().get_infos() | {
            object_type.MATERIAL: self.material,
        }

    def draw_info(self):
        super().draw_info()
        x, y = self.get_xy()

        fuel_info = draw.bar_percentage(
            get_percentage(self.material, self.default_material),
            width=50,
            height=5,
            border_size=1,
            bar_color=pg.Color(0, 0, 250),
        )
        camera.show(fuel_info, (x, y))

    def draw_creatable_range(self):
        from Hex import Hex

        for hex in self.creatable_range:
            hex: Hex
            hex.stat.append(data.hex_type.CAN_CRAFT_ON)

    def create_object_from_infos(w: int, h: int, infos: dict):
        """function return type,name,team,pv,material"""
        type, name, team, pv = __class__.__base__.create_object_from_infos(w, h, infos)
        material = infos[object_type.MATERIAL]
        if type == Usine:
            Usine(w, h, name, team, pv, material)
        else:
            return type, name, team, pv, material

    def clicked_somewhere(self, hex):
        from Hex import Hex

        hex: Hex = hex

        match data.click_stat.stat:
            case data.click_stat.SELECT_UNIT_CREATION:
                if hex in self.get_hex().get_hexs_around_hex():
                    new_unit = Unit(
                        hex.w,
                        hex.h,
                        data.click_stat.unit_name_to_create,
                        self.team,
                    )
                    self.material -= new_unit.cost
                    self.unselect()  # TODO: set max zone to create a unit
                else:
                    self.unselect()
