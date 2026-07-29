import sys, json, random

sys.path.append("/home/louane/git/hexportes")
import pygame as pg
import pyg, camera_movement

from hex import Hex

screen = pg.display.set_mode((720, 500))
pg.init()

pyg.init_all_module(70, False)


from data import OIL, BAREN, GREEN, WATER, ROCKY
import data

possible_terrain: list[str] = [BAREN, GREEN, WATER, ROCKY]
type_selected = BAREN
unit_selected = None

from unit import unit_type, SURFACE, get_unit_surface


class Unit:
    all_unit: dict[tuple[int, int], Unit] = {}
    unit_start_file = "assets/unit_start.json"

    @classmethod
    def init(cls):
        Unit.load_all()

    def __init__(
        self,
        w: int,
        h: int,
        name: str,
        color: str,
    ):
        self.hex = Hex.get_hex_by_wh(w, h)
        self.name = name
        self.color = color
        self.surface = get_unit_surface(self.name, self.color)
        Unit.all_unit[(w, h)] = self

    def step(self):
        self.hex.draw_surface_on_top(self.surface)

    @classmethod
    def step_all(cls):
        for unit_pos in Unit.all_unit:
            unit = Unit.all_unit[unit_pos]
            unit.step()

    @classmethod
    def load_all(cls):
        unit_start: list[dict[str, str]] = json.load(open(Unit.unit_start_file))
        for i, unit_start_per_team in enumerate(unit_start):
            color = data.all_colors[i]
            for unit_pos in unit_start_per_team:
                w, h = pyg.string_to_wh(unit_pos)
                unit_name = unit_start_per_team[unit_pos]
                Unit(w, h, unit_name, color)

    @classmethod
    def save_all(cls):
        all_info: list[dict[str, str]] = []
        for _ in data.all_colors:
            all_info.append({})
        for unit_pos in Unit.all_unit:
            unit = Unit.all_unit[unit_pos]
            unit_team = data.all_colors.index(unit.color)
            unit_pos_str = pyg.wh_to_string(*unit_pos)
            all_info[unit_team][unit_pos_str] = unit.name
        json.dump(all_info, open(Unit.unit_start_file, "w"))


def get_random_terrain():
    map: list[str] = []
    for _ in range(Hex.map_width):
        for _ in range(Hex.map_height):
            terrain = random.choice(possible_terrain)
            map.append(terrain)
    return map


def clicked_on_hex(hex: Hex):
    hex.type = type_selected


def save_map():
    map: list[str] = []
    map_file = open("assets/map.json", "w")
    for hex_list in Hex.all_hexs:
        for hex in hex_list:
            map.append(hex.type)
    map_file.write(
        json.dumps(
            map,
        )
    )
    Unit.save_all()
    print("map saved")


def reload_map():
    init_hex(True)
    remove_all_fog()


def init_hex(force_random: bool = False):
    if data.map is None or force_random:
        map = get_random_terrain()
    else:
        map = data.map
    Hex.create_hexs_map(map)


def init_button():
    button_rect = pg.Rect(0, 0, 50, 50)
    pyg.Button(
        data.next_turn_button,
        save_map,
        button_rect,
    )

    button_rect.move_ip(button_rect.width, 0)
    pyg.Button(
        data.go_button,
        reload_map,
        button_rect,
    )
    for terrain in Hex.terrain_types:

        button_rect.move_ip(button_rect.width, 0)
        pyg.Button(
            Hex.terrain_types[terrain][Hex.SURFACE],
            switch_to_terrain,
            button_rect,
            (terrain),
        )

    for unit_name in unit_type:
        button_rect.left = 0
        button_rect.move_ip(0, button_rect.height)
        for color in data.all_colors:
            unit_surface: pg.Surface = get_unit_surface(unit_name, color)
            pyg.Button(unit_surface, switch_to_unit, button_rect, (unit_name, color))
            button_rect.move_ip(button_rect.width, 0)


def switch_to_terrain(terrain_type: str):
    global type_selected, unit_selected
    type_selected = terrain_type
    unit_selected = None


def switch_to_unit(unit_name: str, color: str):
    global unit_selected, type_selected
    unit_selected = (unit_name, color)
    type_selected = None


def remove_all_fog():
    for hex_list in Hex.all_hexs:
        for hex in hex_list:
            hex.remove_fog()
    Hex.reload_fog_surface()


def init():
    init_button()
    init_hex()
    remove_all_fog()
    data.current_state = data.click_state.MAP_BUILDING
    Unit.init()


@pyg.keyboard.execute_on_click
def on_click():
    if pyg.Button.is_position_in_zone_covered(*pyg.keyboard.mouse_position.xy):
        return
    if Hex.hex_cursor_is_on is None:
        return

    if type_selected is not None:
        Hex.hex_cursor_is_on.change_type(type_selected)
        Hex.reset_maps_surface()
    else:
        w,h=Hex.hex_cursor_is_on.w, Hex.hex_cursor_is_on.h
        if Unit.all_unit.get((w,h)) is not None:
            Unit

        Unit(w,h, *unit_selected)


init()
while 1:
    pyg.step_to_all_module()
    Hex.step_to_all_hex()
    Unit.step_all()
    pg.display.flip()
    screen.fill((0, 0, 0))
    camera_movement.step()
