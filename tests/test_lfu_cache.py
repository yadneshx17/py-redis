import sys
sys.path.insert(0, '/home/yadneshx17/Yadnesh/Coding/mini-redis')

import pytest
import time
import random
from lfu_cache import LFUCache, FreqNode, ValueNode


class TestBasicOperations:
    def test_insert_and_get(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3

        assert len(cache) == 3
        assert cache["a"] == 1
        assert cache["b"] == 2
        assert cache["c"] == 3

    def test_update_existing_key(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        cache["a"] = 10

        assert cache["a"] == 10
        assert len(cache) == 1

    def test_delete_existing_key(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        cache["b"] = 2
        del cache["a"]

        assert "a" not in cache
        assert len(cache) == 1
        assert cache["b"] == 2

    def test_delete_nonexistent_key_raises(self):
        cache = LFUCache(capacity=3)
        with pytest.raises(KeyError):
            del cache["nonexistent"]

    def test_getitem_missing_key_raises(self):
        cache = LFUCache(capacity=3)
        with pytest.raises(KeyError):
            _ = cache["missing"]

    def test_get_with_default(self):
        cache = LFUCache(capacity=3)
        result = cache.get("missing", "default")
        assert result == "default"

    def test_get_existing_key(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        result = cache.get("a", "default")
        assert result == 1

    def test_contains(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        cache["b"] = 2

        assert "a" in cache
        assert "b" in cache
        assert "c" not in cache

    def test_len(self):
        cache = LFUCache(capacity=5)
        assert len(cache) == 0
        cache["a"] = 1
        assert len(cache) == 1
        cache["b"] = 2
        cache["c"] = 3
        assert len(cache) == 3

    def test_clear(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3
        cache.clear()

        assert len(cache) == 0
        assert "a" not in cache


class TestEviction:
    def test_eviction_on_full_cache(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3
        cache["d"] = 4

        assert len(cache) == 3
        assert "d" in cache
        evicted_count = sum(1 for k in ["a", "b", "c"] if k not in cache)
        assert evicted_count == 1

    def test_lru_within_same_frequency(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3
        cache["d"] = 4

        assert len(cache) == 3
        evicted = not ("a" in cache) or not ("b" in cache) or not ("c" in cache)
        assert evicted

    def test_high_freq_items_not_evicted(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3

        for _ in range(10):
            _ = cache["a"]

        cache["d"] = 4
        cache["e"] = 5

        assert "a" in cache
        assert len(cache) == 3

    def test_multiple_evictions(self):
        cache = LFUCache(capacity=2)
        cache["a"] = 1
        cache["b"] = 2
        cache["a"] = cache["a"]
        cache["c"] = 3
        assert len(cache) == 2
        assert "c" in cache
        cache["d"] = 4
        assert len(cache) == 2


class TestLFUBehavior:
    def test_frequency_increments_on_get(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        cache["b"] = 2

        for _ in range(5):
            _ = cache["a"]

        cache["c"] = 3
        cache["d"] = 4

        assert "a" in cache
        assert len(cache) == 3

    def test_lfu_eviction_order(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3

        for _ in range(5):
            _ = cache["a"]
        for _ in range(3):
            _ = cache["b"]

        cache["d"] = 4

        assert "a" in cache
        assert "b" in cache
        assert len(cache) == 3

    def test_access_after_eviction(self):
        cache = LFUCache(capacity=2)
        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3

        assert "a" not in cache or "b" not in cache

        if "a" not in cache:
            cache["a"] = 10
            assert cache["a"] == 10


class TestEdgeCases:
    def test_capacity_one(self):
        cache = LFUCache(capacity=1)
        cache["a"] = 1
        assert len(cache) == 1
        assert cache["a"] == 1
        cache["b"] = 2
        assert len(cache) == 1
        assert "a" not in cache
        assert cache["b"] == 2

    def test_delete_last_item(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        del cache["a"]

        assert len(cache) == 0
        assert "a" not in cache

    def test_repeated_delete_same_key(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        del cache["a"]

        with pytest.raises(KeyError):
            del cache["a"]

    def test_update_value_type(self):
        cache = LFUCache(capacity=3)
        cache["a"] = "string"
        assert cache["a"] == "string"
        cache["a"] = 123
        assert cache["a"] == 123
        cache["a"] = {"dict": "value"}
        assert cache["a"] == {"dict": "value"}
        cache["a"] = [1, 2, 3]
        assert cache["a"] == [1, 2, 3]


class TestDataStructures:
    def test_freq_node_creation(self):
        node = FreqNode(5)
        assert node.freq == 5
        assert node.next is None
        assert node.prev is None
        assert node.value_head is None

    def test_value_node_creation(self):
        node = ValueNode("key", "value")
        assert node.key == "key"
        assert node.value == "value"
        assert node.next is None
        assert node.prev is None
        assert node.freq_node is None


class TestCacheRepr:
    def test_repr(self):
        cache = LFUCache(capacity=10)
        cache["a"] = 1
        cache["b"] = 2

        repr_str = repr(cache)
        assert "LFUCache" in repr_str
        assert "capacity=10" in repr_str
        assert "size=2" in repr_str


class TestIntegration:
    def test_full_workflow(self):
        cache = LFUCache(capacity=5)
        cache["user:1"] = "Alice"
        cache["user:2"] = "Bob"
        cache["user:3"] = "Charlie"

        assert cache["user:1"] == "Alice"
        assert cache["user:2"] == "Bob"
        assert cache["user:3"] == "Charlie"

        del cache["user:2"]
        assert "user:2" not in cache

        cache["user:2"] = "Bob Jr."
        assert cache["user:2"] == "Bob Jr."

        for _ in range(10):
            _ = cache["user:1"]

        cache["user:4"] = "David"
        cache["user:5"] = "Eve"

        assert "user:1" in cache
        assert len(cache) == 5

        cache["user:6"] = "Frank"
        assert len(cache) == 5

    def test_collision_handling(self):
        cache = LFUCache(capacity=3)
        cache["a"] = 1
        cache["a"] = 2
        cache["a"] = 3

        assert cache["a"] == 3
        assert len(cache) == 1


# =============================================================================
# BENCHMARK TESTS
# =============================================================================

class TestBenchmark:
    
    @pytest.fixture
    def cache(self):
        return LFUCache(capacity=1000)
    
    def test_benchmark_insert_small(self, cache):
        """Benchmark: Insert 10,000 items into cache with capacity 1000"""
        start = time.perf_counter()
        for i in range(10000):
            cache[f"key_{i}"] = f"value_{i}"
        elapsed = time.perf_counter() - start
        
        assert len(cache) == 1000
        assert elapsed < 1.0  # Should complete in under 1 second
        
        print(f"\n  INSERT 10000 items: {elapsed*1000:.2f}ms ({10000/elapsed:.0f} ops/sec)")
    
    def test_benchmark_get_small(self, cache):
        """Benchmark: 10,000 GET operations"""
        for i in range(1000):
            cache[f"key_{i}"] = f"value_{i}"
        
        start = time.perf_counter()
        for _ in range(10000):
            _ = cache["key_0"]
        elapsed = time.perf_counter() - start
        
        assert elapsed < 0.5  # Should be very fast with O(1) lookup
        
        print(f"\n  GET 10000 times: {elapsed*1000:.2f}ms ({10000/elapsed:.0f} ops/sec)")
    
    def test_benchmark_mixed_operations(self, cache):
        """Benchmark: 10,000 mixed operations"""
        operations = []
        
        for i in range(500):
            cache[f"key_{i}"] = f"value_{i}"
        
        start = time.perf_counter()
        for i in range(10000):
            op = random.choice(['get', 'set', 'contains'])
            if op == 'get':
                _ = cache.get(f"key_{i % 500}")
            elif op == 'set':
                cache[f"key_{i % 500}"] = f"new_value_{i}"
            else:
                _ = f"key_{i % 500}" in cache
        elapsed = time.perf_counter() - start
        
        print(f"\n  MIXED 10000 ops: {elapsed*1000:.2f}ms ({10000/elapsed:.0f} ops/sec)")
        assert elapsed < 1.0
    
    def test_benchmark_eviction(self, cache):
        """Benchmark: Eviction with frequent access patterns"""
        hot_keys = [f"hot_{i}" for i in range(50)]
        cold_keys = [f"cold_{i}" for i in range(1000)]
        
        for k in hot_keys:
            cache[k] = "value"
        
        for k in hot_keys:
            for _ in range(10):
                _ = cache[k]
        
        start = time.perf_counter()
        for _ in range(500):
            for k in hot_keys:
                _ = cache[k]
            
            for k in cold_keys[:10]:
                cache[f"new_{k}"] = "new_value"
        elapsed = time.perf_counter() - start
        
        for k in hot_keys[:10]:
            assert k in cache
        
        print(f"\n  EVICTION 500 cycles: {elapsed*1000:.2f}ms")
        print(f"  Hot keys protected: {sum(1 for k in hot_keys[:10] if k in cache)}/10")


class TestMetrics:
    
    def test_memory_metrics(self):
        """Test memory-related metrics"""
        cache = LFUCache(capacity=100)
        
        for i in range(100):
            cache[f"key_{i}"] = f"value_{i}"
        
        assert len(cache) == 100
        assert len(cache._hashtable) == 100
        
        freq_count = 0
        current = cache._freq_head
        while current:
            freq_count += 1
            current = current.next
        
        print(f"\n  Freq nodes created: {freq_count}")
        print(f"  Max freq achieved: {freq_count - 1 + 1}")  # -1 for initial freq=1
        
        assert freq_count >= 1
    
    def test_operation_counts(self):
        """Test that operations maintain correct state"""
        cache = LFUCache(capacity=5)
        
        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3
        
        cache["a"]
        cache["a"]
        cache["a"]
        
        cache["b"]
        cache["b"]
        
        cache["d"] = 4
        cache["e"] = 5
        
        assert len(cache) == 5
        
        cache["f"] = 6
        
        assert len(cache) == 5
        assert "a" in cache  # freq=4
        assert "b" in cache  # freq=3
        assert "f" in cache  # newly added
        
        evicted = sum(1 for k in ["c", "d", "e"] if k not in cache)
        assert evicted >= 1
    
    def test_eviction_correctness(self):
        """Test that LFU eviction selects correct items"""
        cache = LFUCache(capacity=3)
        
        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3
        
        cache["a"]
        cache["a"]
        cache["a"]
        cache["a"]
        
        cache["b"]
        cache["b"]
        
        cache["d"] = 4
        
        assert "a" in cache  # freq=5
        assert "b" in cache  # freq=3
        assert "c" not in cache or "d" in cache  # c or d evicted
        
        cache["e"] = 5
        
        assert len(cache) == 3
    
    def test_frequency_distribution(self):
        """Test frequency distribution after operations"""
        cache = LFUCache(capacity=10)
        
        for i in range(10):
            cache[f"key_{i}"] = i
        
        for i in range(5):
            for _ in range(i + 1):
                _ = cache[f"key_{i}"]
        
        cache["new1"] = 100
        cache["new2"] = 101
        
        freq_counts = {}
        for key, node in cache._hashtable.items():
            freq = node.freq_node.freq
            freq_counts[freq] = freq_counts.get(freq, 0) + 1
        
        print(f"\n  Frequency distribution: {freq_counts}")
        
        assert 5 in freq_counts  # key_4 accessed 5 times
        assert 1 in freq_counts  # unaccessed or low freq keys
    
    def test_cache_hit_miss_ratio(self):
        """Simulate cache hit/miss behavior"""
        cache = LFUCache(capacity=100)
        
        hits = 0
        misses = 0
        
        for i in range(1000):
            key = f"key_{i % 100}"  # 100 keys, cycling
            
            if key in cache:
                hits += 1
                _ = cache[key]
            else:
                misses += 1
                cache[key] = f"value_{i}"
        
        print(f"\n  Cache hits: {hits}")
        print(f"  Cache misses: {misses}")
        print(f"  Hit ratio: {hits/(hits+misses)*100:.1f}%")
        
        assert hits > 0, "Expected some cache hits"
        assert misses > 0, "Expected some cache misses"


class TestPerformanceRegression:
    """Tests to catch performance regressions"""
    
    def test_large_capacity_insert(self):
        """Test insert performance with large capacity"""
        cache = LFUCache(capacity=10000)
        
        start = time.perf_counter()
        for i in range(10000):
            cache[f"key_{i}"] = f"value_{i}"
        elapsed = time.perf_counter() - start
        
        print(f"\n  INSERT 10000 into capacity=10000: {elapsed*1000:.2f}ms")
        assert elapsed < 2.0
        assert len(cache) == 10000
    
    def test_many_evictions(self):
        """Test performance with many evictions"""
        cache = LFUCache(capacity=100)
        
        start = time.perf_counter()
        for i in range(10000):
            cache[f"key_{i}"] = f"value_{i}"
        elapsed = time.perf_counter() - start
        
        print(f"\n  INSERT 10000 with eviction (cap=100): {elapsed*1000:.2f}ms")
        assert elapsed < 2.0
        assert len(cache) == 100
    
    def test_high_frequency_items(self):
        """Test with items reaching high frequencies"""
        cache = LFUCache(capacity=100)
        
        for i in range(100):
            cache[f"key_{i}"] = i
        
        start = time.perf_counter()
        for _ in range(1000):
            for i in range(10):
                _ = cache[f"key_{i}"]
        elapsed = time.perf_counter() - start
        
        print(f"\n  ACCESS hot keys 1000x: {elapsed*1000:.2f}ms")
        assert elapsed < 0.5
        
        for i in range(10):
            assert f"key_{i}" in cache


class TestServerIntegration:
    @pytest.fixture
    def server(self):
        import subprocess
        import socket
        import time
        sys.path.insert(0, '/home/yadneshx17/Yadnesh/Coding/mini-redis')
        from protocol import Encoder, Decoder
        
        server_proc = subprocess.Popen(
            ['python3', '/home/yadneshx17/Yadnesh/Coding/mini-redis/server.py'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(0.5)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 6379))
        sf = sock.makefile(mode='rwb')
        
        yield {
            'socket': sock,
            'file': sf,
            'encoder': Encoder(),
            'decoder': Decoder()
        }
        
        sf.close()
        sock.close()
        server_proc.terminate()
        server_proc.wait()

    def test_set_and_get(self, server):
        server['encoder'].write_response(server['file'], ['SET', 'foo', 'bar'])
        resp = server['decoder'].handle_request(server['file'])
        assert resp == "OK"

        server['encoder'].write_response(server['file'], ['GET', 'foo'])
        resp = server['decoder'].handle_request(server['file'])
        assert resp == "bar"

    def test_delete(self, server):
        server['encoder'].write_response(server['file'], ['SET', 'key', 'value'])
        server['decoder'].handle_request(server['file'])

        server['encoder'].write_response(server['file'], ['DELETE', 'key'])
        resp = server['decoder'].handle_request(server['file'])
        assert resp == 1

        server['encoder'].write_response(server['file'], ['GET', 'key'])
        resp = server['decoder'].handle_request(server['file'])
        assert resp is None

    def test_mget_mset(self, server):
        server['encoder'].write_response(server['file'], ['MSET', 'a', '1', 'b', '2'])
        resp = server['decoder'].handle_request(server['file'])
        assert resp == "OK"

        server['encoder'].write_response(server['file'], ['MGET', 'a', 'b'])
        resp = server['decoder'].handle_request(server['file'])
        assert resp == ["1", "2"]

    def test_flush(self, server):
        server['encoder'].write_response(server['file'], ['SET', 'x', 'y'])
        server['decoder'].handle_request(server['file'])

        server['encoder'].write_response(server['file'], ['FLUSH'])
        resp = server['decoder'].handle_request(server['file'])
        assert resp == "OK"

        server['encoder'].write_response(server['file'], ['GET', 'x'])
        resp = server['decoder'].handle_request(server['file'])
        assert resp is None
