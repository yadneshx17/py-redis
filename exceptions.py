from collections import namedtuple

Error = namedtuple("Error", ("messages",))


class Disconnect(Exception):
    pass


class CommandError(Exception):
    pass
