import threading
import time

def cpu_bound_task(n):
    """A CPU-bound task that performs a heavy calculation."""
    result = 0
    for i in range(n):
        result += i * i
    return result

print("\n--- GIL Limitation Example (CPU-bound) ---")
N = 50_000_000 # A large number for computation

# Synchronous execution
start_sync = time.time()
cpu_bound_task(N)
cpu_bound_task(N)
end_sync = time.time()
print(f"Synchronous execution time: {end_sync - start_sync:.2f} seconds")

# Multithreaded execution
start_threads = time.time()
thread1 = threading.Thread(target=cpu_bound_task, args=(N,))
thread2 = threading.Thread(target=cpu_bound_task, args=(N,))

thread1.start()
thread2.start()

thread1.join()
thread2.join()
end_threads = time.time()
print(f"Multithreaded execution time (CPU-bound): {end_threads - start_threads:.2f} seconds")

# You'll notice that the multithreaded time is roughly the same as or slightly worse
# than the synchronous time, demonstrating the GIL's impact on CPU-bound tasks.

