import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
import requests
import io
from datetime import datetime

st.set_page_config(page_title="Global Stock Screener", layout="wide")
st.title("📊 Global Stock Screener — Daily — Ichimoku · SuperTrend · Hull MA")
st.caption("⏱ Timeframe: **Daily (1D)** — Dati aggiornati da Yahoo Finance via yfinance")

# ─── SIDEBAR ────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Parametri")

TICKERS_DEFAULT = "AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META,JPM,XOM,BRK-B,ASML,SAP,TM,BABA,TSM,NESN.SW,SHELL.AS,SIE.DE,AIR.PA,ENI.MI"

tickers_input = st.sidebar.text_area("Ticker (separati da virgola)", value=TICKERS_DEFAULT, height=150)
lookback_days = st.sidebar.slider("Lookback segnali (giorni)", 1, 20, 5)
period        = st.sidebar.selectbox("Storico (daily bars)", ["3mo", "6mo", "1y", "2y"], index=1)

st.sidebar.subheader("🔊 Volume Minimo")
min_volume = st.sidebar.number_input("Vol medio 20gg minimo", value=500000, min_value=0, step=100000, format="%d")

st.sidebar.subheader("SuperTrend")
st_length = st.sidebar.number_input("Length", value=10, min_value=5, max_value=50)
st_mult   = st.sidebar.number_input("Multiplier", value=3.0, min_value=1.0, max_value=10.0, step=0.5)

st.sidebar.subheader("Hull MA")
hma_length = st.sidebar.number_input("HMA Length", value=14, min_value=5, max_value=100)

st.sidebar.subheader("Ichimoku")
ich_tenkan = st.sidebar.number_input("Tenkan (9)",  value=9,  min_value=3)
ich_kijun  = st.sidebar.number_input("Kijun (26)",  value=26, min_value=10)
ich_senkou = st.sidebar.number_input("Senkou (52)", value=52, min_value=26)

st.sidebar.divider()
st.sidebar.subheader("📬 Alert Telegram")
tg_token   = st.sidebar.text_input("Bot Token", type="password", placeholder="123456:ABC-DEF...")
tg_chat_id = st.sidebar.text_input("Chat ID", placeholder="-100xxxxxxxxxx o @username")

tg_on_ich = st.sidebar.checkbox("Alert Ichimoku",          value=True)
tg_on_st  = st.sidebar.checkbox("Alert SuperTrend",        value=True)
tg_on_hma = st.sidebar.checkbox("Alert Hull MA",           value=True)
tg_on_all = st.sidebar.checkbox("Alert Tutti e 3 segnali", value=True)

run = st.sidebar.button("🔍 Esegui Screener", use_container_width=True)

# ─── TELEGRAM ────────────────────────────────────────────────────────────────
def send_telegram(token, chat_id, text):
    if not token or not chat_id:
        return False
    url  = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, data=data, timeout=10)
        return r.status_code == 200
    except Exception:
        return False

def build_alert_message(section_name, rows, ts):
    if not rows:
        return None
    tickers_str = ", ".join([r["Ticker"] for r in rows])
    msg = (
        f"*📊 Stock Screener Alert*\n"
        f"*{section_name}*\n"
        f"🕐 {ts} | ⏱ Timeframe: Daily\n\n"
        f"Ticker: `{tickers_str}`\n"
        f"Totale segnali: *{len(rows)}*"
    )
    return msg

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def to_csv_bytes(df):
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()

def download_btn(df, filename, label):
    if not df.empty:
        st.download_button(label=f"⬇️ {label}", data=to_csv_bytes(df),
                           file_name=filename, mime="text/csv", use_container_width=True)

@st.cache_data(ttl=3600)
def download_data(ticker, period):
    try:
        df = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
        if df.empty or len(df) < 60:
            return None
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df
    except Exception:
        return None

def passes_volume_filter(df, min_vol):
    if min_vol == 0:
        return True
    return df["Volume"].tail(20).mean() >= min_vol

def check_ichimoku(df, tenkan, kijun, senkou, lookback):
    try:
        ich   = ta.ichimoku(df["High"], df["Low"], df["Close"], tenkan=tenkan, kijun=kijun, senkou=senkou)[0]
        col_a = [c for c in ich.columns if "ISA" in c]
        col_b = [c for c in ich.columns if "ISB" in c]
        if not col_a or not col_b:
            return False, None, None, None
        cloud_top = pd.concat([ich[col_a[0]], ich[col_b[0]]], axis=1).max(axis=1)
        signal = any(
            df["Close"].iloc[i-1] <= cloud_top.iloc[i-1] and df["Close"].iloc[i] > cloud_top.iloc[i]
            for i in range(-lookback, 0)
        )
        avg_vol = round(float(df["Volume"].tail(20).mean()))
        return signal, round(float(df["Close"].iloc[-1]), 2), round(float(cloud_top.iloc[-1]), 2), avg_vol
    except Exception:
        return False, None, None, None

