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

