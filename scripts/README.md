# scripts/

## check_schema_sync.py

Fails when the `RiskScore` schema drifts between:

- **Python** — `hedge-rod-backend/detection/risk_score.py` (pydantic `BaseModel`)
- **Rust** — `hedge-rod-contract/contracts/hedge-rod-score/src/types.rs` (`#[contracttype] pub struct RiskScore`)

Pure Python 3 stdlib — no `pyyaml`, no `pydantic`, no third-party parser.
It reads both source files as text and extracts `name: type` pairs with
regexes scoped to each language's field-declaration syntax, then compares
field sets using the documented type mapping (`int<->u32`, `bool<->bool`,
`datetime<->u64`) and the documented exclusion of the on-chain storage-key
fields `wallet` / `asset_pair` (the Rust struct doesn't carry them — Soroban
stores it under `DataKey::Score(Address, Symbol)` instead).

### Local usage

Because this is the org's `.github` repo, `check_schema_sync.py` expects
the two other repos checked out as siblings of this repo (or pass explicit
`--backend` / `--contract` paths):

```
some-workspace/
├── .github/                 ← this repo
├── hedge-rod-backend/
└── hedge-rod-contract/
```

```bash
cd .github
python3 scripts/check_schema_sync.py \
  --backend ../hedge-rod-backend \
  --contract ../hedge-rod-contract
```

Defaults are already `../hedge-rod-backend` and `../hedge-rod-contract`, so
with that layout you can just run:

```bash
python3 scripts/check_schema_sync.py
```

### In CI

`.github/workflows/schema-sync.yml` checks out all three repos side by side
in the runner workspace (`actions/checkout` with an explicit `path:` per
repo) and then runs the script against those checkouts — see that workflow
for the exact steps. It runs on push/PR to this repo and on a weekly
schedule, since drift can be introduced by a merge in either sibling repo
without anything changing here.

### Actual result against the real repos (2026-07-14)

Running the script against the real `hedge-rod-backend` and
`hedge-rod-contract` checkouts in this environment currently reports **real
drift**, not a clean pass:

```
Rust    RiskScore (.../hedge-rod-contract/.../types.rs):
  score:u32, benford_flag:bool, ml_flag:bool, timestamp:u64, confidence:u32, model_version:u32

SCHEMA DRIFT DETECTED between hedge-rod-backend and hedge-rod-contract RiskScore:
  + field 'model_version' (u32) exists in Rust RiskScore but not in Python RiskScore
```

The Rust `RiskScore` struct has picked up a `model_version: u32` field
(added for model-version tracking, per its own doc comment) that was never
mirrored into the Python `RiskScore` in `hedge-rod-backend`. This is exactly
the class of bug this checker exists to catch — see the corresponding
tracked follow-up issue in `hedge-rod-backend` (either add `model_version`
to the Python model, or, if it's meant to stay contract-internal, document
that exclusion the same way `wallet`/`asset_pair` are documented here and
update `IDENTITY_FIELDS_NOT_ON_CHAIN` accordingly).

## self_test_schema_sync.py

Proves `check_schema_sync.py` actually detects drift, not just that it runs
without crashing. Runs the checker against two fixture pairs under
`fixtures/`:

- `fixtures/in_sync/` — matching Python/Rust definitions → expects exit 0.
- `fixtures/mismatch/` — deliberately missing `ml_flag` and a `confidence`
  type flipped to `bool` → expects exit 1, with both problems named in the
  output.

```bash
python3 scripts/self_test_schema_sync.py
```
