from dataclasses import dataclass

import yfinance as yf


@dataclass
class MarketSnapshot:
    ticker: str
    current_price: float | None
    market_cap: float | None
    pe_ratio: float | None
    revenue: float | None


def fetch_market_snapshot(ticker: str) -> MarketSnapshot:
    try:
        data = yf.Ticker(ticker)
        info = data.info if data.info else {}
    except Exception:
        info = {}

    return MarketSnapshot(
        ticker=ticker.upper(),
        current_price=info.get("currentPrice") or info.get("regularMarketPrice"),
        market_cap=info.get("marketCap"),
        pe_ratio=info.get("trailingPE"),
        revenue=info.get("totalRevenue"),
    )
