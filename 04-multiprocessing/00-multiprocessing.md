# Multiprocessing in Python

I briefly showed you, how to use this python's `multiprocessing` library in an earlier example. But here, I'm going to share a bit more about it. The `multiprocessing` module allows you to create separate `processes`, each with its own Python interpreter and memory space. This is the best way to achieve parallelism in Python. This will help to effectively bypass the GIL.

## How Processes work (Bypassing GIL)

Well now, let me explain you how this helps us. 

- Each process runs independently. 
- Each process has its own GIL. This means different processes can execute python *bytecode* on different CPU cores simultaneously. This helps. 
- But now, data sharing between processes is more complex than with threads (e.g., we have use pipes, queues, shared memory). 

## Creating and Starting Processes

Let's get into business. Let me show you how to create and start a new process. 

```python
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
```

ts main purpose is to give you a clear, practical demonstration of why Python's `multiprocessing` module is so powerful for CPU-intensive work. It does this by running the same heavy task in two different ways and comparing the execution time:

1. **Synchronously:** One task runs after the other, in the same single process.
2. **In Parallel:** Both tasks run at the same time, each in its own separate process on a different CPU core (if available).

### Code Breakdown

Let's walk through the script step-by-step.

1. **Imports and Setup**

    - **Imports:** It brings in the necessary libraries:
        - `multiprocessing`: The core library for creating and managing processes.
        - `time`: Used to measure how long the operations take.
        - `os`: Used here to get the Process ID (`os.getpid()`).
        - `psutil`: A handy library to get system information, like the number of CPU cores.
    - **`cpu_intensive_task`:** This function is the "heavy work." It just runs a very large loop, performing calculations that keep a CPU core busy. It prints its name and Process ID (PID) so you can see which process is running.
    - **Setup:** It prints the number of available CPU cores and defines a large number `N` to make the task take a noticeable amount of time.
    
2. **The `if __name__ == "__main__":` Guard**

    This is **essential** for `multiprocessing` to work correctly on macOS and Windows. When you start a new process, it imports your script. This `if` block ensures that the code inside it only runs when the script is executed directly, not when it's imported by a child process. Without it, you'd get an infinite loop of processes spawning more processes.

3. **Synchronous (Sequential) Execution**

    This is the baseline. It calls `cpu_intensive_task` twice, one right after the other. The second call cannot start until the first one is completely finished. The total time will be roughly `(Time for Task 1) + (Time for Task 2)`.

4. **Multiprocessed (Parallel) Execution**

    This is the core of the demonstration:

    1. `multiprocessing.Process(...)`: Two new `Process` objects are created. We tell them which function to run (`target=cpu_intensive_task`) and what arguments to pass to it (`args=...`). This _defines_ the processes but doesn't run them yet.
    2. `p1.start()` and `p2.start()`: This is the magic. The operating system creates two new, independent processes that run in parallel. If you have at least two CPU cores, they will likely run simultaneously on different cores.
    3. `p1.join()` and `p2.join()`: The main script (the parent process) pauses at this point and **waits** for `p1` to finish. Then it waits for `p2` to finish. This is crucial for getting an accurate time measurement. Without `.join()`, the main script would continue immediately and print the elapsed time before the child processes were done.

### Expected Outcome

On a machine with 2 or more cores, you will see that the **Multiprocessed execution time** is roughly **half** of the **Synchronous execution time**. This is because the two tasks were able to run at the same time, effectively bypassing Python's Global Interpreter Lock (GIL) by using separate processes, each with its own memory and Python interpreter.

## Process Communication (Pipes and Queues)

Since the processes don't share memory directly, we need to use specific mechanisms to communicate between them. This is where *Pipes and Queues* come into play.

Let me show you an example now. 

### Pipes (`multiprocessing.Pipe`)

A pipe is a two-way communication channel between two processes. 

Let me show you an example now. 

```python
import multiprocessing
import time

def sender_process(conn):
    print("Sender: Sending messages...")
    conn.send("Hello from sender!")
    time.sleep(1)
    conn.send("Another message.")
    conn.close()

def receiver_process(conn):
    print("Receiver: Waiting for messages...")
    try:
        while True: # Loop until the sender closes the connection
            msg = conn.recv()
            print(f"Receiver: Received '{msg}'")
    except EOFError:
        # This error is raised when the sender closes the connection,
        # signaling that there's no more data.
        print("Receiver: Connection closed by sender.")
    finally:
        conn.close()

print("\n--- Multiprocessing with Pipe Example ---")
if __name__ == "__main__":
    receiver_conn, sender_conn = multiprocessing.Pipe() # Returns two connection objects

    p_sender = multiprocessing.Process(target=sender_process, args=(sender_conn,))
    p_receiver = multiprocessing.Process(target=receiver_process, args=(receiver_conn,))

    p_sender.start()
    p_receiver.start()

    p_sender.join()
    p_receiver.join()
```

