import json
import time
from google import genai
from google.genai import types

from app.config import settings
from app.schemas import TriageResult
from app.observability.metrics import LLM_LATENCY, TOKENS_USED

_client = genai.Client(api_key=settings.gemini_api_key)

SYSTEM_PROMPT = """Você é um classificador de tickets de e-commerce.
Extraia intenção, urgência, sentimento, resumo em exatamente 3 tópicos,
e a fila sugerida. Responda apenas no schema JSON."""


async def triage_email(subject: str, body: str) -> TriageResult:
    start = time.time()
    prompt = f"Assunto: {subject}\n\nCorpo:\n{body}"

    response = _client.models.generate_content(
        model=settings.gemini_model,
        contents=[SYSTEM_PROMPT, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TriageResult,
            temperature=0.1,
        ),
    )

    LLM_LATENCY.labels(model=settings.gemini_model).observe(time.time() - start)
    if response.usage_metadata:
        TOKENS_USED.labels(model=settings.gemini_model, type="input").inc(
            response.usage_metadata.prompt_token_count or 0
        )
        TOKENS_USED.labels(model=settings.gemini_model, type="output").inc(
            response.usage_metadata.candidates_token_count or 0
        )

    data = json.loads(response.text)
    return TriageResult(**data)