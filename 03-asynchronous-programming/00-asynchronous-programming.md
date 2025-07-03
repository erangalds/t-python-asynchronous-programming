# Asynchronous Programming in Python (`asyncio` module)

The `asyncio` is a standard library in python for writing concurrent code using the `async` and `await` syntax. It is a form of **coorperative multitasking**. 

## Introduction to `asyncio` library

When I started to learn about this standard python library, I found three things interesting.

+ **Single Threaded**: `asyncio` runs in a single-thread. Which means a single GIL Instance. 
+ **Coorperative**: Tasks voluntarily give up control (`yield`) when they encounter an `await` expression, allowing other tasks to run. This is totally different to threads behavior, where the OS preemptively switches between them. 
+ **Event loop**: The heart of `asyncio`. It's a loop that monitors `await` able objects and schedules tasks to run when they are `ready` (e.g. an I/O operation is complete). 

## Coroutines: `async def` and `await`

+ `async def`: Defines a coroutine function. When you call an `async def` function, it doesn't execute immediately; instead it returns a coroutine object.
+ `await`: can only be used inside an `async def` function. It pauses the execution of the current coroutine untile the awaited 'awaitable' (another coroutine, a task, a future) is complete. During this pause, the event loop can run other tasks. 

Let me show you an example now. 

```python
import asyncio
import time

async def fetch_data(delay, data):
    """A coroutine that simulates fetching data from a network."""
    print(f"Fetching {data} (will take {delay} seconds)...")
    await asyncio.sleep(delay) # Non-blocking sleep
    print(f"Finished fetching {data}.")
    return f"Data: {data}"

async def main_async():
    print("--- Asyncio Basic Example ---")
    start_time = time.time()

    # Calling coroutines directly returns coroutine objects, doesn't run them
    # c1 = fetch_data(2, "Users")
    # c2 = fetch_data(3, "Products")

    # To run coroutines concurrently, you need to create Tasks or use asyncio.gather
    # Create Tasks
    task1 = asyncio.create_task(fetch_data(2, "Users"))
    task2 = asyncio.create_task(fetch_data(3, "Products"))

    # Now, we'll use asyncio.gather
    results = await asyncio.gather(
        task1,
        task2
    )

    end_time = time.time()
    print(f"All data fetched. Results: {results}")
    print(f"Total time (asyncio): {end_time - start_time:.2f} seconds.")
    # Expected time will be around 3 seconds (max of 2 and 3),
    # demonstrating concurrent I/O.

# To run an async function, you need an event loop. asyncio.run() does this for you.
if __name__ == "__main__":
    asyncio.run(main_async())
```

### How it works

#### High-Level Overview

The script demonstrates how to perform multiple simulated "network calls" (like fetching data from a web API) concurrently. Instead of waiting for the first call to finish before starting the second, `asyncio` allows the program to start both, wait for them to complete simultaneously, and then process the results. This is much more efficient than running them one after another, especially for I/O-bound operations. The total time taken will be close to the duration of the _longest_ operation, not the sum of all operation durations.

Let's break down the script piece by piece.

1. `fetch_data` Coroutine

- **`async def`**: This defines a **coroutine function**. Calling it doesn't run the code immediately but returns a coroutine object, which is a special kind of "awaitable" object.
- **`await asyncio.sleep(delay)`**: This is the core of the asynchronous behavior.
    - `asyncio.sleep()` is a non-blocking version of `time.sleep()`.
    - When the `await` keyword is encountered, it tells the `asyncio` event loop: "I'm going to be waiting here for `delay` seconds. You can pause my execution and go run something else that is ready."
    - This act of pausing and letting other tasks run is called "yielding control".

2. `main_async` Coroutine

- This is the main entry point for our asynchronous logic.
- **`asyncio.gather(...)`**: This is a powerful `asyncio` function. It takes one or more awaitable objects (in this case, the two coroutine objects returned by `fetch_data(2, ...)` and `fetch_data(3, ...)`). It wraps them in Tasks and runs them concurrently.
- **`await asyncio.gather(...)`**: The `main_async` coroutine pauses at this line until _all_ the tasks passed to `gather` have finished their work. Once they are all done, `gather` collects their return values into a list.

3. The Entry Point

- This is how you kick off an `asyncio` program.
- **`asyncio.run(main_async())`**: This function does all the heavy lifting:
    1. It creates a new `asyncio` event loop.
    2. It runs the `main_async` coroutine on that loop.
    3. It manages the execution of all other tasks that are scheduled (like the `fetch_data` tasks).
    4. Once `main_async` is complete, it closes the event loop and cleans up.

#### Step-by-Step Execution Flow

