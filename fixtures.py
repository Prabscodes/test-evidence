"""Execute only immutable snapshots of bundled fixtures, never submitted code.

This is NOT a sandbox. The allowlisted code is trusted app-owned code. Do not extend
this function to accept source text, file paths, commands, or uploaded test files.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import MappingProxyType

from samples import SAMPLES

# Capture copies once, so consumers editing SAMPLES cannot change executable text.
_TRUSTED = MappingProxyType({item["id"]: MappingProxyType(dict(item)) for item in SAMPLES})
_TIMEOUT_SECONDS = 5
_COMMAND = [sys.executable, "-I", "-c",
            "import sys, unittest, json; sys.path.insert(0, '.'); "
            "suite = unittest.defaultTestLoader.discover('.', pattern='test_subject.py'); "
            "result = unittest.TextTestRunner(verbosity=2).run(suite); "
            "print(json.dumps({'tests_run': result.testsRun, 'assertion_failures': len(result.failures), "
            "'errors': len(result.errors), 'skipped': len(result.skipped), "
            "'successful': result.wasSuccessful(), 'failed_tests': [str(t) for t, _ in result.failures], "
            "'error_tests': [str(t) for t, _ in result.errors]})); "
            "raise SystemExit(not result.wasSuccessful())"]
_REQUIREMENT_ORACLE = '''import unittest
from subject import eligible

class RequirementOracle(unittest.TestCase):
    def test_authoritative_age_threshold(self):
        # Independent app-owned oracle derived directly from the stated requirement.
        for age in (0, 16, 17, 18, 19, 100):
            with self.subTest(age=age):
                self.assertEqual(eligible(age), age >= 18)
'''



def _revision(source: str, tests: str) -> dict:
    return {
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "tests_sha256": hashlib.sha256(tests.encode()).hexdigest(),
        "combined_sha256": hashlib.sha256(json.dumps([source, tests]).encode()).hexdigest(),
    }


def _run(label: str, source: str, tests: str) -> dict:
    result = {"label": label, "command": list(_COMMAND),
              "revision": _revision(source, tests), "timeout_seconds": _TIMEOUT_SECONDS}
    with tempfile.TemporaryDirectory(prefix="test-evidence-trusted-") as directory:
        root = Path(directory)
        (root / "subject.py").write_text(source, encoding="utf-8")
        (root / "test_subject.py").write_text(tests, encoding="utf-8")
        # Only OS necessities, no provider keys or inherited application secrets.
        env = {"PATH": os.defpath, "LANG": "C.UTF-8"}
        try:
            process = subprocess.run(_COMMAND, cwd=root, env=env, capture_output=True,
                                     text=True, timeout=_TIMEOUT_SECONDS, check=False)
            try:
                counts = json.loads(process.stdout.strip().splitlines()[-1])
            except (ValueError, IndexError):
                counts = None
            assertion_failed = bool(counts and counts['assertion_failures'] > 0)
            harness_error = counts is None or counts['errors'] > 0
            result.update(returncode=process.returncode, stdout=process.stdout[:12000],
                          stderr=process.stderr[:12000], timed_out=False, counts=counts,
                          observed_failure=assertion_failed, harness_error=harness_error,
                          outcome='harness_error' if harness_error else
                          'assertion_failure' if assertion_failed else
                          'passed' if counts['tests_run'] > 0 else 'no_tests')
        except subprocess.TimeoutExpired:
            result.update(returncode=None, stdout="", stderr="Trusted fixture exceeded timeout.",
                          timed_out=True, observed_failure=None, harness_error=True, counts=None, outcome='timeout')
    return result


def run_fixture(sample_id: str) -> dict:
    """Run app-bundled revisions for an exact allowlisted ID, not edited UI text."""
    if not isinstance(sample_id, str) or sample_id not in _TRUSTED:
        raise ValueError("Unknown bundled fixture ID")
    sample = _TRUSTED[sample_id]
    runs = [
        _run("baseline", sample["source_before"], sample["tests_before"]),
        _run("candidate", sample["source_after"], sample["tests_after"]),
        _run("retained_tests", sample["source_after"], sample["tests_before"]),
        _run("new_tests_on_before_source", sample["source_before"], sample["tests_after"]),
    ]
    if sample_id == 'missing_regression':
        oracle = _run('independent_requirement_oracle', sample['source_after'], _REQUIREMENT_ORACLE)
        oracle['oracle_basis'] = sample['requirement']
        oracle['oracle_scope'] = 'Separately authored fixture oracle, not retained old tests. Finite selected age cases only.'
        runs.append(oracle)
    baseline = runs[0]
    baseline_valid = baseline['outcome'] == 'passed' and baseline['counts']['tests_run'] > 0
    return {
        "sample_id": sample_id,
        "baseline_valid": baseline_valid,
        "requirement_sha256": hashlib.sha256(sample["requirement"].encode()).hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python_version": sys.version.split()[0],
        "origin": "actual_execution",
        "scope": "Trusted bundled fixture only; not user-edited or uploaded code.",
        "disclaimer": "Passing these finite examples is not proof of correctness. A failure against old tests does not establish which behavior is required.",
        "command": list(_COMMAND),
        "revision": {item["label"]: item["revision"] for item in runs},
        "results": runs,
        "observed_failures": [item["label"] for item in runs if item["observed_failure"] is True],
    }
