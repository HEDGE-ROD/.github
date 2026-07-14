# Security Policy

This is the org-wide security policy for HEDGE-ROD. It covers
**`hedge-rod-backend`** (detection engine + REST API), **`hedge-rod-frontend`**
(dashboard), and this **`.github`** repo (CI, templates, schema-sync
tooling).

**`hedge-rod-contract`** (the Soroban smart contract) has its own
[`SECURITY.md`](https://github.com/HEDGE-ROD/hedge-rod-contract/blob/main/SECURITY.md)
with a contract-specific threat model (authorization checks, rate limiting,
upgrade governance, score attestation). This document complements that one
— use the same reporting channel and process below for issues in any repo,
and see the contract repo's policy for on-chain-specific detail (upgrade
governance timelines, attestation verification, etc).

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report security issues by emailing **security@hedge-rod.io** with the
subject line:

```
[SECURITY] <short description> <affected repo>
```

Include:

1. A clear description of the vulnerability and the affected repo/component.
2. Steps to reproduce or a proof-of-concept (PoC) — even a pseudocode
   sketch helps.
3. The potential impact (e.g. unauthorized score submission, API data
   exposure, webhook secret leakage, SSRF, dependency vulnerability).
4. Your contact details if you would like to be credited.

## Scope

| Area | Repo | Examples of in-scope issues |
|---|---|---|
| Detection engine / API | `hedge-rod-backend` | Auth bypass on `/admin/*` endpoints, SSRF in webhook subscriber URLs, secret leakage from `HEDGE_ROD_SERVICE_SECRET_KEY` handling, injection in Horizon ingestion, insecure webhook HMAC verification |
| On-chain contract | `hedge-rod-contract` | See [its own SECURITY.md](https://github.com/HEDGE-ROD/hedge-rod-contract/blob/main/SECURITY.md) — authorization, rate limiting, upgrade governance, attestation |
| Dashboard | `hedge-rod-frontend` | XSS via unsanitized API data rendered in the DOM, insecure handling of `config.js`/API base URL |
| CI / supply chain | `.github` | Compromised reusable workflow, secrets exposure in Actions logs, `check_schema_sync.py` supply-chain issues |

Out of scope: findings that require physical access to a user's device,
social engineering of maintainers, or vulnerabilities in third-party
dependencies without a demonstrated HEDGE-ROD-specific exploit path (report
those upstream instead, and let us know if HEDGE-ROD is affected).

## Response Timeline

| Milestone | Target |
|---|---|
| Acknowledgement | Within 48 hours |
| Triage and severity rating | Within 7 days |
| Fix or mitigation | Within 21 days (severity-dependent) |
| Public disclosure | After a fix ships |

We follow [coordinated disclosure](https://en.wikipedia.org/wiki/Coordinated_vulnerability_disclosure)
and will not take legal action against researchers who follow this policy
in good faith.

## Secrets Handling (applies to all repos)

- Never commit `.env`, API keys, or the `HEDGE_ROD_SERVICE_SECRET_KEY` /
  `HEDGE_ROD_WEBHOOK_ENCRYPTION_KEY` values — see each repo's
  `.env.example` for the expected keys, and set real values only via your
  deployment environment's secret manager or GitHub Actions secrets.
- If you find a committed secret in any HEDGE-ROD repo, report it via the
  channel above rather than opening a public issue — treat it as already
  compromised and rotate it immediately once acknowledged.
- CI workflows in this repo (`workflows/`) are scoped to `contents: read`
  by default and do not require elevated tokens for lint/test/build; the
  schema-sync workflow only reads sibling checkouts.

## Supported Versions

HEDGE-ROD is pre-1.0 and under active development for the Stellar Drip Wave
builder programme. Security fixes land on `main` in each repo; there is no
separate long-term-support branch at this stage.
