# Mutlithreading in Python (`threading` module) 

## How Threads Work

+ Threads are lighweight units of execution within the same process. 
+ They share the same memory space (variables, objects),which makes data sharing easy but also introduces challenges like race conditions. 
+ The operating system schedules threads to run
+ in Python (CPython), the GIL limits true parallelism for CPU-bound tasks, but it's effective for I/O-bound tasks. Because it releases the GIL during I/O tasks. 

## Creating and Starting Threads

Let me now show you how to use the python `threading` module to create and start threads.

Let's look at `01-starting-threads.py`

```python
import threading
import time

def tasks(name, duration):
    """A function to be run by a thread"""
    print(f"Thread {name}: Starting Tasks....")
    time.sleep(duration) # Simulates I/O bound operation
    print(f"Thread {name}: Finished Task. Done!" )

print(f"--- Threading Basic Example ---")

# Create Thread objects
thread1 = threading.Thread(target=tasks, args=("Thread-1", 2))
thread2 = threading.Thread(target=tasks, args=("Thread-2", 3))

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

print(f"Main Thread: Program Finished without completely finishing the threads in {end_time - start_time:.2f} seconds")

```

### How it works

1. **`tasks(name, duration)` function**: This is the function that will be executed by each of our threads. It takes a `name` and a `duration` as arguments. The `time.sleep(duration)` line is crucial; it simulates a task that waits for something, like a network request or reading a file. This is known as an **I/O-bound operation**, which is where threading in Python shines.
    
2. **Creating Threads**:
    
    `thread1 = threading.Thread(target=tasks, args=("Thread-1", 2)) thread2 = threading.Thread(target=tasks, args=("Thread-2", 3))`
    
    Here, two `Thread` objects are created.
    
    - `target=tasks`: This tells the thread which function to run.
    - `args=(...)`: This is a tuple of arguments to pass to the `target` function. `thread1` will call `tasks("Thread-1", 2)` and `thread2` will call `tasks("Thread-2", 3)`.
3. **Starting Threads**:
    
    `thread1.start() thread2.start()`
    
    The `.start()` method is what actually spawns a new thread and begins its execution. A key takeaway is that `.start()` is **non-blocking**. This means the main program does not wait for the thread to finish. It kicks off the thread and immediately continues to the next line of code.
    
4. **Main Thread Execution**:
    
    `print(f"Main Thread: All threads launched. Doing other work...") # ... print(f"Main Thread: Program Finished in {end_time - start_time:.2f} seconds")`
    
    After calling `.start()` on both threads, the main thread continues its own work. It prints some messages, sleeps for a second, and then calculates the time it took to run _its_ part of the script.
    
### What's Happening? (The "Aha!" Moment)

When you run this script, you'll notice something interesting in the output. The main thread will print that it finished in about **1.00 second**. However, you will see the output from `thread1` and `thread2` appearing _after_ that final message from the main thread.

- `Thread-1` will finish after 2 seconds.
- `Thread-2` will finish after 3 seconds.

This demonstrates that the main program and the two threads were all running concurrently. The main thread finished its work and printed its "done" message without waiting for the other threads to complete. The program as a whole only exits after the longest-running thread (`thread2`) is finished.

## Waiting for the Threads to finish before finishing the `main` program. 

The current script demonstrates how threads are launched, but it's not a robust pattern. In most real-world applications, you need the main thread to wait for the background threads to complete their work before the program moves on or exits.

This is done using the .join() method. Calling thread.join() will block the main thread's execution and force it to wait until that specific thread has finished.

Let's look at `02-waiting-for-threads-to-complete.py`

```python
import threading
import time

def tasks(name, duration):
    """A function to be run by a thread"""
    print(f"Thread {name}: Starting Tasks....")
    time.sleep(duration) # Simulates I/O bound operation
    print(f"Thread {name}: Finished Task. Done!" )

print(f"--- Threading Basic Example ---")

# Create Thread objects
thread1 = threading.Thread(target=tasks, args=("Thread-1", 2))
thread2 = threading.Thread(target=tasks, args=("Thread-2", 3))

# Start the threads
start_time = time.time()
thread1.start()
thread2.start()

# The main program continues execution immediately
print(f"Main Thread: All threads launched. Doing other work...")

# Allowing some time for threads to start
time.sleep(1)
print(f"Main Thread: Still doing other work...")

start_to_join = time.time()
thread1.join()
thread2.join()
end_time = time.time()

print(f"Main Thread: Main Program Finished in {start_to_join - start_time:.2f} seconds")
print(f"Main Thread: All threads finished in {end_time - start_time:.2f} seconds")
```

### How it works

1. `.join()`: calling this method will start to block the main thread's execution and force it to wait until that specific thread has finished. Therefore once the the main threads work is done, we can force the main thread to wait for the other threads to finish before exiting. `thread1.join()` and `thread2.join()` does that. 

