import json
import logging
import re
from typing import Any

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.schemas.research import Section

logger = logging.getLogger("klypup.gemini")


def _extract_json_object(text: str) -> dict[str, Any] | None:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def plan_tools(query: str) -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.gemini_api_key:
        logger.debug("Gemini API key not configured; skipping planner")
        return None

    client = genai.Client(api_key=settings.gemini_api_key)

    instruction = (
        "You are a tool planner for an investment research system. "
        "Return only valid JSON with this exact shape: "
        '{"tickers": ["NVDA"], "use_market_data": true, "use_news": true, "use_documents": false}. '
        "Rules: identify up to 5 stock tickers if present, and set tool flags based on user intent. "
        "Do not include any extra keys or prose."
    )

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            config=types.GenerateContentConfig(temperature=0.0),
            contents=f"{instruction}\n\nQuery:\n{query}",
        )
    except Exception as exc:
        logger.warning(f"Gemini planner error: {exc}")
        return None

    parsed = _extract_json_object(response.text or "")
    if not parsed:
        logger.warning(f"Gemini planner returned invalid JSON: {response.text}")
        return None

    tickers_raw = parsed.get("tickers", [])
    tickers = [str(item).upper() for item in tickers_raw if isinstance(item, str)][:5]

    return {
        "tickers": tickers,
        "use_market_data": bool(parsed.get("use_market_data", False)),
        "use_news": bool(parsed.get("use_news", False)),
        "use_documents": bool(parsed.get("use_documents", False)),
    }


def synthesize_summary(query: str, sections: list[Section], tools_used: list[str]) -> str | None:
    settings = get_settings()
    if not settings.gemini_api_key:
        logger.debug("Gemini API key not configured; skipping synthesis")
        return None

    client = genai.Client(api_key=settings.gemini_api_key)

    prompt_payload = {
        "query": query,
        "tools_used": tools_used,
        "sections": [
            {
                "title": section.title,
                "body": section.body,
                "citations": [citation.model_dump() for citation in section.citations],
            }
            for section in sections
        ],
    }

    instruction = (
        "You are an equity research assistant. Return a concise 3-5 sentence executive summary based on the provided tool outputs. "
        "Do not invent facts. If data is incomplete, state uncertainty explicitly."
    )

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            config=types.GenerateContentConfig(temperature=0.2),
            contents=f"{instruction}\n\nData:\n{json.dumps(prompt_payload)}",
        )
    except Exception as exc:
        logger.warning(f"Gemini synthesis error: {exc}")
        return None

    text = (response.text or "").strip()
    return text or None
