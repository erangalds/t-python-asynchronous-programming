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