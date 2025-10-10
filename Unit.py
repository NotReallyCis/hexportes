from pyaddition import camera
import pygame as pg
import unit_type, color_teams_map


class Hex:
    """this is only a class to not depends on hex_file.py for type hints"""


class Unit:
    all_units = []
    unit_selected = None
    color_remaining = color_teams_map.all_colors

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
    ):
        self.w = w
        self.h = h

        self.name = name

        self.team = team
        self.movement_point = unit_type.unit_type[name][unit_type.MOVEMENT_POINT]
        self.default_movement_point = self.movement_point
        self.set_color()
        self.set_image()

        self.get_hex().unit_on_hex = self

        self.get_possible_paths()
        self.is_selected = False

        Unit.all_units.append(self)

    def destroy(self):

        self.get_hex().unit_on_hex = None
        Unit.all_units.remove(self)

    def set_image(self):
        image_name = unit_type.unit_type[self.name][unit_type.IMAGE]
        self.image = pg.image.load(
            "unit_with_team_color/" + self.color + "_" + image_name
        )

    def set_color(self):
        if self.team in Unit.map_teams_to_color.keys():
            self.color = Unit.map_teams_to_color[self.team]
        else:
            Unit.map_teams_to_color[self.team] = Unit.color_remaining[0]
            Unit.color_remaining.pop(0)
            self.color = Unit.map_teams_to_color[self.team]

    def __str__(self):
        return str((self.name, self.team_of_main))

    def __repr__(self):
        return self.__str__()

    def __tuple__(self):
        return (self.name, self.team_of_main)

    def draw(self):
        from Hex import Hex

        x, y = Hex.get_xy_by_wh(self.w, self.h)
        camera.show_on_camera(self.image, (x, y))

    def step(self):
        self.draw()

    def step_all_units():

        for unit in Unit.all_units:
            unit: Unit
            unit.step()

    def destroy_all_units():
        for unit in Unit.all_units:
            unit: Unit
            unit.destroy()

    def get_hex(self) -> Hex:
        from Hex import Hex

        return Hex.get_hex_by_wh(self.w, self.h)

    def move_to(self, w: int, h: int):
        from Hex import Hex

        hex_to_move: Hex = Hex.get_hex_by_wh(w, h)

        if hex_to_move not in self.possible_paths.keys():
            print(
                "Can't get to",
                hex_to_move,
                "from",
                self.get_hex(),
                "with",
                self.movement_point,
                "movement point left",
            )

        else:
            self.get_hex().unit_on_hex = None
            hex_to_move.unit_on_hex = self
            self.w = w
            self.h = h
            self.movement_point = self.possible_paths[hex_to_move][1]
            self.get_possible_paths()

    def clicked(self):
        if not self.is_selected and self.team_of_main == Unit.team_of_main:
            self.select()

    def select(self):
        if not self.is_selected:
            self.is_selected = True
            Unit.unit_selected = self

    def unselect(self):
        if self.is_selected:
            self.is_selected = False
            Unit.unit_selected = None

    def get_possible_paths(self):
        self.possible_paths = {}  # tile_to_go:(path,movement_point_left)
        start_path = []
        self.search_hex(self.get_hex(), self.movement_point, start_path)

    def search_hex(self, hex: "Hex", movement_point_possessed: int, path: list):
        from Hex import Hex

        path = path.copy()
        path.append(hex)

        for hex_around in hex.get_hexs_around_hex():
            hex_around: Hex
            movement_point_needed = hex_around.movement_point_needed

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
                )

        self.add_to_path(hex, path, movement_point_possessed)

    def add_to_path(self, hex: Hex, path: list, movement_point: int):
        self.possible_paths[hex] = (path, movement_point)

    def is_path_from_node_have_not_been_calculated(self, hex: Hex, movement_point: int):
        return (hex not in self.possible_paths.keys()) or (
            self.possible_paths[hex][1] < movement_point
        )
