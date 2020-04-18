import socket


class Server(object):
    """
    An adventure game socket server
    
    An instance's methods share the following variables:
    
    * self.socket: a "bound" server socket, as produced by socket.bind()
    * self.client_connection: a "connection" socket as produced by socket.accept()
    * self.input_buffer: a string that has been read from the connected client and
      has yet to be acted upon.
    * self.output_buffer: a string that should be sent to the connected client; for
      testing purposes this string should NOT end in a newline character. When
      writing to the output_buffer, DON'T concatenate: just overwrite.
    * self.done: A boolean, False until the client is ready to disconnect
    * self.room: one of 0, 1, 2, 3. This signifies which "room" the client is in,
      according to the following map:
      
                                     3                      N
                                     |                      ^
                                 1 - 0 - 2                  |
                                 
    When a client connects, they are greeted with a welcome message. And then they can
    move through the connected rooms. For example, on connection:
    
    OK! Welcome to Realms of Venture! This room has brown wall paper!  (S)
    move north                                                         (C)
    OK! This room has white wallpaper.                                 (S)
    say Hello? Is anyone here?                                         (C)
    OK! You say, "Hello? Is anyone here?"                              (S)
    move south                                                         (C)
    OK! This room has brown wall paper!                                (S)
    move west                                                          (C)
    OK! This room has a green floor!                                   (S)
    quit                                                               (C)
    OK! Goodbye!                                                       (S)
    
    Note that we've annotated server and client messages with *(S)* and *(C)*, but
    these won't actually appear in server/client communication. Also, you'll be
    free to develop any room descriptions you like: the only requirement is that
    each room have a unique description.
    """

    game_name = "Realms of Venture"

    def __init__(self, port=50000):
        self.input_buffer = ""
        self.output_buffer = ""
        self.done = False
        self.socket = None
        self.client_connection = None
        self.port = port

        self.room = 0

    def connect(self):
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP)

        address = ('127.0.0.1', self.port)
        self.socket.bind(address)
        self.socket.listen(1)

        self.client_connection, address = self.socket.accept()

    def room_description(self, room_number):

        return [
            "You are in the room with the paisley wall paper.",
            "You are in the room with the tacky panelling.",
            "You are in the room with the day-glo walls.",
            "You are in the room with the grafitti walls.",
        ] [room_number]


    def greet(self):

        self.output_buffer = "Welcome to {}! {}".format(
            self.game_name,
            self.room_description(self.room)
        )

    def get_input(self):

        received = b''
        while b'\n' not in received:
            received += self.client_connection.recv(16)

        self.input_buffer = received.decode().strip()
        self.client_connection
        pass

    def move(self, argument):

        if self.room == 3 and argument == "south":
            self.room = 0
        room_map = {
            "north": 3,
            "south": 0,
            "east": 2,
            "west": 1
        }
        room_number = room_map[argument]
        self.room = room_number

        # This accounts for the one exception where east doest to to room 2
        if self.room == 1 and argument == "east":
            self.room = 0

        self.output_buffer = self.room_description(self.room)

    def say(self, argument):

        self.output_buffer = 'You, say, "{}"'.format(argument)
        pass

    def quit(self, argument):

        self.done = True
        self.output_buffer ="Salut, my friend!"

    def route(self):

        received = self.input_buffer.split(" ")

        command = received.pop(0)
        arguments = " ".join(received)

        {
            'quit': self.quit,
            'move': self.move,
            'say': self.say,
        }[command](arguments)

    def push_output(self):

        data= "OK! " + self.output_buffer
        self.client_connection.sendall(data.encode('utf8'))

    def serve(self):
        self.connect()
        self.greet()
        self.push_output()

        while not self.done:
            self.get_input()
            self.route()
            self.push_output()

        self.client_connection.close()
        self.socket.close()
