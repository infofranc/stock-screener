import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
from datetime import datetime

st.set_page_config(page_title="STOCK SCREENER TERMINAL", layout="wide", initial_sidebar_state="collapsed")

# TERMINAL CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Courier+Prime:wght@400;700&display=swap');

* { font-family: 'Share Tech Mono', 'Courier New', monospace !important; }

[data-testid="stAppViewContainer"] { background: #0a0a0a; }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }

.main .block-container {
    max-width: 95%;
    padding: 1rem 2rem 2rem;
}

h1,h2,h3 { 
    color: #00ff41 !important; 
    font-family: 'Share Tech Mono' !important; 
    text-transform: uppercase;
    letter-spacing: 2px;
}

p, label, div { color: #00ff41 !important; }

.stSelectbox label, .stSlider label, .stNumberInput label { 
    color: #00ff41 !important; 
    font-size: 11px !important;
    font-weight: bold !important;
}

.stSelectbox > div > div, .stNumberInput > div > div > input {
    background: #0d0d0d !important;
    color: #00ff41 !important;
    border: 1px solid #00ff41 !important;
    font-size: 12px !important;
}

.stButton > button {
    background: #001a00 !important;
    color: #00ff41 !important;
    border: 2px solid #00ff41 !important;
    font-weight: bold !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s;
}

.stButton > button:hover {
    background: #00ff41 !important;
    color: #000 !important;
    box-shadow: 0 0 20px #00ff41;
}

/* DATAFRAME STYLING */
.dataframe {
    background-color: #0d0d0d !important;
    color: #00ff41 !important;
    border: 1px solid #00ff41 !important;
    font-size: 11px !important;
}

.dataframe thead th {
    background-color: #001a00 !important;
    color: #00ff41 !important;
    border: 1px solid #00ff41 !important;
    font-weight: bold !important;
    text-align: left !important;
    padding: 8px !important;
}

.dataframe tbody td {
    background-color: #0a0a0a !important;
    color: #00ff41 !important;
    border: 1px solid #003300 !important;
    padding: 6px !important;
}

.dataframe tbody tr:hover {
    background-color: #001a00 !important;
}

/* Streamlit native table */
[data-testid="stDataFrame"] {
    background: #0d0d0d !important;
    border: 2px solid #00ff41 !important;
}

[data-testid="stDataFrame"] * {
    color: #00ff41 !important;
    background: #0a0a0a !important;
}

.element-container {
    color: #00ff41 !important;
}

/* Metrics */
[data-testid="stMetricValue"] {
    color: #00ff41 !important;
    font-size: 24px !important;
}

[data-testid="stMetricLabel"] {
    color: #00ff41 !important;
    font-size: 12px !important;
}

</style>
""", unsafe_allow_html=True)

st.title("⬛ STOCK SCREENER TERMINAL")
st.markdown("---")

# FUNZIONI INDICATORI
def calculate_hull_ma(data, period=20):
    half_length = int(period / 2)
    sqrt_length = int(np.sqrt(period))
    wma_half = data['Close'].rolling(half_length).apply(lambda x: np.dot(x, np.arange(1, half_length + 1)) / np.arange(1, half_length + 1).sum(), raw=True)
    wma_full = data['Close'].rolling(period).apply(lambda x: np.dot(x, np.arange(1, period + 1)) / np.arange(1, period + 1).sum(), raw=True)
    hull = (2 * wma_half - wma_full).rolling(sqrt_length).apply(lambda x: np.dot(x, np.arange(1, sqrt_length + 1)) / np.arange(1, sqrt_length + 1).sum(), raw=True)
    return hull

def calculate_supertrend(data, period=10, multiplier=3):
    hl2 = (data['High'] + data['Low']) / 2
    atr = data['High'].sub(data['Low']).rolling(period).mean()
    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)
    supertrend = pd.Series(index=data.index, dtype=float)
    direction = pd.Series(index=data.index, dtype=int)
    for i in range(period, len(data)):
        if i == period:
            supertrend.iloc[i] = lower_band.iloc[i]
            direction.iloc[i] = 1
        else:
            if data['Close'].iloc[i] > supertrend.iloc[i-1]:
                supertrend.iloc[i] = lower_band.iloc[i]
                direction.iloc[i] = 1
            else:
                supertrend.iloc[i] = upper_band.iloc[i]
                direction.iloc[i] = -1
    return supertrend, direction

def calculate_ichimoku(data):
    high_9 = data['High'].rolling(9).max()
    low_9 = data['Low'].rolling(9).min()
    tenkan_sen = (high_9 + low_9) / 2
    high_26 = data['High'].rolling(26).max()
    low_26 = data['Low'].rolling(26).min()
    kijun_sen = (high_26 + low_26) / 2
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
    high_52 = data['High'].rolling(52).max()
    low_52 = data['Low'].rolling(52).min()
    senkou_span_b = ((high_52 + low_52) / 2).shift(26)
    return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b

# PARAMETRI CENTRALI
col1, col2, col3, col4 = st.columns(4)

with col1:
    tickers_input = st.text_area("📊 TICKERS (separati da virgola)", "AAPL,MSFT,GOOGL,TSLA,AMZN", height=100)
    tickers = [t.strip().upper() for t in tickers_input.split(',')]

with col2:
    hull_period = st.number_input("🔹 HULL MA PERIOD", 10, 200, 20)
    st_period = st.number_input("🔹 SUPERTREND PERIOD", 5, 50, 10)

with col3:
    st_multiplier = st.number_input("🔹 ST MULTIPLIER", 1.0, 10.0, 3.0, 0.5)
    volume_min = st.number_input("🔹 VOLUME MIN (M)", 0.0, 1000.0, 1.0, 0.5)

with col4:
    st.markdown("### 🎯 AZIONI")
    run_btn = st.button("▶ ESEGUI SCAN", use_container_width=True)
    export_btn = st.button("💾 ESPORTA CSV", use_container_width=True)

st.markdown("---")

if run_btn:
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, ticker in enumerate(tickers):
        try:
            status_text.text(f"⚡ Scanning {ticker}...")
            data = yf.download(ticker, period="1y", interval="1d", progress=False)
            
            if len(data) < 60:
                continue
            
            # Volume filter
            avg_volume = data['Volume'].tail(20).mean()
            if avg_volume < volume_min * 1_000_000:
                continue
            
            # Calcolo indicatori
            hull_ma = calculate_hull_ma(data, hull_period)
            supertrend, st_direction = calculate_supertrend(data, st_period, st_multiplier)
            tenkan, kijun, senkou_a, senkou_b = calculate_ichimoku(data)
            
            last_price = data['Close'].iloc[-1]
            last_hull = hull_ma.iloc[-1]
            last_st = supertrend.iloc[-1]
            last_direction = st_direction.iloc[-1]
            last_tenkan = tenkan.iloc[-1]
            last_kijun = kijun.iloc[-1]
            
            # Segnali
            hull_signal = "🟢 LONG" if last_price > last_hull else "🔴 SHORT"
            st_signal = "🟢 LONG" if last_direction == 1 else "🔴 SHORT"
            ichi_signal = "🟢 LONG" if last_tenkan > last_kijun else "🔴 SHORT"
            
            results.append({
                'TICKER': ticker,
                'PRICE': f"${last_price:.2f}",
                'HULL_MA': f"${last_hull:.2f}",
                'HULL_SIG': hull_signal,
                'SUPERTREND': f"${last_st:.2f}",
                'ST_SIG': st_signal,
                'TENKAN': f"{last_tenkan:.2f}",
                'KIJUN': f"{last_kijun:.2f}",
                'ICHI_SIG': ichi_signal,
                'VOLUME': f"{avg_volume/1e6:.1f}M"
            })
            
        except Exception as e:
            st.warning(f"⚠ Errore su {ticker}: {str(e)}")
        
        progress_bar.progress((idx + 1) / len(tickers))
    
    status_text.text("✅ Scan completato!")
    
    if results:
        df_results = pd.DataFrame(results)
        st.session_state['results'] = df_results
        
        st.markdown("### 📈 RISULTATI SCREENER")
        
        # Mostra tabella con HTML per massima compatibilità
        st.dataframe(df_results, use_container_width=True, height=400)
        
        # Anche versione HTML alternativa
        st.markdown(df_results.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        st.success(f"✅ Trovati {len(df_results)} titoli che soddisfano i criteri")
    else:
        st.error("❌ Nessun risultato trovato")

if export_btn and 'results' in st.session_state:
    csv = st.session_state['results'].to_csv(index=False)
    st.download_button(
        label="⬇ DOWNLOAD CSV",
        data=csv,
        file_name=f"screener_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("🟢 STOCK SCREENER TERMINAL v2.0 | Timeframe: DAILY | Database: Yahoo Finance Free")
