from typing import List, Optional

from .server import Server


class Commands:
    def __init__(self):
        self.commands = {
            "GET": self.get,
            "SET": self.set,
            "DELETE": self.delete,
            "FLUSH": self.flush,
            "MGET": self.mget,
            "MSET": self.mset,
        }
        self.server = Server()

    def get(self, key) -> Optional[str]:
        return self.server._kv.get(key)

    def set(self, key, value) -> int:
        self.server._kv[key] = value
        return 1

    def delete(self, key) -> Optional[str]:
        return self.server._kv.pop(key, None)

    def flush(self) -> int:
        self.server._kv.clear()
        return 1

    # bulk operations
    def mget(self, keys) -> List:
        return [self.server._kv.get(key) for key in keys]

    def mset(self, key_values) -> int:
        for k, v in key_values.items():
            self.server._kv[k] = v
        return len(key_values)
