# Payment reconciliation

`payments.jsonl` is an export of payment events from a payments provider, one JSON object per line. The reconciliation script is meant to work out how much money was actually collected, but it doesn't work.

Fix it, in Python (`reconcile.py`) or JavaScript (`reconcile.js`), whichever you prefer. When it's right, it prints a code. Paste that code into the application form.

## Run the fixed Python version

From this repository's directory, run `python3 reconcile.py`. It uses only the
Python standard library. Run the regression tests with `python3 -m unittest -v`.

The Python script skips unreadable lines and missing transaction IDs, selects
each transaction's latest timestamp before checking its status, and sums amounts
with decimal arithmetic, including amounts formatted with thousands separators.

## How the data works

- Each line is one event: `txn_id`, `status` (`success`, `failed` or `pending`), `amount` in naira, `currency`, and `ts` (when it happened, UTC).
- A payment can be attempted more than once. Every attempt has the same `txn_id`. Only the latest attempt for each `txn_id` counts.
- A payment counts as collected only if its latest attempt is `success`.
- The export comes from a production system and isn't perfectly clean. Ignore lines that can't be read, and events without a `txn_id`. Every other event is valid and must be counted correctly.
- `expected.txt` holds the number of successful payments the finance team counted by hand. The script checks itself against it.

## What to submit

1. Fork this repo, fix the script, and commit your fix to your fork.
2. Run it. Paste the code it prints into the form.
3. Paste the link to your fork into the form.
