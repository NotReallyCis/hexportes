import pygame as pg

pg.init()
screen = pg.display.set_mode((720, 500))
clock = pg.time.Clock()
fps = 120

import math, json, Client, threading

import Unit
from Hex import Hex

from pyaddition import *


@keyboard.execute_on_clik
def executed_on_clik():
    Hex.hex_cursor_is_on.clicked()


def end_of_turn():
    Unit.Unit.on_end_of_turn()

    global has_receive_message_from_server
    has_receive_message_from_server = False
    discusion_with_server_thread = threading.Thread(
        target=handle_discussion_with_server,
    )
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
    send_map_info_to_server()
    receive_map_info_from_server()

    global has_receive_message_from_server
    has_receive_message_from_server = True


def receive_map_info_from_server():
    message = Client.client.receive_from_server()
    print("message is:", message)
    if message != "None":
        uncoded_message = json.loads(message)
        print("uncoded message is:", uncoded_message, type(uncoded_message))
        Hex.load_all_hexs__str__(uncoded_message)
    else:
        print("bad message :<", message)


def send_map_info_to_server():
    Client.client.send_to_server(json.dumps(Hex.get_all_hexs__str__()))


def quit():
    global running
    running = False


def setup():
    init_all_module()
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

    global team
    team = Client.client.id

    global placeholder_image_waiting
    placeholder_image_waiting = pg.image.load("placeholder_image_waiting.png")
    pg.transform.scale(placeholder_image_waiting, screen.get_size())

    receive_map_info_from_server()  # it gets the

    global running
    running = True


def step():
    while running:
        step_to_all_module()

        Hex.step_to_all_hex()
        Unit.Unit.step_all_units()

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
