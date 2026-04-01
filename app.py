import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import io
from datetime import datetime

st.set_page_config(page_title="Global Stock Screener", layout="wide")
st.title("📊 Global Stock Screener — Daily")
st.caption("⏱ Timeframe: **Daily (1D)** — Yahoo Finance via yfinance")

# LISTE MERCATI
SP500 = "AAPL,MSFT,GOOGL,AMZN,NVDA,META,TSLA,BRK-B,LLY,V,UNH,JPM,XOM,MA,JNJ,AVGO,WMT,PG,HD,CVX,MRK,COST,ABBV,KO,PEP,ADBE,NFLX,CRM,BAC,TMO,MCD,CSCO,AMD,ACN,DHR,ABT,TXN,WFC,CMCSA,DIS,PM,INTC,VZ,QCOM,NEE,HON,UNP,NKE,ORCL,IBM,RTX,UPS,LOW,BMY,LIN,COP,MS,SPGI,T,CAT,ELV,GE,AMGN,DE,BA,MDT,AXP,INTU,BLK,GS,PLD,ADI,SYK,SBUX,GILD,AMT,BKNG,TJX,ISRG,ADP,MDLZ,LRCX,MMC,VRTX,NOW,PFE,C,TMUS,REGN,CI,MO,CVS,ZTS,EOG,SO,CB,HCA,DUK,ETN,BDX,SCHW".split(",")
NASDAQ = "AAPL,MSFT,GOOGL,GOOG,AMZN,NVDA,META,TSLA,AVGO,COST,NFLX,AMD,PEP,ADBE,CSCO,TMUS,CMCSA,INTC,TXN,QCOM,INTU,AMGN,HON,AMAT,SBUX,BKNG,ISRG,ADP,VRTX,GILD,REGN,ADI,MU,LRCX,MELI,PANW,KLAC,PYPL,MDLZ,SNPS,CDNS,ASML,MRVL,MAR,CTAS,AZN,ORLY,MNST,FTNT,CSX,ABNB,ADSK,DXCM,CHTR,PCAR,WDAY,NXPI,PAYX,CPRT,CRWD,AEP,ODFL,ROST,KDP,FAST,ON,VRSK,BKR,GEHC,EXC,TEAM,LULU,CSGP,DDOG,CTSH,XEL,IDXX,KHC,BIIB,CCEP,ANSS,ZS,TTD,CDW,WBD,MDB,ILMN,GFS".split(",")
RUSSELL = "SMCI,KVUE,CELH,DOCS,DECK,IONQ,RBLX,HIMS,TPL,JXN,CCCS,FIVE,MNDY,CASY,MOD,FTAI,MATX,IBP,CHH,CNM,GPI,PLAB,COKE,INSM,NEOG,AIT,BCC,GMED,CBZ,AAON,CWEN,DIOD,HELE,CWST,CNX,HQY,CNXC,APAM,MCY,SKYW,TBBK,CRS,CW,VCTR,MWA,SHOO,SANM,POWL,NSP".split(",")
FTSE = "ENI.MI,UCG.MI,ISP.MI,TIT.MI,ENEL.MI,STLAM.MI,STM.MI,G.MI,A2A.MI,AZM.MI,CPR.MI,FBK.MI,RACE.MI,BAMI.MI,BMED.MI,TEN.MI,LDO.MI,HER.MI,PST.MI,ATL.MI,SPM.MI,CNHI.MI,BGN.MI,BZU.MI,PRY.MI,MONC.MI,AMP.MI,IP.MI,SRG.MI,REC.MI".split(",")
DAX = "SIE.DE,SAP.DE,ALV.DE,DTE.DE,VOW3.DE,MBG.DE,BMW.DE,BAYN.DE,ADS.DE,BAS.DE,MUV2.DE,DB1.DE,HEN3.DE,SHL.DE,IFX.DE,DHL.DE,CON.DE,1COV.DE,HNR1.DE,HEI.DE,VOW.DE,BNR.DE,ZAL.DE,RWE.DE,VNA.DE,QIA.DE,PAH3.DE,FRE.DE,P911.DE,HFG.DE".split(",")
ESTOXX = "ASML.AS,SAP.DE,AIR.PA,SIE.DE,LVMH.PA,TTE.PA,MC.PA,SAN.PA,DTE.DE,IBE.MC,PRX.AS,INGA.AS,BN.PA,SU.PA,ADYEN.AS,PHIA.AS,ITX.MC,AD.AS,BBVA.MC,CS.PA,ALV.DE,BNP.PA,ABI.BR,EL.PA,DG.PA,VIE.PA,BAYN.DE,ADS.DE,FP.PA,RMS.PA".split(",")
NIKKEI = "7203.T,6758.T,9984.T,6861.T,8306.T,9433.T,4063.T,6981.T,4502.T,4503.T,8316.T,7974.T,6702.T,8031.T,6501.T,9432.T,4568.T,4507.T,8035.T,2914.T,8001.T,8766.T,4151.T,4188.T,9983.T,6367.T,8058.T,6273.T,4911.T,5108.T".split(",")

