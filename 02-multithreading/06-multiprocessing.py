import multiprocessing
import time

def cpu_bound_task(n):
    """A CPU-bound task that performs a heavy calculation."""
    result = 0
    for i in range(n):
        result += i * i
    return result

def run_sync(n):
    # Synchronous execution
    start_sync = time.time()
    cpu_bound_task(n)
    cpu_bound_task(n)
    end_sync = time.time()
    print(f"Synchronous execution time: {end_sync - start_sync:.2f} seconds")

def run_multiprocess(n):
    # Multiprocessing execution
    start_procs = time.time()
    # Use multiprocessing.Process instead of threading.Thread
    p1 = multiprocessing.Process(target=cpu_bound_task, args=(n,))
    p2 = multiprocessing.Process(target=cpu_bound_task, args=(n,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
    end_procs = time.time()
    print(f"Multiprocessing execution time (CPU-bound): {end_procs - start_procs:.2f} seconds")

if __name__ == "__main__":
    print("\n--- GIL Limitation Example (CPU-bound) ---")
    N = 50_000_000 # A large number for computation

    run_sync(N)
    run_multiprocess(N)

    # You'll notice that the multiprocessing time is now significantly faster
    # (ideally close to half the synchronous time on a 2+ core machine),
    # demonstrating that it bypasses the GIL for true parallelism.

