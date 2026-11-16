"""Simple delayed-feedback simulation; no external services required."""
import argparse, random, time
from datetime import datetime, timezone

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=int, default=20)
    parser.add_argument("--max-delay-seconds", type=float, default=5)
    args = parser.parse_args()
    pending = []
    now = time.time()
    for i in range(args.events):
        impression = {
            "impression_id":f"imp_sim_{i}",
            "created_at":datetime.now(timezone.utc).isoformat(),
            "label_status":"pending",
            "conversion_due":now + random.uniform(0, args.max_delay_seconds)
        }
        pending.append(impression)
    print(f"Created {len(pending)} pending impression labels.")
    while pending:
        current = time.time()
        matured = [x for x in pending if x["conversion_due"] <= current]
        for item in matured:
            # Simulate a conversion/no-conversion outcome only when the delay elapses.
            item["label_status"] = random.choice(["positive", "mature_negative"])
            print(item["impression_id"], "=>", item["label_status"])
            pending.remove(item)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
