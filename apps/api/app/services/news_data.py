from dataclasses import dataclass
import time

import requests

from app.core.config import get_settings


@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    sentiment: str


def _simple_sentiment(text: str) -> str:
    lowered = text.lower()
    positive_words = ["growth", "beat", "surge", "record", "strong"]
    negative_words = ["drop", "decline", "miss", "weak", "risk", "lawsuit"]

    positive_score = sum(1 for word in positive_words if word in lowered)
    negative_score = sum(1 for word in negative_words if word in lowered)

    if positive_score > negative_score:
        return "positive"
    if negative_score > positive_score:
        return "negative"
    return "neutral"


def fetch_news(company: str, page_size: int = 5) -> list[NewsItem]:
    settings = get_settings()
    api_key = getattr(settings, "news_api_key", "")

    if not api_key:
        return []

    payload = None
    max_attempts = max(1, settings.external_request_retries + 1)

    for attempt in range(max_attempts):
        try:
            response = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": company,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": page_size,
                    "apiKey": api_key,
                },
                timeout=settings.external_request_timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            break
        except requests.RequestException:
            if attempt == max_attempts - 1:
                return []
            time.sleep(0.25 * (attempt + 1))

    if payload is None:
        return []

    items: list[NewsItem] = []
    for article in payload.get("articles", []):
        title = article.get("title", "Untitled")
        items.append(
            NewsItem(
                title=title,
                url=article.get("url", ""),
                source=article.get("source", {}).get("name", "NewsAPI"),
                sentiment=_simple_sentiment(title),
            )
        )

    return items
