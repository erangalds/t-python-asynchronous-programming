import threading
import time
import random

# This semaphore will allow up to 3 threads to access the resource pool at once.
semaphore = threading.Semaphore(3)

def access_resource(thread_id):
    """A function that simulates a thread accessing a limited resource."""
    print(f"Thread {thread_id}: Trying to acquire semaphore...")
    # The 'with' statement elegantly handles acquiring and releasing the semaphore.
    # The thread will wait here if all 3 "slots" of the semaphore are taken.
    with semaphore:
        print(f"Thread {thread_id}: Acquired semaphore. Accessing resource...")
        # Simulate doing work that uses the limited resource.
        work_time = random.uniform(1, 3)
        time.sleep(work_time)
        print(f"Thread {thread_id}: Finished work in {work_time:.2f}s.")
    # The semaphore is automatically released when the 'with' block is exited.
    print(f"Thread {thread_id}: Released semaphore.")

print("\n--- Threading with Semaphore Example ---")
threads = []
# We create 10 threads, all competing for the 3 available semaphore slots.
for i in range(10):
    thread = threading.Thread(target=access_resource, args=(i,))
    threads.append(thread)
    thread.start()
    # Staggering thread starts slightly to make the output easier to follow.
    time.sleep(0.1)

for thread in threads:
    thread.join()

print("\nAll threads have finished their work.")