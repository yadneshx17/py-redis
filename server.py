import socket
from collections import namedtuple

from resp_parser import ProtocolHandler


# Exceptions
class Disconnect(Exception):
    pass


class CommandError(Exception):
    pass


Error = namedtuple("Error", ("messages",))


class Server:
    def __init__(self, host="127.0.0.1", port=6379) -> None:
        self.host = host
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.protocol_handler = ProtocolHandler()
        self._kv = {}  # key-value store

    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen()

        print(f"[*] Server running on {self.host}:{self.port} [*]")

        while True:
            conn, addr = self.socket.accept()
            print(f"[*] Connection from {addr} [*]")

            self.connection_handler(conn, addr)

    def connection_handler(self, conn, addr):
        socket_file = conn.makefile("rwb")

        while True:
            try:
                data = socket_file.read()
                if not data:
                    break

                resp = self.protocol_handler.handle_request(data)
            except Disconnect:
                break

            except CommandError as exc:
                resp = Error(exc.args[0])

            self.protocol_handler.write_response(socket_file, resp)

    def get_response(self, data):
        pass
