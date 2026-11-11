"""Regression tests for the reconciliation command (standard library only)."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("reconcile.py")


def event(txn_id, status="success", amount=10, ts="2026-09-01T00:00:00Z"):
    return json.dumps(dict(txn_id=txn_id, status=status, amount=amount,
                           currency="NGN", ts=ts))


class ReconciliationTests(unittest.TestCase):
    def run_fixture(self, lines, expected):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "payments.jsonl").write_text("\n".join(lines), encoding="utf-8")
            (root / "expected.txt").write_text(str(expected), encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPT)], cwd=root,
                                  capture_output=True, text=True)

    def test_latest_attempt_wins_even_when_export_is_out_of_order(self):
        result = self.run_fixture([
            event("paid", amount=75, ts="2026-09-03T00:00:00Z"),
            event("paid", amount=10),
            event("failed", "success"),
            event("failed", "failed", ts="2026-09-02T00:00:00Z"),
            event("pending", "pending", ts="2026-09-02T00:00:00Z"),
            event("pending", "success"),
            event("retried", "failed"),
            event("retried", amount=25, ts="2026-09-02T00:00:00Z"),
        ], 2)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Check passed: 2 successful payments.", result.stdout)
        self.assertIn("Your code: KOYA-100", result.stdout)

    def test_formatted_and_numeric_amounts_are_all_collected(self):
        result = self.run_fixture([
            event("formatted", amount="55,707.77"),
            event("number", amount=10.25),
            event("string", amount="1.99"),
        ], 3)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Your code: KOYA-55720", result.stdout)

    def test_unreadable_lines_and_missing_ids_are_skipped(self):
        result = self.run_fixture([
            "", "{broken", '{"status": "success", "amount": 999}',
            event(None), event(""), event("valid", amount=40),
        ], 1)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Your code: KOYA-40", result.stdout)

    def test_money_is_summed_without_binary_float_precision_loss(self):
        result = self.run_fixture([
            '{"txn_id":"large","status":"success","amount":9007199254740992.49,'
            '"currency":"NGN","ts":"2026-09-01T00:00:00Z"}',
            event("small", amount="0.02"),
        ], 2)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Your code: KOYA-9007199254740993", result.stdout)

    def test_count_mismatch_does_not_print_a_code(self):
        result = self.run_fixture([event("valid")], 2)
        self.assertIn("Check failed: counted 1 successful payments, expected 2.", result.stdout)
        self.assertNotIn("Your code:", result.stdout)

    def test_provided_export_passes_the_finance_count(self):
        result = subprocess.run([sys.executable, str(SCRIPT)], cwd=SCRIPT.parent,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Check passed: 22733 successful payments.", result.stdout)
        self.assertIn("Your code: KOYA-", result.stdout)


if __name__ == "__main__":
    unittest.main()
