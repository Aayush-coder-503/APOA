from simulator import adjust_health
from collections import defaultdict
import time

active_actions = {}

MAX_SHIFT = 0.5        
ACTION_DURATION = 60 

def apply_action(hypothesis):
    bank = hypothesis["bank"]
    card = hypothesis["card"]
    action = hypothesis["suggested_action"]

    key = f"{bank}_{card}"

    if action == "partial_reroute":
        if key in active_actions:
            return False 

        print(f"\n[ACT] Rerouting 50% of traffic away from {bank}-{card}")

        adjust_health(bank, card, 1.0 - MAX_SHIFT)

        active_actions[key] = {
            "bank": bank,
            "card": card,
            "start": time.time()
        }

        return True

    elif action == "monitor_and_alert":
        print(f"[ALERT] {bank}-{card} looks unstable. Monitoring.")
        return False

    return False


def check_rollbacks():
    now = time.time()
    to_remove = []

    for key, info in active_actions.items():
        if now - info["start"] > ACTION_DURATION:
            print(f"\n[ROLLBACK] Restoring normal routing for {info['bank']}-{info['card']}")
            adjust_health(info["bank"], info["card"], 1.0)
            to_remove.append(key)

    for k in to_remove:
        del active_actions[k]