from typing import List, Optional

from exceptions import CommandError


class Commands:
    def __init__(self, _kv):
        self._kv = _kv

        self.commands = {
            "GET": self.get,
            "SET": self.set,
            "DELETE": self.delete,
            "FLUSH": self.flush,
            "MGET": self.mget,
            "MSET": self.mset,
        }

    def get_response(self, data):
        if not isinstance(data, list):
            try:
                data = data.split()  # splits string into a list of words
            except AttributeError:
                raise CommandError("Request must be list or simple string.")

        if not data:
            raise CommandError("Missing command")

        command = data[0].upper()
        if command in self.commands:
            return self.commands[command](*data[1:])

        return

    def get(self, key) -> Optional[str]:
        return self._kv.get(key)

    def set(self, key, value) -> Optional[str]:
        self._kv[key] = value
        return "OK"

    def delete(self, key) -> int:
        if key in self._kv:
            del self._kv[key]
            return 1
        return 0

    def flush(self) -> Optional[str]:
        self._kv.clear()
        return "OK"

    # bulk operations
    def mget(self, *keys) -> List[Optional[str]]:
        if len(keys) == 1 and isinstance(keys[0], list):
            keys = keys[0]
        return [self._kv.get(key) for key in keys]

    def mset(self, *items) -> Optional[str]:
        if len(items) == 1 and isinstance(items[0], dict):
            for k, v in items[0].items():
                self._kv[k] = v
            return "OK"
        if len(items) % 2 != 0:
            raise CommandError("wrong number of arguments for MSET")
        it = iter(items)
        for k, v in zip(it, it):    
            self._kv[k] = v
        return "OK"
