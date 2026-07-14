# Contributing to HEDGE-ROD

HEDGE-ROD is an open-source wash-trading / artificial-volume detector for
the Stellar DEX, built across three repos:

- **[hedge-rod-backend](https://github.com/HEDGE-ROD/hedge-rod-backend)** — Python/FastAPI detection engine + REST API (Benford's Law + RF/XGBoost/LightGBM ensemble + SHAP, webhooks, Soroban publisher)
- **[hedge-rod-contract](https://github.com/HEDGE-ROD/hedge-rod-contract)** — Rust/Soroban on-chain risk registry
- **[hedge-rod-frontend](https://github.com/HEDGE-ROD/hedge-rod-frontend)** — vanilla HTML/CSS/JS dashboard

We're actively looking for contributors with **Rust**, **Python**, **ML**,
and **frontend** experience. This doc covers dev setup for each repo, commit
conventions, test/coverage expectations, and — most importantly — the
cross-repo schema-sync rule, since that's the most common source of bugs in
this project.

## Good first issues

New to the project? Look for issues labeled
[`good first issue`](https://github.com/search?q=org%3AHEDGE-ROD+label%3A%22good+first+issue%22+is%3Aopen&type=issues)
across the org. They're scoped to a single repo, don't touch the shared
`RiskScore` schema, and include enough context to start without a
walkthrough. If nothing is labeled yet, open an issue describing what you'd
like to work on and we'll help you find a starting point.

## Dev setup per repo

### hedge-rod-backend (Python)

```bash
git clone https://github.com/HEDGE-ROD/hedge-rod-backend && cd hedge-rod-backend
pip install -r requirements.txt
cp .env.example .env
pytest
```

Common commands (see repo's own `CONTRIBUTING.md` for the full list):

```bash
python cli.py generate-data   # synthetic labelled dataset
python cli.py train           # train RF/XGBoost/LightGBM ensemble
python cli.py serve --reload  # run the local API while iterating
ruff check .                  # lint (line-length 100, py3.10+ target)
pytest --cov=detection --cov=ingestion --cov=config -q
```

### hedge-rod-contract (Rust / Soroban)

```bash
git clone https://github.com/HEDGE-ROD/hedge-rod-contract && cd hedge-rod-contract
cargo fmt --all -- --check
cargo clippy --all-targets -- -D warnings
cargo test --workspace
cargo build --target wasm32-unknown-unknown --release -p hedge-rod-score
```

### hedge-rod-frontend (vanilla JS)

No build step — it's dependency-free static HTML/CSS/JS.

```bash
git clone https://github.com/HEDGE-ROD/hedge-rod-frontend && cd hedge-rod-frontend
./serve.sh                     # http://localhost:5173, needs the backend API running
```

Syntax-check any JS you touch with `node --check path/to/file.js` before
opening a PR — that's what CI runs (see [`.github/workflows/frontend-ci.yml`](.github/workflows/frontend-ci.yml)).

## Commit conventions

Use [conventional commits](https://www.conventionalcommits.org/):

```
<type>: <short description>

<optional longer body>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`.

Examples:

```
feat: add wallet-graph centrality feature to the ML ensemble
fix: clamp confidence to 0-100 in RiskScore.combine
docs: document query_risk_gate fail-closed behavior
```

## Test and coverage expectations

- New functionality needs tests (unit tests at minimum; integration tests
  for API endpoints or contract functions).
- Backend: `pytest` must pass, and CI runs
  `pytest --cov=detection --cov=ingestion --cov=config`. Aim for meaningful
  coverage of new code paths, not just a percentage.
- Contract: `cargo test --workspace` must pass, including any new
  `test_*.rs` module you add for a new function.
- Frontend: there's no formal test runner today; verify manually against a
  running backend and keep changes syntax-clean (`node --check`).
- Lint must pass before requesting review: `ruff check .` (backend),
  `cargo clippy --all-targets -- -D warnings` (contract).

## The cross-repo schema-sync rule

**This is the rule most likely to bite you.** The `RiskScore` record is
defined twice, in two languages, and both definitions must agree:

| Field | Python (`hedge-rod-backend/detection/risk_score.py`) | Rust (`hedge-rod-contract/contracts/hedge-rod-score/src/types.rs`) |
|---|---|---|
| wallet | `str` | `Address` (on-chain caller arg, not stored in the `RiskScore` struct itself) |
| asset_pair | `str` | `Symbol` (same) |
| score | `int` (0-100) | `u32` (0-100) |
| benford_flag | `bool` | `bool` |
| ml_flag | `bool` | `bool` |
| confidence | `int` (0-100) | `u32` (0-100) |
| timestamp | `datetime` | `u64` (ledger timestamp) |

**If you change a field name, type, or range in one, update the other in
the same change set** (or open a tracked follow-up issue and link it in
your PR — see the PR template's "Cross-repo schema impact" checklist).

This repo (`.github`) ships
[`scripts/check_schema_sync.py`](scripts/check_schema_sync.py), a
zero-dependency Python script that parses both definitions and fails if the
field sets don't match (allowing the documented `int<->u32`,
`bool<->bool`, `datetime<->u64` type mapping). Run it locally with sibling
checkouts of `hedge-rod-backend` and `hedge-rod-contract`:

