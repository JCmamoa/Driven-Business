# AI-Driven Business Ops

> A unified architecture for e-commerce operations and automation:
> margin optimization, LLM-powered ticket triage, and autonomous agents with guardrails.

[![CI](https://github.com/JCmamoa/Driven-Business/actions/workflows/ci.yml/badge.svg)](https://github.com/JCmamoa/Driven-Business/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL + pgvector](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.13-FF6600.svg)](https://www.rabbitmq.com/)
[![Gemini](https://img.shields.io/badge/Google-Gemini%202.5%20Flash-4285F4.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

This project provides a **reference architecture** for AI-powered e-commerce operations across three integrated areas:

| Module | Goal | Business Impact |
|---|---|---|
| **A — Margin Simulator** | Monte Carlo simulation of net margin under return-reduction and order-growth scenarios | Margin protection and data-driven decisions |
| **B — Triage Pipeline** | Automatic ticket classification with Gemini Structured Outputs | Reduced First Response Time (FRT) |
| **C — Autonomous Agents** | ReAct agents with RAG and human-in-the-loop (HITL) guardrails | Increased deflection with appropriate safeguards |

The architecture prioritizes **operational resilience**, **execution reliability**, and **measurable business outcomes** (EBITDA, FRT, and autonomous resolution rate).

---

## Architecture

```text
[Data Sources & Channels] ──► [Ingestion & Messaging] ──► [AI & Analytics Engines] ──► [Action & Observability]
  (ERP, E-commerce, Email)      (Webhooks, RabbitMQ, DLQ)   (Gemini, ML, Simulator)      (External APIs, Dashboards, Outbox)
```

<p align="center">
  <img src="docs/architecture.svg" alt="AI-Driven Business Ops architecture" width="100%">
</p>

### Distributed patterns

- **Transactional Outbox** — transactional consistency between the database and broker
- **Idempotency** — unique keys in `processed_messages` prevent duplicate processing
- **Dead Letter Queue (DLQ)** — exponential backoff for transient failures
- **Structured Outputs** — deterministic JSON schema through `response_schema`
- **Guardrails + Human-in-the-Loop** — refunds above the configured limit require approval
- **Agent tracing** — each agent step is persisted in `agent_traces` for auditing

---

## Technology Stack

| Layer | Technology |
|---|---|
| **API** | FastAPI + Uvicorn |
| **Database** | PostgreSQL 16 + `pgvector` |
| **Messaging** | RabbitMQ 3.13 + `aio-pika` |
| **AI / LLM** | Google Gemini 2.5 Flash (`google-genai`) |
| **Data / ML** | pandas, Polars, Scikit-learn, NumPy |
| **Dashboard** | Streamlit |
| **Observability** | `structlog`, `prometheus-client` |
| **Infrastructure** | Docker + Docker Compose |
| **Testing** | Pytest + pytest-asyncio |

---

## Project Structure

```text
.
├── app/
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Settings (pydantic-settings)
│   ├── db.py                      # Engine + SessionLocal
│   ├── models.py                  # SQLAlchemy models
│   ├── schemas.py                 # Pydantic schemas
│   ├── messaging/                 # Outbox + Broker + DLQ
│   ├── module_a_margin/           # ETL + Simulator + Dashboard
│   ├── module_b_triage/           # Pipeline + LLM client + Connectors
│   ├── module_c_agents/           # ReAct agent + Tools + RAG + Guardrails
│   └── observability/             # Logging + Metrics
├── workers/                       # Triage / agent / outbox publisher
├── migrations/                    # Alembic
├── scripts/                       # Seed data + traffic simulation
│   └── capture_dashboard.py       # Capture a dashboard screenshot
├── docs/
│   ├── architecture.svg
│   └── screenshots/
│       └── dashboard.png
├── tests/                         # Pytest suite
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Quickstart (Windows 10 + VS Code)

```powershell
# 1. Create a Python environment
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Configure environment variables
copy .env.example .env
notepad .env    # set GEMINI_API_KEY

# 3. Start infrastructure (Docker Desktop must be running)
docker compose up -d postgres rabbitmq

# 4. Set up the schema and sample data
alembic upgrade head
python -m scripts.seed_data

# 5. Run tests
pytest -v --asyncio-mode=auto

# 6. Start the services in separate VS Code terminals
uvicorn app.main:app --reload                     # API
python -m workers.triage_worker                   # Triage worker
python -m workers.agent_worker                    # Agent worker
python -m workers.outbox_publisher                # Outbox publisher
streamlit run app/module_a_margin/dashboard.py    # Dashboard
python -m scripts.simulate_traffic                # Sample traffic
```

### Dashboard preview

![Margin simulator dashboard](docs/screenshots/dashboard.png)

*Monte Carlo net-margin simulator with return-reduction and order-growth controls. The dashboard reports P10/P50/P90 estimates.*

To recapture the dashboard, activate the virtual environment and make sure the database is running and populated:

```powershell
pip install playwright
playwright install chromium
python -m scripts.capture_dashboard
```

### Quickstart (macOS / Linux)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # set GEMINI_API_KEY

docker compose up -d postgres rabbitmq
alembic upgrade head
python -m scripts.seed_data
pytest -v --asyncio-mode=auto

uvicorn app.main:app --reload
```

To capture the dashboard on macOS/Linux, install Playwright and Chromium, then run `python -m scripts.capture_dashboard`.

### Default URLs

| Service | URL |
|---|---|
| API / Swagger | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |
| Margin dashboard | http://localhost:8501 |
| RabbitMQ Management | http://localhost:15672 (`aiops` / `aiops`) |

---

## Main Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/webhooks/zendesk` | Ingest a ticket through a webhook |
| `POST` | `/tickets/{id}/run-agent` | Queue an autonomous agent run for a ticket |

### Example: Zendesk webhook

```bash
curl -X POST http://localhost:8000/webhooks/zendesk \
  -H "Content-Type: application/json" \
  -d '{
    "ticket": {
      "id": 12345,
      "requester": {"email": "customer@example.com"},
      "subject": "Size exchange",
      "description": "I bought a size M shirt, but it is too tight."
    }
  }'
```

### Example: run the agent

```bash
curl -X POST "http://localhost:8000/tickets/<UUID>/run-agent?message=I+want+to+exchange+my+order"
```

---

## How the Modules Work

### Module A — Margin Simulator

- **ETL** loads SKU history (price, cost, return rate, and logistics)
- **Simulator** runs Monte Carlo scenarios for return-rate reduction and order growth
- **Dashboard** lets users adjust parameters and view P10/P50/P90 net-profit estimates

```bash
streamlit run app/module_a_margin/dashboard.py
```

### Module B — Triage Pipeline

- Webhook → **Outbox** → RabbitMQ → worker
- The worker calls **Gemini** with `response_schema=TriageResult` for structured output
- Extracts `intent`, `urgency`, `sentiment`, `summary_points`, and `suggested_queue`
- Updates the ticket idempotently

### Module C — Autonomous Agent

- **ReAct / tool use** architecture with native function calling
- **RAG** with `pgvector` for exchange policies, refunds, and manuals
- **Guardrails**: refunds above `REFUND_HUMAN_APPROVAL_THRESHOLD` require human approval
- Each step is recorded in `agent_traces` for auditing

---

## Tests

```bash
pytest -v --asyncio-mode=auto
pytest --cov=app --cov-report=term-missing
```

The test suite covers the simulator, ETL, guardrails, outbox, triage pipeline, and API endpoints.

---

## Configuration

All environment variables are defined in `.env` (see `.env.example`):

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://aiops:aiops@localhost:5432/aiops` |
| `RABBITMQ_URL` | RabbitMQ connection string | `amqp://aiops:aiops@localhost:5672/` |
| `GEMINI_API_KEY` | Google AI Studio API key | — |
| `GEMINI_MODEL` | Gemini model | `gemini-2.5-flash` |
| `REFUND_HUMAN_APPROVAL_THRESHOLD` | Threshold requiring human approval | `200.00` |
| `LOG_LEVEL` | Logging level | `INFO` |

Get a `GEMINI_API_KEY` at https://aistudio.google.com/app/apikey.

---

## Troubleshooting

| Symptom | Solution |
|---|---|
| `ModuleNotFoundError: app` | Run commands from the project root |
| `could not translate host name "postgres"` | Run `docker compose up -d postgres` |
| `relation "vector" does not exist` | Check that the `pgvector/pgvector:pg16` image is in use |
| Worker does not consume messages | Check `docker compose logs -f rabbitmq` |
| Gemini returns 401 errors | Check `GEMINI_API_KEY` |

---

## Roadmap

- [ ] Fine-tune an in-house classifier to reduce LLM dependency at high volume
- [ ] Add a consolidated ROI dashboard (hours saved × cost per ticket)
- [ ] Add real ERP/carrier integrations (replace mocks)
- [ ] Deploy to Kubernetes with HPA based on queue depth
- [ ] Add semantic response caching for the agent

---

## License

Distributed under the **MIT** license. See [LICENSE](LICENSE) for details.

---

## Author

**JCmamoa** — [github.com/JCmamoa](https://github.com/JCmamoa)
