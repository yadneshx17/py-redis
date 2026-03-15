import socket

from exceptions import CommandError, Error
from protocol import Decoder, Encoder


class Client:
    def __init__(self, host="127.0.0.1", port=6379):
        self.encoder = Encoder()
        self.decoder = Decoder()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        self._fh = self.socket.makefile(mode="rwb")

    def execute(self, *args):
        self.encoder.write_response(self._fh, args)
        # Rewind the mock file handle so the decoder can read from it
        resp = self.decoder.handle_request(self._fh)
        if isinstance(resp, Error):
            raise CommandError(resp.messages)
        return resp

    def get(self, key):
        return self.execute("GET", key)

    def set(self, key, value):
        return self.execute("SET", key, value)

    def delete(self, key):
        return self.execute("DELETE", key)

    def flush(self):
        return self.execute("FLUSH")

    def mget(self, *keys):
        if len(keys) == 1 and isinstance(keys[0], list):
            keys = keys[0]
        return self.execute("MGET", *keys)

    def mset(self, *items):
        if len(items) == 1 and isinstance(items[0], dict):
            flat = []
            for k, v in items[0].items():
                flat.extend([k, v])
            items = flat
        return self.execute("MSET", *items)

