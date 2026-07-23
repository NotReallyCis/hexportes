if __name__ != "__main__":
    raise ImportError("Can't import main.py as it is the main game file")

import json, threading
import pygame as pg
import pyg

team: int
screen = pg.display.set_mode((720, 500))
fps = 75

pg.init()
pyg.init_all_module(fps, False)

import client

import data


def init():
    global team
    client.init_all()
    team = client.Client.id
    print("team is:", team)

    unit.Unit.init(team)
    Hex.create_hexs_map(data.map)


from hex import Hex
import unit
import camera_movement


def end_of_turn(is_sending_data_to_server: bool = True):

    client.receive_and_send_maps_info(is_sending_data_to_server)
    client.start_waiting_loop()
    data.current_state = data.click_state.SELECT_UNIT


def unselect_unit():
    if unit.Unit.unit_selected is None:
        return
    unit.Unit.unit_selected.unselect()


def get_number_of_player():
    return unit.Unit.map_teams_to_color.__len__()


pyg.Button(
    data.next_turn_button,
    end_of_turn,
    pg.Rect(0, 0, 50, 50),
    True,
)

pyg.keyboard.set_new_key_map("f5", True, end_of_turn)
pyg.keyboard.set_new_key_map("escape", True, unselect_unit)

start_unit = [
    {(9, 15): unit.USINE, (9, 16): unit.MINER},
    {(21, 14): unit.USINE, (21, 15): unit.MINER},
]


def create_start_units():
    for unit_position in start_unit[get_number_of_player() - 1]:
        unit_name = start_unit[get_number_of_player() - 1][unit_position]
        unit.Unit.from_name(*unit_position, unit_name, team)


def display_fps():
    pyg.camera(pyg.draw.fps_counter(), (0, 0), -1, True)


def step():
    pyg.step_to_all_module()
    display_fps()
    Hex.step_to_all_hex()
    unit.Unit.step_all_units()

    camera_movement.step()
    pg.display.flip()
    screen.fill((0, 0, 0))


init()
end_of_turn(False)  # it gets the map of the server at the start
create_start_units()
while True:
    step()
