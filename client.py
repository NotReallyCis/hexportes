import socket, random, json
import pyaddition as pyadd

intro_length = 20
# the intro length is the number of number that is sent at start of message to give the length of the message
# it should be the same in the server and in the client


class server_class:
    def __init__(self):
        self.address = socket.gethostbyname(
            socket.gethostname()
        )  # it's host so it's own ip
        self.port = 5000


server = server_class()


class client_class:
    def connect(
        self, port: int, addr: str = socket.gethostbyname(socket.gethostname())
    ):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((addr, port))
        except ConnectionRefusedError:
            raise ConnectionRefusedError(
                "Coudln't connect to the server, most likely due to the server not being launched"
            )
        return s

    def __init__(self):

        self.port = 5000 + random.randint(
            1, 1000
        )  # it's random so maybe it can be the same as someone else?
        self.address = socket.gethostbyname(socket.gethostname())

        print("port=", self.port, "addr=", self.address)

        print("triying connect to", server.port, ",", server.address)

        self.socket = self.connect(server.port, server.address)
        print("connected to", server.port, ",", server.address)

        self.get_intro_data_from_server()

    def get_intro_data_from_server(self):
        intro_data = self.receive_from_server()

        intro_data: tuple = json.loads(intro_data)

        self.id = intro_data[0]

    def get_0_before_int(self, number: int | str, length_expected: int) -> str:
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

    def send_to_server(self, info: str, intro_length: int = 20):
        """the intro length is the number of number that is sent at start of message to give the length of the message \n
        it should be the same in the server and in the client"""
        info = str(info)
        output_to_send = self.get_0_before_int(info.__len__(), intro_length) + info

        self.socket.send(output_to_send.encode("utf-8"))

    def receive_from_server(self, intro_length: int = 20):
        """the intro length is the number of number that is sent at start of message to give the length of the message \n
        it should be the same in the server and in the client"""

        length_of_message = self.socket.recv(intro_length)
        length_of_message = length_of_message.decode("utf-8")

        if length_of_message == "":  # 'cause it's disconnected if it received that
            raise ConnectionAbortedError("Server disconnected, pls fix me ><")

        length_of_message = int(length_of_message)

        output = self.socket.recv(length_of_message)

        output = output.decode("utf-8")

        return output

    def disconnect(self):
        print("disconnected :<")
        self.socket.shutdown(1)
        self.socket.close()


client = client_class()