MARKETS = {
    "S&P 500 (Top 100)": SP500,
    "Nasdaq 100": NASDAQ,
    "Russell 2000 (Top 50)": RUSSELL,
    "FTSE MIB Italia": FTSE,
    "DAX 40 Germania": DAX,
    "EuroStoxx 50": ESTOXX,
    "Nikkei 225 (Top 30)": NIKKEI,
    "Tutti i mercati": SP500+NASDAQ+RUSSELL+FTSE+DAX+ESTOXX+NIKKEI,
    "Custom": []
}

# SIDEBAR
st.sidebar.header("⚙️ Parametri")
market_choice = st.sidebar.selectbox("Seleziona mercato", list(MARKETS.keys()), index=0)

if market_choice == "Custom":
    custom_input = st.sidebar.text_area("Inserisci ticker (separati da virgola)", value="AAPL,MSFT,GOOGL", height=100)
    selected_tickers = [t.strip().upper() for t in custom_input.split(",") if t.strip()]
else:
    selected_tickers = MARKETS[market_choice]
    st.sidebar.info(f"🎯 {len(selected_tickers)} ticker selezionati da '{market_choice}'")

add_custom = st.sidebar.text_input("➕ Aggiungi ticker extra (opzionale, separati da virgola)")
if add_custom:
    selected_tickers += [t.strip().upper() for t in add_custom.split(",") if t.strip()]

lookback_days = st.sidebar.slider("Lookback segnali (giorni)", 1, 20, 5)
period        = st.sidebar.selectbox("Storico", ["3mo","6mo","1y","2y"], index=1)

st.sidebar.subheader("🔊 Volume Minimo")
min_volume = st.sidebar.number_input("Vol medio 20gg minimo", value=500000, min_value=0, step=100000)

st.sidebar.subheader("SuperTrend")
st_length = st.sidebar.number_input("Length", value=10, min_value=5, max_value=50)
st_mult   = st.sidebar.number_input("Multiplier", value=3.0, min_value=1.0, max_value=10.0, step=0.5)

st.sidebar.subheader("Hull MA")
hma_length = st.sidebar.number_input("HMA Length", value=14, min_value=5, max_value=100)

st.sidebar.subheader("Ichimoku")
ich_tenkan = st.sidebar.number_input("Tenkan", value=9,  min_value=3)
ich_kijun  = st.sidebar.number_input("Kijun",  value=26, min_value=10)
ich_senkou = st.sidebar.number_input("Senkou", value=52, min_value=26)

st.sidebar.divider()
st.sidebar.subheader("📬 Alert Telegram")
tg_token   = st.sidebar.text_input("Bot Token", type="password")
tg_chat_id = st.sidebar.text_input("Chat ID")
tg_on_ich  = st.sidebar.checkbox("Alert Ichimoku",   value=True)
tg_on_st   = st.sidebar.checkbox("Alert SuperTrend", value=True)
tg_on_hma  = st.sidebar.checkbox("Alert Hull MA",    value=True)
tg_on_all  = st.sidebar.checkbox("Alert Tutti e 3",  value=True)

run = st.sidebar.button("🔍 Esegui Screener", use_container_width=True)

# INDICATORI
def hma(series, length):
    half = int(length / 2)
    sqrt_len = int(np.sqrt(length))
    wma1 = series.rolling(half).mean()
    wma2 = series.rolling(length).mean()
    raw  = 2 * wma1 - wma2
    return raw.rolling(sqrt_len).mean()

