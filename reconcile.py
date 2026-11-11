#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from datetime import datetime
from decimal import Decimal

total = Decimal("0")
count = 0
latest = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line, parse_float=Decimal)
        except json.JSONDecodeError:
            continue
        txn_id = event.get("txn_id")
        if not txn_id:
            continue
        timestamp = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
        if txn_id not in latest or timestamp > latest[txn_id][0]:
            latest[txn_id] = (timestamp, event)

for _, event in latest.values():
    if event["status"] == "success":
        total += Decimal(str(event["amount"]).replace(",", ""))
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