def check_supertrend(df, length, mult, lookback):
    try:
        st_df   = ta.supertrend(df["High"], df["Low"], df["Close"], length=int(length), multiplier=float(mult))
        dir_col = [c for c in st_df.columns if "SUPERTd" in c]
        if not dir_col:
            return False, None, None
        direction = st_df[dir_col[0]]
        avg_vol   = round(float(df["Volume"].tail(20).mean()))
        signal    = any(direction.iloc[i-1] == -1 and direction.iloc[i] == 1 for i in range(-lookback, 0))
        return signal, round(float(df["Close"].iloc[-1]), 2), avg_vol
    except Exception:
        return False, None, None

def check_hma(df, length):
    try:
        hma = ta.hma(df["Close"], length=int(length))
        if hma is None or hma.isna().all():
            return False, None, None, None
        last_hma = float(hma.iloc[-1])
        prev_hma = float(hma.iloc[-2])
        close    = float(df["Close"].iloc[-1])
        avg_vol  = round(float(df["Volume"].tail(20).mean()))
        bullish  = close > last_hma and last_hma > prev_hma
        return bullish, round(close, 2), round(last_hma, 2), avg_vol
    except Exception:
        return False, None, None, None

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if run:
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    total   = len(tickers)
    st.info(f"Analisi di {total} ticker in corso...")
    progress = st.progress(0)

    results_ich, results_st, results_hma, results_all = [], [], [], []
    skipped_vol = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    for i, ticker in enumerate(tickers):
        df = download_data(ticker, period)
        progress.progress((i + 1) / total)
        if df is None:
            continue
        if not passes_volume_filter(df, min_volume):
            skipped_vol.append(ticker)
            continue

        ich_signal, close_ich, cloud_top, vol_ich = check_ichimoku(df, ich_tenkan, ich_kijun, ich_senkou, lookback_days)
        st_signal,  close_st,  vol_st             = check_supertrend(df, st_length, st_mult, lookback_days)
        hma_signal, close_hma, hma_val,  vol_hma  = check_hma(df, hma_length)

        base = {"Ticker": ticker, "Timestamp": ts}
        if ich_signal:
            results_ich.append({**base, "Close": close_ich, "Cloud Top": cloud_top, "Vol Medio 20gg": vol_ich})
        if st_signal:
            results_st.append({**base, "Close": close_st, "Vol Medio 20gg": vol_st})
        if hma_signal:
            results_hma.append({**base, "Close": close_hma, "HMA": hma_val, "Vol Medio 20gg": vol_hma})
        if ich_signal and st_signal and hma_signal:
            results_all.append({**base, "Close": close_hma or close_st or close_ich,
                                 "Vol Medio 20gg": vol_hma or vol_st or vol_ich})

    progress.empty()

    tg_log = []
    if tg_token and tg_chat_id:
        pairs = [
            (tg_on_ich, "🌩️ Ichimoku Breakout ↑",       results_ich),
            (tg_on_st,  "⚡ SuperTrend Reversal Bullish", results_st),
            (tg_on_hma, "〰️ Hull MA Bullish",             results_hma),
            (tg_on_all, "🎯 Tutti e 3 i Segnali",         results_all),
        ]
        for enabled, label, rows in pairs:
            if enabled and rows:
                msg = build_alert_message(label, rows, ts)
                ok  = send_telegram(tg_token, tg_chat_id, msg)
                tg_log.append(("✅" if ok else "❌", label, len(rows)))

    st.success(f"✅ Analisi completata — {ts}")
    if skipped_vol:
        st.warning(f"⚠️ {len(skipped_vol)} ticker esclusi (volume): {', '.join(skipped_vol)}")

    if tg_log:
        with st.expander("📬 Log Alert Telegram"):
            for icon, label, n in tg_log:
                st.write(f"{icon} **{label}** — {n} segnali inviati")
    elif tg_token and tg_chat_id:
        st.info("ℹ️ Nessun alert inviato (nessun segnale attivo).")
    elif not tg_token:
        st.info("💡 Configura Bot Token e Chat ID nella sidebar per ricevere alert Telegram.")

    df_ich = pd.DataFrame(results_ich)
    df_st  = pd.DataFrame(results_st)
    df_hma = pd.DataFrame(results_hma)
    df_all = pd.DataFrame(results_all)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌩️ Ichimoku Breakout",
        "⚡ SuperTrend Reversal",
        "〰️ Hull MA Bullish",
        "🎯 Tutti e 3 i Segnali"
    ])

    with tab1:
        st.subheader(f"Ichimoku — Breakout nuvola ↑ (ultimi {lookback_days} giorni)")
        if not df_ich.empty:
            st.dataframe(df_ich.sort_values("Ticker"), use_container_width=True)
            download_btn(df_ich, f"ichimoku_{ts.replace(' ','_').replace(':','')}.csv", "Esporta CSV Ichimoku")
        else:
            st.warning("Nessun segnale trovato.")

    with tab2:
        st.subheader(f"SuperTrend — Inversione Bullish (ultimi {lookback_days} giorni)")
        if not df_st.empty:
            st.dataframe(df_st.sort_values("Ticker"), use_container_width=True)
            download_btn(df_st, f"supertrend_{ts.replace(' ','_').replace(':','')}.csv", "Esporta CSV SuperTrend")
        else:
            st.warning("Nessun segnale trovato.")

    with tab3:
        st.subheader("Hull MA — Close > HMA con HMA crescente")
        if not df_hma.empty:
            st.dataframe(df_hma.sort_values("Ticker"), use_container_width=True)
            download_btn(df_hma, f"hull_ma_{ts.replace(' ','_').replace(':','')}.csv", "Esporta CSV Hull MA")
        else:
            st.warning("Nessun segnale trovato.")

    with tab4:
        st.subheader("⭐ Ticker con tutti e 3 i segnali attivi")
        if not df_all.empty:
            st.dataframe(df_all, use_container_width=True)
            download_btn(df_all, f"all_signals_{ts.replace(' ','_').replace(':','')}.csv", "Esporta CSV Tutti i Segnali")
        else:
            st.warning("Nessun ticker soddisfa tutti e 3 i segnali.")

    st.divider()
    st.subheader("📈 Grafico dettaglio ticker")
    selected = st.selectbox("Seleziona un ticker", tickers)
    if selected:
        df = download_data(selected, period)
        if df is not None:
            hma_series = ta.hma(df["Close"], length=int(hma_length))
            st_df_plot = ta.supertrend(df["High"], df["Low"], df["Close"],
                                       length=int(st_length), multiplier=float(st_mult))
            st_col = [c for c in st_df_plot.columns
                      if c.startswith("SUPERT_") and "d" not in c and "l" not in c and "s" not in c]
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df.index, open=df["Open"], high=df["High"],
                low=df["Low"], close=df["Close"], name="Prezzo"
            ))
            if hma_series is not None:
                fig.add_trace(go.Scatter(x=df.index, y=hma_series, name=f"HMA({hma_length})",
                                         line=dict(color="orange", width=1.5)))
            if st_col:
                fig.add_trace(go.Scatter(x=df.index, y=st_df_plot[st_col[0]], name="SuperTrend",
                                         line=dict(color="purple", width=1.5, dash="dot")))
            colors_vol = ["green" if c >= o else "red" for c, o in zip(df["Close"], df["Open"])]
            fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume",
                                 marker_color=colors_vol, opacity=0.25, yaxis="y2"))
            fig.update_layout(
                title=f"{selected} — Daily Candlestick + HMA + SuperTrend + Volume",
                xaxis_title="Data",
                yaxis=dict(title="Prezzo"),
                yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False),
                xaxis_rangeslider_visible=False, height=580,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👈 Configura i parametri nella sidebar e premi **Esegui Screener**.")
    st.markdown("""
    ### Come funziona — Timeframe: **Daily (1D)**
    | Indicatore | Segnale cercato |
    |---|---|
    | **Ichimoku** | Close che rompe la nuvola verso l'alto negli ultimi N giorni |
    | **SuperTrend** | Direzione che passa da -1 (bearish) a +1 (bullish) |
    | **Hull MA** | Close sopra HMA e HMA con pendenza positiva |

    ### Alert Telegram
    1. Apri Telegram → cerca **@BotFather**
    2. Invia `/newbot` → segui le istruzioni → ricevi il **Bot Token**
    3. Scrivi un messaggio al tuo bot
    4. Vai su `https://api.telegram.org/bot<TOKEN>/getUpdates` → copia il **chat id**
    5. Incolla Token e Chat ID nella sidebar
    """)
