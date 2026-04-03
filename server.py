import socket

from commands import Commands
from exceptions import CommandError, Disconnect, Error
from lfu_cache import LFUCache
from protocol import Decoder, Encoder


class Server:
    def __init__(self, host="127.0.0.1", port=6379) -> None:
        self.host = host
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.protocol_decoder = Decoder()
        self.protocol_encoder = Encoder()
        # self._kv = {} 
        self._kv = LFUCache(capacity=100)  # key-value store
        self._commands = Commands(self._kv)

    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen()

        print(f"[*] Server running on {self.host}:{self.port} [*]")

        while True:
            conn, addr = self.socket.accept()
            print(f"[*] Connection from {addr} [*]")

            self.connection_handler(conn, addr)

    def connection_handler(self, conn, addr):

        # Converts the socket to a file-like object for reading/writing
        socket_file = conn.makefile(mode="rwb")

        while True:
            try:
                data = self.protocol_decoder.handle_request(socket_file)
                if not data:
                    raise CommandError("Missing command")

            except Disconnect:
                break

            try:
                resp = self._commands.get_response(data)
            except CommandError as exc:
                resp = Error(exc.args[0])

            self.protocol_encoder.write_response(socket_file, resp)

        socket_file.close()
        conn.close()


if __name__ == "__main__":
    server = Server()
    server.start()
