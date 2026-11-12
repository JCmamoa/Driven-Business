# Driven-Business

## AI-Driven Business Ops

Arquitetura unificada de inteligência operacional e automação:
simulador de margem, triagem automática com LLM e agentes autônomos com guardrails.

## Stack
- FastAPI + Uvicorn
- SQLAlchemy + PostgreSQL (pgvector)
- RabbitMQ (broker) + Transactional Outbox + DLQ
- Google Gemini (2.5 Flash) com Structured Outputs
- Streamlit (dashboard de margem)
- Pytest (testes)

## Quickstart (Windows 10 + VS Code)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # edite GEMINI_API_KEY

docker compose up -d postgres rabbitmq
alembic upgrade head
python -m scripts.seed_data

pytest -v --asyncio-mode=auto

uvicorn app.main:app --reload
# em terminais separados:
python -m workers.triage_worker
python -m workers.agent_worker
python -m workers.outbox_publisher
streamlit run app/module_a_margin/dashboard.py
```

- API: http://localhost:8000/docs
- Dashboard: http://localhost:8501
- RabbitMQ: http://localhost:15672 (aiops/aiops)

## Módulos
- **A** — Simulador de margem (ETL + Monte Carlo + Streamlit)
- **B** — Pipeline de triagem (Gemini + Structured Outputs + idempotência)
- **C** — Agentes autônomos (ReAct + RAG + Guardrails HITL)
