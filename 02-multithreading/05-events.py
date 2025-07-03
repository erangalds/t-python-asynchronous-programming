import threading
import time

# 1. Create the shared Event object.
#    Initially, its internal flag is False (it's "clear").
event = threading.Event()

def waiter_thread():
    print("Waiter: Waiting for event to be set...")
    # 3. The waiter thread calls event.wait(). Since the event is not set,
    #    this thread BLOCKS here. It pauses execution and waits.
    event.wait()
    # 6. Once the event is set by the setter, wait() unblocks,
    #    and this thread continues execution.
    print("Waiter: Event set! Continuing...")
    # 7. (Optional) The event is cleared, resetting its flag to False
    #    so it can be used again in the future.
    event.clear()

def setter_thread():
    print("Setter: Doing some work...")
    # 4. The setter thread does some "work" (simulated by sleeping for 2 seconds).
    time.sleep(2)
    print("Setter: Setting event!")
    # 5. The setter thread calls event.set(). This changes the internal
    #    flag to True and wakes up any threads waiting on the event.
    event.set()

print("\n--- Threading with Event Example ---")
# 2. Create and start both threads. They will run concurrently.
t1 = threading.Thread(target=waiter_thread)
t2 = threading.Thread(target=setter_thread)

t1.start()
t2.start()

# 8. The main thread waits for both t1 and t2 to finish their execution
#    before the program exits.
t1.join()
t2.join()