1. `asyncio.run(main_async())` starts the event loop and tells it to run `main_async`.
2. `main_async` starts. It prints the start message and records the `start_time`.
3. It calls `asyncio.gather` with two new coroutine objects: `fetch_data(2, "Users")` and `fetch_data(3, "Products")`.
4. `gather` schedules both coroutines to run on the event loop.
5. The event loop starts the first task, `fetch_data(2, "Users")`. It prints `"Fetching Users..."` and immediately hits `await asyncio.sleep(2)`.
6. The first task is paused, and control is yielded back to the event loop.
7. The event loop sees the second task is ready, `fetch_data(3, "Products")`. It starts it. It prints `"Fetching Products..."` and hits `await asyncio.sleep(3)`.
8. The second task is also paused, yielding control.
9. Now, the event loop is waiting. Both tasks are "sleeping".
10. After **2 seconds**, the `sleep(2)` in the first task finishes. The event loop resumes it. It prints `"Finished fetching Users."` and returns its result.
11. At the **3-second** mark, the `sleep(3)` in the second task finishes. The event loop resumes it. It prints `"Finished fetching Products."` and returns its result.
12. Both tasks given to `gather` are now complete. The `await` on `asyncio.gather` in `main_async` unblocks.
13. `main_async` resumes, prints the collected results, and calculates the total time, which will be just over 3 seconds.



## The Event Loop

The event loop is the central orchestrator of the `asyncio`. It manages and executes asynchronous tasks. 

+ It registers tasks. 
+ It monitors for events (like an I/O operation completing).
+ When an event occurs, it wakes up the corresponding task and schedule it to run. 
+ When a task `await`s, it yields control back to the event loop, which then picks the next ready task. 

You typically interact with the event loop indirectly through `asyncio.run()` or `asyncio.create_task()`. 

## Tasks

A Task is an `asyncio` object that wraps a coroutine and schedules its execution on the event loop. That's how you run multiple coroutines concurrently. 

Let's look at an example now. 

```python
import asyncio
import time

async def worker(name, delay):
    print(f"Worker {name}: Starting...")
    await asyncio.sleep(delay)
    print(f"Worker {name}: Finished.")
    return f"{name} done"

async def main_tasks():
    print("\n--- Asyncio with Tasks Example ---")
    start_time = time.time()

    # Create tasks from coroutines
    task1 = asyncio.create_task(worker("A", 2))
    task2 = asyncio.create_task(worker("B", 1))
    task3 = asyncio.create_task(worker("C", 3))

    # Await the tasks to get their results. This also implicitly waits for them.
    # Note: If you don't await a task, it might not run or its result/exception
    # might not be handled.
    results = await asyncio.gather(task1, task2, task3)

    end_time = time.time()
    print(f"All workers completed. Results: {results}")
    print(f"Total time (asyncio tasks): {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(main_tasks())
```

### How it works
This works very similar to the previous example. 

## Running `asyncio` Programs

+ `asyncio.run(coroutine())`: The simplest way to run a top-level `async` function. It manages the even loop for you (creates it, runs the coroutine, and closes it). Only call this once in your main program. 
+ `asyncio.create_task(coroutine())`: Schedules a coroutine to run as an `asynio` task. Returns a task object. You still need to `await` the task or `asynio.gather()` it for its result and to ensure it completes. 
+ `asyncio.gather(*coroutines or tasks)`: Run multiple awaitable (coroutines or tasks) concurrently and waits for all of them to complete. It returns their results in the order they were passed. 

## Real Worl Asynchronous Programming

### Example with HTTP Requests with `aiohttp`

To truely leverage `asyncio` for I/O, we need asynchronous versions of I/O libraries. For HTTP requests, `requests` library is a *blocking* type. Therefore, we need `aiohttp` for asynchronous HTTP. 

```python
# pip install aiohttp
import asyncio
import aiohttp
import time

async def fetch_url(session, url):
    print(f"Fetching: {url}")
    async with session.get(url) as response:
        # await response.text() or await response.json() if needed
        status = response.status
        print(f"Finished fetching {url} with status: {status}")
        return status

async def main_http_requests():
    print("\n--- Asyncio HTTP Requests with aiohttp ---")
    urls = [
        "https://www.google.com",
        "https://www.github.com",
        "https://www.python.org",
        "https://httpbin.org/delay/2", # This one will take 2 seconds
        "https://www.example.com"
    ]

    start_time = time.time()
    async with aiohttp.ClientSession() as session: # Create a session for efficient requests
        tasks = [fetch_url(session, url) for url in urls]
        # Run all tasks concurrently and wait for them to finish
        results = await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"All URLs fetched. Statuses: {results}")
    print(f"Total time (aiohttp): {end_time - start_time:.2f} seconds.")
    # Notice how the total time is dominated by the longest running request (2 seconds),
    # not the sum of all individual request times.

if __name__ == "__main__":
    asyncio.run(main_http_requests())
```

#### High-Level Overview

The script's goal is to fetch several web pages from a list of URLs as quickly as possible. Instead of fetching them one by one (sequentially), it uses `asyncio` and the `aiohttp` library to send all the requests concurrently.

