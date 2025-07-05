import multiprocessing
import time
import os

def square(number):
    """A simple CPU-bound task."""
    pid = os.getpid()
    print(f"Process {pid}: Calculating square of {number}...")
    time.sleep(0.1) # Small delay to show concurrency
    return number * number

print("\n--- Multiprocessing Pool Example ---")
if __name__ == "__main__":
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    num_processes = 4 # Or multiprocessing.cpu_count()

    start_time = time.time()
    with multiprocessing.Pool(processes=num_processes) as pool:
        # map() blocks until all results are ready, preserving order
        results = pool.map(square, numbers)

    end_time = time.time()
    print(f"Results: {results}")
    print(f"Total time (multiprocessing pool): {end_time - start_time:.2f} seconds.")