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