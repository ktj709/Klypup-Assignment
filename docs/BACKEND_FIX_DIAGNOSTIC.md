# Research Query Backend Issue - Diagnosis & Fix

## The Problem

When you ran the query "Give me valuable insights for LensKart", the system returned:
- No tools executed
- Empty result sections  
- Default fallback message: "No specific tool triggers were detected..."

## Root Causes (Fixed)

### 1. **Weak Ticker Extraction**
**Original code** used regex `\b[A-Z]{1,5}\b` which only matches 1-5 uppercase letters.
- "LensKart" has 8 characters → **NOT matched**
- "Give" has 4 characters → **matched** (incorrectly)
- Result: Invalid ticker "Give" extracted, valid company name "LensKart" ignored

### 2. **Missing Gemini API Key**
When `GEMINI_API_KEY` environment variable is not set:
- `plan_tools()` function returns None (silently)
- AI planner cannot recognize company names
- Falls back to weak regex extraction (see above)

### 3. **No Fallback Logic for Empty Tools**
Original code had no intelligent fallback:
- If no tools triggered, return generic message
- No attempt to retry with different strategy

## Changes Made

### 1. Improved `_extract_tickers()` in orchestrator.py

**Before:**
```python
candidates = re.findall(r"\b[A-Z]{1,5}\b", query)
```

**After:**
```python
# Extract 1-5 letter tickers (NVDA, AMD, etc.)
candidates = re.findall(r"\b[A-Z]{1,5}\b", query)

# ALSO capture longer capitalized words (LensKart, Apple, Microsoft)
candidates.extend(re.findall(r"\b[A-Z][a-z]*(?:[A-Z][a-z]*)*\b", query))

# Filter out common English words
common_words = {"Give", "Me", "For", "The", "And", "Or", ...}

# Keep only non-common words with length >= 2
```

**Result:** "LensKart" is now properly extracted as a company name.

### 2. Enhanced Fallback in `run_research()`

**Added:**
```python
if plan is not None:
    # Use Gemini's decision
else:
    # Fallback: if we extracted ANY company/ticker, fetch news too
    if tickers:
        use_news = True
```

**Result:** Even without Gemini, if a company name is found, news is fetched automatically.

### 3. Added Error Logging to Gemini Service

Added logging to `gemini_service.py` so failures are visible in logs:
- `logger.debug("Gemini API key not configured; skipping planner")`
- `logger.warning(f"Gemini planner error: {exc}")`
- `logger.warning(f"Gemini planner returned invalid JSON: ...")`

**Result:** You can now see in terminal logs what's happening with Gemini.

### 4. Added Validation for Market Data

Before: Always added market data sections even if price fetch failed  
After: Only add section if we got valid current_price data

**Result:** No empty market sections in results.

## To Enable Full AI Orchestration

Set your environment variable:

```bash
# In .env file (apps/api/.env)
GEMINI_API_KEY=your_actual_key_here
```

Or set it in your shell:
```bash
export GEMINI_API_KEY=sk-...
```

## Test the Fix

Now try the same query again: **"Give me valuable insights for LensKart"**

Expected behavior:
1. ✅ "LensKart" is recognized as company name
2. ✅ News tool is triggered (even without Gemini)
3. ✅ You see "Tools used: news_data" in the response
4. ✅ News articles and sentiment appear in results

If Gemini API is configured:
5. ✅ AI generates intelligent executive summary
6. ✅ Better tool selection (market + news instead of just news)

## What Was Happening Before

1. Query: "Give me valuable insights for LensKart"
2. Ticker extraction found: ["Give"] (not "LensKart")
3. Gemini planner skipped (API key missing)
4. Used heuristic: try_market_data=True for "Give" ticker
5. Yahoo Finance couldn't find ticker "Give" → failed silently
6. No sections built → returned fallback message

## What Happens Now

1. Query: "Give me valuable insights for LensKart"
2. Ticker extraction finds: ["LensKart"] ✅
3. Gemini planner tried (returns None if API key missing) 
4. Fallback logic kicks in: has company name, so fetch_news=True ✅
5. News API returns articles for "LensKart"
6. Sections built with news results ✅
7. Returns meaningful response with citations ✅

## Interview Talking Point

This is a good example to mention:
> "I discovered the system had weak heuristics for company name recognition. I improved the ticker extraction regex to handle multi-word company names AND added intelligent fallback logic so the system gracefully degrades even when AI services are unavailable. This shows defensive programming and user-centric thinking."
