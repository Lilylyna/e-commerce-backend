import time
import threading
import queue
import random

class WebhookQueue:
    def __init__(self, retry_delays=None):
        self.queue = queue.Queue()
        self.retry_delays = retry_delays if retry_delays is not None else [5, 10, 30] # Seconds for retries
        self.processing_thread = threading.Thread(target=self._process_webhooks, daemon=True)
        self.processing_thread.start()
        print("WebhookQueue initialized. Processing thread started.")

    def add_webhook(self, url: str, payload: dict, current_retries: int = 0):
        """
        Adds a webhook task to the queue for asynchronous delivery.
        """
        task = {
            "url": url,
            "payload": payload,
            "current_retries": current_retries,
            "next_attempt_time": time.time()
        }
        self.queue.put(task)
        print(f"Webhook added to queue: {payload.get("invoice_id", "N/A")}")

    def _process_webhooks(self):
        while True:
            try:
                task = self.queue.get(timeout=1)
                url = task["url"]
                payload = task["payload"]
                current_retries = task["current_retries"]
                next_attempt_time = task["next_attempt_time"]

                if time.time() < next_attempt_time:
                    # If it's not time to retry yet, put it back and continue
                    self.queue.put(task)
                    time.sleep(0.1)
                    continue

                print(f"Attempting to send webhook (invoice: {payload.get("invoice_id", "N/A")}, retry: {current_retries})...")
                success = self._send_webhook(url, payload)

                if success:
                    print(f"Webhook sent successfully for invoice: {payload.get("invoice_id", "N/A")}")
                else:
                    if current_retries < len(self.retry_delays):
                        next_delay = self.retry_delays[current_retries]
                        task["current_retries"] = current_retries + 1
                        task["next_attempt_time"] = time.time() + next_delay
                        self.queue.put(task)
                        print(f"Webhook failed, retrying in {next_delay} seconds (invoice: {payload.get("invoice_id", "N/A")})")
                    else:
                        print(f"Webhook failed after multiple retries for invoice: {payload.get("invoice_id", "N/A")}. Giving up.")
            except queue.Empty:
                time.sleep(0.5) # Sleep if queue is empty
            except Exception as e:
                print(f"Error in webhook processing thread: {e}")
                time.sleep(1) # Prevent busy-loop on unexpected errors

    def _send_webhook(self, url: str, payload: dict) -> bool:
        """
        Simulates sending an HTTP POST request to the webhook URL.
        In a real application, this would use requests.post or similar.
        """
        print(f"Simulating POST to {url} with payload: {payload}")
        # Simulate success or failure randomly
        return random.choice([True, True, True, False]) # 75% success rate for simulation

# Example Usage:
if __name__ == "__main__":
    webhook_queue = WebhookQueue()

    print("\n--- Adding webhooks to the queue ---")
    webhook_queue.add_webhook("http://example.com/webhook", {"invoice_id": "inv_001", "status": "paid"})
    webhook_queue.add_webhook("http://example.com/webhook", {"invoice_id": "inv_002", "status": "confirmed"})
    webhook_queue.add_webhook("http://example.com/another_webhook", {"invoice_id": "inv_003", "status": "expired"})

    # Give the thread some time to process (in a real app, this would be a long-running process)
    print("\n--- Allowing webhook processing... (Ctrl+C to stop) ---")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped webhook queue example.")
