import random
import time
import uuid
from datetime import datetime

BANKS = ["HDFC", "SBI", "ICICI", "AXIS"]
CARDS = ["VISA", "MASTERCARD", "RUPAY"]

# Baseline success probabilities
BASE_SUCCESS = {
    ("HDFC", "VISA"): 0.96,
    ("HDFC", "MASTERCARD"): 0.95,
    ("SBI", "VISA"): 0.97,
    ("SBI", "MASTERCARD"): 0.96,
    ("ICICI", "VISA"): 0.95,
    ("ICICI", "MASTERCARD"): 0.95,
    ("AXIS", "VISA"): 0.94,
    ("AXIS", "MASTERCARD"): 0.94,
}

health_modifiers = {
    key: 1.0 for key in BASE_SUCCESS.keys()
}

ACTIVE_OUTAGE = None 


def set_outage(bank, card, severity=0.5):
    global ACTIVE_OUTAGE
    ACTIVE_OUTAGE = (bank, card, severity)

def clear_outage():
    global ACTIVE_OUTAGE
    ACTIVE_OUTAGE = None

def adjust_health(bank, card, multiplier):
    health_modifiers[(bank, card)] = multiplier

def generate_payment():
    bank = random.choice(BANKS)
    card = random.choice(CARDS)

    base = BASE_SUCCESS.get((bank, card), 0.95)
    modifier = health_modifiers.get((bank, card), 1.0)

    success_prob = base * modifier

    if ACTIVE_OUTAGE:
        o_bank, o_card, severity = ACTIVE_OUTAGE
        if bank == o_bank and card == o_card:
            success_prob *= severity

    success = random.random() < success_prob

    latency = random.randint(300, 2000)
    if not success:
        latency += random.randint(500, 2000)

    error = None
    if not success:
        error = random.choice(["timeout", "issuer_decline", "network_error"])

    return {
        "payment_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "bank": bank,
        "card": card,
        "amount": round(random.uniform(10, 500), 2),
        "latency_ms": latency,
        "status": "success" if success else "fail",
        "error_code": error
    }


def stream_payments(callback, rate_per_sec=5):
    while True:
        event = generate_payment()
        callback(event)
        time.sleep(1 / rate_per_sec)



if __name__ == "__main__":
    def print_event(e):
        print(e)

    print("Starting payment simulator...")
    stream_payments(print_event, rate_per_sec=2)
