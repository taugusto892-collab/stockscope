document.addEventListener("DOMContentLoaded", function () {
    // ── Navbar search ────────────────────────────────────────────────────────
    const navInput = document.getElementById("navbar-search");
    const navBtn   = document.getElementById("navbar-search-btn");
    if (navBtn) {
        navBtn.addEventListener("click", () => goToStock(navInput.value));
        navInput.addEventListener("keydown", e => { if (e.key === "Enter") goToStock(navInput.value); });
    }

    // ── Main page search ─────────────────────────────────────────────────────
    const mainInput = document.getElementById("main-search");
    const mainBtn   = document.getElementById("main-search-btn");
    if (mainBtn) {
        mainBtn.addEventListener("click", () => goToStock(mainInput.value));
        mainInput.addEventListener("keydown", e => { if (e.key === "Enter") goToStock(mainInput.value); });
    }

    // ── Route detection ──────────────────────────────────────────────────────
    if (document.getElementById("compare-chart")) initComparePage();
    if (document.getElementById("price-chart"))   initStockPage();
});

function goToStock(ticker) {
    ticker = (ticker || "").trim().toUpperCase();
    if (ticker) window.location.href = "/stock/" + ticker;
}

// ════════════════════════════════════════════════════════════════════════════
// INDEX PAGE — comparação 2025
// ════════════════════════════════════════════════════════════════════════════

function initComparePage() {
    fetch("/api/compare/2025?tickers=PETR4.SA,VALE3.SA")
        .then(r => r.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            renderComparePage(data);
        })
        .catch(err => {
            hide("compare-loading");
            show("compare-error");
            document.getElementById("compare-error").textContent =
                "Erro ao carregar dados: " + err.message;
        });
}

function renderComparePage(data) {
    hide("compare-loading");
    show("compare-section");

    const container = document.getElementById("summary-cards");
    data.summaries.forEach(s => {
        const ret      = s.year_return;
        const sign     = ret >= 0 ? "+" : "";
        const cls      = ret >= 0 ? "text-success" : "text-danger";
        const sym      = s.currency === "BRL" ? "R$" : "$";
        const arrow    = ret >= 0 ? "▲" : "▼";

        container.innerHTML += `
            <div class="col-md-6">
                <div class="card border-secondary summary-card">
                    <div class="card-body py-3 px-4">
                        <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
                            <div>
                                <div class="fw-bold fs-5">${s.ticker}</div>
                                <div class="text-secondary small">${s.longName}</div>
                            </div>
                            <div class="text-end">
                                <div class="small text-secondary">Fechamento 2025</div>
                                <div class="fw-semibold">${sym} ${fmtNum(s.last_close, 2)}</div>
                            </div>
                            <div class="text-end">
                                <div class="small text-secondary">Retorno anual</div>
                                <div class="fw-bold fs-4 ${cls}">${arrow} ${sign}${fmtNum(ret, 2)}%</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;
    });

    const fig = JSON.parse(data.comparison_chart);
    Plotly.react("compare-chart", fig.data, fig.layout, { responsive: true, displayModeBar: false });
}

// ════════════════════════════════════════════════════════════════════════════
// STOCK DETAIL PAGE
// ════════════════════════════════════════════════════════════════════════════

function initStockPage() {
    const ticker = document.getElementById("app").dataset.ticker;

    fetch("/api/stock/" + ticker)
        .then(r => r.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            renderStockPage(data);
        })
        .catch(() => {
            hide("stock-loading");
            show("stock-error");
            document.getElementById("stock-error").textContent =
                `Ativo "${ticker}" não encontrado. Verifique se o ticker está correto (ex: PETR4.SA, AAPL).`;
        });
}

function renderStockPage(data) {
    const m = data.metrics;
    const p = data.performance;

    hide("stock-loading");
    show("stock-content");

    // Header
    setText("s-name",     m.longName || "");
    setText("s-exchange", m.exchange || "");
    setText("s-currency", m.currency || "");
    if (m.lastDate) setText("s-lastdate", "Dados até " + m.lastDate);

    // Preço atual
    const sym      = m.currency === "BRL" ? "R$ " : "$ ";
    const dayRet   = p["1D"];
    const priceClr = dayRet == null ? "" : (dayRet >= 0 ? "text-success" : "text-danger");
    const priceEl  = document.getElementById("m-price");
    priceEl.innerHTML = `<span class="${priceClr}">${sym}${fmtNum(m.currentPrice, 2)}</span>`;
    if (dayRet != null) {
        const sign = dayRet >= 0 ? "+" : "";
        priceEl.innerHTML += `<br><small class="${priceClr} fw-normal">${sign}${fmtNum(dayRet, 2)}% hoje</small>`;
    }

    setText("m-mktcap",  fmtMarketCap(m.marketCap, m.currency));
    setText("m-pe",      m.trailingPE != null ? fmtNum(m.trailingPE, 2) + "x" : "—");
    setText("m-volume",  fmtVolume(m.volume));
    setText("m-52h",     m.fiftyTwoWeekHigh != null ? sym + fmtNum(m.fiftyTwoWeekHigh, 2) : "—");
    setText("m-52l",     m.fiftyTwoWeekLow  != null ? sym + fmtNum(m.fiftyTwoWeekLow,  2) : "—");
    setText("m-div",     m.dividendYield != null ? fmtNum(m.dividendYield * 100, 2) + "%" : "—");
    setText("m-beta",    m.beta != null ? fmtNum(m.beta, 2) : "—");

    // Performance badges
    const perfBar = document.getElementById("perf-bar");
    [["1D","1 dia"],["1W","1 sem."],["1M","1 mês"],["6M","6 meses"],["1Y","1 ano"]].forEach(([key, label]) => {
        const val = p[key];
        if (val == null) return;
        const sign = val >= 0 ? "+" : "";
        const cls  = val >= 0 ? "bg-success" : "bg-danger";
        perfBar.innerHTML += `
            <span class="badge ${cls} px-3 py-2" style="font-size:0.85rem">
                ${label}: ${sign}${fmtNum(val, 2)}%
            </span>`;
    });

    // Charts
    const priceChart = JSON.parse(data.price_chart);
    Plotly.react("price-chart", priceChart.data, priceChart.layout,
        { responsive: true, displayModeBar: true, displaylogo: false });

    const volChart = JSON.parse(data.volume_chart);
    Plotly.react("volume-chart", volChart.data, volChart.layout,
        { responsive: true, displayModeBar: false });
}

// ════════════════════════════════════════════════════════════════════════════
// HELPERS
// ════════════════════════════════════════════════════════════════════════════

function show(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = "";
}
function hide(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = "none";
}
function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val ?? "—";
}

function fmtNum(val, decimals) {
    if (val == null) return "—";
    return Number(val)
        .toFixed(decimals)
        .replace(".", ",")
        .replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

function fmtMarketCap(val, currency) {
    if (val == null) return "—";
    const sym = currency === "BRL" ? "R$ " : "$ ";
    if (val >= 1e12) return sym + fmtNum(val / 1e12, 2) + " T";
    if (val >= 1e9)  return sym + fmtNum(val / 1e9,  2) + " B";
    if (val >= 1e6)  return sym + fmtNum(val / 1e6,  2) + " M";
    return sym + fmtNum(val, 0);
}

function fmtVolume(val) {
    if (val == null) return "—";
    if (val >= 1e9) return fmtNum(val / 1e9, 2) + " B";
    if (val >= 1e6) return fmtNum(val / 1e6, 2) + " M";
    if (val >= 1e3) return fmtNum(val / 1e3, 1) + " K";
    return String(Math.round(val));
}
