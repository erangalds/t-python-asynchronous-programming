# High Level Concurrency with `concurrent.futures` Module

The `concurrent.futures` module provides a high-level interface for asynchronously executing callables. It includes `ThreadPoolExecutor` and `ProcessPoolExecutor`, which manage pools of threads or processes for you, simplifying common concurrency patterns.

## Introduction to `ThreadPoolExecutor`

Simplifies multithreading, especially for I/O-bound tasks. 

Let's see an example now. 

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import requests

def download_url(url):
    """Simulates downloading a URL (I/O-bound)."""
    print(f"Downloading: {url}")
    try:
        response = requests.get(url, timeout=5)
        print(f"Finished downloading {url} (Status: {response.status_code})")
        return f"{url}: {len(response.content)} bytes"
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return f"{url}: Error"

print("\n--- ThreadPoolExecutor Example ---")
urls = [
    "https://www.google.com",
    "https://www.github.com",
    "https://www.python.org",
    "https://www.wikipedia.org",
    "https://www.example.com",
    "https://www.invalid-url-hopefully.com" # To demonstrate error handling
]

start_time = time.time()
# Create a thread pool with a maximum of 5 worker threads
with ThreadPoolExecutor(max_workers=5) as executor:
    # submit() returns a Future object immediately
    futures = [executor.submit(download_url, url) for url in urls]

    # This loop processes results in the order they were SUBMITTED.
    # If the first URL is slow, the program will wait for it before printing any other results,
    # even if others are already finished.
    for future in futures:
        result = future.result() # Blocks until THIS specific future is done.
        print(f"Result received: {result}")

end_time = time.time()
print(f"Total time (ThreadPoolExecutor): {end_time - start_time:.2f} seconds.")

print("\n\n")
# Using as_completed to handle results as they complete
print("\n--- Using as_completed with ThreadPoolExecutor ---")
start_time = time.time()
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(download_url, url): url for url in urls}

    # as_completed() yields futures as they complete. This is more efficient
    # as it allows processing results as soon as they are available.
    for future in as_completed(futures):
        url = futures[future]
        try:
            result = future.result()
            print(f"Result received (from as_completed) for {url}: {result}")
        except Exception as e:
            print(f"Error for {url}: {e}")

