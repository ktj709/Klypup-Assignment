import json

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.schemas.research import Section


def synthesize_summary(query: str, sections: list[Section], tools_used: list[str]) -> str | None:
    settings = get_settings()
    if not settings.gemini_api_key:
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

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(temperature=0.2),
        contents=f"{instruction}\n\nData:\n{json.dumps(prompt_payload)}",
    )

    text = (response.text or "").strip()
    return text or None
