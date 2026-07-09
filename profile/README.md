# HEDGE-ROD Dashboard 🔍

[![Built on Stellar](https://img.shields.io/badge/Built%20on-Stellar-blue?logo=stellar)](https://stellar.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Lightweight web dashboard for **HEDGE-ROD** — wash-trading and artificial-volume
risk scores for the Stellar DEX. It is a dependency-free static app (vanilla
HTML/CSS/JS) that reads from the [`hedge-rod-backend`](https://github.com/HEDGE-ROD/hedge-rod-backend)
REST API.

## Features

- **Score lookup** — risk score (0–100) for a wallet + asset pair, with Benford
  and ML flags plus the top SHAP feature contributions
- **Recent alerts** — wallets at or above the alert threshold (score ≥ 75)
- **Asset risk ranking** — average risk score and wallet count per asset pair
- **Live stats + health indicator**, auto-refreshing every 60s

## Quick start

The dashboard needs the backend API running first (default `http://localhost:8000`):

```bash
# in the hedge-rod-backend repo
uvicorn api.main:app --reload
```

Then serve the dashboard:

```bash
./serve.sh            # http://localhost:5173
# or: python3 -m http.server 5173
```

## Configuration

Point the dashboard at a different API by editing [`config.js`](config.js):

```js
window.HEDGE_ROD_API = "https://api.your-host.example";
```

## API endpoints consumed

| Endpoint | Used for |
|---|---|
| `GET /health` | status indicator |
| `GET /scores` | wallets-scored stat |
| `GET /scores/{wallet}` | score lookup card |
| `GET /scores/{wallet}/explain` | SHAP feature contributions |
| `GET /alerts` | recent alerts table + flagged stat |
| `GET /assets/risk-ranking` | asset ranking grid + stats |

## License

MIT — see [LICENSE](LICENSE).
# HEDGE-ROD 🔍

[![Built on Stellar](https://img.shields.io/badge/Built%20on-Stellar-blue?logo=stellar)](https://stellar.org)
[![Soroban Smart Contracts](https://img.shields.io/badge/Smart%20Contracts-Soroban-purple)](https://soroban.stellar.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)


Hybrid on-chain fraud detection for the Stellar DEX — detecting wash trading and artificial volume using Benford's Law combined with ensemble machine learning, with risk scores anchored on Soroban.

## Overview

HEDGE-ROD is a fraud detection system for the Stellar Decentralised Exchange (SDEX). It ingests trade data from the Stellar Horizon API, scores wallets and asset pairs for wash-trading risk using a combination of Benford's Law digit-distribution analysis and ensemble ML classifiers, and publishes those scores both via a public REST API and an on-chain Soroban contract so other protocols can consume them natively.

### The Problem

Wash trading — simultaneously buying and selling the same asset to artificially inflate trading volume — is one of the most pervasive forms of market manipulation in DeFi. Blockchain transparency means every transaction is recorded, but the sheer volume of on-chain activity makes manual detection impossible.

On DEXs, wash trading causes real harm:

- **Traders are misled** into believing an asset has genuine liquidity and market interest when it does not
- **Token issuers manipulate rankings** on DEX aggregators and data platforms by inflating 24-hour volume figures
- **Liquidity providers lose funds** by entering pools that appear active but are dominated by self-dealing activity
- **Ecosystem credibility suffers** — inflated volume metrics on the Stellar DEX undermine confidence from institutional participants, exchanges, and new users

Existing detection approaches are either manual (slow and unscalable) or rely on simple heuristics (easily gamed). No production-grade, open-source wash trading detection system exists for the Stellar DEX — HEDGE-ROD is built to fill that gap.

### What HEDGE-ROD Does

At a high level, it does three things:

- **🔍 Detects** — identifies wallet pairs, trading clusters, and asset pools exhibiting statistically anomalous transaction patterns consistent with wash trading, including circular trade routing, self-matching order behaviour, and artificial volume concentration
- **📊 Scores** — assigns each wallet and each trading pair a **HEDGE-ROD Risk Score (0–100)** based on the combined output of its Benford anomaly metrics and ML classifiers, updating continuously as new ledger data is processed
- **📡 Reports** — exposes risk scores and flagged activity through a public API and lightweight dashboard, making the intelligence accessible to DEX users, protocol teams, wallet providers, and compliance integrators without requiring technical expertise

## Features

- **Benford's Law Anomaly Engine**: Chi-square, per-digit Z-score, and MAD analysis of transaction amounts across rolling time windows (1h, 4h, 24h, 7d, 30d)
- **Ensemble ML Scoring**: Random Forest, XGBoost, and LightGBM classifiers trained on labelled wash-trade patterns with SHAP interpretability
- **HEDGE-ROD Risk Score (0–100)**: Continuously updated composite score per wallet and per trading pair
- **On-Chain Risk Registry**: Soroban smart contract exposes risk scores so AMMs, lending protocols, and aggregators can gate suspicious activity natively
- **Public REST API**: Query scores, recent alerts, and asset risk rankings
- **Lightweight Dashboard**: Web UI for risk-score visibility without requiring technical expertise
- **Open Methodology**: Scores, features, and training data are fully transparent and auditable

## Architecture

```mermaid
graph TB
    subgraph Ingestion["Layer 1: Data Ingestion"]
        HOR[Stellar Horizon API]
        STREAM[horizon_streamer.py]
        HIST[historical_loader.py]
    end

    subgraph Detection["Layer 2: Detection Engine"]
        BENF[benford_engine.py]
        FEAT[feature_engineering.py]
        TRAIN[model_training.py]
        INFER[model_inference.py]
        SHAP[shap_explainer.py]
        SCORE[HEDGE-ROD Risk Score]
    end

    subgraph Output["Layer 3: Contract + API"]
        CONTRACT[Soroban Contract\nhedge-rod-score]
        API[FastAPI REST API]
        DASH[Web Dashboard]
        WEBHOOK[Webhook Alerts]
    end

    subgraph Consumers["Ecosystem Consumers"]
        AMM[AMMs / Lending Protocols]
        AGG[DEX Aggregators]
        USERS[Traders / Issuers]
    end

    HOR --> STREAM
    HOR --> HIST
    STREAM --> FEAT
    HIST --> FEAT
    FEAT --> BENF
    FEAT --> TRAIN
    TRAIN --> INFER
    BENF --> SCORE
    INFER --> SCORE
    SCORE --> SHAP
    SCORE --> CONTRACT
    SCORE --> API
    API --> DASH
    API --> WEBHOOK
    CONTRACT -->|get_score| AMM
    CONTRACT -->|get_score| AGG
    API --> USERS
```

### Core Components

- **ingestion/horizon_streamer.py**: Real-time trade data from the Horizon API (SSE / per-ledger polling)
- **ingestion/historical_loader.py**: Bulk historical trade ingestion
- **ingestion/operations_loader.py**: Order-book event ingestion (offer create/update/cancel) from Horizon operations
- **ingestion/account_loader.py**: Account funding-source and creation-time metadata for wallet-graph features
- **ingestion/data_models.py**: Pydantic schemas for trade, asset, and order-book records
- **detection/benford_engine.py**: Benford's Law feature computation (chi-square, Z-score, MAD)
- **detection/feature_engineering.py**: On-chain ML feature extraction
- **detection/risk_score.py**: Shared `RiskScore` schema and Benford+ML score blending
- **detection/model_training.py**: Trains the Random Forest / XGBoost / LightGBM ensemble
- **detection/model_inference.py**: Real-time risk scoring
- **detection/shap_explainer.py**: SHAP-based interpretability layer

The REST API ships in this repo under `api/`. The Soroban contract and the web
dashboard live in the `hedge-rod-contract` and `hedge-rod-frontend` repos
respectively — see [HEDGE-ROD Organization](#hedge-rod-organization).

## Benford's Law on the Blockchain

Benford's Law predicts that the leading digit of naturally occurring transaction amounts follows a known, non-uniform distribution (digit 1 ≈ 30.1%, digit 9 ≈ 4.6%). Wash-trading bots tend to use fixed lot sizes or round/algorithmic amounts, producing distributions that diverge from this expectation.

| Metric | What it measures |
|---|---|
| **Chi-square statistic** | Whether the overall digit distribution deviates significantly from Benford's expected distribution |
| **Z-score (per digit)** | Whether any individual digit (1–9) appears with significantly higher or lower frequency than expected |
| **Mean Absolute Deviation (MAD)** | Composite divergence measure; values above 0.015 indicate non-conformity |

Benford signals alone are insufficient (legitimate market makers can also be non-Benford), so they are combined with the ML layer below.

## Machine Learning Layer

### Feature groups (26 features, see `detection/feature_engineering.FEATURE_NAMES`)

- **Benford features (15)**: Chi-square, Z-score, and MAD across 5 rolling windows (1h, 4h, 24h, 7d, 30d)
- **Trade pattern features (4)**: counterparty concentration ratio, round-trip trade frequency, self-matching rate, order cancellation rate
- **Volume and timing features (4)**: volume-to-unique-counterparty ratio, intra-minute clustering, off-hours activity ratio, volume spike frequency
- **Wallet graph features (3)**: funding source similarity, network centrality within the trading graph, account age at time of activity

### Models

| Model | Role |
|---|---|
| **Random Forest** | Stable baseline; handles missing features gracefully |
| **XGBoost** | Primary classifier; strongest performance on tabular on-chain data |
| **LightGBM** | High-speed inference for real-time scoring |

Models are trained with **SMOTE** for class imbalance and evaluated with **AUC-ROC**, **Precision-Recall AUC**, and **F1-score**. SHAP values provide per-score interpretability.

## Soroban Smart Contract Layer

The Soroban contract is the on-chain truth layer for HEDGE-ROD risk scores.

### Contract Functions

- `submit_score(wallet: Address, asset_pair: Symbol, score: u32, timestamp: u64)` - Registers a computed risk score on-chain (authorised HEDGE-ROD service account only)
- `get_score(wallet: Address, asset_pair: Symbol) -> RiskScore` - Read-only; returns the most recent risk score and timestamp for a wallet/asset pair, callable by any other Soroban contract

```rust
// Simplified Soroban interface (Rust pseudocode)
pub struct RiskScore {
    pub score: u32,          // 0–100; higher = more suspicious
    pub benford_flag: bool,  // True if Benford anomaly detected
    pub ml_flag: bool,       // True if ML classifier flagged
    pub timestamp: u64,      // Ledger timestamp of last update
    pub confidence: u32,     // Model confidence 0–100
}
```

This composability lets AMMs, lending protocols, and DEX aggregators on Stellar query HEDGE-ROD scores natively — for example, gating liquidity provision from wallets above a configurable risk threshold — without an external oracle.

### Soroban Integration (`detection/soroban_publisher.py`)

After each pipeline run, all `RiskScore` records above `RISK_SCORE_THRESHOLD` are submitted on-chain via `SorobanPublisher.submit_batch()`. This transforms HEDGE-ROD from a standalone detection tool into composable on-chain financial infrastructure.

**Configuration** (see `.env.example` for defaults):

| Variable | Purpose |
|---|---|
| `HEDGE_ROD_SCORE_CONTRACT_ID` | Soroban contract ID of the deployed `hedge-rod-score` contract |
| `HEDGE_ROD_SERVICE_SECRET_KEY` | **Secret**: Stellar account key authorized to call `submit_score()` on the contract |
| `SOROBAN_RPC_URL` | Soroban RPC endpoint (separate from Horizon; defaults to Testnet) |
| `NETWORK_PASSPHRASE` | Stellar network passphrase (must match the network the contract is on) |
| `SOROBAN_CIRCUIT_BREAKER_THRESHOLD` | Consecutive failures before the circuit opens (default: 5) |
| `SOROBAN_CIRCUIT_RESET_SECONDS` | Seconds until the circuit resets (default: 300) |

**Transaction lifecycle**:

1. **Build** — create an `InvokeContractFunction` operation for `submit_score(wallet, asset_pair, score, timestamp)`
2. **Simulate** — call `simulate_transaction` to obtain the resource fee
3. **Sign** — sign with the service account keypair (in-process; the key never leaves the machine)
4. **Submit** — `send_transaction` with the signed transaction
5. **Poll** — `get_transaction` every 1 second until `SUCCESS` or `FAILED`

**Error handling & retry logic**:

- `tx_bad_seq` — refresh the account sequence number and retry once
- `INSUFFICIENT_FEE` — multiply the fee by 1.5 and retry once
- Soroban `auth_failed` — log `ERROR` and raise `SorobanSubmissionError` immediately (do not retry — the service key is misconfigured)
- All other errors — log `WARNING`, record the failure, and include the error in the `submit_batch` results dict

**Circuit breaker**: after `SOROBAN_CIRCUIT_BREAKER_THRESHOLD` consecutive failures within a 60-second rolling window, the publisher stops calling the contract and raises `SorobanCircuitOpenError`. The circuit auto-resets after `SOROBAN_CIRCUIT_RESET_SECONDS`. This prevents submission storms on contract failures without blocking the pipeline.

**Security**:
- `HEDGE_ROD_SERVICE_SECRET_KEY` is converted to a `Keypair` at construction time; the raw key string is not retained as an instance variable
- The keypair object's secret is never included in `__repr__`, logs, or the `on_chain_submissions` audit table
- The publisher overrides `__getstate__` to exclude the keypair from pickle serialization
- Running with `--no-submit` (via `cli.py score --no-submit`) skips all on-chain calls

**Audit log**: every submission attempt (success, failure, or skip) is written to the `on_chain_submissions` table in the local SQLite store. The table records wallet, asset pair, score, transaction hash (if available), status, error message, and timestamp.

## Repository Structure

This repository (`hedge-rod-backend`) contains the detection engine and the
public REST API. The web dashboard and Soroban contract live in separate
repos — see [HEDGE-ROD Organization](#hedge-rod-organization) below.

```
hedge-rod-backend/
│
├── README.md                         ← This file
├── requirements.txt                  ← Python dependencies
├── pyproject.toml                    ← Project metadata, pytest config
├── .env.example                      ← Configuration template (incl. cross-repo keys)
├── run_pipeline.py                   ← Full detection pipeline entry point
├── cli.py                            ← `hedge-rod` CLI (generate-data, train, score, serve)
├── Dockerfile / docker-compose.yml   ← Containerized local API
│
├── config/
│   └── settings.py                   ← Environment-driven configuration
│
├── ingestion/
│   ├── horizon_streamer.py           ← Real-time trade data from Horizon API
│   ├── historical_loader.py          ← Bulk historical trade ingestion
│   ├── operations_loader.py          ← Order-book event ingestion (offer ops)
│   ├── account_loader.py             ← Account funding-source / creation-time metadata
│   ├── synthetic_data.py             ← Synthetic trade/wash-ring generator for local training
│   ├── http_client.py                ← Retrying HTTP helper for Horizon calls
│   └── data_models.py                ← Pydantic schemas for trade/asset/order-book records
│
├── detection/
│   ├── benford_engine.py             ← Benford's Law feature computation
│   ├── feature_engineering.py        ← On-chain ML feature extraction
│   ├── dataset.py                    ← Labelled feature dataset builder (training)
│   ├── model_training.py             ← Train ensemble classifiers
│   ├── model_inference.py            ← Real-time risk scoring
│   ├── shap_explainer.py             ← SHAP interpretability layer
│   ├── risk_score.py                 ← Shared `RiskScore` schema + scoring logic
│   └── storage.py                    ← SQLite-backed local RiskScore store
│
├── api/
│   └── main.py                       ← Local read-only FastAPI app serving RiskScores
│
└── tests/
    └── ...
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Fill in the Horizon, model, and cross-repo settings described in
[HEDGE-ROD Organization](#hedge-rod-organization).

### 3. Train on synthetic data

No external labelled dataset is required to get started —
`cli.py train` generates a synthetic trade history with labelled
wash-trading rings (`ingestion/synthetic_data.py`) and trains the
RF/XGBoost/LightGBM ensemble on it:

```bash
python cli.py train
```

### 4. Run the detection pipeline

```bash
python run_pipeline.py
```

This scores each wallet/asset-pair combination and writes the resulting
`RiskScore` records to the local SQLite store (`HEDGE_ROD_DB_PATH`).

### 5. Serve the local API

```bash
python cli.py serve --reload
```

Exposes `/health`, `/scores`, `/scores/{wallet}`, `/alerts`, and
`/assets/risk-ranking` over the locally stored `RiskScore` records. This is
the project's REST API, consumed directly by `hedge-rod-frontend`.

> The web dashboard and Soroban contract live in their respective repos
> (`hedge-rod-frontend`, `hedge-rod-contract`).

### Docker

```bash
docker compose up --build
```

## CLI Reference

```bash
python cli.py generate-data   # write synthetic trades/labels to CSV
python cli.py train           # train the ensemble on synthetic data
python cli.py score           # run the pipeline against live Horizon data
python cli.py retrain-check   # check for distribution drift and retrain if needed
python cli.py serve           # serve the local API
python cli.py webhook-worker  # run the webhook delivery worker
python cli.py db-migrate      # apply any pending SQLite schema migrations
```

## Continuous Retraining

HEDGE-ROD models are trained once on synthetic data, but in production, wash-trading strategies evolve — bots adapt their lot sizes, timing patterns, and circular routing to evade detection. Without detecting and responding to this **concept drift**, model performance silently degrades over time.

The continuous retraining pipeline automatically monitors the distribution of features in production scoring and triggers retraining when drift is detected, with safe rollback to the previous model if the new model underperforms.

### Drift Detection Methodology

Drift is detected using the **Population Stability Index (PSI)**, a statistical measure of how much a feature distribution has shifted between training and production:

$$\text{PSI} = \sum_{i=1}^{n} \left( \text{current}_i - \text{training}_i \right) \times \ln\left(\frac{\text{current}_i}{\text{training}_i}\right)$$

**PSI Interpretation:**
- **PSI = 0**: Distributions are identical
- **0 < PSI < 0.10**: Negligible drift; no action needed
- **0.10 ≤ PSI < 0.20**: Small drift; monitor closely
- **PSI ≥ 0.20**: Significant drift; retraining recommended
- **PSI > 0.25**: Severe drift; retraining strongly advised

Drift is declared when **at least 3 features** exceed PSI threshold (default 0.20). This threshold minimizes false positives from natural market dynamics while capturing genuine performance-degrading drift.

### Running Drift Checks

After the pipeline records scored features (automatic on each `python cli.py score` run), trigger a drift check and potential retrain:

```bash
python cli.py retrain-check
```

**Options:**
- `--psi-threshold 0.20`: PSI threshold for marking a feature as drifted (default 0.20)
- `--min-drifted-features 3`: Minimum number of drifted features to trigger retraining (default 3)
- `--force-retrain`: Force retraining even if no drift detected (useful for manual updates)

**What happens:**
1. Computes PSI for all features, comparing production data (last 30 days) against training reference
2. If drift detected (or force-retrain enabled), trains a new ensemble on the original training distribution (synthetic data)
3. Compares new models' AUC-ROC scores against previous models
4. **Promotes** new models only if AUC-ROC ≥ previous version (safer rollout)
5. **Reverts** to previous version if new models underperform
6. Writes a drift report to `./drift_reports/YYYYMMDD_HHMM.json` with PSI values and promotion decision

### Model Versioning and Rollback

Each trained model is stored with a version hash (SHA-256[:8] of training data fingerprint + timestamp):

```
models/
├── random_forest_v12a3b4c5.joblib      # Versioned model
├── random_forest_latest.txt              # Points to current version
├── xgboost_v12a3b4c5.joblib
├── xgboost_latest.txt
├── lightgbm_v12a3b4c5.joblib
├── lightgbm_latest.txt
├── training_reference.csv                # Reference dataset for drift detection
└── training_metadata.json                # Training metadata, AUC-ROC scores, etc.
```

If a newly promoted model degrades performance, rollback is automatic:

```bash
# Manual rollback (if needed):
# Edit random_forest_latest.txt, xgboost_latest.txt, lightgbm_latest.txt
# to point to a previous version (e.g., 12a3b4c5)
```

### Feature Distribution Tracking

Every time the scoring pipeline runs, feature vectors are persisted to SQLite for drift monitoring:

```sql
CREATE TABLE feature_distribution_snapshots (
    id INTEGER PRIMARY KEY,
    wallet TEXT,
    asset_pair TEXT,
    feature_name TEXT,
    feature_value REAL,
    recorded_at TIMESTAMP
);
```

**Storage budget**: At 1,000 wallets/run × 4 runs/day × 30 days × 26 features × ~8 bytes/float ≈ 25 MB. Hard cap: **500,000 rows**; oldest rows are pruned to 450,000 when exceeded.

### Scheduling Retrain Checks

For production deployments, schedule retrain checks via cron or systemd timer:

**Cron example (daily at 2 AM):**
```cron
0 2 * * * cd /path/to/hedge-rod-backend && python cli.py retrain-check >> /var/log/hedge-rod-retrain.log 2>&1
```

**Systemd timer example:**

`/etc/systemd/system/hedge-rod-retrain.service`
```ini
[Unit]
Description=HEDGE-ROD Continuous Retrain Check
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/path/to/hedge-rod-backend
ExecStart=/usr/bin/python cli.py retrain-check
StandardOutput=journal
StandardError=journal
```

`/etc/systemd/system/hedge-rod-retrain.timer`
```ini
[Unit]
Description=Daily HEDGE-ROD Retrain Check

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
systemctl enable hedge-rod-retrain.timer
systemctl start hedge-rod-retrain.timer
```

### Monitoring and Alerts

Inspect drift reports to monitor model stability:

```bash
ls -lh ./drift_reports/
# Example output:
# 20240615_0200.json: {"drift_detected": true, "promoted": true, ...}
# 20240614_0200.json: {"drift_detected": false, "promoted": false, ...}
```

**Alert on failures**: If `promoted: false` but `drift_detected: true`, the new models failed to outperform the current ones. Investigate feature shifts in the drift report's `psi_report` field and consider:

- Expanding the training dataset with recent adversarial examples
- Adjusting feature engineering (e.g., new adversarial or graph features)
- Lowering the PSI threshold if the drift is natural (market regime change) rather than evasion

### Model Observability API

Every `cli.py retrain-check` run also persists its drift report and per-model retrain outcome to SQLite, queryable over HTTP instead of grepping `./drift_reports/`:

| Method | Endpoint                | Description                                  |
|--------|--------------------------|-----------------------------------------------|
| `GET`  | `/admin/drift-reports`   | Most recent drift checks (PSI report, threshold, detected flag) |
| `GET`  | `/admin/retrain-runs`    | Most recent per-model retrain outcomes (old/new version, AUC-ROC, promoted, forced); filter with `?model_name=` |

Both endpoints require an admin key, since they expose internal model governance data. Set `HEDGE_ROD_ADMIN_API_KEY` and pass it via the `X-HEDGE-ROD-Admin-Key` header:

```bash
export HEDGE_ROD_ADMIN_API_KEY="$(openssl rand -hex 32)"
curl -H "X-HEDGE-ROD-Admin-Key: $HEDGE_ROD_ADMIN_API_KEY" http://localhost:8000/admin/retrain-runs?model_name=random_forest
```

If `HEDGE_ROD_ADMIN_API_KEY` is unset, both endpoints return `503` rather than allowing unauthenticated access.

## Webhook Alerts

HEDGE-ROD can push risk-score alerts to subscriber URLs via webhooks.
When the detection pipeline (`run_pipeline.py`) produces scores above a
subscriber's threshold, a signed payload is POSTed to their endpoint.

### Subscriber Registration

Register a webhook subscriber via the API:

```bash
curl -X POST http://localhost:8000/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://my-protocol.xyz/webhook",
    "secret": "whsec_your_hmac_secret",
    "min_score": 70
  }'
```

Optional filters restrict alerts by wallet or asset pair:

```json
{
  "url": "https://my-protocol.xyz/webhook",
  "secret": "whsec_your_hmac_secret",
  "min_score": 80,
  "wallet_filter": "GABC123,GDEF456",
  "asset_pair_filter": "XLM/USDC"
}
```

The response returns a `subscriber_id` (UUID) used for management.

### Management Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST`   | `/webhooks`                  | Register a subscriber        |
| `GET`    | `/webhooks`                  | List active subscribers      |
| `DELETE` | `/webhooks/{subscriber_id}`  | Deactivate a subscriber      |
| `GET`    | `/webhooks/dead-letters`     | List permanently failed deliveries |

### Payload Format

Every webhook POST carries this JSON body:

```json
{
  "event": "risk_score_alert",
  "data": {
    "wallet": "GABCDEF123...",
    "asset_pair": "XLM/USDC",
    "score": 85,
    "benford_flag": true,
    "ml_flag": true,
    "confidence": 90,
    "timestamp": "2026-06-16T12:00:00Z"
  },
  "timestamp": "2026-06-16T12:00:05Z"
}
```

### HMAC Verification

Each request includes a `X-HEDGE-ROD-Signature` header:

```
X-HEDGE-ROD-Signature: sha256=<hex-digest>
```

The digest is an HMAC-SHA256 of the raw request body using the
subscriber's `secret`. Receivers **must** verify this signature before
trusting the payload. Example verification in Python:

```python
import hmac, hashlib

def verify_hedge-rod_webhook(body: bytes, secret: str, signature: str) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode(), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

The `X-HEDGE-ROD-Timestamp` header contains the Unix epoch second when
the delivery was attempted. Receivers SHOULD reject timestamps older than
5 minutes to prevent replay attacks.

### Delivery Guarantees

- **At-least-once delivery**: unacknowledged items stay `pending` in the
  queue and are retried on worker restart.
- **Exponential backoff**: attempt N is retried at `now + 2^N × 5s`
  (capped at 1 hour).
- **Dead-letter queue**: after 8 consecutive failures the item moves to
  `dead` status. Inspect via `GET /webhooks/dead-letters`.
- **Concurrency limit**: at most 10 deliveries run in parallel; slow
  subscribers do not block others.

### Running the Delivery Worker

```bash
python cli.py webhook-worker --interval 5
```

This polls the delivery queue every 5 seconds and delivers due webhooks.
Run as a long-lived foreground process (e.g., under systemd or supervisor).

### Security Notes

- Subscriber URLs must use `https://`. HTTP URLs and private/reserved IPs
  are rejected at registration (SSRF protection).
- HMAC secrets are encrypted at rest with AES-256-GCM. The encryption key
  is loaded from `HEDGE_ROD_WEBHOOK_ENCRYPTION_KEY` (32-byte base64,
  stored in the environment **only**).
- Raw secrets never appear in API responses, logs, or error messages.
- The response body from the webhook receiver is discarded entirely to
  prevent log injection.

## Testing

```bash
pytest
```

Covers:
- ✅ Benford's Law feature computation
- ✅ ML feature engineering (trade pattern, volume/timing features)
- ✅ Synthetic data generation and labelled dataset building
- ✅ RiskScore combination logic and SQLite storage
- ✅ Local API and CLI
- ✅ Horizon HTTP retry/backoff behaviour

## Roadmap

### Phase 1 — Foundation *(Months 1–2)*
- [x] Stellar Horizon API ingestion pipeline (historical + streaming)
- [x] Benford's Law engine for on-chain transaction amounts
- [x] Initial feature engineering from SDEX trade data
- [x] Baseline ML model training on synthetic wash trade patterns
- [ ] Internal testing on Stellar Testnet

### Phase 2 — Core Product *(Months 3–4)*
- [x] Full ensemble model training and evaluation
- [x] SHAP interpretability integration
- [ ] Soroban smart contract deployment on Testnet
- [x] Local REST API (v1, read-only) — see `api/main.py`
- [ ] Public REST API with rate limiting (hardening of `api/`)
- [ ] Web dashboard (beta)

### Phase 3 — Ecosystem Integration *(Months 5–6)*
- [ ] Mainnet deployment
- [ ] SDK for protocol integrations (Python + JavaScript)
- [ ] Webhook alert system for asset issuers and protocol teams
- [ ] Open dataset release: labelled SDEX wash trade patterns
- [ ] Community feedback and model refinement cycle

### Phase 4 — Scale *(Post-Grant)*
- [ ] Continuous model retraining pipeline
- [ ] Coverage expansion to AMM pools and cross-asset paths
- [ ] Integration partnerships with Stellar DEX aggregators
- [ ] Developer documentation portal

## Why This Matters for the Stellar Ecosystem

A DEX where volume figures can't be trusted is one that institutional participants and serious traders avoid. HEDGE-ROD addresses this directly:

- **For traders** — Risk scores show which assets have genuine liquidity, without requiring on-chain expertise
- **For asset issuers** — A low risk score is a credibility signal for listings and investor materials
- **For protocol teams** — Integrate HEDGE-ROD scores into AMM/lending contract logic to protect users from wash-traded assets
- **For the Stellar Foundation and ecosystem** — An open, verifiable, community-maintained fraud detection layer strengthens Stellar's case as trustworthy financial infrastructure

HEDGE-ROD is an **open-source public good** — methodology, scores, and training data are transparent and auditable, and the project will always be free to query.

## Dependencies

- Python 3.10+ (`requirements.txt`)
- `soroban-sdk` — for the on-chain risk registry contract
- FastAPI, scikit-learn, XGBoost, LightGBM, SHAP

## License

MIT

## Contributing

HEDGE-ROD is being developed as an open-source contribution to the Stellar ecosystem, submitted as part of the **Drip Wave builder programme**. We are actively looking for collaborators with experience in:

- Stellar / Soroban smart contract development (Rust)
- Python backend development and ML pipeline engineering
- On-chain data analysis and blockchain forensics
- Frontend development (dashboard)
- DeFi protocol integration

Quick checklist for contributions:
- All tests pass: `pytest`
- Code follows project style guidelines
- New features include tests
- Documentation is updated

## HEDGE-ROD Organization

This repo is one of **three** in the HEDGE-ROD organization. If a change here
touches a shared contract (below), call it out so the matching repo can be
updated.

| Repo | Role | Primary language |
|---|---|---|
| **`hedge-rod-backend`** *(this repo)* | Detection engine **and** public REST API: Horizon ingestion, Benford's Law analysis, ML feature engineering, ensemble training/inference, SHAP explanations, `RiskScore` computation, the FastAPI service (`/score`, `/alerts/recent`, `/assets/risk-ranking`), and on-chain publishing to the contract | Python (FastAPI) |
| **`hedge-rod-frontend`** | Web dashboard consuming `hedge-rod-backend`. Visualizes risk scores, SHAP explanations, recent alerts, and asset risk rankings | HTML / CSS / JS (vanilla) |
| **`hedge-rod-contract`** | Soroban smart contract — the on-chain risk registry (`hedge-rod-score`). Exposes `submit_score` / `get_score` for composability with other Stellar protocols | Rust (Soroban) |

### Data Flow

```
       Horizon API ──(trades)──▶  hedge-rod-backend
                                       │  (ingestion + detection + REST API)
                                       ▼
                              RiskScore records
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                              ▼
       hedge-rod-frontend                        hedge-rod-contract (Soroban)
         (dashboard)                                          │
                                                              ▼
                                                other Stellar protocols
                                                (AMMs, lending, aggregators)
```

1. **`hedge-rod-backend`** (this repo) runs `run_pipeline.py`: `ingestion/` pulls trades from the Stellar Horizon API, `detection/feature_engineering.py` computes Benford + ML features, `detection/model_inference.py` scores with the trained ensemble, and `detection/risk_score.py` produces a `RiskScore` record. The bundled FastAPI service (`api/main.py`) exposes those records over REST, and `detection/soroban_publisher.py` forwards scores above `RISK_SCORE_THRESHOLD` to the contract via `submit_score`.
2. **`hedge-rod-frontend`** calls the backend API to render scores, alerts, and SHAP-based explanations.
3. **`hedge-rod-contract`** persists the score on-chain via the `hedge-rod-score` Soroban contract, making it queryable by any other Soroban contract via `get_score`.

### Shared Contracts (must stay in sync across repos)

**1. `RiskScore` schema** — defined here at `detection/risk_score.py`, served by this repo's FastAPI response models (`api/main.py`) and mirrored by `hedge-rod-contract`'s on-chain `RiskScore` struct (`contracts/hedge-rod-score/src/lib.rs`):

```python
class RiskScore:
    wallet: str
    asset_pair: str
    score: int        # 0-100
    benford_flag: bool
    ml_flag: bool
    confidence: int    # 0-100
    timestamp: datetime
```

If you change a field name, type, or range here, update the Rust struct in `hedge-rod-contract` in the same change set (or open a tracked follow-up).

**2. Trade / Asset schema** — defined here at `ingestion/data_models.py` (`Trade`, `Asset`, `OrderBookEvent`). These shape the records persisted by this repo's storage layer (`detection/storage.py`).

**3. Environment variables / config keys** — `.env.example` defines the keys shared with the contract:
- `HEDGE_ROD_SCORE_CONTRACT_ID` — the deployed Soroban contract id (shared with `hedge-rod-contract`)
- `HEDGE_ROD_SERVICE_SECRET_KEY` — the Soroban service account authorized to call `submit_score` (never commit)
- `RISK_SCORE_THRESHOLD` — score above which the backend pushes to the contract

**4. Soroban contract interface** — `hedge-rod-contract` exposes:
- `submit_score(wallet: Address, asset_pair: Symbol, score: u32, timestamp: u64)`
- `get_score(wallet: Address, asset_pair: Symbol) -> RiskScore`

The backend must call `submit_score` with `score` already clamped to 0-100 (see `RiskScore.combine` in `detection/risk_score.py`).

### Open Integration Points (not yet implemented)

- Order-book event ingestion (needed for `round_trip_trade_frequency`, cancellation-rate features) — see TODOs in `detection/feature_engineering.py`.

### Conventions for AI Agents

- Treat this section as the source of truth for **cross-repo** contracts. Each repo's own README covers repo-local conventions.
- When a change in this repo affects a shared contract above, call it out explicitly so the corresponding change can be made in the other repo(s).
- Keep `RiskScore` and `Trade`/`Asset` field names identical (same casing, same units) across Python (`hedge-rod-backend`) and Rust (`hedge-rod-contract`) — translation layers are a common source of bugs.

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/hedge-rod/issues)
- Stellar Discord: https://discord.gg/stellar

## References

- Benford, F. (1938) 'The law of anomalous numbers', *Proceedings of the American Philosophical Society*, 78(4), pp. 551–572.
- Al Ali, A. et al. (2023) 'A powerful predicting model for financial statement fraud based on optimized XGBoost ensemble learning technique', *Applied Sciences*, 13(4).
- Antonio, G.R. (2023) 'Numbers don't lie: Decoding financial error and fraud through Benford's law', *Journal of Entrepreneurship*.
- Nti, I.K. and Somanathan, A.R. (2024) 'A scalable RF-XGBoost framework for financial fraud mitigation', *IEEE Transactions on Computational Social Systems*, 11(2), pp. 410–422.
- Yadavalli, R. and Polisetti, R. (2025) 'Optimized financial fraud detection using SMOTE-enhanced ensemble learning with CatBoost and LightGBM', *ICVADV 2025*.
- Harea, R. and Mihailă, S. (2025) 'Benford's law: Applicability in accounting and financial anomaly detection', *Challenges of Accounting for Young Researchers*, 3(1).
- Stellar Development Foundation (2024) *Horizon API Documentation*. Available at: https://developers.stellar.org/api/horizon
- Stellar Development Foundation (2024) *Soroban Smart Contract Documentation*. Available at: https://soroban.stellar.org/docs

---

<div align="center">

**HEDGE-ROD** — Making the Stellar ledger legible.

*Built for the Stellar ecosystem. Open source. Community owned.*

</div>
# HEDGE-ROD Contract 🔍

[![Built on Stellar](https://img.shields.io/badge/Built%20on-Stellar-blue?logo=stellar)](https://stellar.org)
[![Soroban Smart Contracts](https://img.shields.io/badge/Smart%20Contracts-Soroban-purple)](https://soroban.stellar.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Soroban smart contract that serves as the on-chain risk-score registry for **HEDGE-ROD**, a hybrid fraud detection system for the Stellar DEX combining Benford's Law digit analysis with ensemble machine learning.

## Overview

HEDGE-ROD detects wash trading and artificial volume on the Stellar Decentralised Exchange (SDEX) by analysing trade data with statistical (Benford's Law) and machine learning techniques. The off-chain detection pipeline computes a **HEDGE-ROD Risk Score (0-100)** for wallets and asset pairs, and this contract acts as the **on-chain truth layer** for those scores — making fraud signals composable with other Soroban protocols (AMMs, lending platforms, DEX aggregators) without relying on an external oracle.

## Features

- **On-Chain Risk Score Registry**: Stores the latest HEDGE-ROD risk score, flags, confidence, and timestamp per wallet/asset-pair
- **Authorized Score Submission**: Only the authorised HEDGE-ROD off-chain service account can write scores
- **Composable Read Access**: Any Soroban contract can query risk scores to gate suspicious activity
- **Benford & ML Flags**: Distinguishes between statistical anomaly flags and ML classifier flags
- **Confidence Scoring**: Each risk score carries a model confidence value (0-100)
- **Open and Auditable**: Methodology, scores, and contract logic are fully transparent

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     LAYER 1: DATA INGESTION                 │
│  Stellar Horizon API → trade history, order book events,    │
│  account activity, asset metadata                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  LAYER 2: DETECTION ENGINE                   │
│  Benford's Law Anomaly Engine + Ensemble ML Models           │
│  (Random Forest, XGBoost, LightGBM)                          │
│             → HEDGE-ROD Risk Score (0-100)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           LAYER 3: SOROBAN CONTRACT (this repo) + API        │
│  • submit_score() — write risk scores on-chain               │
│  • get_score()    — read risk scores from any contract       │
│  • Public REST API and dashboard consume this contract       │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

- **lib.rs**: Main contract implementation — `submit_score` and `get_score`
- **types.rs**: `RiskScore` data structure (score, flags, confidence, timestamp)
- **storage.rs**: Persistent storage for per-wallet/asset-pair risk scores
- **errors.rs**: Custom error types for contract operations
- **test.rs**: Test suite covering submission, retrieval, and authorization

## Contract Functions

### `initialize(admin: Address, service: Address)`
One-time setup. Sets the admin (who can rotate the service address) and the HEDGE-ROD off-chain service account authorised to submit scores.

### `submit_score(signers: Vec<Address>, wallet: Address, asset_pair: Symbol, score: u32, benford_flag: bool, ml_flag: bool, timestamp: u64, confidence: u32, model_version: u32, attestation: Option<ScoreAttestation>)`
Called by the authorised HEDGE-ROD off-chain service to register a computed risk score on-chain. Requires authorization from the configured HEDGE-ROD service account (or, under the M-of-N multisig model, from `threshold` of the listed `signers`). `score` and `confidence` must be in the range 0-100. `attestation` is required once `set_service_pubkey` has been configured — see [Score Attestation](#score-attestation).

### `get_score(wallet: Address, asset_pair: Symbol) -> RiskScore`
Read-only function callable by any Soroban contract. Returns the most recent HEDGE-ROD risk score and metadata for a given wallet and asset pair.

### `get_score_count(wallet: Address, asset_pair: Symbol) -> u32`
Read-only function callable by any account or contract. Returns the total number of score submissions ever recorded for `wallet` / `asset_pair`. Unlike `get_score_history` (which caps at `HISTORY_MAX_DEPTH`), this counter is never truncated, giving off-chain services a cheap O(1) signal to distinguish newly monitored wallets from those with a long history.

### `set_service(new_service: Address)`
Rotates the authorised off-chain scoring service address. Admin only.

### `get_admin() -> Address` / `get_service() -> Address`
Read-only lookups of the current admin and authorised scoring service addresses.

### `get_pending_admin() -> Address` / `has_pending_admin_transfer() -> Address`
Read-only function to check the state of a pending admin.

### `get_aggregate_score(wallet: Address) -> AggregateRiskScore`
Read-only function. Returns `wallet`'s cross-asset aggregate risk score — a weighted average computed live from every asset pair the wallet has a `RiskScore` for. Always recomputed from current per-pair scores, never served from a stale cache. Returns `ScoreNotFound` if the wallet has no scores.

### `set_pair_weight(asset_pair: Symbol, weight: u32)`
Sets the weight used for `asset_pair` in the aggregate risk computation. Defaults to `1` (simple average) for any pair the admin hasn't configured. A weight of `0` excludes the pair from the aggregate's denominator. Admin only.

### `get_pair_weight(asset_pair: Symbol) -> u32`
Read-only lookup of the configured weight for `asset_pair`.

### `submit_scores_batch(submissions: Vec<ScoreSubmission>) -> BatchResult`

Called by the authorised HEDGE-ROD off-chain service to register multiple risk scores in a single invocation. The service account authorises once for the whole batch.

Returns a `BatchResult` containing per-entry outcomes so the caller knows exactly which entries succeeded and why any failed. Entries with out-of-range `score` (>100) or `confidence` (>100), zero `timestamp`, or that arrive before the submission cooldown has elapsed, are recorded as rejected with an appropriate `rejection_code`.

**ABI change in contract version 2:** The return type changed from `u32` (count of accepted entries) to the structured `BatchResult`. Callers built against the old ABI must regenerate their client bindings.

### `query_risk_gate(wallet: Address, asset_pair: Symbol, gate_threshold: u32) -> bool`
The cross-contract integration primitive. Returns `true` when the wallet's score is **strictly below** `gate_threshold` (safe to proceed), and `false` when the score is `>= gate_threshold` **or no score exists**. It is **infallible** (returns `bool`, never an error), **never panics**, and is **side-effect free** — designed to be called directly from inside another protocol's guard clause. See [Composability](#composability) and [`docs/interface-spec.md`](docs/interface-spec.md).

### `supports_interface(capability: Symbol) -> bool`
Runtime capability detection for the composability interface. Returns `true` for the registered capabilities `score`, `history`, `batch`, `gate`, and `aggr`, letting integrators feature-detect instead of hardcoding contract version numbers.

### `propose_upgrade(new_wasm_hash: BytesN<32>)`
Admin only. Starts a time-locked contract upgrade by committing to `new_wasm_hash`. Stores an `UpgradeProposal` with `executable_after = now + get_upgrade_delay()` and emits `upgrade_proposed`. Does not change the code. Rejected with `UpgradeAlreadyPending` if a proposal is already in flight. See [Upgrade Governance](#upgrade-governance).

### `execute_upgrade()`
Admin only. After the time-lock elapses, re-verifies `now >= executable_after` and installs the new WASM via `env.deployer().update_current_contract_wasm(...)`, clears the proposal, and emits `upgrade_executed`. Returns `UpgradeNotReady` before the delay or `NoPendingUpgrade` if none exists.

### `veto_upgrade()`
Admin only. Cancels the pending proposal during the time-lock window (emergency escape hatch for a malicious proposal or compromised key) and emits `upgrade_vetoed`.

### `get_pending_upgrade() -> UpgradeProposal`
Permissionless. Returns the in-flight proposal so anyone can audit it during the window. Returns `NoPendingUpgrade` if none.

### `set_upgrade_delay(delay_secs: u64)` / `get_upgrade_delay() -> u64`
Admin sets the time-lock delay applied to future proposals, bounded to `[MIN_UPGRADE_DELAY_SECS, MAX_UPGRADE_DELAY_SECS]` (48 hours – 14 days); out-of-range values are rejected with `InvalidUpgradeDelay`. Defaults to 48 hours.

### `set_cooldown(secs: u64)` / `get_cooldown() -> u64`
Admin sets the cooldown enforced between accepted submissions for the same `(wallet, asset_pair)`, bounded to `[MIN_COOLDOWN_SECS, MAX_COOLDOWN_SECS]` (1 minute – 24 hours); out-of-range values are rejected with `InvalidCooldown`. Defaults to 1 hour. See [Rate Limiting](#rate-limiting).

### `override_rate_limit(wallet: Address, asset_pair: Symbol)`
Admin-only emergency escape hatch. Immediately clears the stored cooldown deadline for `(wallet, asset_pair)`, so the next `submit_score` / `submit_scores_batch` call for that pair is accepted regardless of how recently the last one was. Intended for correcting a known-bad score right away, not for routine use. Emits `rl_ovrd`.

### `get_last_submit_time(wallet: Address, asset_pair: Symbol) -> u64`
Read-only lookup of the ledger timestamp of the last accepted submission for `(wallet, asset_pair)`, or `0` if none has ever been accepted (or it was cleared by `override_rate_limit`).

### `set_service_pubkey(pubkey: Bytes)` / `get_service_pubkey() -> Bytes`
Admin sets (or rotates) the off-chain detection pipeline's secp256k1 public key — 33 bytes compressed or 65 bytes uncompressed, rejected otherwise with `InvalidPubkeyLength` — used to verify `ScoreAttestation`s. Once set it cannot be unset, only rotated. `get_service_pubkey` returns `ServicePubkeyNotSet` before one has been configured. See [Score Attestation](#score-attestation).

### `RiskScore` Structure

```rust
pub struct RiskScore {
    pub score: u32,          // 0-100; higher = more suspicious
    pub benford_flag: bool,  // True if Benford anomaly detected
    pub ml_flag: bool,       // True if ML classifier flagged
    pub timestamp: u64,      // Ledger timestamp of last update
    pub confidence: u32,     // Model confidence 0-100
    pub model_version: u32,  // Detection-pipeline model version
}
```

### `AggregateRiskScore` Structure

A wallet that is moderately suspicious across several asset pairs poses a higher *portfolio-level* risk than its individual per-pair scores suggest in isolation. `AggregateRiskScore` expresses that risk on-chain:

```rust
pub struct AggregateRiskScore {
    pub aggregate_score: u32,     // 0-100, weighted average across all pairs
    pub pair_count: u32,          // number of distinct pairs the wallet has a score for
    pub max_pair_score: u32,      // highest individual pair score
    pub max_pair: Symbol,         // the pair with the highest score
    pub benford_flag_count: u32,  // number of pairs with benford_flag = true
    pub ml_flag_count: u32,       // number of pairs with ml_flag = true
    pub last_updated: u64,        // timestamp of the most recently updated pair score
}
```

### `BatchResult` and `BatchEntryResult` Structures

`submit_scores_batch` returns a `BatchResult` that the off-chain API service can inspect to learn which entries succeeded and which were rejected:

```rust
pub struct BatchEntryResult {
    pub index: u32,           // zero-based position in the submitted batch
    pub accepted: bool,       // true if written to storage
    pub rejection_code: u32,  // 0 if accepted; Error discriminant if rejected
}

pub struct BatchResult {
    pub accepted_count: u32,                      // number of entries written to storage
    pub rejected_count: u32,                      // number of entries rejected
    pub results: Vec<BatchEntryResult>,            // per-entry outcomes, same order as input
}
```

Possible `rejection_code` values (from the `Error` enum):

| Code | Meaning |
|-----:|---------|
| 4 | `InvalidScore` — score > 100 |
| 5 | `InvalidConfidence` — confidence > 100 |
| 23 | `RateLimitExceeded` — submission cooldown not yet elapsed |
| 25 | `InvalidTimestamp` — timestamp == 0 |

The weighted average is:

```
aggregate_score = Σ (pair_weight[i] * pair_score[i]) / Σ pair_weight[i]
```

`pair_weight[i]` defaults to `1` for every pair (a plain average) unless the admin sets a different weight via `set_pair_weight`. A pair with weight `0` is excluded from the denominator — its score still counts toward `pair_count`, `max_pair_score`, the flag counts, and `last_updated`, but not toward `aggregate_score`.

#### Worked example

A wallet has three scored pairs:

| Pair | Score | Weight |
|---|---|---|
| XLM_USDC | 60 | 1 |
| XLM_BTC | 65 | 1 |
| XLM_ETH | 70 | 1 |

With default (equal) weights: `aggregate_score = (60 + 65 + 70) / 3 = 65`.

Now suppose the admin sets `XLM_BTC`'s weight to `2` (e.g. because BTC pairs carry more systemic risk):

```
aggregate_score = (60*1 + 65*2 + 70*1) / (1 + 2 + 1)
                = (60 + 130 + 70) / 4
                = 260 / 4
                = 65
```

A wallet scoring 60-70 on three pairs individually might not breach the per-pair `RiskThreshold` (default 75), but the aggregate view makes the *combined* exposure visible to any contract or dashboard that queries `get_aggregate_score` — without needing to fetch and average every pair manually.

`get_aggregate_score` iterates the wallet's full pair list, so its cost is O(N) in the number of distinct pairs the wallet has scores for. The contract is designed around a practical maximum of `MAX_WALLET_PAIRS` (20) pairs per wallet; this is documented as a constant but not enforced on-chain.

## Upgrade Governance

Soroban contracts can be upgraded by the admin via `update_current_contract_wasm`, which replaces the **entire** contract logic in a single transaction. Without governance, one admin key — or a compromised one — could silently install a backdoor or disable a security check with no warning. HEDGE-ROD gates every upgrade behind an on-chain **time-lock** so the community always gets a mandatory window to inspect and react.

**The flow:**

1. The admin **proposes** an upgrade, committing to a new WASM hash.
2. A mandatory delay passes (**minimum 48 hours**, configurable up to 14 days). During this window anyone can call `get_pending_upgrade` to inspect the committed hash and alert the community.
3. Only after the delay can the admin **execute** the upgrade. Alternatively, the admin can **veto** it at any time during the window (e.g. if the key was compromised).

```
   admin                         contract                        community
     │                              │                                │
     │ propose_upgrade(hash)        │                                │
     ├─────────────────────────────►│  store UpgradeProposal         │
     │                              │  emit upgrade_proposed ────────►│  inspect via
     │                              │  executable_after = now + delay │  get_pending_upgrade
     │                              │                                │  (≥ 48 h to react)
     │            ⏳  time-lock window (no execution possible)  ⏳    │
     │                              │                                │
     │   ┌── after executable_after ──┐                              │
     │   │ execute_upgrade()          │                              │
     ├───┘                            │  require now ≥ executable_after
     │                              │  update_current_contract_wasm  │
     │                              │  emit upgrade_executed ────────►│
     │                              │  clear PendingUpgrade          │
     │                              │                                │
     │   ── OR, any time in window ──                                │
     │ veto_upgrade()               │                                │
     ├─────────────────────────────►│  clear PendingUpgrade          │
     │                              │  emit upgrade_vetoed ──────────►│
```

The time-lock is computed from `env.ledger().timestamp()` (deterministic, not caller-settable) and re-verified at execution time — never cached. The configurable delay is bounded to `[MIN_UPGRADE_DELAY_SECS, MAX_UPGRADE_DELAY_SECS]`; **raising** it is always safe, while **lowering** it shortens the veto window and should require community consensus. See [`SECURITY.md`](SECURITY.md#upgrade-governance--threat-model) for the full threat model and monitoring guidance.

## Rate Limiting

A compromised or malfunctioning off-chain service could otherwise flood the contract with submissions for the same `(wallet, asset_pair)`, exhausting storage rent, overwhelming indexers, and poisoning the score signal with rapid fluctuations. HEDGE-ROD enforces a configurable **cooldown** between accepted submissions for any given wallet/asset-pair to bound that blast radius.

**The flow:**

1. On every `submit_score` (and per-entry in `submit_scores_batch`), the contract compares `env.ledger().timestamp()` against the pair's last accepted submission time plus the configured cooldown.
2. If the cooldown hasn't elapsed, `submit_score` returns `RateLimitExceeded`; in `submit_scores_batch` the offending entry is silently skipped (the rest of the batch still processes) and counted as not accepted.
3. A successful submission updates the pair's last-submit timestamp, starting the next cooldown window.

The cooldown defaults to **1 hour** and is admin-configurable via `set_cooldown`, bounded to `[MIN_COOLDOWN_SECS, MAX_COOLDOWN_SECS]` (1 minute – 24 hours) so the admin can neither disable rate limiting entirely nor lock a pair out indefinitely. For situations that need an immediate re-score (e.g. correcting a known-bad score), the admin can call `override_rate_limit` to clear a specific pair's cooldown rather than lowering the global setting.

Like the upgrade time-lock, the cooldown deadline is computed from `env.ledger().timestamp()` — deterministic and not caller-settable — so it cannot be bypassed by manipulating submission metadata such as the `timestamp` field on `RiskScore` itself.

## Score Attestation

The service account's `require_auth` proves a transaction was sent by the authorised key, but says nothing about whether the score payload inside that transaction matches what the off-chain detection pipeline actually computed — relevant when the service key is held by infrastructure (a relayer, a batching service, a multisig signer) that's trusted to submit transactions but shouldn't be able to silently alter scores in transit.

`submit_score`'s optional `attestation: Option<ScoreAttestation>` closes that gap with a secp256k1 signature over the exact payload:

1. The admin registers the off-chain pipeline's public key via `set_service_pubkey`. Until this is called, `attestation` is ignored entirely and every existing integration keeps working unchanged.
2. Once a pubkey is configured, every `submit_score` call must carry a valid `ScoreAttestation` — a missing or invalid one is rejected with `InvalidAttestation`. There is no way to turn this back off short of a contract upgrade.
3. On each call, the contract independently recomputes the SHA-256 commitment over the wallet, asset pair, score fields, this contract's address, and the network id (binding the signature to one deployment on one network), and rejects the call if it disagrees with the attestation's `commitment` field — that field is never trusted as input, only checked.
4. The signature is then verified via `secp256k1_recover` against the registered pubkey, supporting both compressed and uncompressed key formats.

The full byte layout and verification algorithm are specified in [`docs/attestation-spec.md`](docs/attestation-spec.md).

## Composability

HEDGE-ROD is only useful if other protocols can actually *act* on its scores. A risk score that lives in isolation is a dashboard widget; a risk score that an AMM, a lending market, or a DEX aggregator can read mid-transaction is a shared fraud-prevention layer for the entire Stellar DeFi ecosystem.

The problem with composing on a raw getter is fragility. If every integrator reverse-engineers `get_score` and decodes the `RiskScore` struct by hand, then the day we add a field or change an error code, every downstream protocol breaks silently. So HEDGE-ROD exposes a **stable, versioned composability interface** — `IHEDGE-RODScore` — as the canonical integration point. It is fully specified in [`docs/interface-spec.md`](docs/interface-spec.md); the headline function is `query_risk_gate`.

### Why a dedicated gate function?

A guard clause inside someone else's contract has hard requirements that a normal getter doesn't meet:

- **It must never panic.** A panic in a cross-contract call traps the *caller's* transaction. If HEDGE-ROD could panic, an attacker could craft inputs that disable the AMM's risk guard — or simply burn its gas. So `query_risk_gate` returns a plain `bool` and is engineered to be infallible.
- **It must fail closed.** Because the answer is a single `bool`, the "we have no score for this wallet" case has to collapse to one value — and that value is `false`. Unknown wallets are treated as *potentially risky*, not waved through.
- **It must be cheap and side-effect free.** It is a pure read that doesn't even extend storage TTL, so calling it from a hot path is safe.

### The AMM pattern

Here is the entire integration — drop `query_risk_gate` into your swap guard and refuse risky wallets:

```rust
fn swap(env: Env, user: Address, amount: i128) -> Result<(), AmmError> {
    // The HEDGE-ROD contract ID you trust, stored at init time.
    let llens_contract: Address = env
        .storage()
        .instance()
        .get(&DataKey::HEDGE-ROD)
        .ok_or(AmmError::NotConfigured)?;

    let client = HEDGE-RODScoreContractClient::new(&env, &llens_contract);

    // Note: no `try_`, no `?`, no error handling — the gate cannot fail.
    let is_safe = client.query_risk_gate(&user, &symbol_short!("XLM_USDC"), &75u32);
    if !is_safe {
        return Err(AmmError::HighRiskWallet);
    }

    // ... rest of swap logic ...
    Ok(())
}
```

A complete, compiling reference contract lives in [`examples/amm_gate.rs`](examples/amm_gate.rs) (build it with `cargo build --example amm_gate -p hedge-rod-score`). For versioning, error-code stability, threshold selection, and caching guidance, read the full [interface specification](docs/interface-spec.md).

## Security Features

1. **Authorization Checks**: Only the authorised HEDGE-ROD service account can submit scores
2. **Read-Only Composability**: `get_score` is permissionless and side-effect free, safe for any contract to call
3. **Bounded Values**: Scores and confidence are constrained to the 0-100 range
4. **Overflow Protection**: Safe math operations with overflow checks
5. **Time-Locked Upgrades**: Contract WASM upgrades require a mandatory delay (≥48 h) with a public proposal anyone can inspect and an admin veto — see [Upgrade Governance](#upgrade-governance)
6. **Submission Rate Limiting**: A configurable per-`(wallet, asset_pair)` cooldown (default 1 h) bounds how often the service account can overwrite a score — see [Rate Limiting](#rate-limiting)
7. **Score Attestation**: An opt-in secp256k1 signature over the score payload lets the off-chain pipeline vouch for its contents independent of `require_auth` — see [Score Attestation](#score-attestation)

## Testing

Run the test suite with:

```bash
cargo test
```

## Quick Start

### 1. Build the Contract

```bash
cargo build --target wasm32-unknown-unknown --release
soroban contract optimize --wasm target/wasm32-unknown-unknown/release/hedge_rod_score.wasm
```

### 2. Deploy to Testnet

```bash
soroban contract deploy \
  --wasm target/wasm32-unknown-unknown/release/hedge_rod_score.optimized.wasm \
  --source deployer \
  --network testnet
```

### 3. Submit a Risk Score

```bash
soroban contract invoke \
  --id <CONTRACT_ID> \
  --source hedge_rod_service \
  --network testnet \
  -- \
  submit_score \
  --wallet <WALLET_ADDRESS> \
  --asset_pair <ASSET_PAIR_SYMBOL> \
  --score 87 \
  --benford_flag true \
  --ml_flag true \
  --timestamp 1700000000 \
  --confidence 92
```

### 4. Query a Risk Score

```bash
soroban contract invoke \
  --id <CONTRACT_ID> \
  --source deployer \
  --network testnet \
  -- \
  get_score \
  --wallet <WALLET_ADDRESS> \
  --asset_pair <ASSET_PAIR_SYMBOL>
```

## Repository Structure

```
.
├── .github/
│   └── workflows/
│       └── ci.yml                      ← Format, lint, test, wasm build
├── Cargo.toml                          ← Workspace manifest
├── Cargo.lock                          ← Pinned dependency versions
├── rustfmt.toml
├── clippy.toml
├── deploy.sh                           ← Build, optimize, deploy, initialize
├── docs/
│   └── interface-spec.md               ← IHEDGE-RODScore composability spec
├── examples/
│   └── amm_gate.rs                     ← Reference AMM integration (query_risk_gate)
├── contracts/
│   └── hedge-rod-score/
│       ├── Cargo.toml
│       └── src/
│           ├── lib.rs                  ← Contract entrypoints
│           ├── types.rs                ← RiskScore, DataKey
│           ├── storage.rs              ← Persistent/instance storage helpers
│           ├── errors.rs               ← Contract error codes
│           ├── events.rs               ← Event emission helpers
│           ├── test.rs                 ← Implementation unit tests
│           ├── test_interface.rs       ← Interface stability tests
│           ├── test_upgrade.rs         ← Upgrade-governance tests
│           └── test_rate_limit.rs      ← Submission rate-limiting tests
├── LICENSE
├── CONTRIBUTING.md
└── README.md                            ← This file
```

## Organization Architecture

HEDGE-ROD is split across **3 repositories**. This section orients anyone (or any AI agent) working in this contract repo on how it connects to the rest of the organization.

### The Three Repositories

| Repo | Language / Stack | Responsibility |
|---|---|---|
| **`hedge-rod-backend`** | Python (FastAPI) | Detection engine **and** REST API — Horizon ingestion, Benford's Law analysis, ensemble ML (Random Forest, XGBoost, LightGBM), SHAP, `RiskScore` computation, the public API, and the service account that calls `submit_score` on this contract |
| **`hedge-rod-frontend`** | HTML / CSS / JS (vanilla) | Web dashboard — visualises risk scores, alerts, and asset rankings via the backend API |
| **`hedge-rod-contract`** *(this repo)* | Rust (Soroban) | On-chain truth layer — `hedge-rod-score` Soroban contract storing the latest risk score per wallet/asset-pair |

### End-to-End Data Flow

```
 hedge-rod-backend (ingestion + detection + REST API)
   │  pulls Horizon trades, computes Benford + ML ensemble
   │  → RiskScore{score, benford_flag, ml_flag, confidence, timestamp}
   │  holds the "service" keypair authorised on-chain
   │  calls contract.submit_score(wallet, asset_pair, ...)
   ▼
 hedge-rod-contract (this repo)   ◄── any external Soroban contract can call get_score()
   │  on-chain RiskScore registry
   ▼
 hedge-rod-frontend
   └─ reads the backend API (which may read through to contract.get_score for
      verification) and renders risk scores, flags, and alerts to end users
```

### The Shared `RiskScore` Type — Source of Truth for Cross-Repo Types

The single most important cross-repo agreement is the **`RiskScore`** shape, defined canonically in this repo at `contracts/hedge-rod-score/src/types.rs`:

```rust
pub struct RiskScore {
    pub score: u32,          // 0-100, higher = more suspicious
    pub benford_flag: bool,  // Benford's Law anomaly detected
    pub ml_flag: bool,       // ML ensemble classifier flagged
    pub timestamp: u64,      // ledger timestamp of computation
    pub confidence: u32,     // model confidence, 0-100
    pub model_version: u32,  // detection-pipeline model version
}
```

- **`hedge-rod-backend`** must produce scores matching these fields and ranges (0-100) before calling `submit_score`, and must mirror this shape in its Pydantic models so JSON responses to the frontend stay consistent with on-chain data.
- **`hedge-rod-frontend`** should treat `score`/`confidence` as 0-100 integers and `benford_flag`/`ml_flag` as booleans when rendering badges.
- **Any change to this struct is a breaking change across all 3 repos** — update the backend's models and the frontend's rendering in the same release window.

### Contract Interface (what other repos call)

| Function | Caller | Auth required | Used by |
|---|---|---|---|
| `initialize(admin, service)` | deployer | admin (one-time) | deployment tooling only |
| `submit_score(wallet, asset_pair, score, benford_flag, ml_flag, timestamp, confidence)` | HEDGE-ROD service account | `service.require_auth()` | **`hedge-rod-backend`** — writes computed scores |
| `get_score(wallet, asset_pair)` | anyone | none (read-only) | **`hedge-rod-backend`**, the frontend (via the API), and any third-party Soroban contract that wants to gate on HEDGE-ROD risk |
| `get_score_count(wallet, asset_pair)` | anyone | none (read-only) | **`hedge-rod-backend`** — detects newly monitored vs. long-history wallets |
| `set_service(new_service)` | admin | `admin.require_auth()` | ops/admin tooling for key rotation |
| `get_admin()` / `get_service()` | anyone | none (read-only) | ops tooling, backend health checks |

`asset_pair` is a `Symbol` (≤ 9 chars in Soroban's short-symbol form, e.g. `XLM_USDC`). If the backend needs pair identifiers longer than 9 characters, it must agree on a canonical short encoding here before the contract is deployed to mainnet.

### Events Emitted (for off-chain listeners)

- `score` — `(wallet, asset_pair) -> (score, benford_flag, ml_flag, confidence, timestamp)`, emitted on every `submit_score`
- `svc_upd` — emitted when the admin rotates the authorised service address
- `pw_upd` — `(asset_pair) -> weight`, emitted when the admin sets a pair's aggregate-risk weight via `set_pair_weight`
- `cd_upd` — `() -> cooldown_secs`, emitted when the admin changes the submission cooldown via `set_cooldown`
- `rl_ovrd` — `(wallet, asset_pair) -> admin`, emitted when the admin clears a pair's cooldown via `override_rate_limit`

The backend (or a dedicated indexer) should subscribe to these for audit trails and to keep an off-chain cache in sync with on-chain state.

### Conventions Shared Across Repos

- **Networks**: `testnet` for development, `mainnet` for production. Contract IDs per network are recorded in this repo's deployment docs and must be mirrored into the backend's environment configuration (`HEDGE_ROD_SCORE_CONTRACT_ID`, `RPC_URL`, `NETWORK`).
- **Secrets**: the "service" keypair that calls `submit_score` lives in the backend's secret store — never in the frontend. This repo only ever stores the **public address** of that account on-chain.
- **CI**: this repo's contract CI builds with `cargo build --target wasm32-unknown-unknown --release` and runs `cargo test`.
- **Versioning**: tag contract releases as `contract-vX.Y.Z`. The backend should pin against a specific deployed contract id + ABI version, not "latest".

### Notes for Other Repos

- **Working in `hedge-rod-backend`**: you depend on the contract interface and the `RiskScore` shape above. Check `contracts/hedge-rod-score/src/types.rs` and `lib.rs` in this repo for the current signatures before writing client code, and ensure output scores conform to the 0-100 ranges (the contract rejects out-of-range `score`/`confidence`).
- **Working in `hedge-rod-frontend`**: you consume the backend API, not this contract directly; but the field names/ranges above flow through unchanged.

## Dependencies

- `soroban-sdk` - Soroban smart contract SDK

## License

MIT

## Roadmap

- [ ] Initial `submit_score` / `get_score` implementation
- [ ] Testnet deployment
- [ ] Integration with off-chain detection pipeline
- [ ] Mainnet deployment
- [ ] Support for batched score updates

## Contributing

Contributions are welcome. HEDGE-ROD is an open-source public good built for the Stellar ecosystem. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, required checks, and PR guidelines.

## References

- Benford, F. (1938) 'The law of anomalous numbers', *Proceedings of the American Philosophical Society*, 78(4), pp. 551-572.
- Al Ali, A. et al. (2023) 'A powerful predicting model for financial statement fraud based on optimized XGBoost ensemble learning technique', *Applied Sciences*, 13(4).
- Antonio, G.R. (2023) 'Numbers don't lie: Decoding financial error and fraud through Benford's law', *Journal of Entrepreneurship*.
- Nti, I.K. and Somanathan, A.R. (2024) 'A scalable RF-XGBoost framework for financial fraud mitigation', *IEEE Transactions on Computational Social Systems*, 11(2), pp. 410-422.
- Yadavalli, R. and Polisetti, R. (2025) 'Optimized financial fraud detection using SMOTE-enhanced ensemble learning with CatBoost and LightGBM', *ICVADV 2025*.
- Harea, R. and Mihailă, S. (2025) 'Benford's law: Applicability in accounting and financial anomaly detection', *Challenges of Accounting for Young Researchers*, 3(1).
- Stellar Development Foundation (2024) *Horizon API Documentation*. Available at: https://developers.stellar.org/api/horizon
- Stellar Development Foundation (2024) *Soroban Smart Contract Documentation*. Available at: https://soroban.stellar.org/docs
