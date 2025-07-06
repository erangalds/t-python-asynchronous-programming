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