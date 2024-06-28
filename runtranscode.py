#!/usr/bin/env python3

import os
import subprocess
import time
from google.cloud import pubsub_v1

# Set up Pub/Sub client
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("your-project-id", "topic-id")
#time to wait before next split
pause_time = 300 #5 min
# Set the starting file
start_file = "split_aah"  # Replace with the desired starting file


# Function to monitor Pub/Sub topic for messages
def monitor_pubsub(timeout_seconds=120):
    """Monitors the Pub/Sub topic for messages for a specified timeout.

    Args:
        timeout_seconds: The maximum time to wait for messages (in seconds).

    Returns:
        True if a message is received within the timeout, False otherwise.
    """
    subscription_path = publisher.subscription_path("your-project-id", "your-subscription-id")
    subscriber = pubsub_v1.SubscriberClient()
    with subscriber:
        subscription = subscriber.subscription(subscription_path)
        future = subscriber.subscribe(subscription, callback=callback)
        try:
            future.result(timeout=timeout_seconds)
            return True
        except TimeoutError:
            print(f"No messages received within {timeout_seconds} seconds.")
            return False

# Callback function for Pub/Sub messages
def callback(message):
    """Processes a Pub/Sub message.

    Args:
        message: The Pub/Sub message.
    """
    print(f"Received message: {message.data}")
    message.ack()

# Main script
if __name__ == "__main__":
    # Get a list of files starting with 'filesplit*'
    files = [f for f in os.listdir(".") if f.startswith("split_*")]
    files.sort()  # Sort the files alphabetically

    

    # Iterate through the files, starting from the specified file
    for i, file in enumerate(files):
        if file == start_file:
            print(f"Starting from file: {file}")
            break

    for file in files[i:]:
        print(f"Executing file: {file}")
        # Execute the file with '/bin/sh'
        subprocess.run(["/bin/sh", file])

        # Monitor the Pub/Sub topic for messages
        if monitor_pubsub():
            print("Message received on Pub/Sub topic. Continuing to next file.")
        else:
            print("No message received within 2 minutes. Waiting for 2 minutes before continuing.")
            time.sleep(120)
    # Iterate through the files
    for file in files:
        print(f"Executing file: {file}")
        # Execute the file with '/bin/sh'
        subprocess.run(["/bin/sh", file])

        # Monitor the Pub/Sub topic for messages
        if monitor_pubsub():
            print("Message received on Pub/Sub topic. Continuing to next file.")
        else:
            print("No message received within 2 minutes. Waiting for 2 minutes before continuing.")
            time.sleep(pause_time)
