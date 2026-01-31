import time
from collections import defaultdict, deque

WINDOW_SECONDS = 60

events = deque()


def ingest(event):
    events.append(event)
    prune_old()

def prune_old():
    if not events:
        return

    newest = parse_time(events[-1]["timestamp"])

    while events and (newest - parse_time(events[0]["timestamp"])) > WINDOW_SECONDS:
        events.popleft()

from datetime import datetime

def parse_time(ts):
    return datetime.fromisoformat(ts).timestamp()


def compute_metrics():
    stats = defaultdict(lambda: {
        "total": 0,
        "success": 0,
        "fail": 0,
        "latency_sum": 0,
        "errors": defaultdict(int)
    })

    for e in events:
        key = (e["bank"], e["card"])
        s = stats[key]

        s["total"] += 1
        s["latency_sum"] += e["latency_ms"]

        if e["status"] == "success":
            s["success"] += 1
        else:
            s["fail"] += 1
            s["errors"][e["error_code"]] += 1

    result = {}

    for key, s in stats.items():
        total = s["total"]
        if total == 0:
            continue

        result[key] = {
            "success_rate": round(s["success"] / total, 3),
            "failure_rate": round(s["fail"] / total, 3),
            "avg_latency": round(s["latency_sum"] / total, 1),
            "errors": dict(s["errors"]),
            "total": total
        }

    return result


def print_metrics():
    metrics = compute_metrics()
    print("\n--- LIVE PAYMENT HEALTH ---")
    for (bank, card), m in metrics.items():
        print(f"{bank}-{card} | Success: {m['success_rate']*100:.1f}% | "
              f"Latency: {m['avg_latency']}ms | Errors: {m['errors']}")
