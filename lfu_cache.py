class FreqNode:
    def __init__(self, freq: int):
        self.freq = freq
        self.next = None     
        self.prev = None
        self.values_head = None # Head of.... value list of frequency Node

class ValueNode:
    def __init__(self, key, value) -> None:
        self.key = key
        self.value = value
        self.next = None
        self.prev = None
        self.freq_node = None # pointing back to freq node
        
class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity # Max items
        self._hashtable = {}     # key -> valueNode mapping
        self._freq_head = None   # Head fo freq list (min freq) 
        self._size = 0           # current item count
        
        