# py-Redis

py-Redis is a lightweight, simplified implementation of a Redis-like in-memory key-value data store written in Python. It supports basic operations over a custom RESP (REdis Serialization Protocol) implementation with **LFU (Least Frequently Used) cache eviction**.

## Features

- **In-Memory Store**: Fast key-value storage.
- **Custom RESP Implementation**: Includes Encoders and Decoders to serialize and deserialize data for client-server communication.
- **Bulk Operations**: Perform multiple get or set operations in a single network round-trip.
- **LFU Cache Eviction**: Automatic eviction of least frequently used items when capacity is reached.
- **O(1) Operations**: All cache operations (insert, get, delete) run in constant time.

## Supported Commands

The following commands are currently implemented:
- `SET key value`: Sets the value of a key.
- `GET key`: Gets the value of a key.
- `DELETE key`: Deletes a key.
- `FLUSH`: Clears the entire database.
- `MSET key value [key value ...]`: Sets multiple keys to multiple values. Also accepts a dictionary in the Python client.
- `MGET key [key ...]`: Gets values for multiple keys. Also accepts a list in the Python client.

## Folder Structure

```text
mini-redis/
├── lfu_cache.py          # LFU Cache implementation with doubly linked list + hashtable
├── server.py             # Server implementation
├── commands.py           # Command execution logic
├── exceptions.py         # Custom exceptions
├── protocol/
│   ├── decoder.py        # RESP decoder
│   ├── encoder.py        # RESP encoder
│   └── __init__.py
├── tests/
│   └── test_lfu_cache.py # Comprehensive test suite (42 tests)
├── venv/                 # Virtual environment
├── requirements.txt      # Dependencies
└── README.md
```

## Requirements

```
pytest>=7.0.0
```

## LFU Cache Implementation

### Data Structures

The LFU cache is implemented using two doubly linked lists and a hashtable:

1. **Frequency Doubly Linked List**: Groups items by access frequency
2. **Value Doubly Linked List** (per frequency): Maintains LRU order within each frequency
3. **Hashtable**: O(1) key lookup

```
┌─────────────────────────────────────────────────────────────┐
│                 Frequency Doubly Linked List                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │ freq=1   │◄──►│ freq=2   │◄──►│ freq=N   │           │
│  └──────────┘    └──────────┘    └──────────┘           │
│        │                                                    │
│        │ points to                                          │
│        ▼                                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Value Doubly Linked List (per frequency)       │ │
│  │  HEAD (MRU) ◄──────► ◄──────► ◄──────► TAIL (LRU)   │ │
│  │  [key_a]        [key_c]         [key_b]               │ │
│  │  Evicted last                              Evicted first│ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           ▼                                  │
│              ┌─────────────────────────────┐                │
│              │         Hashtable          │                │
│              │   key → ValueNode          │                │
│              │   O(1) lookup/insert/delete│                │
│              └─────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

- **O(1) Operations**: Insert, Get, Delete all run in constant time
- **LFU + LRU**: Least Frequently Used items are evicted; LRU breaks ties within same frequency
- **Drop-in Dict Replacement**: Same interface as Python dict

## Usage

### Starting the Server

```bash
python server.py
```
The server will start listening on `127.0.0.1:6379` with an LFU cache of capacity 100.

### Using the Client

```python
from client import Client

client = Client(host="127.0.0.1", port=6379)

# Basic Operations
client.set("name", "Alice")
print(client.get("name"))

# Bulk Operations
client.mset({"user:1": "John", "user:2": "Jane"})
print(client.mget(["user:1", "user:2"]))
```

## Benchmarks

### Network Optimization: MSET/MGET vs Individual Commands

MGET and MSET commands significantly reduce the network round-trip time compared to individual SET and GET commands.

| Operation Type | Time Taken (Seconds) | Speed/Operation |
|----------------|----------------------|-----------------|
| SET (Individual) | 0.2915 s | ~0.029 ms/op |
| GET (Individual) | 0.2802 s | ~0.028 ms/op |
| MSET (Dictionary) | 0.0491 s | Total Time |
| MSET (Args) | 0.0484 s | Total Time |
| MGET (List) | 0.0480 s | Total Time |
| MGET (Args) | 0.0473 s | Total Time |

**MSET is ~5.9x faster than individual SET operations.**
**MGET is ~5.8x faster than individual GET operations.**

### LFU Cache Performance

All operations run in O(1) time complexity.

| Operation | Performance |
|-----------|-------------|
| INSERT 10,000 items | 136.65ms (**73,179 ops/sec**) |
| GET 10,000 times (same key) | 4.08ms (**2,453,425 ops/sec**) |
| MIXED 10,000 operations | 6.16ms (**1,623,922 ops/sec**) |
| INSERT 10,000 (capacity=10,000) | 6.44ms |
| INSERT 10,000 with eviction (cap=100) | 21.00ms |

### Cache Hit Ratio

With capacity=100 and 1000 operations on 100 rotating keys:

| Metric | Value |
|--------|-------|
| Cache Hits | 900 |
| Cache Misses | 100 |
| Hit Ratio | **90%** |

## Testing

### Run All Tests

```bash
# Activate venv
source venv/bin/activate

# Run tests
pytest tests/test_lfu_cache.py -v
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Server                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Decoder   │───►│  Commands   │───►│   Encoder   │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                          │                                  │
│                          ▼                                  │
│                  ┌───────────────┐                        │
│                  │  LFUCache     │                        │
│                  │  (capacity=100)│                        │
│                  └───────┬───────┘                        │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │    RESP Protocol       │
              └─────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │     Client      │
                  └─────────────────┘
```
