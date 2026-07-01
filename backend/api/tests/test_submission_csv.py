"""Submission CSV format and validator regression tests."""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SUBMISSION = PROJECT_ROOT / "submission.csv"
VALIDATOR = PROJECT_ROOT / "validate_submission.py"


class SubmissionCsvTests(SimpleTestCase):
    def test_submission_file_exists_with_100_rows(self):
        if not SUBMISSION.exists():
            self.skipTest("submission.csv not generated yet")
        with open(SUBMISSION, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 100)
        self.assertEqual(rows[0]["rank"], "1")
        self.assertTrue(rows[0]["candidate_id"].startswith("CAND_"))

    def test_validator_passes(self):
        if not SUBMISSION.exists() or not VALIDATOR.exists():
            self.skipTest("submission or validator missing")
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(SUBMISSION)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
