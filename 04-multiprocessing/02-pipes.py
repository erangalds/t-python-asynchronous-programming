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

    # It's crucial for the parent process to close its ends of the pipe.
    # If it doesn't, the receiver's conn.recv() will never get an EOFError
    # because the pipe will still be open from the parent's side, causing a deadlock.
    sender_conn.close()
    receiver_conn.close()

    p_sender.join()
    p_receiver.join()