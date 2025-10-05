import socket, random, json
import pyaddition as pyadd

intro_length = 20
# the intro length is the number of number that is sent at start of message to give the length of the message
# it should be the same in the server and in the client


class server_class:

    address = socket.gethostbyname(socket.gethostname())  # it's host so it's own ip
    port = 5000


server = server_class()


class client_class:
    def init():
        client_class.port = 5000 + random.randint(
            1, 1000
        )  # it's random so maybe it can be the same as someone else?
        client_class.address = socket.gethostbyname(socket.gethostname())

        print("port=", client_class.port, "addr=", client_class.address)

        print("triying connect to", server.port, ",", server.address)

        client_class.socket = client_class.connect(server.port, server.address)
        print("connected to", server.port, ",", server.address)

        client_class.get_intro_data_from_server()

    def connect(port: int, addr: str = socket.gethostbyname(socket.gethostname())):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((addr, port))
        except ConnectionRefusedError:
            raise ConnectionRefusedError(
                "Coudln't connect to the server, most likely due to the server not being launched"
            )
        return s

    def get_intro_data_from_server(self):
        intro_data = client_class.receive_from_server()

        intro_data: tuple = json.loads(intro_data)

        client_class.id = intro_data[0]

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

    def send_to_server(info: str, intro_length: int = 20):
        """the intro length is the number of number that is sent at start of message to give the length of the message \n
        it should be the same in the server and in the client"""
        info = str(info)
        output_to_send = (
            client_class.get_0_before_int(info.__len__(), intro_length) + info
        )

        client_class.socket.send(output_to_send.encode("utf-8"))

    def receive_from_server(intro_length: int = 20):
        """the intro length is the number of number that is sent at start of message to give the length of the message \n
        it should be the same in the server and in the client"""

        length_of_message = client_class.socket.recv(intro_length)
        length_of_message = length_of_message.decode("utf-8")

        if length_of_message == "":  # 'cause it's disconnected if it received that
            raise ConnectionAbortedError("Server disconnected, pls fix me ><")

        length_of_message = int(length_of_message)

        output = client_class.socket.recv(length_of_message)

        output = output.decode("utf-8")

        return output

    def disconnect(self):
        print("disconnected :<")
        client_class.socket.shutdown(1)
        client_class.socket.close()
