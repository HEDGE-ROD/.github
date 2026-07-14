#!/usr/bin/env python3
"""Fail CI when the shared RiskScore schema drifts between repos.

HEDGE-ROD defines the `RiskScore` record twice, in two languages:

  * Python  — hedge-rod-backend/detection/risk_score.py   (pydantic BaseModel)
  * Rust    — hedge-rod-contract/contracts/hedge-rod-score/src/types.rs (#[contracttype] struct)

The backend README calls this out explicitly: "translation layers are a
common source of bugs." This script parses both definitions with plain
string/regex handling (stdlib only, no third-party deps — this environment
has no pip) and asserts the field sets agree, modulo the documented type
mapping (int<->u32, bool<->bool, datetime<->u64) and the documented
exclusion of the on-chain storage-key fields `wallet` / `asset_pair`
(the Rust `RiskScore` struct does not carry them — they're the map key
`DataKey::Score(Address, Symbol)` under which the struct is stored, per
hedge-rod-contract's own README).

Usage:
    python3 check_schema_sync.py [--backend PATH] [--contract PATH]

Exit codes:
    0  schemas match
    1  schemas differ (prints a diff)
    2  one of the source files could not be found/parsed
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Fields that exist on the Python RiskScore but are intentionally absent
# from the Rust struct because they're the on-chain storage *key*
# (DataKey::Score(Address, Symbol)), not part of the stored value.
# Documented in hedge-rod-contract's README ("RiskScore Structure") and in
# this org's CONTRIBUTING.md.
IDENTITY_FIELDS_NOT_ON_CHAIN = {"wallet", "asset_pair"}

# Documented cross-language type equivalences for the fields that ARE
# expected to match between the two definitions.
TYPE_EQUIVALENCE = {
    "int": {"u32", "u64", "i32", "i64"},
    "bool": {"bool"},
    "datetime": {"u64"},  # datetime <-> ledger timestamp (u64)
    "str": {"Address", "Symbol", "BytesN", "Bytes"},
}


@dataclass(frozen=True)
class Field:
    name: str
    type_: str


def _strip_comments(text: str) -> str:
    # Remove Rust doc comments (///, //!, //) and Python comments (#) on
    # each line so they never smuggle in a lookalike field.
    lines = []
    for line in text.splitlines():
        stripped = line
        for marker in ("///", "//!", "//"):
            idx = stripped.find(marker)
            if idx != -1:
                stripped = stripped[:idx]
        if "#" in stripped:
            # crude but sufficient here: Python source in this file has no
            # '#' inside the RiskScore class body other than comments.
            stripped = stripped.split("#", 1)[0]
        lines.append(stripped)
    return "\n".join(lines)


def parse_python_risk_score(path: Path) -> list[Field]:
    """Parse the `class RiskScore(BaseModel): ...` block field:type pairs."""
    if not path.is_file():
        raise FileNotFoundError(f"Python RiskScore source not found: {path}")

    text = _strip_comments(path.read_text())

    class_match = re.search(r"^class RiskScore\([^)]*\):\s*\n(.*?)(?=^class |\Z)", text, re.MULTILINE | re.DOTALL)
    if not class_match:
        raise ValueError(f"Could not find 'class RiskScore(...):' block in {path}")

    body = class_match.group(1)
    fields: list[Field] = []
    # Matches lines like:  score: int = Field(ge=0, le=100, ...)
    # or plain:            wallet: str
    field_pattern = re.compile(r"^\s{4}([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE)
    for line in body.splitlines():
        # Stop at the first method/classmethod definition — fields are
        # only ever declared before the first `def`.
        if re.match(r"^\s{4}(def |@)", line):
            break
        m = field_pattern.match(line)
        if m:
            fields.append(Field(name=m.group(1), type_=m.group(2)))

    if not fields:
        raise ValueError(f"Parsed zero fields from RiskScore in {path} — regex likely out of date")
    return fields


def parse_rust_risk_score(path: Path) -> list[Field]:
    """Parse the `pub struct RiskScore { ... }` block field:type pairs."""
    if not path.is_file():
        raise FileNotFoundError(f"Rust RiskScore source not found: {path}")

    text = _strip_comments(path.read_text())

    # Find the specific `pub struct RiskScore { ... }` block (not
    # ScoreSubmission / AggregateRiskScore / etc., which share some field
    # names but are different types).
    struct_match = re.search(r"pub struct RiskScore\s*\{(.*?)\n\}", text, re.DOTALL)
    if not struct_match:
        raise ValueError(f"Could not find 'pub struct RiskScore {{ ... }}' in {path}")

