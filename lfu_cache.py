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
        # self._size = 0  # current item count


    def __repr__(self):
        return f"LFUCache(capacity={self.capacity}, size={len(self)})"


    def _add_to_freq_value_head(self, value_node, freq_node):
        value_node.next = freq_node.value_head
        if freq_node.value_head:
            freq_node.value_head.prev = value_node
        freq_node.value_head = value_node
        value_node.prev = None
        value_node.freq_node = freq_node


    def _remove_value_node(self, freq_node, value_node):
        if value_node.prev:
            value_node.prev.next = value_node.next
        if value_node.next:
            value_node.next.prev = value_node.prev

        if value_node == freq_node.value_head:
            freq_node.value_head = value_node.next


    def _get_or_create_freq(self, freq) -> FreqNode:
        current = self._freq_head
        last = None  
        while current:
            if current.freq == freq:
                return current
            elif current.freq > freq:
                # create new and insert before current
                new_node = FreqNode(freq)
                new_node.next = current
                if current.prev:
                    new_node.prev = current.prev
                    current.prev.next = new_node
                else:
                    self._freq_head = new_node
                current.prev = new_node
                return new_node
            last = current
            current = current.next

        # Reached end without finding
        # Create new at end
        new_node = FreqNode(freq)
        new_node.prev = last
        if last:
            last.next = new_node
        else:
            self._freq_head = new_node  # edge case: empty list

        return new_node


    def _remove_freq_if_empty(self, freq_node):
        # only remove if no values AND not freq=1 (always keep freq=1)
        if freq_node.value_head is not None or freq_node.freq == 1:
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
        new_freq_node = self._get_or_create_freq(new_freq)
        self._add_to_freq_value_head(node, new_freq_node)


    # Dict interface
    def __setitem__(self, key, value):
        if len(self._hashtable) == self.capacity:
            self._evict_lfu()

        if key in self._hashtable:
            # update existing
            node = self._hashtable[key]
            node.value = value
            
            # updating value without accessing shouldn''t bump frequency.
            # self._move_to_freq(node, node.freq_node.freq + 1) # optional
        else:
            # insert new
            node = ValueNode(key, value)
            self._hashtable[key] = node
            self._add_to_freq_value_head(node, self._freq_head)


    def __getitem__(self, key):
        node = self._hashtable.get(key)
        if not node:
            raise KeyError(key)

        # increment frequency
        self._move_to_freq(node, node.freq_node.freq + 1)
        return node.value


    def __delitem__(self, key):
        value_node = self._hashtable[key]
        self._remove_value_node(value_node.freq_node, value_node)
        self._remove_freq_if_empty(value_node.freq_node)
        del self._hashtable[key]


    # EVICTION
    def _evict_lfu(self):
        freq_node = self._freq_head
        
        # traverse frequency list and find the first node that has a value to evict.
        while freq_node and freq_node.value_head is None:
            freq_node = freq_node.next
        
        if not freq_node or not freq_node.value_head:
            return
        
        tail = freq_node.value_head
        while tail.next:
            tail = tail.next
        
        del self._hashtable[tail.key]
        
        if tail.prev:
            tail.prev.next = tail.next
        if tail.next:
            tail.next.prev = tail.prev
        if freq_node.value_head == tail:
            freq_node.value_head = tail.next
            
        self._remove_freq_if_empty(freq_node)

    def __contains__(self, key):
        return key in self._hashtable

    def get(self, key, default=None):
        node = self._hashtable.get(key)
        if node is None:
            return default
        self._move_to_freq(node, node.freq_node.freq + 1)
        return node.value

    def __len__(self):
        return len(self._hashtable)

    def clear(self):
        self._hashtable.clear()
        self._freq_head = FreqNode(1)
