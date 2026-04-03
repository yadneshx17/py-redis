class FreqNode:
    def __init__(self, freq: int):
        self.freq = freq
        self.next = None
        self.prev = None
        self.value_head = None  # Head of value list


class ValueNode:
    def __init__(self, key, value) -> None:
        self.key = key
        self.value = value
        self.next = None
        self.prev = None
        self.freq_node = None  # Back-pointer to parent


class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity  # Max items
        self._hashtable = {}  # key -> valueNode mapping
        self._freq_head = FreqNode(1)  # Head fo freq list (min freq)
        self._size = 0  # current item count

    def _add_to_freq_head(self, value_node, freq_node):
        value_node.next = freq_node.value_head
        if freq_node.value_head:
            freq_node.value_head.prev = value_node
        freq_node.value_head = value_node
        value_node.prev = None  # new head has no prev

    def _remove_value_node(self, freq_node, value_node):
        if value_node.prev:
            value_node.prev.next = value_node.next
        if value_node.next:
            value_node.next.prev = value_node.prev

        if value_node == freq_node.value_head:
            freq_node.value_head = value_node.next

    def _get_or_create_freq(self, freq) -> FreqNode:
        current = self._freq_head
        while current:
            if current.freq == freq:
                return current
            elif current.freq > freq:
                # create new and insert before current
                new_node = FreqNode(freq)
                new_node.next = current
                new_node.prev = current.prev
                if current.prev:
                    current.prev.next = new_node
                current.prev = new_node
                return new_node

            current = current.next

        # Reached end without finding
        # Create new at end
        new_node = FreqNode(freq)
        current.prev.next = new_node  # Link from previous node
        new_node.prev = current.prev
        new_node.next = current
        current.prev = new_node
        return new_node

    def _remove_freq_if_empty(self, freq_node):
        # only remove if no values
        if freq_node.value_head is not None:
            return

        # unlink from doubly linked list
        if freq_node.prev:
            freq_node.prev.next = freq_node.next
        else:
            #  This is the HEAD - update _freq_head
            self._freq_head = freq_node.next

        if freq_node.next:
            freq_node.next.prev = freq_node.prev

    def _move_to_freq(self, node, new_freq):
        old_freq_node = node.freq_node

        # unlink node
        if node.prev:
            node.prev.next = node.next
        else:
            # Node was HEAD of freq list
            old_freq_node.value_head = node.next

        if node.next:
            node.next.prev = node.prev

        # check if old_freq_node is now empty
        self._remove_freq_if_empty(old_freq_node)

        # Get/Create new freq and add to head
        new_freq_node = self._get_or_create_freq
        self._add_to_freq_head(node, new_freq_node)
