# HEDGE-ROD org profile

This repo configures the [HEDGE-ROD](https://github.com/HEDGE-ROD) GitHub
organization: the profile page, shared reusable CI workflows, issue/PR
templates, and cross-repo governance docs.

- **Org profile page**: [`profile/README.md`](profile/README.md) — what
  HEDGE-ROD is, the architecture, and where to start.
- **Reusable CI**: [`.github/workflows/`](.github/workflows) — Python, Rust, and frontend
  jobs the other repos call via `workflow_call`.
- **Schema-sync check**: [`scripts/check_schema_sync.py`](scripts/check_schema_sync.py)
  — fails CI when the `RiskScore` schema drifts between
  `hedge-rod-backend` (Python) and `hedge-rod-contract` (Rust).
- **Contributing / governance**: [`CONTRIBUTING.md`](CONTRIBUTING.md),
  [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md), [`SECURITY.md`](SECURITY.md).

The actual product lives in
[`hedge-rod-backend`](https://github.com/HEDGE-ROD/hedge-rod-backend),
[`hedge-rod-contract`](https://github.com/HEDGE-ROD/hedge-rod-contract), and
[`hedge-rod-frontend`](https://github.com/HEDGE-ROD/hedge-rod-frontend).
