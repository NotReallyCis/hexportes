import socket, random, json, threading
import pyg, data
import pygame as pg

intro_length = 20
""" the intro length is the number of number that is sent at start of message to give the length of the message
it should be the same in the Server and in the client"""

has_receive_message_from_server: bool


class Server:

    address = socket.gethostbyname(socket.gethostname())
    port = 5000


class Client:
    port = 5000 + random.randint(
        1, 1000
    )  # it's random so maybe it can be the same as someone else though it's 0.1% chance
    address = socket.gethostbyname(socket.gethostname())
    socket_to_server: socket.socket
    id: int

    @classmethod
    def init(cls):

        print(f"""port= {Client.port}, addr= {Client.address}
        trying to connect to {Server.port, Server.address})""")

        Client.socket_to_server = Client.connect(Server.port, Server.address)
        print(f"connected to {Server.port,Server.address}")

        Client.get_intro_data_from_server()

    @classmethod
    def connect(cls, port: int, addr: str = socket.gethostbyname(socket.gethostname())):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((addr, port))
        except ConnectionRefusedError:
            raise ConnectionRefusedError(
                "Coudln't connect to the server, most likely due to the server not being launched"
            )
        return s

    @classmethod
    def get_intro_data_from_server(cls):
        intro_data = Client.receive_message()

        intro_data: tuple = json.loads(intro_data)
        Client.id = intro_data[0]

    @classmethod
    def get_0_before_int(cls, number: int | str, length_expected: int) -> str:
        """get 0 before the int so it correspond to a certain length (eg: input 1,4 it will output 0001)"""
        if isinstance(number, int):
            number = str(number)

        number_length = len(number)
        if number_length > length_expected:
            raise ValueError(
                "Number length is greater to expected length, increment expected length or lower number"
            )
        for _ in range(length_expected - number_length):
            number = "0" + number

        return number

    @classmethod
    def send(cls, info: str, intro_length: int = 20):
        """the intro length is the number of number that is sent at start of message to give the length of the message \n
        it should be the same in the Server and in the client"""
        info = str(info)
        output_to_send = Client.get_0_before_int(info.__len__(), intro_length) + info

        Client.socket_to_server.send(output_to_send.encode("utf-8"))

    @classmethod
    def receive_message(cls, intro_length: int = 20):
        """the intro length is the number of number that is sent at start of message to give the length of the message \n
        it should be the same in the Server and in the client"""

        length_of_message = Client.socket_to_server.recv(intro_length)
        length_of_message = length_of_message.decode("utf-8")

        if length_of_message == "":  # 'cause it's disconnected if it received that
            raise ConnectionAbortedError("Server disconnected, pls fix me ><")

        length_of_message = int(length_of_message)

        output = Client.socket_to_server.recv(length_of_message)

        output = output.decode("utf-8")

        return output

    @classmethod
    def disconnect(cls):
        print("disconnected :<")
        Client.socket_to_server.shutdown(1)
        Client.socket_to_server.close()


def start_waiting_loop():
    """start While loop with the loading screen waiting for an answer of the server"""

    while not has_receive_message_from_server:
        pg.display.get_surface().blit(data.background_waiting_image, (0, 0))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pyg.shutdown()

        pg.display.flip()
        pg.display.get_surface().fill((0, 0, 0))
        pyg.clock.tick(pyg.fps)


def receive_and_send_maps_info(is_sending_data: bool):
    """send (if is_sending_data is True) and receive the map info for the server

    Args:
        is_sending_data (bool): give or not the local map to the server
    """
    if is_sending_data:
        send_map_info_to_server()

    from hex import Hex
    from unit import Unit

    Unit.destroy_all_units()  # it must be between the send and the receive to reset
    Hex.on_end_of_turn()
    global has_receive_message_from_server
    has_receive_message_from_server = False
    thread_discussion_server = threading.Thread(target=receive_map_info_from_server)
    thread_discussion_server.daemon = True  # thread will stop when main quit
    thread_discussion_server.start()


def receive_map_info_from_server():
    from unit import Unit

    uncoded_message = json.loads(Client.receive_message())
    print(uncoded_message)
    Unit.load_all_info(uncoded_message)

    global has_receive_message_from_server
    has_receive_message_from_server = True


def send_map_info_to_server():
    from unit import Unit

    Client.send(json.dumps(Unit.get_all_info()))


def init_all():
    Client.init()
