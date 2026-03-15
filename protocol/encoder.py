from io import BytesIO

from exceptions import CommandError, Error

"""
Serialise the data to send back to the client
"""


class Encoder:
    def __init__(self):
        pass

    def write_response(self, socket_file, data):
        buffer = BytesIO()  # stores binary data
        self._write(buffer, data)
        buffer.seek(0)
        b = buffer.getvalue()
        socket_file.write(b)  # write requires bytes
        socket_file.flush() # explicitly flush the buffer (not doing this will lead to data not being sent to the client), hangs both client and the server
        return b

    def _write(self, buffer, data):
        if isinstance(data, str):
            data = data.encode("utf-8")

        if isinstance(data, bytes):
            buffer.write(b"$%d\r\n%s\r\n" % (len(data), data))
        elif isinstance(data, int):
            buffer.write(b":%d\r\n" % data)
        elif isinstance(data, Error):
            buffer.write("-%s\r\n" % data.messages)
        elif isinstance(data, (list, tuple)):
            buffer.write(b"*%d\r\n" % len(data))
            for item in data:
                self._write(buffer, item)
        elif isinstance(data, dict):
            buffer.write(b"%%%d\r\n" % len(data))
            for key in data:
                self._write(buffer, key)
                self._write(buffer, data[key])
        elif data is None:
            buffer.write(b"$-1\r\n")
        else:
            raise CommandError("unrecognized type: %s" % type(data))
