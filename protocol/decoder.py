from exceptions import CommandError, Disconnect, Error

"""
RESP Protocol

"""


class Decoder:
    def __init__(self):
        self.handlers = {
            "+": self.handle_simple_string,
            "-": self.handle_error,
            ":": self.handle_integer,
            "$": self.handle_string,
            "*": self.handle_array,
            "%": self.handle_dict,
        }

    def handle_request(self, socket_file):
        # parse the request from the client into its components parts
        # Returns a list of strings representing the parsed request

        first_byte = socket_file.read(
            1
        )  # first byte of the request/payload/data is the data type indicator
        first_byte = first_byte.decode("utf-8")

        if not first_byte:
            raise Disconnect()

        try:
            # Delegate to the appropriate handler based on the first byte.
            return self.handlers[first_byte](socket_file)
        except KeyError:
            raise CommandError("bad request")

    def handle_simple_string(self, socket_file):
        return socket_file.readline().rstrip(b"\r\n").decode("utf-8")

    def handle_error(self, socket_file):
        return Error(socket_file.readline().rstrip(b"\r\n").decode("utf-8"))

    def handle_integer(self, socket_file):
        return int(socket_file.readline().rstrip(b"\r\n"))

    def handle_string(self, socket_file):
        length = int(socket_file.readline().rstrip(b"\r\n"))
        if length == -1:
            return None
        length += 2
        return socket_file.read(length)[:-2].decode("utf-8")
    def handle_array(self, socket_file):
        num_elements = int(socket_file.readline().rstrip(b"\r\n"))
        return [self.handle_request(socket_file) for _ in range(num_elements)]

    def handle_dict(self, socket_file):
        num_items = int(socket_file.readline().rstrip(b"\r\n"))
        elements = [self.handle_request(socket_file) for _ in range(num_items * 2)]
        return dict(zip(elements[::2], elements[1::2]))