def supertrend(high, low, close, length, mult):
    hl2 = (high + low) / 2
    tr  = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(int(length)).mean()
    upper = hl2 + mult * atr
    lower = hl2 - mult * atr
    direction = pd.Series(1, index=close.index)
    for i in range(1, len(close)):
        if close.iloc[i] > upper.iloc[i-1]:
            direction.iloc[i] = 1
        elif close.iloc[i] < lower.iloc[i-1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i-1]
            if direction.iloc[i] == 1:
                lower.iloc[i] = max(lower.iloc[i], lower.iloc[i-1])
            else:
                upper.iloc[i] = min(upper.iloc[i], upper.iloc[i-1])
    st_line = pd.Series(np.where(direction == 1, lower, upper), index=close.index)
    return direction, st_line

def ichimoku(high, low, tenkan, kijun, senkou):
    t = (high.rolling(tenkan).max() + low.rolling(tenkan).min()) / 2
    k = (high.rolling(kijun).max()  + low.rolling(kijun).min())  / 2
    sa = ((t + k) / 2).shift(kijun)
    sb = ((high.rolling(senkou).max() + low.rolling(senkou).min()) / 2).shift(kijun)
    cloud_top = pd.concat([sa, sb], axis=1).max(axis=1)
    return cloud_top

# HELPERS
def send_telegram(token, chat_id, text):
    if not token or not chat_id: return False
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)
        return r.status_code == 200
    except: return False

def to_csv(df):
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()

def dl_btn(df, fname, label):
    if not df.empty:
        st.download_button(f"⬇️ {label}", data=to_csv(df), file_name=fname, mime="text/csv", use_container_width=True)

@st.cache_data(ttl=3600)
def get_data(ticker, period):
    try:
        df = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
        if df.empty or len(df) < 60: return None
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df
    except: return None

def vol_ok(df, minv):
    return minv == 0 or float(df["Volume"].tail(20).mean()) >= minv

def check_ich(df, tenkan, kijun, senkou, lb):
    try:
        cloud = ichimoku(df["High"], df["Low"], tenkan, kijun, senkou)
        signal = any(df["Close"].iloc[i-1] <= cloud.iloc[i-1] and df["Close"].iloc[i] > cloud.iloc[i] for i in range(-lb, 0))
        return signal, round(float(df["Close"].iloc[-1]),2), round(float(cloud.iloc[-1]),2), int(df["Volume"].tail(20).mean())
    except: return False, None, None, None

def check_st(df, length, mult, lb):
    try:
        direction, _ = supertrend(df["High"], df["Low"], df["Close"], length, mult)
        signal = any(direction.iloc[i-1]==-1 and direction.iloc[i]==1 for i in range(-lb,0))
        return signal, round(float(df["Close"].iloc[-1]),2), int(df["Volume"].tail(20).mean())
    except: return False, None, None

def check_hma(df, length):
    try:
        h = hma(df["Close"], int(length))
        bullish = float(df["Close"].iloc[-1]) > float(h.iloc[-1]) and float(h.iloc[-1]) > float(h.iloc[-2])
        return bullish, round(float(df["Close"].iloc[-1]),2), round(float(h.iloc[-1]),2), int(df["Volume"].tail(20).mean())
    except: return False, None, None, None