The script's primary goal is to demonstrate **Inter-Process Communication (IPC)**. Since processes have separate memory, you can't just share a variable between them. A `Pipe` provides a direct, two-way communication channel, like a private telephone line, for exactly two processes to exchange data.

#### Code Analysis: A Step-by-Step Walkthrough

Let's break down the key components of this improved script.

1. **The `sender_process` Function**

    This function's role is straightforward: it sends data.

    - `conn.send(...)`: This method takes a Python object (here, a string), serializes it (a process called "pickling"), and sends it through its end of the pipe.
    - `conn.close()`: This is a **critical** step. When the sender closes its end of the pipe, it sends an "end-of-file" signal. The receiver will detect this signal, which is how it knows the conversation is over and no more data is coming.

2. **The `receiver_process` Function (The Robust Version)**

    This is a significant improvement over a simpler implementation. It's designed to be resilient.

    - `conn.recv()`: This is a **blocking** call. The process will pause on this line and wait until it receives an object from the pipe.
    - `while True:`: The receiver enters an infinite loop, ready to receive any number of messages the sender might send.
    - `try...except EOFError:`: This is the most important part of the robust design. The loop will run until the sender calls `conn.close()`. When that happens, the `conn.recv()` call has nothing left to receive and raises an `EOFError`. We catch this specific error, which tells us the sender is done. It's a clean and reliable way to terminate the receiving loop.
    - `finally: conn.close()`: This ensures that the receiver's end of the pipe is always closed, whether the loop finished normally (which it won't because of `while True`) or an error occurred.

3. **The Main Execution Block**

    This is the setup and coordination part.

    1. **`receiver_conn, sender_conn = multiprocessing.Pipe()`**: This creates the pipe and returns two `Connection` objects representing the two ends. Your variable naming here is excellent, as it makes the code's intent self-documenting.
    2. **Process Creation**: Two processes are created. The `sender_process` is given the `sender_conn` end of the pipe, and the `receiver_process` is given the `receiver_conn` end. This establishes the communication channel.
    3. **Execution**: The processes are started, and the main script waits for both to complete using `.join()`. But before calling the `.join()`, the main process needs to close it's end of the pipe. That's why we used a `sender_conn.close()` and a `receiver_conn.close()`. If not, the receiver will never receive the `EOFError`. Which means the receiver will get into an infinite loop.


#### Summary of Execution Flow

1. The main process creates a pipe with two ends: `sender_conn` and `receiver_conn`.
2. It starts two child processes, giving one end of the pipe to each, then it closes it's own end of the pipes.
3. The `sender` sends two messages. After the second message, it closes its connection.
4. The `receiver` starts its loop, receives the first message, prints it, and loops again. It receives the second message and prints it.
5. On the next loop, `conn.recv()` finds that the sender has closed the connection, so it raises an `EOFError`.
6. The `except` block catches the error, prints a confirmation message, and the `finally` block closes the receiver's connection.
7. Both processes have now finished, so the `.join()` calls in the main script unblock, and the program exits cleanly.

### Queues (`multiprocessing.Queue`)

A queue is a more flexible and robust way to communicate between processes. Especially between multiple producers and consumers. 

Let me show you an example now. 

```python
import multiprocessing
import time
import random

def producer(queue, num_consumers):
    print(f"Producer: Starting to produce 10 messages...")
    for i in range(10):
        message = f"Message {i}"
        print(f"Producer: Putting '{message}' on queue")
        queue.put(message)
        time.sleep(random.uniform(0.1, 0.5))
    # Add a sentinel value for each consumer to signal completion
    for _ in range(num_consumers):
        queue.put(None)

def consumer(name, queue):
    while True:
        message = queue.get()
        if message is None: # Check for sentinel
            print(f"Consumer {name}: Received sentinel, exiting.")
            break
        print(f"Consumer {name}: Got '{message}' from queue")
        time.sleep(random.uniform(0.2, 0.8))

print("\n--- Multiprocessing with Queue Example ---")
if __name__ == "__main__":
    q = multiprocessing.Queue() # Create a Queue object

    num_consumers = 2
    p_producer = multiprocessing.Process(target=producer, args=(q, num_consumers))
    
    consumers = []
    for i in range(num_consumers):
        p_consumer = multiprocessing.Process(target=consumer, args=(f"C-{i+1}", q))
        consumers.append(p_consumer)

    p_producer.start()
    for c in consumers:
        c.start()

    p_producer.join()
    for c in consumers:
        c.join()
# This script demonstrates how to use a `multiprocessing.Queue` to communicate between a producer and multiple consumers.
```


