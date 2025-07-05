from concurrent.futures import ProcessPoolExecutor, as_completed
import time 
import os

def heavy_calculation(n):
    """A CPU-bound task."""
    pid = os.getpid()
    print(f"Process {pid}: Starting heavy calculation for {n}...")
    result = sum(i * i for i in range(n))
    print(f"Process {pid}: Finished heavy calculation for {n}.")
    return result

print("\n--- ProcessPoolExecutor Example with map() ---")
if __name__ == "__main__": # Essential for multiprocessing
    numbers = [5_000_000, 7_000_000, 4_000_000, 6_000_000]
    num_processes = os.cpu_count() # Use number of CPU cores

    start_time = time.time()
    # Create a process pool
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        # map() is simple: it applies the function to each item, blocks until all are done,
        # and returns results in the same order as the input.
        results = list(executor.map(heavy_calculation, numbers))

    end_time = time.time()
    print(f"Calculation results: {results}")
    print(f"Total time with map(): {end_time - start_time:.2f} seconds.")

    print("\n\n--- ProcessPoolExecutor Example with submit() and as_completed() ---")
    start_time = time.time()
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        # submit() schedules a task and returns a Future object immediately.
        futures = {executor.submit(heavy_calculation, n): n for n in numbers}

        # as_completed() yields futures as they finish, allowing for immediate processing.
        for future in as_completed(futures):
            result = future.result()
            print(f"Result received (from as_completed) for input {futures[future]} is {result}")
    end_time = time.time()
    print(f"Total time with as_completed(): {end_time - start_time:.2f} seconds.")