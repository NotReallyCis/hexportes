# def debug_path_finding():
#     test_unit = Unit_uwu(4, 4, placeholder_test_unit2, 4)
#     test_unit.get_possible_paths()
#     print(
#         "number_of_case:",
#         test_unit.possible_paths.__len__(),
#     )
#     for hex in test_unit.possible_paths:
#         hex: Hex
#         hex.debug_highlight(placeholder_test_unit4)
#     return 1

import pygame as pg
import math, json, client, threading


pg.init()
screen = pg.display.set_mode((720, 500))
clock = pg.time.Clock()
fps = 120
team = 1
import unit
from Hex import Hex

from pyaddition import *


@keyboard.execute_on_clik
def executed_on_clik():
    Hex.hex_cursor_is_on.clicked()


def end_of_turn():
    client.client.send_to_server(json.dumps(Hex.get_all_hexs__str__()))
    unit.Unit.on_end_of_turn()
    discusion_with_server_thread = threading.Thread(
        target=handle_discussion_with_server,
    )
    global has_receive_message_from_server
    has_receive_message_from_server = False

    discusion_with_server_thread.start()

    while (
        not has_receive_message_from_server
    ):  # loop when waiting for the server answer
        screen.blit(placeholder_image_waiting, (0, 0))

        pg.display.flip()
        screen.fill((0, 0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                has_receive_message_from_server = True  # to quit the loop
                quit()
        clock.tick(fps)


def handle_discussion_with_server():
    message = client.client.receive_from_server()
    print("message is:", message)
    if message != "None":
        uncoded_message = json.loads(message)
        print("uncoded message is:", uncoded_message, type(uncoded_message))
        Hex.load_all_hexs__str__(uncoded_message)
    else:
        print("bad message :<", message)
    global has_receive_message_from_server
    has_receive_message_from_server = True


def quit():
    global running
    running = False


def setup():

    Hex.create_hexs_map()

    placeholder_next_turn_button = pg.image.load(
        "Complete_UI_Essential_Pack_Free/Complete_UI_Essential_Pack_Free/01_Flat_Theme/Sprites/UI_Flat_IconCheck01a.png"
    )
    Button(
        placeholder_next_turn_button,
        end_of_turn,
        0,
        0,
        50,
        50,
    )

    first_player = int(input("player(1 or 2)?")) == 1  # it's a bool, dw
    global team
    if first_player:
        team = 1
    else:
        team = 2
    global placeholder_image_waiting
    placeholder_image_waiting = pg.image.load("placeholder_image_waiting.png")
    pg.transform.scale(placeholder_image_waiting, screen.get_size())

    import unit_type

    if team == 1:
        unit.Unit(4, 4, unit_type.TEST_UNIT, team)
    else:
        unit.Unit(8, 4, unit_type.TEST_UNIT, team)

    global running
    running = True

    if not first_player:  # equal to if input ==2
        end_of_turn()


def step():
    while running:
        step_to_all_module()

        Hex.step_to_all_hex()
        unit.Unit.step_all_units()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()

        pg.display.flip()
        screen.fill((0, 0, 0))
        clock.tick(fps)
    pg.quit()


if __name__ == "__main__":
    setup()
    print(team)
    step()