2. Re-calculate the timings: `start_to_join - start_time:.2f` is the time taken by the main thread to complete its work. `end_time - start_time:.2f` is the time taken to complete the complete program (including both threads).


## Thread Synchronization (Locks, Semaphores, Events, Conditions)

Sometimes, when multiple threads try to access shared resources (like a global variable, or a file), you need to synchronization mechanisms to prevent conflicts. We call these conflicts as *race conditions*. What it means is "situations where the final outcome depends on the unpredictable timing of multiple threads.". 

### Locks

A lock is the synchronization primitive. It's used to protest a critical section of the code. This ensures that only one thread can access the critical section at a time and execute it. 

Let me now show you an example. Let's look at `03-locks.py`

```python
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
```

#### How it works

##### The Problem: What is a Race Condition?

Imagine two threads trying to update a shared counter. The operation `counter = counter + 1` seems simple, but for the computer, it's three distinct steps:

1. Read the current value of `counter`.
2. Add 1 to that value in a temporary location.
3. Write the new value back to `counter`.

A race condition occurs when the timing of threads causes an incorrect result. For example:

- `shared_counter` is `50`.
- **Thread A** reads `50`.
- The OS switches to **Thread B**.
- **Thread B** reads `50`.
- **Thread B** calculates `51` and writes it back. `shared_counter` is now `51`.
- The OS switches back to **Thread A**.
- **Thread A**, which had already read `50`, calculates `51` and writes it back. `shared_counter` is _still_ `51`.

We've lost an increment! The final value should be `52`, but it's `51`. When you run this thousands of times, the final count will be unpredictably less than the expected total.

##### The Solution: `threading.Lock`

The script uses a `threading.Lock` to solve this problem. A lock is a synchronization mechanism that acts like a key to a restricted area (a "critical section" of code). Only one thread can "hold" the lock at any given time.

Let's break down the code.

1. **`shared_counter = 0` and `lock = threading.Lock()`**:
    
    - We define the shared resource (`shared_counter`) that multiple threads will try to modify.
    - We create a single `Lock` object that will be used by all threads to coordinate access to the counter.
2. **`increment_counter(iterations)` function**:
    
    - This is the function each thread will run.
    - `lock.acquire()`: This is the crucial first step. A thread will attempt to acquire the lock. If the lock is available, the thread "takes" it and continues. If another thread already holds the lock, this thread will **wait (block)** until the lock is released.
    - `try...finally`: This is a very important and robust pattern. The code that modifies the shared resource (the _critical section_) is placed inside the `try` block. The `lock.release()` is placed in the `finally` block. This **guarantees** that the lock is released, even if an error occurs within the `try` block. If you didn't do this, a thread could crash and hold the lock forever, preventing any other threads from ever acquiring it (a situation called deadlock).
    - `lock.release()`: The thread releases the lock, allowing one of the waiting threads (if any) to acquire it and enter the critical section.
3. **Main Execution Block**:
    
    - The script creates 5 threads, each tasked with incrementing the counter 100,000 times.
    - It starts all the threads.
    - `thread.join()`: The main thread waits for all the worker threads to complete their execution.
    - Finally, it prints the expected value (`5 * 100000 = 500000`) and the actual final value of `shared_counter`.

4. **Using the `with` Context Manager:

    - Instead of specifically saying `threading.Lock.acquire()` and `threading.Lock.release()` we can implemenent the same logic using a context manager for the lock
    - You can see that I used the `with lock:` and then started the section of the critical code which automatically acquires the lock, and when the `with` section ends it automatically releases the lock. 


**How the thread joining loop works**:

