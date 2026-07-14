## Summary

<!-- What does this PR change, and why? -->

## Repo / area

- [ ] hedge-rod-backend
- [ ] hedge-rod-contract
- [ ] hedge-rod-frontend
- [ ] .github (org repo)

## Type of change

- [ ] fix
- [ ] feat
- [ ] refactor
- [ ] docs
- [ ] test
- [ ] chore / ci

## Cross-repo schema impact

Does this PR change the shared `RiskScore` schema, the `Trade`/`Asset`/
`OrderBookEvent` schemas, the Soroban contract interface
(`submit_score` / `get_score` / `query_risk_gate`), or any shared
environment variable / config key?

- [ ] No — purely local to this repo
- [ ] Yes — and the matching change has been made (or a tracked follow-up
      issue opened) in the corresponding repo(s):

<!-- List the follow-up issue/PR link(s) here if applicable -->

If you checked "Yes", run `scripts/check_schema_sync.py` from the
`.github` repo against sibling checkouts of `hedge-rod-backend` and
`hedge-rod-contract` before merging — see that repo's README for the
checkout layout CI expects.

## Testing

<!-- How was this verified? Include commands run and their output. -->

- [ ] Tests pass locally (`pytest` / `cargo test --workspace` / `node --check`, as applicable)
- [ ] New behavior has test coverage
- [ ] Lint passes (`ruff check .` / `cargo clippy -- -D warnings`, as applicable)

## Checklist

- [ ] I've read [CONTRIBUTING.md](https://github.com/HEDGE-ROD/.github/blob/main/CONTRIBUTING.md)
- [ ] Commit messages follow the conventional-commit style (`feat:`, `fix:`, `docs:`, ...)
- [ ] Documentation (README, CHANGELOG, or docs/) updated for any user-facing change
- [ ] No secrets, keys, or credentials included in this diff
