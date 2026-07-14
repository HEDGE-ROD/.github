# Reusable CI workflows

These are `workflow_call` workflows other repos in the HEDGE-ROD org call
instead of duplicating CI logic. They mirror what each repo's own CI already
does today (see `python-ci.yml` / `rust-ci.yml` / `frontend-ci.yml` headers
for the source repo each one was modeled on).

| Workflow | Mirrors | Use in |
|---|---|---|
| `python-ci.yml` | `hedge-rod-backend/.github/workflows/ci.yml` (ruff + pytest) | `hedge-rod-backend` |
| `rust-ci.yml` | `hedge-rod-contract/.github/workflows/ci.yml` (fmt + clippy + test + wasm build) | `hedge-rod-contract` |
| `frontend-ci.yml` | new — `hedge-rod-frontend` has no CI today | `hedge-rod-frontend` |

## Calling this workflow

Each downstream repo keeps a thin caller workflow at
`.github/workflows/ci.yml` that delegates to the shared job. Reusable
workflows are referenced with `owner/repo/.github/workflows/<file>.yml@ref`
— because this repo *is* the org's `.github` repo, the path repeats:
`HEDGE-ROD/.github/.github/workflows/<file>.yml@main`.

### `hedge-rod-backend/.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  python:
    uses: HEDGE-ROD/.github/.github/workflows/python-ci.yml@main
    with:
      coverage-args: "--cov=detection --cov=ingestion --cov=config"
```

### `hedge-rod-contract/.github/workflows/ci.yml`

```yaml
name: Contract CI

