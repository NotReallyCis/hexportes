if __name__ == "__main__":
    import client

    client.init_all()
    team: int = client.Client.id

    import pygame as pg

    pg.init()
    screen = pg.display.set_mode((720, 500))
    clock = pg.time.Clock()
    fps = 120

    print("team is:", team)

    import json, threading, client
    from Hex import Hex
    import unit

    from pyaddition import *

    import camera_movement

    @keyboard.execute_on_click
    def executed_on_clik():
        if not Button.is_position_in_zone_covered(*keyboard.mouse_position.xy):
            Hex.hex_cursor_is_on.clicked()

    def start_of_turn(is_sending_data_to_server: bool = True):
        data.click_stat.stat = data.click_stat.SELECT_UNIT

        global has_receive_message_from_server
        has_receive_message_from_server = False
        handle_discussion_with_server(is_sending_data_to_server)

        start_waiting_loop()

    def start_waiting_loop():
        global has_receive_message_from_server

        while (
            not has_receive_message_from_server
        ) and running:  # loop when waiting for the server answer
            screen.blit(placeholder_image_waiting, (0, 0))

            pg.display.flip()
            screen.fill((0, 0, 0))
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    has_receive_message_from_server = True  # to quit the loop
                    quit()
            clock.tick(fps)

    def handle_discussion_with_server(is_sending_data: bool):
        if is_sending_data:
            send_map_info_to_server()

        unit.Object.destroy_all_units()  # it must be between the send and the receive
        Hex.on_end_of_turn()
        discusion_with_server_thread = threading.Thread(
            target=receive_map_info_from_server
        )
        discusion_with_server_thread.daemon = True  # thread will stop when main quit
        discusion_with_server_thread.start()

    def receive_map_info_from_server():

        uncoded_message = json.loads(client.Client.receive_message())
        Hex.load_all_hexs__str__(uncoded_message)

        global has_receive_message_from_server
        has_receive_message_from_server = True

    def send_map_info_to_server():
        client.Client.send(json.dumps(Hex.get_all_hexs__str__()))

    def quit():
        global running
        running = False
        pg.quit()
        exit()

    def show_fps(show: bool):
        import pyaddition

        if show:
            text_surface: pg.Surface = pyaddition.draw.text(clock.get_fps())
            pyaddition.camera.show(
                text_surface,
                (
                    screen.get_width() - 50,
                    0,
                ),
                True,
            )  # 200 is a random value

    init_all_module()
    unit.Object.init(team)
    Hex.create_hexs_map()

    import data

    data.click_stat.stat = data.click_stat.SELECT_UNIT  # the stat at start

    Button(
        data.next_turn_button,
        start_of_turn,
        0,
        0,
        50,
        50,
        True,
        True,
    )

    data.key_map.create_function_on_key_map("end_of_turn", start_of_turn)

    data.key_map.create_function_on_key_map(
        "escape",
        unit.Object.unselect_unit_selected,
    )

    placeholder_image_waiting = data.background_waiting_image
    placeholder_image_waiting = placeholder_image_waiting.scale(*screen.get_size())

    running = True

    start_of_turn(False)  # it gets the map of the server at the start

    import object_type

    unit.Usine(6, 6, object_type.TEST_USINE, team)
    unit.Usine(6, 7, object_type.TEST_USINE, team)
    unit.Usine(6, 8, object_type.TEST_USINE, team)
    unit.Unit(5, 6, object_type.TEST_UNIT, team)

    while running:
        Hex.step_to_all_hex()  # better to put that before button step is called
        unit.Object.step_all_objects()

        step_to_all_module()
        camera_movement.step()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            elif event.type == pg.KEYDOWN:
                keyboard.key_press(event.key)
            elif event.type == pg.KEYUP:
                keyboard.key_release(event.key)

        show_fps(True)
        pg.display.flip()
        screen.fill((0, 0, 0))
        clock.tick_busy_loop(fps)

    pg.quit()
