# Mini-Redis

Mini-Redis is a lightweight, simplified implementation of a Redis-like in-memory key-value data store written in Python. It supports basic operations over a custom RESP (REdis Serialization Protocol) implementation.

## Features

- **In-Memory Store**: Fast key-value storage.
- **Custom RESP Implementation**: Includes Encoders and Decoders to serialize and deserialize data for client-server communication.
- **Bulk Operations**: Perform multiple get or set operations in a single network round-trip.

## Supported Commands

The following commands are currently implemented:
- `SET key value`: Sets the value of a key.
- `GET key`: Gets the value of a key.
- `DELETE key`: Deletes a key.
- `FLUSH`: Clears the entire database.
- `MSET key value [key value ...]`: Sets multiple keys to multiple values. Also accepts a dictionary in the Python client.
- `MGET key [key ...]`: Gets values for multiple keys. Also accepts a list in the Python client.

## Usage

### Starting the Server

To start the Mini-Redis server, run the `server.py` file:

```bash
python server.py
```
The server will start listening on `127.0.0.1:6379`.

### Using the Client

You can interact with the server using the provided `Client` class in Python:

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

MGET and MSET commands significantly reduce the network round-trip time and protocol overhead compared to individual SET and GET commands.

### Results

Testing with 10,000 operations yields the following performance metrics:

| Operation Type | Time Taken (Seconds) | Speed/Operation |
|----------------|----------------------|-----------------|
| SET (Individual) | 0.2915 s | ~0.029 ms/op |
| GET (Individual) | 0.2802 s | ~0.028 ms/op |
| MSET (Dictionary) | 0.0491 s | Total Time |
| MSET (Args) | 0.0484 s | Total Time |
| MGET (List) | 0.0480 s | Total Time |
| MGET (Args) | 0.0473 s | Total Time |

### Comparison summary

- **MSET** is approximately **5.9x faster** than individual SET operations.
- **MGET** is approximately **5.8x faster** than individual GET operations.
