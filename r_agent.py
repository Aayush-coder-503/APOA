import threading
import time
import json

from simulator import stream_payments, set_outage
from metrics import ingest, compute_metrics, print_metrics
from agent import analyze, explain, update_learning
from actions import apply_action, check_rollbacks


def serialize_metrics(metrics):
    out = {}
    for (bank, card), v in metrics.items():
        out[f"{bank}-{card}"] = v
    return out


def on_payment(event):
    ingest(event)


t = threading.Thread(target=stream_payments, args=(on_payment, 10))
t.daemon = True
t.start()

print("System started. Collecting payments...")


def trigger_outage():
    time.sleep(15)
    print("\n*** SIMULATING HDFC VISA OUTAGE ***\n")
    set_outage("HDFC", "VISA", severity=0.5)

threading.Thread(target=trigger_outage, daemon=True).start()


while True:
    time.sleep(10)

    print_metrics()
    metrics = compute_metrics()

    with open("live_metrics.json", "w") as f:
        json.dump(serialize_metrics(metrics), f, indent=2)

    hypotheses = analyze(metrics)
    explain(hypotheses)

    with open("live_decisions.json", "w") as f:
        json.dump(hypotheses, f, indent=2)

    for h in hypotheses:
        apply_action(h)

    check_rollbacks()

    update_learning(metrics)
