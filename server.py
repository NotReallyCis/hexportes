import socket, threading, json

intro_length = 20
# the intro length is the number of number that is sent at start of message to give the length of the message
# it should be the same in the server and in the client


class server_class:
    def __init__(self):
        self.address = socket.gethostbyname(socket.gethostname())  # it's the host
        self.port = 5000  # could be changed

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        self.socket.listen(1)  # 1 is the number of people to listen
        print("listening on", self.port, ",", self.address)

    def loop_to_accept(self):
        (client_socket, client_address) = self.socket.accept()
        print(
            "connected to", client_address[1]
        )  # [1] to only get the ip, idk what's the second number
        self.create_client(client_socket, client_address)

    def create_client(self, client_socket: socket.socket, client_address):
        thread_of_discussion = threading.Thread(
            target=Client,
            args=(
                client_socket,
                client_address,
            ),  # should be a tuple 'cause it only accepts iterable
        )
        thread_of_discussion.start()
        # not ".run" because ".start" have to be called at least once per thread


class Client:

    all_clients = []
    all_map_info: str | None = None

    def __init__(self, client_socket: socket.socket, client_address: str):
        self.socket = client_socket
        self.is_connected_to_server = True
        self.address = client_address

        print(self.address, "connected to server")
        Client.all_clients.append(self)

        while self.is_connected_to_server:  # constant loop
            self.step()

    def step(self):

        message = self.receive_from_client()

        if message is None:
            self.disconnect()
            return None  # important to return something or the rest will run one more time before stopping

        print("the message from:", self.address, " ,is:", message)
        if message != "":
            Client.all_map_info = message
            self.send_new_infos_to_all_others_client()

    def send_new_infos_to_all_others_client(self):
        for client in Client.all_clients:
            client: Client

            if client != self:
                print(client, "!=?", self)
                print(Client.all_map_info, "sent to", client)
                client.send(Client.all_map_info)

    def receive_from_client(self):
        try:
            length_of_message = self.socket.recv(intro_length).decode("utf-8")
        except ConnectionResetError:
            return None
        if length_of_message == "":  # 'cause it's disconnected if it receive that
            return None  # returning None automaticly disconnect

        length_of_message = int(length_of_message)

        output = self.socket.recv(length_of_message).decode("utf-8")
        return output

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

    def send(self, *info):
        info = str(*info)

        output_to_send = self.get_0_before_int(info.__len__(), intro_length) + info

        self.socket.send(output_to_send.encode("utf-8"))

    def disconnect(self):
        Client.all_clients.remove(self)
        print(self.address, "disconnected :<")
        self.socket.shutdown(1)
        self.socket.close()

        self.is_connected_to_server = False

    def __str__(self):
        return str(self.address)

    def __repr__(self):
        return self.__str__()


server = server_class()

while True:
    server.loop_to_accept()
