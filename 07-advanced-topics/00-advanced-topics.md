# Advanced Topics and Best Practices 

## Debugging Concurrent Code

I learned to code by learning the concept of sequential execution. Under sequential execution its very easy to plan the required functionality. But sequential programming has a big limitation when it comes to handling concurrency. Because you always have to finish one task and then moves to the other tasks. On the otherhand cocurrent programming can help to solve the performance improvements with concurrent user or task handling. But the nature of execution makes debugging code challenging, because of the non-deterministic behavior. 

Below are few ways which we can use to debug concurrent code. 

+**`print` statements:** Use them judiciously to trace execution flow and variable states.
- **Logging:** A more robust alternative to `print`. Include thread/process IDs in logs.
- **`pdb` (Python Debugger):** Can be used, but stepping through concurrent code is tricky. You might need to set breakpoints strategically.
- **Visual debuggers:** IDEs like PyCharm offer more advanced debugging tools for concurrent applications.
- **Timeouts:** Always use timeouts for I/O operations and for `join()` on threads/processes to prevent indefinite blocking.

## Race Conditions and Deadlocks a brief overview

- **Race Condition:** Occurs when multiple threads or processes access and modify shared data concurrently, and the final result depends on the non-deterministic order of operations. 
    - **Solutions:** Locks, Semaphores, Queues.
- **Deadlock:** A situation where two or more threads/processes are blocked indefinitely, waiting for each other to release a resource that the other one needs. Often happens with multiple locks acquired in different orders.        
    - **Solution:** Consistent locking order, timeouts, careful resource allocation.


## Graceful Shutdown

Ensure your concurrent applications can shut down cleanly.

- **`thread.join()` / `process.join()`:** Wait for workers to finish.
- **Sentinel values in queues:** Send a special value (like `None`) to consumers to tell them to stop.
- **Timeouts:** Prevent endless waiting.
- **Signal handling:** Catch OS signals (e.g., `Ctrl+C` via `signal` module) to initiate graceful shutdown.

## Integrating `asyncio` with Blocking Code

Sometimes you have a blocking function (e.g., a synchronous database call, a CPU-bound calculation) that you need to run within an `asyncio` event loop without blocking the entire loop.

`asyncio.to_thread()` (Python 3.9+) or `loop.run_in_executor()` (older versions) are used for this. They execute the blocking code in a separate thread (from a default `ThreadPoolExecutor`) and then return control to the event loop when the blocking task completes.

Let me show this to you using an example. 

```python 
import asyncio
import time
import requests
from typing import List, Coroutine, Any

def blocking_io_call(url: str) -> str:
    """A blocking (synchronous) I/O call."""
    print(f"  [Blocking] Starting fetch from {url}...")
    response = requests.get(url, timeout=5)
    time.sleep(1) # Simulate additional blocking work
    print(f"  [Blocking] Finished fetch from {url}.")
    return f"Data from {url} (Status: {response.status_code})"

async def main_async_with_blocking() -> None:
    print("\n--- Asyncio with Blocking Calls (via `to_thread`) ---")
    start_time = time.time()

    # Create a list of async tasks
    async_tasks: List[asyncio.Task[Any]] = [
        asyncio.create_task(asyncio.sleep(0.5, result="Async task 1 done")),
        asyncio.create_task(asyncio.sleep(1.0, result="Async task 2 done")),
    ]

    # Run blocking I/O calls in a separate thread pool managed by asyncio
    # asyncio.to_thread() is the modern and simpler way (Python 3.9+)
    # It returns a coroutine that runs the blocking function in a thread.
    blocking_coroutines: List[Coroutine[Any, Any, str]] = [
        asyncio.to_thread(blocking_io_call, "https://www.example.com"),
        asyncio.to_thread(blocking_io_call, "https://www.bing.com"),
    ]

    # Gather all tasks (async and those offloaded to threads)
    results = await asyncio.gather(*async_tasks, *blocking_coroutines)

    end_time = time.time()
    print(f"All tasks completed. Results: {results}")
    print(f"Total time (asyncio + blocking): {end_time - start_time:.2f} seconds.")
    # The total time will be roughly max(longest_async_task_time, longest_blocking_task_time),
    # demonstrating that blocking calls don't block the event loop.

if __name__ == "__main__":
    print("Starting main program...")
    # Run the async function using asyncio.run()
    asyncio.run(main_async_with_blocking())
    print("Main program finished.")
```

### High-Level Goal

The primary objective of this script is to demonstrate how to execute **blocking, synchronous code** (like a standard `requests.get()` call) within an **asynchronous `asyncio` program** without freezing the entire application.

In `asyncio`, the event loop runs in a single thread. If you call a regular function that blocks (e.g., waits for a network response or a file to be read), the entire event loop pauses. This stops all other asynchronous tasks from running and defeats the purpose of concurrency. This script showcases the modern and recommended solution to this problem: `asyncio.to_thread()`.

### Code Breakdown

Let's walk through the script, piece by piece.

#### 1. `blocking_io_call(url: str) -> str`

- This is a standard, **synchronous** Python function. It doesn't use `async` or `await`.
- `requests.get()` is a classic blocking I/O call. The function's execution will halt at this line until the web server sends back a response.
- `time.sleep(1)` is also a blocking call, making the current thread do nothing for one second.
- If you were to call this function directly from an `async def` block, the `asyncio` event loop would be completely frozen during the network request and the sleep, preventing any other tasks from running.

#### 2. `main_async_with_blocking() -> None`

This is the main asynchronous "orchestrator" where all the concurrent tasks are managed.

- First, it creates a couple of native `asyncio` tasks. `asyncio.sleep()` is a non-blocking operation. When awaited, it yields control back to the event loop, allowing other tasks to run while it "waits".
- This is the most important part of the script. `asyncio.to_thread()` is a high-level utility (introduced in Python 3.9) designed specifically for this scenario.
- It takes a blocking function (`blocking_io_call`) and its arguments.
- It tells the `asyncio` event loop: "Please run this blocking function for me, but do it in a **separate background thread** from a managed thread pool so you (the event loop) don't get stuck."
- It immediately returns special `Coroutine` objects. These can be awaited just like native `async` functions.
- `asyncio.gather()` is a powerful tool for running multiple awaitable objects concurrently.
- We pass it both our native `async_tasks` and the `blocking_coroutines` that were created by `to_thread`.
- The `await` keyword pauses `main_async_with_blocking` until **all** of these tasks are complete, whether they are running on the main event loop or in background threads.

#### 3. The Entry Point (`if __name__ == "__main__":`)

- This is the standard way to start an `asyncio` application.
- `asyncio.run()` creates the event loop, runs the `main_async_with_blocking` coroutine until it completes, and then cleanly closes the loop.

### How It All Works Together (Execution Flow)

1. `asyncio.run()` starts the event loop.
2. The two native `async_tasks` (`asyncio.sleep`) are scheduled to run on the event loop.
3. The two `blocking_io_call` functions are handed off to a background thread pool via `asyncio.to_thread`.
4. **The event loop is now free!** While the `requests.get()` calls are blocking in their separate threads, the event loop can concurrently manage the `asyncio.sleep` tasks.
5. You will see output from both the `[Blocking]` calls and the native async tasks interleaved, proving that the program is running concurrently and the event loop was never frozen.
6. The total execution time will be determined by the longest-running task (in this case, the blocking calls which take a bit over 1 second each), not the sum of all task times. This is the key benefit of this pattern.

The use of type hints (`List`, `Coroutine`, `str`, `None`) throughout the code is excellent practice, making it more readable, self-documenting, and easier for tools to analyze.

