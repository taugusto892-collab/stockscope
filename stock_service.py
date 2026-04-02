import yfinance as yf
import pandas as pd
import math


def _safe(val):
    if val is None:
        return None
    try:
        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else f
    except (TypeError, ValueError):
        return None


def get_stock_data(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1y")

        if df.empty:
            return {"error": f"Ticker '{ticker}' não encontrado"}

        # Remove timezone info from index
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()
        df["SMA200"] = df["Close"].rolling(200).mean()

        try:
            info = t.info
        except Exception:
            info = {}

        closes = df["Close"]

        def pct(offset):
            if len(closes) > offset:
                return _safe((closes.iloc[-1] / closes.iloc[-1 - offset] - 1) * 100)
            return None

        performance = {
            "1D": pct(1),
            "1W": pct(5),
            "1M": pct(21),
            "6M": pct(126),
            "1Y": _safe((closes.iloc[-1] / closes.iloc[0] - 1) * 100),
        }

        history = []
        for idx, row in df.iterrows():
            history.append({
                "date": str(idx)[:10],
                "open": _safe(row["Open"]),
                "high": _safe(row["High"]),
                "low": _safe(row["Low"]),
                "close": _safe(row["Close"]),
                "volume": _safe(row["Volume"]),
                "sma20": _safe(row["SMA20"]),
                "sma50": _safe(row["SMA50"]),
                "sma200": _safe(row["SMA200"]),
            })

        is_br = ".SA" in ticker.upper()
        current_price = (
            _safe(info.get("currentPrice") or info.get("regularMarketPrice"))
            or _safe(closes.iloc[-1])
        )
        prev_close = _safe(info.get("previousClose")) or (
            _safe(closes.iloc[-2]) if len(closes) > 1 else None
        )

        metrics = {
            "longName": info.get("longName", ticker),
            "exchange": info.get("exchange", "B3" if is_br else "NYSE"),
            "currency": info.get("currency", "BRL" if is_br else "USD"),
            "currentPrice": current_price,
            "previousClose": prev_close,
            "marketCap": _safe(info.get("marketCap")),
            "trailingPE": _safe(info.get("trailingPE")),
            "volume": _safe(info.get("volume") or info.get("regularMarketVolume")),
            "fiftyTwoWeekHigh": _safe(info.get("fiftyTwoWeekHigh")),
            "fiftyTwoWeekLow": _safe(info.get("fiftyTwoWeekLow")),
            "dividendYield": _safe(info.get("dividendYield")),
            "beta": _safe(info.get("beta")),
            "lastDate": history[-1]["date"] if history else None,
        }

        return {
            "ticker": ticker,
            "metrics": metrics,
            "performance": performance,
            "history": history,
        }
    except Exception as e:
        return {"error": str(e)}


def get_year_data(ticker: str, year: int) -> dict:
    try:
        t = yf.Ticker(ticker)
        df = t.history(start=f"{year}-01-01", end=f"{year + 1}-01-01")

        if df.empty:
            return {"error": f"Sem dados para {ticker} em {year}"}

        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        first_close = float(df["Close"].iloc[0])
        df["return_pct"] = (df["Close"] / first_close - 1) * 100

        dates = [str(idx)[:10] for idx in df.index]
        closes = [_safe(v) for v in df["Close"]]
        returns = [_safe(v) for v in df["return_pct"]]
        volumes = [_safe(v) for v in df["Volume"]]

        year_return = _safe((df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100)

        try:
            info = t.info
        except Exception:
            info = {}

        is_br = ".SA" in ticker.upper()

        return {
            "ticker": ticker,
            "year": year,
            "longName": info.get("longName", ticker),
            "currency": info.get("currency", "BRL" if is_br else "USD"),
            "dates": dates,
            "closes": closes,
            "returns": returns,
            "volumes": volumes,
            "year_return": year_return,
            "first_close": _safe(first_close),
            "last_close": _safe(df["Close"].iloc[-1]),
        }
    except Exception as e:
        return {"error": str(e)}
