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
    import Unit

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

        Unit.Unit.destroy_all_units()  # it must be between the send and the receive
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
        pygame.quit()
        exit()

    init_all_module()
    Unit.Unit.init(team)
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
    )

    def set_click_stat_at_attack():
        data.click_stat.stat = data.click_stat.SELECT_UNIT_ATTACK

    attack_button = Button(
        data.attack_button,
        set_click_stat_at_attack,
        50,
        0,
        50,
        50,
    )

    def set_click_stat_at_go():
        data.click_stat.stat = data.click_stat.SELECT_UNIT_DESTINATION

    go_button = Button(
        data.go_button,
        set_click_stat_at_go,
        100,
        0,
        50,
        50,
    )

    data.create_function_on_key_map("end_of_turn", start_of_turn)

    placeholder_image_waiting = data.background_waiting_image
    pg.transform.scale(placeholder_image_waiting, screen.get_size())

    running = True

    start_of_turn(False)  # it gets the map of the server at the start

    import unit_type

    Unit.Unit(5, 5, unit_type.TEST_UNIT, team)
    while running:
        Hex.step_to_all_hex()  # better to put that before button step is called
        Unit.Unit.step_all_units()

        for line in Hex.all_hexs:
            for hex in line:
                hex: Hex

        step_to_all_module()
        camera_movement.step()

        if Unit.Unit.unit_selected == None:
            attack_button.is_alive = False
            go_button.is_alive = False
        else:
            attack_button.is_alive = True
            go_button.is_alive = True

        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            elif event.type == pg.KEYDOWN:
                keyboard.key_press(event.key)
            elif event.type == pg.KEYUP:
                keyboard.key_release(event.key)

        pg.display.flip()
        screen.fill((0, 0, 0))
        clock.tick(fps)
    pg.quit()