end_time = time.time()
print(f"Total time (as_completed with ThreadPoolExecutor): {end_time - start_time:.2f} seconds.")   
```

### High-Level Goal

The script's purpose is to download multiple web pages concurrently using a pool of threads. This is a classic I/O-bound task where `ThreadPoolExecutor` excels. 

### Shared Component: The Worker Function

Both examples in the script use the same worker function:

- **`download_url(url)`**: This function does the actual work. It takes a URL, uses the `requests` library to download it (the I/O-bound part), and handles potential network errors gracefully with a `try...except` block. It returns a string with the result.

---

### Part 1: The Simple (but less responsive) Approach

The first block of code demonstrates the most straightforward way to get results.

#### How It Works:

1. **`with ThreadPoolExecutor(...)`**: Creates a pool of 5 worker threads. The `with` statement ensures the pool is properly shut down.
2. **`futures = [executor.submit(...)`**: This line submits all the download jobs to the pool. `executor.submit()` is non-blocking; it returns a `Future` object immediately for each job. `futures` becomes a list of these `Future` objects, in the same order as the `urls` list.
3. **`for future in futures:`**: This is the key part. The code iterates through the `futures` list **in the order the jobs were submitted**.
4. **`result = future.result()`**: This call **blocks**. It waits for that _specific_ future to complete.

#### The "Gotcha"

The major drawback here is the processing order. If `urls[0]` ("google.com") is fast but `urls[1]` ("github.com") is very slow, the loop will get the result for Google, but then it will **wait** for the GitHub download to finish before it can even check on the results for the other URLs, even if they are already done. You process results in submission order, not completion order.

---

### Part 2: The `as_completed` (more responsive) Approach

The second block demonstrates a more advanced and generally preferred pattern.

#### How It Works:

1. **`futures = {executor.submit(...): url ...}`**: This is a clever use of a dictionary comprehension. It submits each job and creates a dictionary mapping the `Future` object to its original `url`. This is a very common pattern that makes it easy to know which input a result belongs to.
2. **`for future in as_completed(futures):`**: This is the magic. `as_completed` is an iterator that takes a collection of futures and **yields each future as it completes**. It doesn't care about the submission order. The first future to be yielded by this loop is the one whose task finished first.
3. **Processing**: Inside the loop, you can get the result from the completed `future` and use the dictionary to look up which `url` it corresponds to.

#### The Advantage

This approach is far more responsive. As soon as _any_ download finishes, its result is processed and printed, regardless of its position in the original list. This is ideal for most real-world applications where you want to process data as soon as it's available.

## Introduction to `ProcessPoolExecutor`

Simplifies multiprocessing, especially for CPU-bound tasks. 

```python

```

### High-Level Goal

The script's purpose is to execute multiple computationally expensive tasks in parallel to speed up the total execution time. It achieves this by using a `ProcessPoolExecutor`, which distributes the work across multiple processes, allowing them to run on different CPU cores simultaneously. This is the ideal approach for **CPU-bound** work, as it effectively bypasses Python's Global Interpreter Lock (GIL).

The script clearly demonstrates two distinct methods for submitting work and retrieving results: the simple `map` function and the more flexible `submit` + `as_completed` pattern.

### Core Components

1. **`heavy_calculation(n)` function**: This is the worker function. It's designed to be CPU-bound by performing a large number of calculations (`sum(i*i ...)`). It also prints its Process ID (`os.getpid()`) to provide clear evidence that the tasks are running in separate, parallel processes.
    
2. **`if __name__ == "__main__":` guard**: This is **non-negotiable** when using `multiprocessing` or `ProcessPoolExecutor`. It prevents a catastrophic infinite loop of child processes being created when the script is re-imported by a new process. 
    
---

### Part 1: The `map()` Approach (Simple and Ordered)

The first block uses `executor.map`, which is a high-level and convenient method.

#### How It Works:

1. **`with ProcessPoolExecutor(...)`**: Creates a pool of worker processes, defaulting to the number of CPU cores on your machine (`os.cpu_count()`). The `with` statement ensures the pool is properly shut down.
2. **`executor.map(heavy_calculation, numbers)`**: This is the key line.
    - It behaves like Python's built-in `map()` function but distributes the work across the processes in the pool.
    - It takes the worker function (`heavy_calculation`) and an iterable of inputs (`numbers`).
    - It is a **blocking** call. The main program will pause here until _all_ calculations are finished.
    - It returns an iterator that yields results **in the same order as the original inputs**. Wrapping it in `list()` consumes the iterator and gives you the final list of results.

This method is perfect when you have a straightforward task: apply one function to many inputs and get all the results back at the end, in order.

---

### Part 2: The `submit()` + `as_completed()` Approach (Flexible and Responsive)

The second block demonstrates a more powerful and flexible pattern.

#### How It Works:

1. **`futures = {executor.submit(...): n ...}`**: This is a very common and effective pattern.
    - `executor.submit()` schedules a single task to run and immediately returns a `Future` object, which is a placeholder for the eventual result. This call is non-blocking.
    - The dictionary comprehension creates a mapping from each `Future` object to its original input (`n`). This is essential for knowing which result corresponds to which task later on.
2. **`for future in as_completed(futures):`**: This is the core of this pattern's advantage.
    - `as_completed` is an iterator that takes a collection of `Future` objects.
    - It **yields each future as soon as its task is complete**, regardless of the order in which the tasks were submitted.
3. **`result = future.result()`**: Inside the loop, you can immediately get the result from the completed future.

This approach is superior when tasks might take different amounts of time to complete and you want to process results as soon as they are available, rather than waiting for the entire batch to finish.

## When to Use `concurrent.futures`

Knowing when to use `concurrent.futures` is very important. 

- **Simplifying boilerplate:** You don't have to manually manage thread/process creation, starting, joining, and basic result collection.
- **Mixed tasks:** When you have a list of independent tasks, and you want to delegate them to either threads or processes without getting into the lower-level details of `threading` or `multiprocessing`.
- **I/O-bound tasks:** Use `ThreadPoolExecutor`.
- **CPU-bound tasks:** Use `ProcessPoolExecutor`.