The key takeaway is that the total time to fetch all URLs is determined by the single _slowest_ request (in this case, the one with a 2-second delay), not the sum of all the individual request times. This demonstrates a massive performance gain for real-world applications.

Let's go through the script section by section.

1. `fetch_url(session, url)` Coroutine

- **`async def`**: This declares the function as a **coroutine**. It can be paused and resumed.
- **`async with session.get(url) as response:`**: This is the core of the asynchronous operation.
    - `session.get(url)` initiates an HTTP GET request but **does not block**. It immediately returns an awaitable object.
    - The `await` (implicit in `async with`) tells the `asyncio` event loop: "I'm starting a network request. This will take time. You can pause me here and go run other tasks that are ready."
    - Once the web server responds and the data starts arriving, the event loop will "wake up" this coroutine and resume its execution inside the `with` block.
- **`status = response.status`**: This line runs only _after_ the `await` is complete and we have a response from the server. It extracts the HTTP status code (e.g., 200 for OK).
- **`return status`**: The coroutine finishes by returning the status code.

2. `main_http_requests()` Coroutine

- **`async with aiohttp.ClientSession() as session:`**: This is a crucial best practice. It creates a single `ClientSession` object that manages a pool of connections. Reusing the session for all requests is much more efficient than creating a new one for each URL, as it avoids the overhead of setting up new connections every time.
- **`tasks = [fetch_url(session, url) for url in urls]`**: This line uses a list comprehension to create a list of coroutine objects. **It does not run them yet.** It's like preparing a to-do list.
- **`results = await asyncio.gather(*tasks)`**: This is where the magic happens.
    - `asyncio.gather()` takes all the coroutine objects from the `tasks` list.
    - It schedules all of them to run on the event loop concurrently.
    - The `await` keyword pauses the `main_http_requests` function until **all** the tasks passed to `gather` have completed.
    - Once all are done, it collects their return values (the status codes) into a single list, `results`.

#### Step-by-Step Execution Flow

1. `asyncio.run(main_http_requests())` starts the event loop and begins executing `main_http_requests`.
2. A `ClientSession` is created.
3. The list comprehension creates five coroutine objects, one for each URL.
4. `asyncio.gather` schedules all five coroutines to run.
5. The event loop starts the first task (`fetch_url` for google.com). It prints "Fetching..." and immediately hits `await session.get()`. The task is paused, and the network request is initiated.
6. The event loop, seeing the first task is paused, immediately starts the second task (github.com). It also prints "Fetching..." and is paused at its `await session.get()`.
7. This continues for all five URLs. In a very short amount of time, all five network requests have been _started_ and the program is now waiting for them to complete.
8. As servers respond (e.g., example.com might be the fastest), their corresponding tasks are "woken up" by the event loop. They resume, get the status, print "Finished...", and return.
9. This continues until the slowest request (`httpbin.org/delay/2`) finally completes after about 2 seconds.
10. Once the last task is done, `await asyncio.gather()` unblocks, and the `main_http_requests` coroutine resumes.
11. The total time is calculated and printed. It will be just over 2 seconds because all the waiting happened in parallel.



## Comparing Threads and Asyncio




| Feature           | Multithreading (Python `threading`)                                       | Asynchronous Programming (`asyncio`)                                    |
| :---------------- | :------------------------------------------------------------------------ | :---------------------------------------------------------------------- |
| **Multitasking**  | Preemptive (OS decides when to switch threads)                            | Cooperative (tasks explicitly yield control via `await`)                |
| **Execution**     | Multiple threads run, but only one Python bytecode at a time (due to GIL) | Single thread, tasks take turns                                         |
| **Parallelism**   | No true parallelism for CPU-bound tasks (due to GIL)                      | No true parallelism (single-threaded)                                   |
| **Best for**      | I/O-bound tasks (where GIL is released)                                   | I/O-bound tasks, high concurrency with low overhead                     |
| **Overhead**      | Higher (thread creation, context switching by OS)                         | Lower (coroutine switching is lighter)                                  |
| **Shared State**  | Easier to share state (same memory space), but prone to race conditions   | Easier to manage shared state (explicit yielding, less race conditions) |
| **Debugging**     | Can be harder due to unpredictable thread scheduling                      | Generally easier to debug due to explicit control flow                  |
| **Blocking Code** | A blocking call in one thread blocks _only that thread_.                  | A blocking call (without `await`) blocks the _entire event loop_.       |


## When to use `asyncio`?

- **I/O-bound tasks with high concurrency:** When you need to handle many concurrent operations that involve waiting (network requests, database queries, file I/O). This is where `asyncio` shines.
- **Web servers/APIs (FastAPI, Starlette):** Perfect for highly concurrent web applications that need to handle many client requests.
- **Long-polling, WebSockets:** Ideal for maintaining many open connections.
- **Scraping, Bots:** Efficiently making many requests without blocking.


