import socket, random, json

intro_length = 20
# the intro length is the number of number that is sent at start of message to give the length of the message
# it should be the same in the Server and in the client


class Server:

    address = "172.25.87.200"
    port = 5000


class Client:
    port = 5000 + random.randint(
        1, 1000
    )  # it's random so maybe it can be the same as someone else though it's 0.1% chance
    address = socket.gethostbyname(socket.gethostname())
    socket_to_server: socket.socket = None
    id: int

    def init():

        print("port=", Client.port, "addr=", Client.address)

        print("trying to connect to", Server.port, ",", Server.address)
        Client.socket_to_server = Client.connect(Server.port, Server.address)
        print("connected to", Server.port, ",", Server.address)

        Client.get_intro_data_from_server()

    def connect(port: int, addr: str = socket.gethostbyname(socket.gethostname())):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((addr, port))
        except ConnectionRefusedError:
            raise ConnectionRefusedError(
                "Coudln't connect to the Server, most likely due to the Server not being launched"
            )
        return s

    def get_intro_data_from_server():
        intro_data = Client.receive_message()

        intro_data: tuple = json.loads(intro_data)
        Client.id = intro_data[0]

    def get_0_before_int(number: int | str, length_expected: int) -> str:
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

    def send(info: str, intro_length: int = 20):
        """the intro length is the number of number that is sent at start of message to give the length of the message \n
        it should be the same in the Server and in the client"""
        info = str(info)
        output_to_send = Client.get_0_before_int(info.__len__(), intro_length) + info

        Client.socket_to_server.send(output_to_send.encode("utf-8"))

    def receive_message(intro_length: int = 20):
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

    def disconnect():
        print("disconnected :<")
        Client.socket_to_server.shutdown(1)
        Client.socket_to_server.close()


def init_all():

    Client.init()
