from flask import Flask, render_template, jsonify, request
from stock_service import get_stock_data, get_year_data
from chart_builder import build_price_chart, build_volume_chart, build_comparison_chart

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stock/<ticker>")
def stock(ticker):
    ticker = ticker.upper().strip()
    return render_template("stock.html", ticker=ticker)


@app.route("/api/stock/<ticker>")
def api_stock(ticker):
    ticker = ticker.upper().strip()
    data = get_stock_data(ticker)
    if "error" in data:
        return jsonify(data), 404

    data["price_chart"] = build_price_chart(data["history"])
    data["volume_chart"] = build_volume_chart(data["history"])
    del data["history"]

    return jsonify(data)


@app.route("/api/compare/<int:year>")
def api_compare(year):
    tickers_param = request.args.get("tickers", "PETR4.SA,VALE3.SA")
    tickers = [t.strip().upper() for t in tickers_param.split(",") if t.strip()]

    stocks_data = [get_year_data(ticker, year) for ticker in tickers]
    valid = [s for s in stocks_data if "error" not in s]

    if not valid:
        return jsonify({"error": "Nenhum dado encontrado para os tickers informados"}), 404

    summaries = [
        {
            "ticker": s["ticker"],
            "longName": s.get("longName", s["ticker"]),
            "year_return": s.get("year_return"),
            "first_close": s.get("first_close"),
            "last_close": s.get("last_close"),
            "currency": s.get("currency", "BRL"),
        }
        for s in valid
    ]

    return jsonify({
        "year": year,
        "comparison_chart": build_comparison_chart(valid),
        "summaries": summaries,
    })


if __name__ == "__main__":
    app.run(debug=True)