# MAIN
if run:
    tickers = list(set(selected_tickers))
    prog = st.progress(0)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    res_ich, res_st, res_hma, res_all, skipped = [], [], [], [], []

    for i, ticker in enumerate(tickers):
        df = get_data(ticker, period)
        prog.progress((i+1)/len(tickers))
        if df is None: continue
        if not vol_ok(df, min_volume):
            skipped.append(ticker); continue

        s_ich, c_ich, ct,   v_ich = check_ich(df, ich_tenkan, ich_kijun, ich_senkou, lookback_days)
        s_st,  c_st,        v_st  = check_st(df, st_length, st_mult, lookback_days)
        s_hma, c_hma, hv,   v_hma = check_hma(df, hma_length)

        base = {"Ticker": ticker, "Timestamp": ts}
        if s_ich: res_ich.append({**base, "Close": c_ich, "Cloud Top": ct,  "Vol 20gg": v_ich})
        if s_st:  res_st.append( {**base, "Close": c_st,                     "Vol 20gg": v_st})
        if s_hma: res_hma.append({**base, "Close": c_hma, "HMA": hv,         "Vol 20gg": v_hma})
        if s_ich and s_st and s_hma:
            res_all.append({**base, "Close": c_hma or c_st, "Vol 20gg": v_hma or v_st})

    prog.empty()
    st.success(f"✅ Analisi completata — {ts} — Scannerizzati {len(tickers)} ticker")
    if skipped: st.warning(f"⚠️ {len(skipped)} ticker esclusi per volume basso")

    # Telegram
    tg_log = []
    for enabled, label, rows in [
        (tg_on_ich, "🌩️ Ichimoku Breakout", res_ich),
        (tg_on_st,  "⚡ SuperTrend Bullish", res_st),
        (tg_on_hma, "〰️ Hull MA Bullish",    res_hma),
        (tg_on_all, "🎯 Tutti e 3 Segnali",  res_all),
    ]:
        if enabled and rows and tg_token and tg_chat_id:
            msg = f"*📊 Screener*\n*{label}*\n🕐 {ts} | Daily | {market_choice}\n`{'`, `'.join([r['Ticker'] for r in rows[:10]])}`\nTotale: *{len(rows)}*"
            ok  = send_telegram(tg_token, tg_chat_id, msg)
            tg_log.append(("✅" if ok else "❌", label))

    if tg_log:
        with st.expander("📬 Log Telegram"):
            for icon, label in tg_log:
                st.write(f"{icon} {label}")

    df_ich = pd.DataFrame(res_ich)
    df_st  = pd.DataFrame(res_st)
    df_hma = pd.DataFrame(res_hma)
    df_all = pd.DataFrame(res_all)

    tab1, tab2, tab3, tab4 = st.tabs(["🌩️ Ichimoku","⚡ SuperTrend","〰️ Hull MA","🎯 Tutti e 3"])
    with tab1:
        st.subheader(f"Ichimoku Breakout nuvola ↑ (ultimi {lookback_days}gg)")
        st.dataframe(df_ich, use_container_width=True) if not df_ich.empty else st.warning("Nessun segnale.")
        dl_btn(df_ich, f"ichimoku_{ts[:10]}.csv", "Esporta CSV")
    with tab2:
        st.subheader(f"SuperTrend inversione Bullish (ultimi {lookback_days}gg)")
        st.dataframe(df_st,  use_container_width=True) if not df_st.empty  else st.warning("Nessun segnale.")
        dl_btn(df_st,  f"supertrend_{ts[:10]}.csv", "Esporta CSV")
    with tab3:
        st.subheader("Hull MA — Close > HMA con pendenza positiva")
        st.dataframe(df_hma, use_container_width=True) if not df_hma.empty else st.warning("Nessun segnale.")
        dl_btn(df_hma, f"hullma_{ts[:10]}.csv", "Esporta CSV")
    with tab4:
        st.subheader("⭐ Ticker con tutti e 3 i segnali attivi")
        st.dataframe(df_all, use_container_width=True) if not df_all.empty else st.warning("Nessun ticker con tutti e 3.")
        dl_btn(df_all, f"all_signals_{ts[:10]}.csv", "Esporta CSV")

    # Grafico
    st.divider()
    st.subheader("📈 Grafico dettaglio ticker")
    sel = st.selectbox("Seleziona ticker", tickers)
    if sel:
        df = get_data(sel, period)
        if df is not None:
            h_series = hma(df["Close"], int(hma_length))
            dir_st, st_line = supertrend(df["High"], df["Low"], df["Close"], st_length, st_mult)
            colors_vol = ["green" if c>=o else "red" for c,o in zip(df["Close"], df["Open"])]
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Prezzo"))
            if h_series is not None and not h_series.isna().all():
                fig.add_trace(go.Scatter(x=df.index, y=h_series, name=f"HMA({hma_length})", line=dict(color="orange", width=1.5)))
            if st_line is not None and not st_line.isna().all():
                fig.add_trace(go.Scatter(x=df.index, y=st_line, name="SuperTrend", line=dict(color="purple", width=1.5, dash="dot")))
            fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color=colors_vol, opacity=0.25, yaxis="y2"))
            fig.update_layout(title=f"{sel} — Daily Candlestick + HMA + SuperTrend + Volume", xaxis_title="Data", yaxis=dict(title="Prezzo"),
                              yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False), xaxis_rangeslider_visible=False, height=580,
                              legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("👈 Configura i parametri nella sidebar e premi **Esegui Screener**.")
    st.markdown(f"""
    ### Come funziona — Timeframe: **Daily (1D)**  
    🎯 Mercato selezionato: **{market_choice}** ({len(selected_tickers)} ticker)
    
    | Indicatore | Segnale cercato |
    |---|---|
    | **Ichimoku** | Close che rompe la nuvola verso l'alto negli ultimi N giorni |
    | **SuperTrend** | Direzione che passa da -1 (bearish) a +1 (bullish) |
    | **Hull MA** | Close sopra HMA e HMA con pendenza positiva |
    """)
