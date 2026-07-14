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

