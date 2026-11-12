from prometheus_client import Counter, Histogram, Gauge

LLM_LATENCY = Histogram("llm_call_latency_seconds", "Latência de chamadas LLM", ["model"])
TICKETS_TRIAGED = Counter("tickets_triaged_total", "Tickets triados", ["intent"])
AGENT_ACTIONS = Counter("agent_actions_total", "Ações de agentes", ["tool", "status"])
QUEUE_DEPTH = Gauge("queue_depth", "Profundidade da fila", ["queue"])
TOKENS_USED = Counter("llm_tokens_total", "Tokens consumidos", ["model", "type"])
DEFLECTION_RATE = Gauge("deflection_rate", "Taxa de resolução autônoma")