This script implements the classic **Producer-Consumer pattern** with one producer and multiple consumers, which is a cornerstone of concurrent application design.

#### Core Concept: One Producer, Multiple Consumers

The fundamental idea is to have one process (the "producer") that generates tasks and puts them onto a shared "conveyor belt" (the `Queue`). Multiple other processes (the "consumers") can then pick tasks from that belt and work on them simultaneously. This allows you to process a large workload much faster than a single consumer could.

#### Code Analysis: A Step-by-Step Walkthrough

Let's break down how this is achieved in the script.

1. **The `producer` Function**

    This function's role is to create work.

    - `queue.put(message)`: It adds 10 messages to the shared queue.
    - **The Sentinel Pattern (for multiple consumers)**: Instead of putting just one `None` on the queue, it now puts `num_consumers` `None` values. This is crucial because each consumer needs to receive its own "poison pill" to know when to shut down. If you only sent one, the first consumer to get it would exit, leaving the others waiting forever on an empty queue.

2. **The `consumer` Function**

    This function's role is to process work. 

    - `message = queue.get()`: This is a **blocking** call. The process waits here until an item is available. The `Queue` ensures that even though multiple consumers are calling `.get()`, each message is only delivered to **one** of them.
    - `if message is None: break`: When a consumer receives its `None` sentinel, it breaks the loop and terminates gracefully.

3. **The Main Execution Block**

    This is the orchestrator.

    1. It creates a single `Queue` that will be shared among all processes.
    2. It creates one `producer` process.
    3. It creates a list of `consumer` processes in a loop. This is a clean, scalable way to manage multiple workers.
    4. It starts the producer and all the consumers.
    5. It then waits for all processes to finish using `.join()`.

    When you run this, you'll see `Consumer C-1` and `Consumer C-2` picking up and processing messages concurrently, demonstrating how the workload is shared between them.


### Process Pools (`multiprocessing.Pool`)

A `Pool` object controls a pool of worker processes to which jobs can be submitted. It takes care of distributing the tasks to the available workers and collecting the results, all in a few lines of code.

**Key Concept:**

- **Managed Workers:** You create a `Pool` and tell it how many worker processes to use (it defaults to the number of CPU cores on your machine). This prevents you from accidentally starting too many processes and overloading your system.
- **`pool.map()`:** This is the most common method. It's a parallel equivalent of Python's built-in `map()` function. You give it a function and a list of inputs, and it automatically applies the function to every item in the list using the pool of worker processes. It blocks until all results are ready and returns them in a list.
- **Automatic Cleanup:** When used with a `with` statement, the pool is automatically closed (no more tasks can be submitted) and joined (the main process waits for all workers to finish) for you.

For common scenarios where you want to apply a function to a collection of inputs using multiple processes, `multiprocessing.Pool` is very convenient. It manages a pool of worker processes for you, handling task distribution and result collection automatically.

Let's see how it simplifies the CPU-bound task from our first example.

```python
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
    with multiprocessing.Pool(processes=os.cpu_count()) as pool:
        # pool.map is a blocking call. It distributes the tasks in tasks_to_run
        # to the worker processes and waits for all results to complete.
        results = pool.map(cpu_intensive_task, tasks_to_run)

    end_time = time.time()

    print(f"\nResults (not all shown): {results[:3]}...")
    print(f"Total time with Pool: {end_time - start_time:.2f} seconds")
```

#### How it works

1.  **`with multiprocessing.Pool() as pool:`**: This is the recommended way to use a `Pool`. It creates a pool of worker processes (as many as you have CPU cores, by default). The `with` statement ensures the pool is properly closed and terminated when the block is finished.
2.  **`results = pool.map(cpu_intensive_task, tasks_to_run)`**: This is the key line.
    *   It takes the function to execute (`cpu_intensive_task`) and an iterable of inputs (`tasks_to_run`).
    *   It automatically distributes the items from `tasks_to_run` among the available worker processes.
    *   It's a **blocking** call, meaning the main script pauses here until all the tasks are finished.
    *   It collects the return value from every task and returns them as a single list, `results`, in the same order as the original input.

Compared to creating and managing `Process` objects manually, the `Pool` is significantly simpler and cleaner for this type of "map-reduce" workload.

Another example

```python
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
```

Here the difference is that we create only 4 proceses in the pool. Other than that the functionality is the same. 

## When to use Processes

Its good to know when we should consider to use processes.

**CPU-bound tasks:** When you need true parallelism and want to utilize multiple CPU cores.
- **Heavy computation:** Image processing, scientific computing, data crunching.
- **Isolation:** When tasks need to be completely isolated from each other in terms of memory and state (safer from unexpected side effects).
- **Robustness:** If one process crashes, it generally doesn't bring down the entire application (unlike threads within the same process).

