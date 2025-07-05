import multiprocessing
import time
import os
# You may need to install psutil: pip install psutil
import psutil

def cpu_intensive_task(name, n):
    """A CPU-bound task that performs a heavy calculation."""
    current_process = psutil.Process()
    print(f"Process {name} (PID: {os.getpid()}) starting...")
    result = 0
    for i in range(n):
        result += i * i
    print(f"Process {name}: Finished. Result (truncated): {str(result)[:10]}...")
    return result

print("\n--- Multiprocessing Basic Example ---")
# Show the total number of CPU cores on the host machine
print(f"Total CPU cores available: {psutil.cpu_count(logical=True)}")
N = 50_000_000 # A large number for computation

if __name__ == "__main__": # Essential for multiprocessing on Windows/macOS
    main_process = psutil.Process()
    print(f"Main process (PID: {main_process.pid}) is running.")

    # Synchronous execution (for comparison)
    print("\n--- Running tasks synchronously in the main process ---")
    start_sync = time.time()
    cpu_intensive_task("Sync-1", N)
    cpu_intensive_task("Sync-2", N)
    end_sync = time.time()
    print(f"Synchronous execution time: {end_sync - start_sync:.2f} seconds")

    # Multiprocessed execution
    print("\n--- Running tasks in parallel with multiprocessing ---")
    p1 = multiprocessing.Process(target=cpu_intensive_task, args=("Proc-1", N))
    p2 = multiprocessing.Process(target=cpu_intensive_task, args=("Proc-2", N))

    start_multi = time.time()
    p1.start()
    p2.start()

    p1.join()
    p2.join()
    end_multi = time.time()
    print(f"Multiprocessed execution time (CPU-bound): {end_multi - start_multi:.2f} seconds")

    # You should see a significant speedup for multiprocessing here compared to synchronous or multithreaded.
    # The time will be roughly half of the synchronous time on a multi-core machine.
