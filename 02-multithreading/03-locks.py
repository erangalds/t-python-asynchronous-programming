import threading
import time

shared_counter = 0
lock = threading.Lock() # Create a Lock object

def increment_counter(iterations):
    global shared_counter
    for _ in range(iterations):
        # Acquire the lock before modifying the shared resource
        lock.acquire()
        try:
            current_value = shared_counter
            time.sleep(0.0001) # Simulate some work
            shared_counter = current_value + 1
        finally:
            # Release the lock when done, even if an error occurs
            lock.release()

print("\n--- Threading with Lock Example ---")
NUM_THREADS = 5
ITERATIONS_PER_THREAD = 10000

threads = []
for i in range(NUM_THREADS):
    thread = threading.Thread(target=increment_counter, args=(ITERATIONS_PER_THREAD,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print(f"Expected counter value: {NUM_THREADS * ITERATIONS_PER_THREAD}")
print(f"Actual counter value: {shared_counter}")
# Without a lock, 'Actual counter value' would often be less than 'Expected counter value'
# due to race conditions. With a lock, they should match.

# -----------------------------------------------------------------------------------

# We can implement the same logic using a context manager for the lock:
shared_counter = 0
lock = threading.Lock() # Create a Lock object)
def increment_counter_with_context_manager(iterations):
    global shared_counter
    for _ in range(iterations):
        # Acquire the lock before modifying the shared resource
        # The 'with' statement automatically acquires and releases the lock.
        with lock:
            current_value = shared_counter
            time.sleep(0.0001) # Simulate some work
            shared_counter = current_value + 1

print("\n--- Threading with Lock and Context Manager Example ---")
threads = []
for i in range(NUM_THREADS):
    thread = threading.Thread(target=increment_counter_with_context_manager, args=(ITERATIONS_PER_THREAD,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print(f"Expected counter value: {NUM_THREADS * ITERATIONS_PER_THREAD}")
print(f"Actual counter value: {shared_counter}")
# Again, without a lock, 'Actual counter value' would often be less than 'Expected