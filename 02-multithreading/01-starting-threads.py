import threading
import time

def tasks(name, duration):
    """A function to be run by a thread"""
    print(f"Thread {name}: Starting Tasks....")
    time.sleep(duration) # Simulates I/O bound operation
    print(f"Thread {name}: Finished Task. Done!" )

print(f"--- Threading Basic Example ---")

# Create Thread objects
thread1 = threading.Thread(target=tasks, args=("Thread-1", 5))
thread2 = threading.Thread(target=tasks, args=("Thread-2", 10))

# Start the threads
start_time = time.time()
thread1.start()
thread2.start()

# The main program continues execution immediately
print(f"Main Thread: All threads launched. Doing other work...")

# Allowing some time for threads to start
time.sleep(1)
print(f"Main Thread: Still doing other work...")

end_time = time.time()

print(f"Main Thread: Program Finished in {end_time - start_time:.2f} seconds")
