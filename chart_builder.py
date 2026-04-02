import plotly.graph_objects as go
import plotly.io as pio


def build_price_chart(history: list) -> str:
    dates = [r["date"] for r in history]

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=dates,
        open=[r["open"] for r in history],
        high=[r["high"] for r in history],
        low=[r["low"] for r in history],
        close=[r["close"] for r in history],
        name="Preço",
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
        increasing_fillcolor="#26a69a",
        decreasing_fillcolor="#ef5350",
    ))

    fig.add_trace(go.Scatter(
        x=dates, y=[r["sma20"] for r in history],
        name="SMA 20", line=dict(color="#ff9800", width=1.5), opacity=0.9,
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=[r["sma50"] for r in history],
        name="SMA 50", line=dict(color="#2196f3", width=1.5), opacity=0.9,
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=[r["sma200"] for r in history],
        name="SMA 200", line=dict(color="#f44336", width=2), opacity=0.9,
    ))

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#1a1d2e",
        paper_bgcolor="#1a1d2e",
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01,
            xanchor="right", x=1, font=dict(size=11),
        ),
        margin=dict(l=10, r=10, t=35, b=10),
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1A", step="year", stepmode="backward"),
                    dict(step="all", label="Tudo"),
                ],
                bgcolor="#252836",
                activecolor="#3a3d4e",
                font=dict(color="#ccc"),
            )
        ),
    )

    return pio.to_json(fig)


def build_volume_chart(history: list) -> str:
    dates = [r["date"] for r in history]
    volumes = [r["volume"] for r in history]
    colors = [
        "#26a69a" if (r.get("close") or 0) >= (r.get("open") or 0) else "#ef5350"
        for r in history
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dates, y=volumes,
        marker_color=colors,
        name="Volume",
        showlegend=False,
    ))

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#1a1d2e",
        paper_bgcolor="#1a1d2e",
        margin=dict(l=10, r=10, t=5, b=10),
        yaxis=dict(title="Volume"),
    )

    return pio.to_json(fig)


def build_comparison_chart(stocks_data: list) -> str:
    COLORS = ["#00e676", "#2979ff", "#ff9800", "#e91e63", "#9c27b0"]

    fig = go.Figure()

    for i, stock in enumerate(stocks_data):
        if "error" in stock:
            continue

        ticker = stock["ticker"]
        year_return = stock.get("year_return") or 0
        sign = "+" if year_return >= 0 else ""
        color = COLORS[i % len(COLORS)]

        fig.add_trace(go.Scatter(
            x=stock["dates"],
            y=stock["returns"],
            name=f"{ticker} ({sign}{year_return:.1f}%)",
            line=dict(color=color, width=2.5),
            hovertemplate=(
                "<b>" + ticker + "</b><br>"
                "%{x}<br>"
                "Retorno: %{y:.2f}%<extra></extra>"
            ),
        ))

    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="rgba(255,255,255,0.25)",
        line_width=1,
    )

    year = stocks_data[0].get("year", 2025) if stocks_data else 2025

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#1a1d2e",
        paper_bgcolor="#1a1d2e",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=13),
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        yaxis=dict(
            title="Retorno acumulado (%)",
            ticksuffix="%",
            zeroline=False,
        ),
        xaxis=dict(title=""),
        hovermode="x unified",
        title=dict(
            text=f"Performance em {year} — Retorno acumulado desde 01/01/{year}",
            font=dict(size=14),
            x=0.5,
            xanchor="center",
        ),
    )

    return pio.to_json(fig)
