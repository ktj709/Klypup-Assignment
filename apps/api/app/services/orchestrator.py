import re

from app.schemas.research import Citation, ResearchRequest, ResearchResponse, Section
from app.services.document_retrieval import retrieve_documents
from app.services.gemini_service import plan_tools, synthesize_summary
from app.services.market_data import fetch_market_snapshot
from app.services.news_data import fetch_news


def _extract_tickers(query: str) -> list[str]:
    # Extract potential ticker symbols and company names from query.
    # First, try 1-5 letter uppercase words (classic ticker format).
    candidates = re.findall(r"\b[A-Z]{1,5}\b", query)
    
    # Also capture longer capitalized words that might be company names (e.g., LensKart, Apple, Microsoft).
    candidates.extend(re.findall(r"\b[A-Z][a-z]*(?:[A-Z][a-z]*)*\b", query))
    
    # Filter out common English words that aren't tickers/companies.
    common_words = {"Give", "Me", "For", "The", "And", "Or", "Is", "A", "An", "In", "On", "At", "To", "From", "By", "With"}
    
    seen: set[str] = set()
    tickers: list[str] = []
    for candidate in candidates:
        if candidate not in seen and candidate not in common_words and len(candidate) >= 2:
            seen.add(candidate)
            tickers.append(candidate)
    return tickers[:5]


def _needs_news(query: str) -> bool:
    keywords = ["news", "sentiment", "headlines", "recent"]
    return any(keyword in query.lower() for keyword in keywords)


def _needs_documents(query: str) -> bool:
    keywords = ["filing", "earnings", "transcript", "sec", "balance sheet"]
    return any(keyword in query.lower() for keyword in keywords)


def run_research(request: ResearchRequest) -> ResearchResponse:
    query = request.query
    tickers = _extract_tickers(query)

    use_market_data = bool(tickers)
    use_news = _needs_news(query)
    use_documents = _needs_documents(query)

    plan = plan_tools(query)
    if plan is not None:
        planned_tickers = plan.get("tickers", [])
        if planned_tickers:
            tickers = planned_tickers
        use_market_data = plan.get("use_market_data", use_market_data)
        use_news = plan.get("use_news", use_news)
        use_documents = plan.get("use_documents", use_documents)
    else:
        # Fallback heuristic: if we have tickers or company names, fetch news and market data
        if tickers:
            use_news = True

    sections: list[Section] = []
    tools_used: list[str] = []

    if use_market_data and tickers:
        market_lines: list[str] = []
        market_citations: list[Citation] = []
        for ticker in tickers:
            snapshot = fetch_market_snapshot(ticker)
            # Only add to sections if we have valid market data
            if snapshot.current_price is not None:
                market_lines.append(
                    f"{snapshot.ticker}: price={snapshot.current_price}, market_cap={snapshot.market_cap}, P/E={snapshot.pe_ratio}, revenue={snapshot.revenue}"
                )
                market_citations.append(
                    Citation(
                        source_type="api",
                        source_name="Yahoo Finance",
                        reference=f"yfinance:{snapshot.ticker}",
                    )
                )

        if market_lines:
            sections.append(
                Section(
                    title="Market Snapshot",
                    body="\n".join(market_lines),
                    citations=market_citations,
                )
            )
            tools_used.append("market_data")

    if use_news:
        company = tickers[0] if tickers else query.split(" ")[0]
        items = fetch_news(company)
        news_body = "\n".join(
            f"[{item.sentiment}] {item.title} ({item.source})" for item in items
        ) or "No recent items found from configured source."
        news_citations = [
            Citation(source_type="article", source_name=item.source, reference=item.url)
            for item in items
            if item.url
        ]
        sections.append(Section(title="News and Sentiment", body=news_body, citations=news_citations))
        tools_used.append("news_data")

    if use_documents:
        hits = retrieve_documents(query)
        doc_body = "\n".join(f"{hit.title}: {hit.snippet}" for hit in hits)
        doc_citations = [
            Citation(source_type="document", source_name="Internal KB", reference=hit.source_ref)
            for hit in hits
        ]
        sections.append(Section(title="Filing and Document Insights", body=doc_body, citations=doc_citations))
        tools_used.append("document_retrieval")

    if not sections:
        sections.append(
            Section(
                title="Query Interpretation",
                body="No specific tool triggers were detected. Try including ticker symbols, earnings, filings, or recent news.",
                citations=[],
            )
        )

    draft_summary = "Automated research summary generated from selected data tools."
    synthesized = synthesize_summary(query=query, sections=sections, tools_used=tools_used)
    if synthesized:
        draft_summary = synthesized

    return ResearchResponse(
        title="AI Research Result",
        executive_summary=draft_summary,
        sections=sections,
        tools_used=list(dict.fromkeys(tools_used)),
    )
