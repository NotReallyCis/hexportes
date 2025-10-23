import socket, threading, json, data


intro_length = 20
# the intro length is the number of number that is sent at start of message to give the length of the message
# it should be the same in the server and in the client


class Server:

    address = socket.gethostbyname(socket.gethostname())  # it's the host
    port = 5000  # could be changed

    socket_of_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_of_server.bind((address, port))
    socket_of_server.listen(1)  
    print("listening on", port, ",", address)

    def loop_to_accept():
        (client_socket, client_address) = Server.socket_of_server.accept()
        Server.create_client(client_socket, client_address)

    def create_client(client_socket: socket.socket, client_address):
        thread_of_discussion = threading.Thread(
            target=Client,
            args=(
                client_socket,
                client_address,
            ),  # should be a tuple 'cause it only accepts iterable
        )
        thread_of_discussion.start()
        # not ".run" because ".start" have to be called at least once per thread

    def destroy_disconnected_units(team_disconnected: int):
        import object_type

        map_info = json.loads(Client.all_map_info)
        for x, line in enumerate(map_info):
            for y, unit in enumerate(line):
                if unit != None:
                    unit_team = unit[object_type.TEAM]
                    if unit_team == team_disconnected:
                        map_info[x][y] = None

        Client.all_map_info = json.dumps(map_info)


class Client:

    all_clients = {}

    all_map_info: str = data.empty_map_str
    max_team_given = 0

    def __init__(self, client_socket: socket.socket, client_address: str):
        self.socket = client_socket
        self.is_connected_to_server = True
        self.address = client_address

        self.team = Client.max_team_given
        Client.max_team_given += 1  # so two client can't have the same id, though the number become pretty large

        Client.all_clients[self.team] = self
        self.send_intro_data()
        print(self.__str__(), "connected to server")
        if Client.all_clients.__len__() == 1:  # aka it's the first player
            self.send_map_infos()

        while self.is_connected_to_server:  # constant loop
            self.step()

    def send_intro_data(self):
        intro_data = (self.team,)
        self.send(json.dumps(intro_data))

    def step(self):

        message = self.receive_from_client()

        if message is None:
            self.disconnect()
            return None  # important to return something or the rest will run one more time before stopping

        print("the message from:", self.__str__(), " ,is:", message)

        if message != "":
            Client.all_map_info = message
            self.get_next_client().send_map_infos()

    def send_map_infos(self):
        self.send(Client.all_map_info)

    def get_next_client(self) -> "Client":
        all_clients_list = list(Client.all_clients.keys())
        position_of_self = all_clients_list.index(self.team)
        if (
            position_of_self != all_clients_list.__len__() - 1
        ):  # if it's not the last player
            next_client_id = all_clients_list[position_of_self + 1]
        else:
            next_client_id = all_clients_list[0]
        return Client.all_clients[next_client_id]

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

    def send(self, info):
        if not isinstance(info, str):
            info = json.dumps(info)

        output_to_send = self.get_0_before_int(info.__len__(), intro_length) + info
        try:
            self.socket.send(output_to_send.encode("utf-8"))
        except ConnectionResetError:
            self.disconnect()
        print(info, "sent to", self.__str__())

    def disconnect(self):
<<<<<<< HEAD
        if len(Client.all_clients.keys()) != 1:
            self.get_next_client().send_map_infos()
=======
>>>>>>> parent of ad10661 (Merge branch 'main' of https://github.com/femboyv/hexportes)
        Server.destroy_disconnected_units(self.team)
        Client.all_clients.pop(self.team)
        print(self.__str__(), "disconnected :<")
        self.socket.shutdown(1)
        self.socket.close()

        self.is_connected_to_server = False

    def __str__(self):
        return str((self.address, self.team))

    def __repr__(self):
        return self.__str__()


while True:
    Server.loop_to_accept()
