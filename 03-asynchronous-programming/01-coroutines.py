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

