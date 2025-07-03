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

