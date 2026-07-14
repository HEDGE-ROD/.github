#!/usr/bin/env python3
"""Self-test for check_schema_sync.py — stdlib only, no third-party deps.

Runs check_schema_sync.py as a subprocess against two fixture pairs:

  * fixtures/in_sync/   — Python and Rust RiskScore definitions that agree.
                           Expected: exit 0, "OK" printed.
  * fixtures/mismatch/  — deliberately drifted definitions (missing
                           `ml_flag`, `confidence` retyped to `bool`).
                           Expected: exit 1, drift lines printed for both
                           the missing field and the type mismatch.

This is what CI (or a contributor) runs to prove the checker actually
catches drift, not just that it runs without crashing.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECK_SCRIPT = HERE / "check_schema_sync.py"


def run_check(backend: Path, contract: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), "--backend", str(backend), "--contract", str(contract)],
        capture_output=True,
        text=True,
    )


def main() -> int:
    failures: list[str] = []

    # --- Case 1: in-sync fixtures must PASS ---------------------------------
    in_sync = HERE / "fixtures" / "in_sync"
    result = run_check(in_sync / "hedge-rod-backend", in_sync / "hedge-rod-contract")
    print("=== self-test: in_sync fixtures ===")
    print(result.stdout)
    if result.returncode != 0:
        failures.append(f"in_sync fixtures: expected exit 0, got {result.returncode}")
    if "OK: RiskScore schema is in sync" not in result.stdout:
        failures.append("in_sync fixtures: expected 'OK' message not found in output")

    # --- Case 2: mismatch fixtures must FAIL --------------------------------
    mismatch = HERE / "fixtures" / "mismatch"
    result = run_check(mismatch / "hedge-rod-backend", mismatch / "hedge-rod-contract")
    print("=== self-test: mismatch fixtures ===")
    print(result.stdout)
    if result.returncode == 0:
        failures.append(f"mismatch fixtures: expected non-zero exit, got {result.returncode}")
    if "SCHEMA DRIFT DETECTED" not in result.stdout:
        failures.append("mismatch fixtures: expected 'SCHEMA DRIFT DETECTED' not found in output")
    if "ml_flag" not in result.stdout:
        failures.append("mismatch fixtures: expected the dropped field 'ml_flag' to be reported")
    if "confidence" not in result.stdout or "type mismatch" not in result.stdout:
        failures.append("mismatch fixtures: expected a type mismatch on 'confidence' to be reported")

    print("=== self-test summary ===")
    if failures:
        print(f"FAILED ({len(failures)} problem(s)):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("PASSED: check_schema_sync.py correctly passes in-sync fixtures and fails mismatched fixtures.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
