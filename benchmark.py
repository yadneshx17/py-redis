import sys
import threading
import time
from time import perf_counter

from client import Client
from server import Server


def run_server():
    server = Server()
    server.start()


# Start server in background thread
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
time.sleep(1)  # wait for server to bind

client = Client()

N = 10000

print(f"\n{'=' * 40}")
print(f"BENCHMARKING MINI-REDIS ({N} iterations)")
print(f"{'=' * 40}\n")

# Single SET
start = perf_counter()
for i in range(N):
    client.set(f"k{i}", f"v{i}")
end = perf_counter()
set_time = end - start
print(
    f"SET {N} items individually:    {set_time:.4f} seconds ({set_time / N * 1000:.3f} ms/op)"
)

# Single GET
start = perf_counter()
for i in range(N):
    client.get(f"k{i}")
end = perf_counter()
get_time = end - start
print(
    f"GET {N} items individually:    {get_time:.4f} seconds ({get_time / N * 1000:.3f} ms/op)"
)

# MSET using a dictionary
mset_data = {f"mk{i}": f"mv{i}" for i in range(N)}
start = perf_counter()
client.mset(mset_data)
end = perf_counter()
mset_dict_time = end - start
print(
    f"MSET {N} items (dict arg):      {mset_dict_time:.4f} seconds ({(mset_dict_time):.3f}s total)"
)

# MSET using positional arguments
mset_args = []
for k, v in mset_data.items():
    mset_args.extend([k, v])
start = perf_counter()
client.mset(*mset_args)
end = perf_counter()
mset_args_time = end - start
print(
    f"MSET {N} items (pos args):      {mset_args_time:.4f} seconds ({(mset_args_time):.3f}s total)"
)

# MGET using a list
mget_keys = list(mset_data.keys())
start = perf_counter()
client.mget(mget_keys)
end = perf_counter()
mget_list_time = end - start
print(
    f"MGET {N} items (list arg):      {mget_list_time:.4f} seconds ({(mget_list_time):.3f}s total)"
)

# MGET using positional arguments
start = perf_counter()
client.mget(*mget_keys)
end = perf_counter()
mget_args_time = end - start
print(
    f"MGET {N} items (pos args):      {mget_args_time:.4f} seconds ({(mget_args_time):.3f}s total)"
)

print(f"\n{'=' * 40}")
print("BENCHMARK COMPARISON")
print(f"{'=' * 40}")
print(f"MSET (dict) is {set_time / mset_dict_time:.1f}x faster than individual SETs")
print(f"MGET (list) is {get_time / mget_list_time:.1f}x faster than individual GETs")

sys.exit(0)
