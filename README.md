# AI-Driven Business Ops

> Arquitetura unificada de inteligência operacional e automação para e-commerce:
> otimização de margem, triagem automática com LLM e agentes autônomos com guardrails.

[![CI](https://github.com/JCmamoa/Driven-Business/actions/workflows/ci.yml/badge.svg)](https://github.com/JCmamoa/Driven-Business/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL + pgvector](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.13-FF6600.svg)](https://www.rabbitmq.com/)
[![Gemini](https://img.shields.io/badge/Google-Gemini%202.5%20Flash-4285F4.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Visão Geral

Este projeto implementa uma **arquitetura de referência** para operações de e-commerce orientadas por IA, cobrindo três frentes integradas:

| Módulo | Objetivo | Impacto de Negócio |
|---|---|---|
| **A — Margin Simulator** | Simulação Monte Carlo de margem líquida com redução de devoluções e escala de pedidos | Proteção de margem e decisões data-driven |
| **B — Triage Pipeline** | Classificação automática de tickets via Gemini com Structured Outputs | Redução drástica do First Response Time (FRT) |
| **C — Autonomous Agents** | Agentes ReAct com RAG e guardrails HITL para resolução ponta a ponta | Aumento do *Deflection Rate* com segurança |

A arquitetura prioriza **resiliência operacional**, **confiabilidade de execução** e **impacto direto em métricas** (EBITDA, FRT e taxa de resolução autônoma).

---

## Arquitetura

```text
[Data Sources & Channels] ──► [Ingestion & Messaging] ──► [AI & Analytics Engines] ──► [Action & Observability]
  (ERP, E-commerce, Email)      (Webhooks, RabbitMQ, DLQ)   (Gemini, ML, Simulator)      (External APIs, Dashboards, Outbox)
```

<p align="center">
  <img src="docs/architecture.svg" alt="Arquitetura AI-Driven Business Ops" width="100%">
</p>

### Padrões distribuídos implementados

- **Transactional Outbox** — consistência transacional entre DB e broker
- **Idempotência** — chaves únicas em `processed_messages` evitam ações duplicadas
- **Dead Letter Queue (DLQ)** — com *exponential backoff* para falhas transitórias
- **Structured Outputs** — schema JSON determinístico via `response_schema`
- **Guardrails + Human-in-the-Loop** — reembolsos acima do limite exigem aprovação
- **Tracing completo de agentes** — cada passo do raciocínio persistido em `agent_traces`

---

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| **API** | FastAPI + Uvicorn |
| **Banco** | PostgreSQL 16 + `pgvector` |
| **Mensageria** | RabbitMQ 3.13 + `aio-pika` |
| **IA / LLM** | Google Gemini 2.5 Flash (`google-genai`) |
| **Dados / ML** | pandas, Polars, Scikit-learn, NumPy |
| **Dashboard** | Streamlit |
| **Observabilidade** | `structlog`, `prometheus-client` |
| **Infra** | Docker + Docker Compose |
| **Testes** | Pytest + pytest-asyncio |

---

## Estrutura do Projeto

```text
.
├── app/
│   ├── main.py                    # FastAPI entrypoint
│   ├── config.py                  # Settings (pydantic-settings)
│   ├── db.py                      # Engine + SessionLocal
│   ├── models.py                  # SQLAlchemy models
│   ├── schemas.py                 # Pydantic schemas
│   ├── messaging/                 # Outbox + Broker + DLQ
│   ├── module_a_margin/           # ETL + Simulador + Dashboard
│   ├── module_b_triage/           # Pipeline + LLM client + Connectors
│   ├── module_c_agents/           # ReAct agent + Tools + RAG + Guardrails
│   └── observability/             # Logging + Metrics
├── workers/                       # triage / agent / outbox_publisher
├── migrations/                    # Alembic
├── scripts/                       # seed_data + simulate_traffic
│   └── capture_dashboard.py       # captura screenshot do dashboard
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
# 1. Ambiente Python
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Variáveis
copy .env.example .env
notepad .env    # preencha GEMINI_API_KEY

# 3. Infraestrutura (Docker Desktop aberto)
docker compose up -d postgres rabbitmq

# 4. Schema + dados de exemplo
alembic upgrade head
python -m scripts.seed_data

# 5. Testes
pytest -v --asyncio-mode=auto

# 6. Runtime — abra terminais separados no VS Code
uvicorn app.main:app --reload                     # API
python -m workers.triage_worker                   # Triage
python -m workers.agent_worker                    # Agent
python -m workers.outbox_publisher                # Outbox
streamlit run app/module_a_margin/dashboard.py    # Dashboard
python -m scripts.simulate_traffic                # Tráfego de teste
```

### Preview

![Dashboard de margem](docs/screenshots/dashboard.png)

*Simulador Monte Carlo de margem líquida com redução de devolução e escala de pedidos. Parâmetros ajustáveis em tempo real; saída em P10/P50/P90.*

Para gerar novamente a captura, com o ambiente virtual ativo, o banco populado e o dashboard disponível:

```powershell
pip install playwright
playwright install chromium
python -m scripts.capture_dashboard
```

### Quickstart (macOS / Linux)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # editar GEMINI_API_KEY

docker compose up -d postgres rabbitmq
alembic upgrade head
python -m scripts.seed_data
pytest -v --asyncio-mode=auto

uvicorn app.main:app --reload
```

Para capturar o dashboard no macOS/Linux, instale o Playwright e o Chromium e execute `python -m scripts.capture_dashboard`.

### URLs padrão

| Serviço | URL |
|---|---|
| API / Swagger | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |
| Dashboard de margem | http://localhost:8501 |
| RabbitMQ Management | http://localhost:15672 (`aiops` / `aiops`) |

---

## Endpoints principais

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/webhooks/zendesk` | Ingestão de ticket via webhook |
| `POST` | `/tickets/{id}/run-agent` | Dispara agente autônomo para um ticket |

### Exemplo: webhook Zendesk

```bash
curl -X POST http://localhost:8000/webhooks/zendesk \
  -H "Content-Type: application/json" \
  -d '{
    "ticket": {
      "id": 12345,
      "requester": {"email": "cliente@example.com"},
      "subject": "Troca de tamanho",
      "description": "Comprei uma camiseta M mas ficou apertada."
    }
  }'
```

### Exemplo: acionar agente

```bash
curl -X POST "http://localhost:8000/tickets/<UUID>/run-agent?message=Quero+trocar+meu+pedido"
```

---

## Como os módulos funcionam

### Módulo A — Margin Simulator

- **ETL** lê histórico de SKUs (preço, custo, devolução, logística)
- **Simulador** executa Monte Carlo sobre taxa de devolução e escala de pedidos
- **Dashboard** permite ajustar parâmetros e ver P10/P50/P90 de lucro líquido em tempo real

```bash
streamlit run app/module_a_margin/dashboard.py
```

### Módulo B — Triage Pipeline

- Webhook → **Outbox** → RabbitMQ → Worker
- Worker chama **Gemini** com `response_schema=TriageResult` (JSON determinístico)
- Extrai `intent`, `urgency`, `sentiment`, `summary_points` e `suggested_queue`
- Atualiza o ticket no banco de forma **idempotente**

### Módulo C — Autonomous Agent

- Arquitetura **ReAct / Tool-Use** com `function_calling` nativo
- **RAG** com `pgvector` sobre políticas de troca, reembolso e manuais
- **Guardrails**: reembolsos > `REFUND_HUMAN_APPROVAL_THRESHOLD` viram `pending_human_approval`
- Cada passo registrado em `agent_traces` para auditoria

---

## Testes

```bash
pytest -v --asyncio-mode=auto
pytest --cov=app --cov-report=term-missing
```

Suíte cobre: simulador, ETL, guardrails, outbox, pipeline de triagem e endpoints da API.

---

## Configuração

Todas as variáveis estão em `.env` (veja `.env.example`):

| Variável | Descrição | Padrão |
|---|---|---|
| `DATABASE_URL` | Conexão PostgreSQL | `postgresql+psycopg://aiops:aiops@localhost:5432/aiops` |
| `RABBITMQ_URL` | Conexão RabbitMQ | `amqp://aiops:aiops@localhost:5672/` |
| `GEMINI_API_KEY` | Chave do Google AI Studio | — |
| `GEMINI_MODEL` | Modelo Gemini | `gemini-2.5-flash` |
| `REFUND_HUMAN_APPROVAL_THRESHOLD` | Limite para aprovação humana | `200.00` |
| `LOG_LEVEL` | Nível de log | `INFO` |

Obtenha a `GEMINI_API_KEY` em https://aistudio.google.com/app/apikey.

---

## Troubleshooting

| Sintoma | Solução |
|---|---|
| `ModuleNotFoundError: app` | Execute comandos na raiz do projeto |
| `could not translate host name "postgres"` | `docker compose up -d postgres` |
| `relation "vector" does not exist` | Confirme a imagem `pgvector/pgvector:pg16` |
| Worker não consome | `docker compose logs -f rabbitmq` |
| Erros 401 do Gemini | Verifique `GEMINI_API_KEY` |

---

## Roadmap

- [ ] Fine-tuning de classificador próprio para reduzir dependência de LLM em alto volume
- [ ] Painel de ROI consolidado (horas economizadas × custo por ticket)
- [ ] Integração real com ERP/transportadoras (substituir mocks)
- [ ] Deploy em Kubernetes com HPA baseado em profundidade de fila
- [ ] Cache semântico de respostas do agente

---

## Licença

Distribuído sob licença **MIT**. Veja `LICENSE` para detalhes.

---

## Autor

**JCmamoa** — [github.com/JCmamoa](https://github.com/JCmamoa)
