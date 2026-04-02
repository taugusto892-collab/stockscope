# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**StockScope** is a Flask web application for real-time stock market analysis. It supports both Brazilian stocks (B3 exchange, `.SA` suffix) and US stocks, with a Portuguese-language UI.

## Running the App

```bash
pip install -r requirements.txt
python app.py
# Runs on http://localhost:5000 with debug mode enabled
```

No build step required. No test suite or linting configured.

## Architecture

The app has three backend modules with clear responsibilities:

- **`app.py`** — Flask routes only. Four endpoints: `GET /`, `GET /stock/<ticker>`, `GET /api/stock/<ticker>`, `GET /api/compare/<year>`.
- **`stock_service.py`** — All yfinance data fetching and pandas calculations (SMAs, returns, metrics). `_safe(val)` handles NaN/Inf normalization.
- **`chart_builder.py`** — Builds Plotly chart JSON (candlestick, volume, comparison). Returns serializable dicts, not rendered HTML.

**Data flow:** `main.js` fetches JSON from API routes → Flask delegates to `stock_service.py` → `chart_builder.py` → Plotly.js renders on the client.

## Key Behaviors

- Ticker suffix `.SA` determines exchange (B3/BRL) vs US (NYSE/USD) — used for currency display and labeling throughout.
- Comparison endpoint defaults to `PETR4.SA,VALE3.SA` and accepts `?tickers=T1,T2` query param.
- All tickers are `.upper()`-ed at the route level before processing.
- No caching — every request calls yfinance live.

## GitHub Repository

Repository: https://github.com/taugusto892-collab/stockscope  
Remote: `origin` (HTTPS, authenticated via GitHub CLI)  
Default branch: `master`

## Auto-sync to GitHub (MANDATORY)

**After every file change in this project, you MUST:**

1. Stage all modified files: `git add <changed files>`
2. Commit with a descriptive message
3. Push to GitHub: `git push origin master`

Use the `gh` CLI located at `C:\Program Files\GitHub CLI\gh.exe` if needed.  
Always use the full path `/c/Program Files/GitHub CLI/gh.exe` in bash.

The commit message format:
```
<short description of what changed>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

Do this automatically without asking for confirmation — syncing to GitHub is always authorized for this project.
