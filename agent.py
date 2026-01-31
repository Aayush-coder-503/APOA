import json
from datetime import datetime

MEMORY_FILE = "memory.json"
last_metrics = {}


def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

memory = load_memory()


def analyze(metrics):
    hypotheses = []

    for (bank, card), m in metrics.items():
        success = m["success_rate"]
        latency = m["avg_latency"]
        errors = m["errors"]

        if success < 0.90 or latency > 1500:
            key = f"{bank}_{card}"

            past = memory.get(key, {"confidence": 0.5, "times_seen": 0})

            prob = 0.6
            if "timeout" in errors or "network_error" in errors:
                prob += 0.2
            if latency > 2000:
                prob += 0.1

            prob = min(prob + past["confidence"] * 0.1, 0.95)

            impact = round((1 - success) * 100, 1)

            hypotheses.append({
                "bank": bank,
                "card": card,
                "probability": round(prob, 2),
                "impact_percent": impact,
                "latency": latency,
                "errors": errors,
                "suggested_action": suggest_action(prob, impact)
            })

    return hypotheses


def suggest_action(prob, impact):
    if prob > 0.8 and impact > 10:
        return "partial_reroute"
    elif prob > 0.6 and impact > 5:
        return "monitor_and_alert"
    else:
        return "do_nothing"



def learn(bank, card, outcome_improved):
    key = f"{bank}_{card}"
    record = memory.get(key, {"confidence": 0.5, "times_seen": 0})

    record["times_seen"] += 1

    if outcome_improved:
        record["confidence"] = min(record["confidence"] + 0.05, 1.0)
    else:
        record["confidence"] = max(record["confidence"] - 0.05, 0.1)

    memory[key] = record
    save_memory(memory)


def update_learning(current_metrics):
    global last_metrics

    for (bank, card), now in current_metrics.items():
        key = f"{bank}_{card}"

        if (bank, card) in last_metrics:
            prev = last_metrics[(bank, card)]

            if now["success_rate"] > prev["success_rate"]:
                learn(bank, card, True)
            else:
                learn(bank, card, False)

    last_metrics = current_metrics.copy()



def explain(hypotheses):
    print("\n=== AGENT DECISIONS ===")
    for h in hypotheses:
        print(
            f"{h['bank']}-{h['card']} | "
            f"Prob: {h['probability']} | "
            f"Impact: {h['impact_percent']}% | "
            f"Latency: {h['latency']}ms | "
            f"Action: {h['suggested_action']} | "
            f"Errors: {h['errors']}"
        )
