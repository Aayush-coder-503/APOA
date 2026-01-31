from simulator import stream_payments
from metrics import ingest, print_metrics
import threading
import time

def callback(event):
    ingest(event)

t = threading.Thread(target=stream_payments, args=(callback, 5))
t.daemon = True
t.start()

while True:
    time.sleep(5)
    print_metrics()
