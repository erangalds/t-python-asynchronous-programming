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

