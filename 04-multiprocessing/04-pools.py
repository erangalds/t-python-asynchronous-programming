import multiprocessing
import time
import os

def cpu_intensive_task(n):
    """A CPU-bound task that takes a single number as input."""
    # Note: We removed the 'name' argument for simplicity with pool.map
    print(f"Processing {n} in process {os.getpid()}...")
    result = 0
    for i in range(n):
        result += i * i
    return result

if __name__ == "__main__":
    print("\n--- Multiprocessing with Pool Example ---")
    # A list of different inputs to process
    tasks_to_run = [50_000_000, 50_000_001, 50_000_002, 50_000_003, 49_999_999]

    start_time = time.time()

    # The 'with' statement handles closing and joining the pool automatically.
    # By default, Pool() uses os.cpu_count() worker processes.
    # Let's make the number of processes explicit for clarity.
    # You can set it to a specific number or leave it to use the default.
    with multiprocessing.Pool(processes=os.cpu_count()) as pool:
        # pool.map is a blocking call. It distributes the tasks in tasks_to_run
        # to the worker processes and waits for all results to complete.
        results = pool.map(cpu_intensive_task, tasks_to_run)

    end_time = time.time()

    print(f"\nResults (not all shown): {results[:3]}...")
    print(f"Total time with Pool: {end_time - start_time:.2f} seconds")