1. **Start of the Loop**: The `for` loop begins. It takes the first thread object from the `threads` list (let's call it `thread_0`).
2. **`thread_0.join()`**: The main thread calls `.join()` on `thread_0`. This call **blocks** the main thread. It essentially says, "I will pause my own execution right here and wait until `thread_0` has finished its task."
    - _Crucially_, while the main thread is waiting for `thread_0`, the other threads (`thread_1`, `thread_2`, etc.) are still running in the background, doing their work and competing for the lock. The `join()` call only affects the main thread.
3. **`thread_0` Finishes**: Once `thread_0` completes its `increment_counter` function, the `thread_0.join()` call returns, and the main thread is "unblocked."
4. **Next Iteration**: The `for` loop proceeds to the next item in the list, `thread_1`.
5. **`thread_1.join()`**: The main thread now calls `.join()` on `thread_1`.
    - If `thread_1` has already finished its work (which is possible, as it was running concurrently), the `.join()` call will return immediately.
    - If `thread_1` is still running, the main thread will wait again until it's done.
6. **Repeat**: This process repeats for every thread in the `threads` list. The main thread calls `join()` and waits for each thread, one by one, in the order they appear in the list.
7. **Loop Ends**: Only after the main thread has successfully "joined" with every single worker thread does the loop finish.
8. **Program Continues**: The program then proceeds to the final `print()` statements, confident that all the counting work has been completed.

Because the lock ensures that only one thread can modify the counter at a time, no increments are lost, and the "Actual" value will correctly match the "Expected" value.

### Semaphores (`threading.Semaphore`)

This take the lock to another level. A semaphore is a more generalized lock that can be acquired by a limited number of threads concurrently. It's often used to limit access to a resource. 

#### The Concept: What is a Semaphore?

I just introduced the cocept of *lock* earlier. The *locks* can be taken by only one thread at a time. Only one thread can hold the lock and be 'inside' that *critical section* of the code. 

A `semaphore` is a more generalized version of this. This is a security guard in a bank, who helps to coordinate customers in a brank which has a fixed number of teller agents (let's say 3). So the security guard will take three customers from the queue and allocate them to the three teller agents. Whenever one teller agent gets free, he will allocate a new customer to him from the queue. 

+ The `semaphore` (security guard) starts with a counter of 3. 
+ When a thread (a customer) wants to enter the *critical section of the code* (go to a tellar agent) it asks the `semaphore`. If the counter is greater than zero, the `semaphore` lets the thread in and decrements the counter. 
+ If the counter is zero, all the tellar agents are fully occupied. The thread must wait outside in a queue untill a customer who was with a tellar agent leaves.
+ When a thread finishes its work and leaves the *critical section*, it signals the `semaphore` which increments the counter, allowing one of the waiting threads to enter.  


Let me now show you an example. Let's look at `04-semaphores.py`

```python
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
```

#### How it works

1. **`semaphore = threading.Semaphore(3)`**: We initialize our semaphore with a counter of `3`. This means a maximum of 3 threads can be "inside" the critical section at once.
2. **`with semaphore:`**: This is the modern, idiomatic way to use a semaphore. It's a context manager that automatically calls `semaphore.acquire()` when the block is entered and `semaphore.release()` when it's exited (even if an error occurs).
    - **`acquire()`**: If the internal counter is greater than 0, the thread proceeds and the counter is decremented. If the counter is 0, the thread **blocks** (waits) at this line until another thread calls `release()`.
    - **`release()`**: Increments the internal counter, which may unblock a waiting thread.
3. **Execution Flow**: When you run this, you'll see the first 3 threads immediately acquire the semaphore. The other 7 will print "Trying to acquire..." and then wait. As soon as one of the first three finishes its work and releases the semaphore, one of the waiting threads will instantly acquire it and proceed. This continues until all 10 threads have completed, but never with more than 3 working concurrently inside the `with` block.

### Events (`threading.Event`)

#### What is `threading.Event`?

An *event* is a simple signaling mechanism. One thread signals an event, and other threads waits for it. 

This of a `treading.Event` as a simple signaling mechanism, like a flag or a traffic light that threads can watch. It can be one of two states. 

+ **Clear (or unset)**: The default state. It's like a red light.
+ **Set*: It's like a green light.

Let me now show you an example. Let's look at `05-events.py`

```python
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
```

#### How it works

1. An `Event` object is created in its default "clear" state.
2. `t1` (`waiter_thread`) and `t2` (`setter_thread`) are started and begin running at roughly the same time.
3. The `waiter_thread` immediately prints its "Waiting..." message and then calls `event.wait()`. Because the event is "clear", the `waiter_thread` stops right there and waits.
4. Meanwhile, the `setter_thread` prints its "Doing some work..." message and sleeps for 2 seconds. The `waiter_thread` is still patiently waiting during this time.
5. After 2 seconds, the `setter_thread` wakes up, prints "Setting event!", and calls `event.set()`.
6. The moment `event.set()` is called, the `Event` object's state changes to "set". This immediately unblocks the `waiter_thread`.
7. The `waiter_thread` resumes execution, prints its "Event set! Continuing..." message, and then finishes.
8. The main thread, which was waiting on the `.join()` calls, sees that both threads have completed, and the program exits.

In short, `threading.Event` is a perfect tool for situations where one thread needs to wait for another thread to complete a specific task or reach a certain state before it can proceed.

## Limitations due to the GIL

The Global Interpreter Lock (GIL) prevents true parallelism for CPU-bound tasks. Let us look at an example. Let's look at `06-gil-impact-cpu-bound-tasks.py`


```python 
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
```

### How it works

1. **`cpu_bound_task()`** function is designed to be a 'pure' CPU-bound task. It does nothing but arithmatic calculations in a loop. It doesn't wait for network requests, read from a disk or pause for user input etc. Its execution time is directly proportioned to how fast the CPU can perform the calculation. 

2. **Synchronous Execution**: Then we call the function twice, with `N=50_000_000` then calculates the total time taken to finish both function calls. The total time is equal to the time taken to finish the first function call and the time taken to finish the second function call. Because they run sequentially on a single CPU core. 

3. **Multithreaded Execution**: We create two threads, with `N=50_000_000` each. Then we start the threads and expect them to finish faster than the synchronous execution. Because we assume then they are started almost at the same time, the threads will run in parallel. But when we see the actual time, we see that, there isn't much difference. 

### Why isn't it faster?

When you run the script, you'll see that the multithreaded execution time is almost identical to, or even slightly _longer_ than, the synchronous time.

This is the **Global Interpreter Lock (GIL)** in action.

As I explained earlier, the GIL is a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecode at the same time within a single process.

- **No True Parallelism:** Even though you have two threads and (likely) multiple CPU cores, the GIL ensures that only **one** of those threads can be executing Python code at any given moment.
- **Taking Turns:** The threads are forced to take turns using the CPU. Thread 1 runs for a short while, then the Python interpreter forces it to release the GIL. Then Thread 2 gets the GIL and runs for a bit, and so on. They are running concurrently (making progress in overlapping time), but not in parallel (executing at the exact same instant).
- **Overhead:** The process of switching between threads (context switching) and managing the GIL adds a small amount of overhead. This is why the multithreaded version can sometimes be slightly slower.

Therefore for CPU-bound tasks, multithreading in Python is not the solution for performance. The real solution for CPU-bound parallelism is using the `multiprocessing` module, which bypasses the GIL by giving each task its own separate process and its own Python interpreter.

Let me show you the same example using `multiprocessing`. Let's look at `07-multiprocessing.py`. 

```python
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
```

### How it works

#### Key Changes and "Why"

1. **`import multiprocessing`**: We import the `multiprocessing` library instead of `threading`.
2. **`multiprocessing.Process`**: We create `Process` objects instead of `Thread` objects. The arguments (`target`, `args`) are identical.
3. **`if __name__ == "__main__":`**: This is **essential** for `multiprocessing`. When a new process is spawned, it re-imports the script. This guard ensures that the process-creation code only runs in the main script, not in the spawned child processes, preventing an infinite loop of process creation.

By making this simple change, you effectively sidestep the GIL and unlock the full power of your machine's multiple cores for heavy computational work.

#### NOTE:

1. What is `__name__ == "__main__"` in python?

    Every python script has a special built-in variable called `__name__`. Its value depends on how the script is being used. 
    
    + When you run the script directly (e.g. python my_script.py), the python intepreter sets `__name__` to `__main__`.
    + When you import the script as a module into another script (e.g. `import my_script`), the interpreter sets `__name__` to the module's name `my_script`.

    Therefore `if __name__ == "__main__" block is a standard python idiom that creates a section of code that will only run when the script is executed directly.

2. How `multiprocessing` spawns new processes?

    Unlike threads, which live inside the same process, `multiprocessing` creates entirely new, independent processes. This means on the operating systems like windows, and macOS (by default), a new process is created by:

    + lanuching a fresh python interpreter.
    + This new interpreter `imports` our script file to get the code it needs to run (like the `target` function).

3. Putting it all together: The problem.

If we had the code as below. 

```python
# DANGEROUS - DO NOT RUN
import multiprocessing
import os

def worker():
    print(f"I am a worker process with PID: {os.getpid()}")

# This code is NOT protected by the guard
print(f"Starting script with PID: {os.getpid()}")
p = multiprocessing.Process(target=worker)
p.start()
p.join()
```

Here is the disastrous sequence of events:

1. **Main Script Runs**: You execute the script. Its `__name__` is `"__main__"`. It prints its PID and creates a new child process (`p`).
2. **Child Process Spawns**: The `multiprocessing` library starts a new Python interpreter for the child process.
3. **Child Process Imports Script**: To get the `worker` function, the child process imports your script file.
4. **Infinite Loop**: As the child process executes the imported script from top to bottom, it reaches the line `p = multiprocessing.Process(...)` and `p.start()`. It will then try to spawn _its own_ child process.
5. **Crash**: This new child will also import the script and spawn another child, and so on. You get an infinite recursion of process creation that will quickly consume all your system's memory and crash.

**The Solution**: The `if __name__ == "__main__"` Guard

By placing the process-starting code inside the guard, you break this cycle.


## When to use Threads?

So, from all that I learnt is that we can use threads for:
+ I/O-Bound Tasks: When our program spends a lot of time waiting for external resources (network, disk, user input)
    + Downloaing multiple files concurrently. 
    + Making multiple API calls.
    + Reading / Writing large files
+ Simple background tasks: Running a short, infrequent task in the background without blocking the main UI / Process. 
+ When data sharing is simple: If threads need to share a lot of mutable data, careful synchronization is required, which can make code complex and error-prone. 

