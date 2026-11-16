# AdTech Bidding System

A modular, runnable miniature of a real-time ad decisioning platform. It demonstrates:

- FastAPI ad-decision API
- Eligibility filtering and candidate retrieval
- Online feature lookup (Redis, with in-process fallback)
- CTR/CVR prediction using scikit-learn logistic regression models
- Bid optimization for CPC, CPA and CPM campaigns
- Creative selection and simplified auction ranking
- Kafka-compatible event publishing/consumption (Redpanda)
- Impression, click and delayed-conversion simulation
- Synthetic model training and model artifact versioning

> This is an educational reference implementation, not a production ad exchange. It does not implement real identity resolution, consent management, fraud detection, billing, a complete auction protocol, or production-grade budget reservation.

## Architecture

```text
                   ONLINE REQUEST (FastAPI)
Publisher -> /decide -> Eligibility -> Candidate Retrieval
                                |              |
                                +------ Feature lookup (Redis)
                                               |
                                      CTR + CVR models
                                               |
                                     Bid/value optimizer
                                               |
                                  Creative choice + ranking
                                               |
                                         Ad response
                                               |
                                    Publish impression event
                                               v
                              Redpanda / Kafka topic: ad-events
                                               |
                    +--------------------------+------------------+
                    |                                             |
              Event consumer                                Simulator
                    |                                  click / delayed CV
                    v                                             |
           Redis feature aggregates <-----------------------------+
                    |
             Training data (JSONL)
                    |
             scripts/train_models.py
                    |
            models/ctr_model.joblib
            models/cvr_model.joblib
```

## Requirements

- Python 3.10+
- Docker + Docker Compose (recommended)
- Or run the API locally with Redis/Kafka disabled for a lightweight demo

## Quick start with Docker

```bash
cp .env.example .env
docker compose up --build
```

API: http://localhost:8000  
Swagger UI: http://localhost:8000/docs  
Health: http://localhost:8000/health

The compose stack starts Redis, Redpanda, and the API. The API starts with a seeded demo campaign catalog and synthetic baseline models if no trained model artifacts exist.

## Try an ad decision

```bash
curl -X POST http://localhost:8000/decide \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req-demo-001",
    "user_id": "user-42",
    "publisher_id": "publisher-news",
    "placement": "homepage-banner",
    "country": "FR",
    "device": "mobile",
    "page_category": "travel"
  }'
```

The response includes the selected campaign, ad, creative, predicted CTR/CVR, bid, and decision latency.

## Simulate feedback

Record a click:

```bash
curl -X POST http://localhost:8000/events/click \
  -H "Content-Type: application/json" \
  -d '{"impression_id":"<ID_FROM_DECISION>","user_id":"user-42"}'
```

Record a conversion (can be sent days later; this demo lets you simulate it immediately):

```bash
curl -X POST http://localhost:8000/events/conversion \
  -H "Content-Type: application/json" \
  -d '{"impression_id":"<ID_FROM_DECISION>","user_id":"user-42","conversion_value":79.90}'
```

Events are published to Redpanda when Kafka is available. If the broker is unavailable, the API still accepts the request and logs the event locally.

## Run locally without Docker

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Redis and Kafka are optional. Without them, the application uses an in-memory feature store and local event log.

## Train models

Generate a synthetic training dataset and train two simple classifiers:

```bash
python scripts/generate_training_data.py
python scripts/train_models.py
```

The resulting artifacts are written to `models/`. Restart the API to load them.

The sample models are intentionally small and CPU-friendly. For a real platform, evaluate LightGBM / CatBoost / DeepFM and calibrate probabilities on temporally separated, mature-label datasets.

## Delayed conversion handling

The event consumer maintains impressions as pending until a conversion arrives or the configured attribution window expires. A pending impression is **not** treated as a negative conversion. The demo consumer records event state and aggregate counters; the training-data generator demonstrates mature labels separately.

A production implementation should additionally use:
- deterministic attribution rules and click/view windows
- idempotency keys and deduplication
- event-time processing and late-event handling
- right-censoring / delay-distribution correction
- point-in-time feature joins
- explicit consent and privacy controls

## Latency notes

`/decide` reports its own decisioning duration. It is not a guarantee of <30 ms in every environment. Docker networking, cold starts, Redis, machine size, and concurrent load all affect observed latency.

For a production SLA:
1. Define whether 30 ms means server compute or end-to-end exchange latency.
2. Set p95/p99 budgets per component.
3. Keep candidate count bounded.
4. Parallelize independent feature reads.
5. Co-locate services and use local caches.
6. Load-test at expected RPS and monitor p99/p99.9.
7. Add deadline propagation and safe fallbacks.

## Project structure

```text
app/
  api/             HTTP routes
  core/            configuration and logging
  data/            demo campaign catalog
  models/           model loading and inference
  services/         retrieval, features, ranking, bidding, events
  schemas/          API contracts
scripts/            synthetic data and model training
tests/              basic unit tests
models/             model artifacts (generated locally)
```

## Main endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health and dependency status |
| POST | `/decide` | Choose ad + creative + bid |
| POST | `/events/click` | Record click feedback |
| POST | `/events/conversion` | Record conversion feedback |
| GET | `/campaigns` | Inspect demo campaigns |
| GET | `/metrics` | Basic in-process counters |

## Configuration

See `.env.example`. The app is deliberately tolerant of unavailable Redis/Kafka in local development.

## Tests

```bash
pytest -q
```

## Next production steps

- Replace demo catalog with a campaign-management database and indexed eligibility service.
- Replace in-memory budget checks with atomic reservations / regional budget tokens.
- Add authenticated publisher/advertiser APIs and request signing.
- Add consent-aware data collection, retention limits, deletion workflows, and regional policy enforcement.
- Use a real attribution service and mature-label training pipeline.
- Add OpenTelemetry traces, Prometheus metrics, dashboards, canary model deployment, and rollback.
