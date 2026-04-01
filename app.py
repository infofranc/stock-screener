import streamlit as st
import yfinance as yf
import streamlit.components.v1 as components
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
[data-testid="stSidebar"] { display: none; }
.main .block-container { 
    max-width: 1400px; 
    padding: 0 1rem 2rem 1rem; 
    background: #0a0a0a; 
}
h1,h2,h3 { 
    color: #00ff41 !important; 
    font-family: 'Share Tech Mono' !important; 
}
p, label, div { color: #00ff41 !important; }
.stSelectbox label, .stSlider label, .stNumberInput label { 
    color: #00ff41 !important;
    font-size: 0.8rem !important;
}
/* Fix visibility for interactive elements */
[data-baseweb="select"] {
    background: #1a1a1a !important;
    border: 1px solid #00ff41 !important;
}
[data-baseweb="select"] * {
    color: #00ff41 !important;
}
input {
    background: #1a1a1a !important;
    color: #00ff41 !important;
    border: 1px solid #00ff41 !important;
}
.stButton>button {
    background: #0d1117 !important;
    color: #00ff41 !important;
    border: 1px solid #00ff41 !important;
    font-family: 'Share Tech Mono' !important;
    letter-spacing: 2px !important;
    transition: all 0.2s;
    width: 100%;
}
.stButton>button:hover {
    background: #00ff41 !important;
    color: #0a0a0a !important;
    box-shadow: 0 0 20px #00ff41;
}
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #00ff41;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #555 !important;
}
.stTabs [aria-selected="true"] {
    color: #00ff41 !important;
    border-bottom: 2px solid #00ff41 !important;
}
.stProgress > div > div { background: #00ff41 !important; }
/* Metrics */
[data-testid="stMetricValue"] { color: #00ff41 !important; }
/* Ensure table visibility */
.stTable {
    background-color: #0d1117 !important;
    color: #00ff41 !important;
    border: 1px solid #00ff41 !important;
}
table { color: #00ff41 !important; }
thead th { background-color: #1a1a1a !important; color: #00ff41 !important; border: 1px solid #00ff41 !important; }
tbody td { background-color: #0d1117 !important; color: #00ff41 !important; border: 1px solid #1a1a1a !important; }
.stSuccess { background: transparent !important; border: 1px solid #00ff41 !important; color: #00ff41 !important; }
.stInfo { background: transparent !important; border: 1px solid #ffff00 !important; color: #ffff00 !important; }
.stWarning { background: transparent !important; border: 1px solid #ff6b00 !important; color: #ff6b00 !important; }
</style>
""", unsafe_allow_html=True)

# HEADER TERMINAL
now = datetime.now().strftime("%a, %b %d, %Y %H:%M:%S")
st.markdown(f"""
<div style="border: 2px solid #00ff41; padding: 10px; background: #0d1117; margin-bottom: 20px;">
    <h1 style="margin:0; font-size: 1.5rem;">█ STOCK SCREENER TERMINAL</h1>
    <p style="margin:5px 0; font-size: 0.8rem; color: #00ff41; opacity: 0.8;">
        DAILY (1D) &nbsp;|&nbsp; YAHOO FINANCE &nbsp;|&nbsp; ICHIMOKU • SUPERTREND • HULL MA
    </p>
    <div style="text-align: right; font-size: 0.8rem;">{now} ●</div>
</div>
""", unsafe_allow_html=True)

# LISTE MERCATI
SP500="AAPL,MSFT,GOOGL,AMZN,NVDA,META,TSLA,BRK-B,LLY,V,UNH,JPM,XOM,MA,JNJ,AVGO,WMT,PG,HD,CVX,MRK,COST,ABBV,KO,PEP,ADBE,NFLX,CRM,BAC,TMO,MCD,CSCO,AMD,ACN,DHR,ABT,TXN,WFC,CMCSA,DIS,PM,INTC,VZ,QCOM,NEE,HON,UNP,NKE,ORCL,IBM,RTX,UPS,LOW,BMY,LIN,COP,MS,SPGI,T,CAT,ELV,GE,AMGN,DE,BA,MDT,AXP,INTU,BLK,GS,PLD,ADI,SYK,SBUX,GILD,AMT,BKNG,TJX,ISRG,ADP,MDLZ,LRCX,MMC,VRTX,NOW,PFE,C,TMUS,REGN,CI,MO,CVS,ZTS,EOG,SO,CB,HCA,DUK,ETN,BDX,SCHW".split(",")
NASDAQ="AAPL,MSFT,GOOGL,GOOG,AMZN,NVDA,META,TSLA,AVGO,COST,NFLX,AMD,PEP,ADBE,CSCO,TMUS,CMCSA,INTC,TXN,QCOM,INTU,AMGN,HON,AMAT,SBUX,BKNG,ISRG,ADP,VRTX,GILD,REGN,ADI,MU,LRCX,MELI,PANW,KLAC,PYPL,MDLZ,SNPS,CDNS,ASML,MRVL,MAR,CTAS,AZN,ORLY,MNST,FTNT,CSX,ABNB,ADSK,DXCM,CHTR,PCAR,WDAY,NXPI,PAYX,CPRT,CRWD,AEP,ODFL,ROST,KDP,FAST,ON,VRSK,BKR,GEHC,EXC,TEAM,LULU,CSGP,DDOG,CTSH,XEL,IDXX,KHC,BIIB,CCEP,ANSS,ZS,TTD,CDW,WBD,MDB,ILMN,GFS".split(",")
RUSSELL="SMCI,KVUE,CELH,DOCS,DECK,IONQ,RBLX,HIMS,TPL,JXN,CCCS,FIVE,MNDY,CASY,MOD,FTAI,MATX,IBP,CHH,CNM,GPI,PLAB,COKE,INSM,NEOG,AIT,BCC,GMED,CBZ,AAON,CWEN,DIOD,HELE,CWST,CNX,HQY,CNXC,APAM,MCY,SKYW,TBBK,CRS,CW,VCTR,MWA,SHOO,SANM,POWL,NSP".split(",")
FTSE="ENI.MI,UCG.MI,ISP.MI,TIT.MI,ENEL.MI,STLAM.MI,STM.MI,G.MI,A2A.MI,AZM.MI,CPR.MI,FBK.MI,RACE.MI,BAMI.MI,BMED.MI,TEN.MI,LDO.MI,HER.MI,PST.MI,ATL.MI,SPM.MI,CNHI.MI,BGN.MI,BZU.MI,PRY.MI,MONC.MI,AMP.MI,IP.MI,SRG.MI,REC.MI".split(",")
DAX="SIE.DE,SAP.DE,ALV.DE,DTE.DE,VOW3.DE,MBG.DE,BMW.DE,BAYN.DE,ADS.DE,BAS.DE,MUV2.DE,DB1.DE,HEN3.DE,SHL.DE,IFX.DE,DHL.DE,CON.DE,1COV.DE,HNR1.DE,HEI.DE,VOW.DE,BNR.DE,ZAL.DE,RWE.DE,VNA.DE,QIA.DE,PAH3.DE,MRK.DE,BEI.DE,P911.DE".split(",")
CAC40="OR.PA,AIR.PA,MC.PA,KER.PA,RMS.PA,EL.PA,SAN.PA,BNP.PA,TTE.PA,CS.PA,DG.PA,BN.PA,SU.PA,VIE.PA,STLAP.PA,ACA.PA,ML.PA,GLE.PA,SGO.PA,AI.PA".split(",")
CRYPTO="BTC-USD,ETH-USD,BNB-USD,SOL-USD,XRP-USD,ADA-USD,DOGE-USD,AVAX-USD,DOT-USD,TRX-USD".split(",")
ESTOXX="ASML.AS,SAP.DE,AIR.PA,SIE.DE,LVMH.PA,TTE.PA,MC.PA,SAN.PA,DTE.DE,IBE.MC,PRX.AS,INGA.AS,BN.PA,SU.PA,ADYEN.AS,PHIA.AS,ITX.MC,AD.AS,BBVA.MC,CS.PA,ALV.DE,BNP.PA,ABI.BR,EL.PA,DG.PA,VIE.PA,BAYN.DE,ADS.DE,FP.PA,RMS.PA".split(",")
NIKKEI="7203.T,6758.T,9984.T,6861.T,8306.T,9433.T,4063.T,6981.T,4502.T,4503.T,8316.T,7974.T,6702.T,8031.T,6501.T,9432.T,4568.T,4507.T,8035.T,2914.T,8001.T,8766.T,4151.T,4188.T,9983.T,6367.T,8058.T,6273.T,4911.T,5108.T".split(",")

MARKETS={
    "S&P 500":SP500,
    "NASDAQ 100":NASDAQ,
    "RUSSELL 2000":RUSSELL,
    "FTSE MIB":FTSE,
    "DAX 40":DAX,
    "CAC 40":CAC40,
    "EUROSTOXX 50":ESTOXX,
    "NIKKEI 225":NIKKEI,
    "CRYPTO":CRYPTO,
    "ALL MARKETS":SP500+NASDAQ+RUSSELL+FTSE+DAX+CAC40+ESTOXX+NIKKEI+CRYPTO
}

# PANNELLO PARAMETRI CENTRALE
st.markdown("""
<div style="background: #1a1a1a; padding: 15px; border-radius: 5px; border-left: 5px solid #00ff41; margin-bottom: 20px;">
    <h3 style="margin-top:0;">> PARAMETRI SCREENER</h3>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns([2,1,1,1])
with c1:
    market = st.selectbox("MERCATO", list(MARKETS.keys()))
    ticker_list = MARKETS[market]
with c2:
    lookback = st.slider("LOOKBACK (GG)", 1, 20, 5)
with c3:
    min_vol = st.number_input("VOL. MIN", value=500000, step=100000, format="%d")
with c4:
    period = st.selectbox("STORICO", ["3mo","6mo","1y","2y"], index=1)

st.markdown(f"""
<div style="background: #0d1117; padding: 10px; border: 1px dashed #00ff41; font-family: monospace; font-size: 0.85rem; color: #00ff41;">
    MERCATO: <span style="color:#fff;">{market}</span> &nbsp;&nbsp; 
    TICKER: <span style="color:#fff;">{len(ticker_list)}</span> &nbsp;&nbsp; 
    LOOKBACK: <span style="color:#fff;">{lookback}D</span> &nbsp;&nbsp; 
    TIMEFRAME: <span style="color:#fff;">DAILY 1D</span>
</div>
""", unsafe_allow_html=True)

run = st.button("[ ESEGUI SCREENER ]")

# INDICATORI
def hma(s,l):
    h=int(l/2);sq=int(np.sqrt(l))
    return (2*s.rolling(h).mean()-s.rolling(l).mean()).rolling(sq).mean()

def supertrend(h,l,c,length,mult):
    hl2=(h+l)/2
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    atr=tr.rolling(int(length)).mean()
    up=hl2+mult*atr
    low=hl2-mult*atr
    d=pd.Series(1,index=c.index)
    for i in range(1,len(c)):
        if c.iloc[i]>up.iloc[i-1]: d.iloc[i]=1
        elif c.iloc[i]<low.iloc[i-1]: d.iloc[i]=-1
        else: d.iloc[i]=d.iloc[i-1]
    return d,atr

def get_data(t,p):
    try:
        d = yf.download(t, period=p, interval="1d", progress=False)
        if len(d)<30: return None
        return d
    except: return None

def to_csv(df): return df.to_csv(index=False).encode('utf-8')

if run:
    res_ich, res_st, res_hma, res_all = [],[],[],[]
    prog = st.progress(0)
    status_msg = st.empty()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    for i, t in enumerate(ticker_list):
        status_msg.markdown(f"⚡ ANALISI: {t}")
        df=get_data(t,period)
        prog.progress((i+1)/len(ticker_list))
        
        if df is None: continue
        
        try:
            # Volume filter
            if float(df["Volume"].iloc[-20:].mean()) < min_vol: continue
            
            # Ichimoku
            cl = df["Close"]
            hi = df["High"]
            lo = df["Low"]
            # Senkou Span B (52)
            span_b = (hi.rolling(52).max() + lo.rolling(52).min()) / 2
            # Senkou Span A (9,26)
            tenkan = (hi.rolling(9).max() + lo.rolling(9).min()) / 2
            kijun = (hi.rolling(26).max() + lo.rolling(26).min()) / 2
            span_a = (tenkan + kijun) / 2
            
            # Ichimoku breakout detection
            s_ich = any(cl.iloc[j-1] < max(span_a.iloc[j-26], span_b.iloc[j-26]) and 
                       cl.iloc[j] > max(span_a.iloc[j-26], span_b.iloc[j-26]) 
                       for j in range(-lookback, 0))
            
            # SuperTrend reversal
            d, _ = supertrend(df["High"], df["Low"], df["Close"], 10, 3)
            s_st = any(d.iloc[j-1] == -1 and d.iloc[j] == 1 for j in range(-lookback, 0))
            
            # HMA trend
            hv = hma(df["Close"], 14)
            s_hma = float(df["Close"].iloc[-1]) > float(hv.iloc[-1]) and \
                    float(hv.iloc[-1]) > float(hv.iloc[-2])
            
            last_close = round(float(df["Close"].iloc[-1]), 2)
            vol_avg = int(df["Volume"].iloc[-20:].mean())
            base = {"TICKER": t, "CLOSE": last_close, "VOL_20GG": vol_avg, "SCAN": ts}
            
            if s_ich: res_ich.append(base)
            if s_st: res_st.append(base)
            if s_hma: res_hma.append(base)
            if s_ich and s_st and s_hma: res_all.append(base)
            
        except: continue
        
    prog.empty()
    status_msg.empty()
    
    st.markdown(f"""
    <div style="background: #00ff41; color: #0a0a0a; padding: 10px; font-weight: bold; border-radius: 3px; margin-bottom: 20px;">
        > SCAN COMPLETATO — {ts} — {len(ticker_list)} TICKER — ICH:{len(res_ich)} ST:{len(res_st)} HMA:{len(res_hma)} COMBO:{len(res_all)}
    </div>
    """, unsafe_allow_html=True)
    
    tab1,tab2,tab3,tab4=st.tabs(["1 ICHIMOKU","2 SUPERTREND","3 HULL MA","4 ALL SIGNALS"])
    
    with tab1:
        st.markdown(f"### > ICHIMOKU BREAKOUT NUVOLA [N={lookback}gg] — {len(res_ich)} SEGNALI")
        if res_ich:
            df_ich = pd.DataFrame(res_ich)
            st.table(df_ich)
            st.download_button("[ EXPORT CSV ]", data=to_csv(df_ich), file_name=f"ichimoku_{ts[:10]}.csv", mime="text/csv", key="d1")
        else: st.markdown("> NO SIGNALS DETECTED")
        
    with tab2:
        st.markdown(f"### > SUPERTREND REVERSAL BULLISH [N={lookback}gg] — {len(res_st)} SEGNALI")
        if res_st:
            df_st = pd.DataFrame(res_st)
            st.table(df_st)
            st.download_button("[ EXPORT CSV ]", data=to_csv(df_st), file_name=f"supertrend_{ts[:10]}.csv", mime="text/csv", key="d2")
        else: st.markdown("> NO SIGNALS DETECTED")
        
    with tab3:
        st.markdown(f"### > HULL MA BULLISH [CLOSE > HMA, SLOPE+] — {len(res_hma)} SEGNALI")
        if res_hma:
            df_hma = pd.DataFrame(res_hma)
            st.table(df_hma)
            st.download_button("[ EXPORT CSV ]", data=to_csv(df_hma), file_name=f"hullma_{ts[:10]}.csv", mime="text/csv", key="d3")
        else: st.markdown("> NO SIGNALS DETECTED")
        
    with tab4:
        st.markdown(f"### > ALL 3 SIGNALS ACTIVE — {len(res_all)} TICKER")
        if res_all:
            df_all = pd.DataFrame(res_all)
            st.table(df_all)
            st.download_button("[ EXPORT CSV ]", data=to_csv(df_all), file_name=f"all_signals_{ts[:10]}.csv", mime="text/csv", key="d4")
        else: st.markdown("> NO TICKER WITH ALL 3 SIGNALS")

    # TRADINGVIEW INTEGRATION
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.markdown("### > ANALISI GRAFICA TRADINGVIEW", unsafe_allow_html=True)
    
    all_found = sorted(list(set([x['TICKER'] for x in (res_ich + res_st + res_hma)])))
    if all_found:
        sel_ticker = st.selectbox("DETTAGLIO TICKER", all_found)
        tv_s = sel_ticker
        if ".MI" in tv_s: tv_s = "MIL:" + tv_s.replace(".MI","")
        elif ".DE" in tv_s: tv_s = "XETR:" + tv_s.replace(".DE","")
        elif ".PA" in tv_s: tv_s = "EURONEXT:" + tv_s.replace(".PA","")
        
        components.html(f"""
            <div id="tv-chart"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
              "width": "100%",
              "height": 500,
              "symbol": "{tv_s}",
              "interval": "D",
              "timezone": "Etc/UTC",
              "theme": "dark",
              "style": "1",
              "locale": "it",
              "toolbar_bg": "#f1f3f6",
              "enable_publishing": false,
              "allow_symbol_change": true,
              "container_id": "tv-chart"
            }});
            </script>
        """, height=520)
    else:
        st.info("Esegui lo screener per visualizzare i grafici dei ticker identificati.")

else:
    st.markdown("""
    <div style="text-align: center; padding: 50px; border: 2px solid #00ff41; background: #0d1117;">
        <h2 style="color: #00ff41;">███████████████</h2>
        <p>> SELEZIONA PARAMETRI E PREMI [ ESEGUI SCREENER ]</p>
        <p style="font-size: 0.8rem; opacity: 0.6;">ICHIMOKU BREAKOUT &nbsp;•&nbsp; SUPERTREND REVERSAL &nbsp;•&nbsp; HULL MA BULLISH</p>
        <h2 style="color: #00ff41;">███████████████</h2>
    </div>
    """, unsafe_allow_html=True)import streamlit as st
import yfinance as yf
import streamlit.components.v1 as components
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
[data-testid="stSidebar"] { display: none; }
.main .block-container { 
    max-width: 1400px; 
    padding: 0 1rem 2rem 1rem; 
    background: #0a0a0a; 
}
h1,h2,h3 { 
    color: #00ff41 !important; 
    font-family: 'Share Tech Mono' !important; 
}
p, label, div { color: #00ff41 !important; }
.stSelectbox label, .stSlider label, .stNumberInput label { 
    color: #00ff41 !important;
    font-size: 0.8rem !important;
}
/* Fix visibility for interactive elements */
[data-baseweb="select"] {
    background: #1a1a1a !important;
    border: 1px solid #00ff41 !important;
}
[data-baseweb="select"] * {
    color: #00ff41 !important;
}
input {
    background: #1a1a1a !important;
    color: #00ff41 !important;
    border: 1px solid #00ff41 !important;
}
.stButton>button {
    background: #0d1117 !important;
    color: #00ff41 !important;
    border: 1px solid #00ff41 !important;
    font-family: 'Share Tech Mono' !important;
    letter-spacing: 2px !important;
    transition: all 0.2s;
    width: 100%;
}
.stButton>button:hover {
    background: #00ff41 !important;
    color: #0a0a0a !important;
    box-shadow: 0 0 20px #00ff41;
}
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #00ff41;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #555 !important;
}
.stTabs [aria-selected="true"] {
    color: #00ff41 !important;
    border-bottom: 2px solid #00ff41 !important;
}
.stProgress > div > div { background: #00ff41 !important; }
/* Metrics */
[data-testid="stMetricValue"] { color: #00ff41 !important; }
/* Ensure table visibility */
.stTable {
    background-color: #0d1117 !important;
    color: #00ff41 !important;
    border: 1px solid #00ff41 !important;
}
table { color: #00ff41 !important; }
thead th {
    background-color: #1a1a1a !important;
    color: #00ff41 !important;
    border: 1px solid #00ff41 !important;
}
tbody td {
    background-color: #0d1117 !important;
    color: #00ff41 !important;
    border: 1px solid #1a1a1a !important;
}
.stSuccess { background: transparent !important; border: 1px solid #00ff41 !important; color: #00ff41 !important; }
.stInfo { background: transparent !important; border: 1px solid #ffff00 !important; color: #ffff00 !important; }
.stWarning { background: transparent !important; border: 1px solid #ff6b00 !important; color: #ff6b00 !important; }
</style>
""", unsafe_allow_html=True)

# HEADER TERMINAL
now = datetime.now().strftime("%a, %b %d, %Y %H:%M:%S")
st.markdown(f"""
<div style="border: 2px solid #00ff41; padding: 20px; text-transform: uppercase;">
    <h1 style="margin:0; font-size: 2.5rem;">█ STOCK SCREENER TERMINAL</h1>
    <p style="margin:5px 0; color: #00ff41; opacity: 0.8;">DAILY (1D) &nbsp;|&nbsp; YAHOO FINANCE &nbsp;|&nbsp; ICHIMOKU • SUPERTREND • HULL MA</p>
    <p style="margin:0; text-align: right; font-size: 0.9rem;">{now} ●</p>
</div>
""", unsafe_allow_html=True)

# LISTE MERCATI
SP500="AAPL,MSFT,GOOGL,AMZN,NVDA,META,TSLA,BRK-B,LLY,V,UNH,JPM,XOM,MA,JNJ,AVGO,WMT,PG,HD,CVX,MRK,COST,ABBV,KO,PEP,ADBE,NFLX,CRM,BAC,TMO,MCD,CSCO,AMD,ACN,DHR,ABT,TXN,WFC,CMCSA,DIS,PM,INTC,VZ,QCOM,NEE,HON,UNP,NKE,ORCL,IBM,RTX,UPS,LOW,BMY,LIN,COP,MS,SPGI,T,CAT,ELV,GE,AMGN,DE,BA,MDT,AXP,INTU,BLK,GS,PLD,ADI,SYK,SBUX,GILD,AMT,BKNG,TJX,ISRG,ADP,MDLZ,LRCX,MMC,VRTX,NOW,PFE,C,TMUS,REGN,CI,MO,CVS,ZTS,EOG,SO,CB,HCA,DUK,ETN,BDX,SCHW".split(",")
NASDAQ="AAPL,MSFT,GOOGL,GOOG,AMZN,NVDA,META,TSLA,AVGO,COST,NFLX,AMD,PEP,ADBE,CSCO,TMUS,CMCSA,INTC,TXN,QCOM,INTU,AMGN,HON,AMAT,SBUX,BKNG,ISRG,ADP,VRTX,GILD,REGN,ADI,MU,LRCX,MELI,PANW,KLAC,PYPL,MDLZ,SNPS,CDNS,ASML,MRVL,MAR,CTAS,AZN,ORLY,MNST,FTNT,CSX,ABNB,ADSK,DXCM,CHTR,PCAR,WDAY,NXPI,PAYX,CPRT,CRWD,AEP,ODFL,ROST,KDP,FAST,ON,VRSK,BKR,GEHC,EXC,TEAM,LULU,CSGP,DDOG,CTSH,XEL,IDXX,KHC,BIIB,CCEP,ANSS,ZS,TTD,CDW,WBD,MDB,ILMN,GFS".split(",")
RUSSELL="SMCI,KVUE,CELH,DOCS,DECK,IONQ,RBLX,HIMS,TPL,JXN,CCCS,FIVE,MNDY,CASY,MOD,FTAI,MATX,IBP,CHH,CNM,GPI,PLAB,COKE,INSM,NEOG,AIT,BCC,GMED,CBZ,AAON,CWEN,DIOD,HELE,CWST,CNX,HQY,CNXC,APAM,MCY,SKYW,TBBK,CRS,CW,VCTR,MWA,SHOO,SANM,POWL,NSP".split(",")
FTSE="ENI.MI,UCG.MI,ISP.MI,TIT.MI,ENEL.MI,STLAM.MI,STM.MI,G.MI,A2A.MI,AZM.MI,CPR.MI,FBK.MI,RACE.MI,BAMI.MI,BMED.MI,TEN.MI,LDO.MI,HER.MI,PST.MI,ATL.MI,SPM.MI,CNHI.MI,BGN.MI,BZU.MI,PRY.MI,MONC.MI,AMP.MI,IP.MI,SRG.MI,REC.MI".split(",")
DAX="SIE.DE,SAP.DE,ALV.DE,DTE.DE,VOW3.DE,MBG.DE,BMW.DE,BAYN.DE,ADS.DE,BAS.DE,MUV2.DE,DB1.DE,HEN3.DE,SHL.DE,IFX.DE,DHL.DE,CON.DE,1COV.DE,HNR1.DE,HEI.DE,VOW.DE,BNR.DE,ZAL.DE,RWE.DE,VNA.DE,QIA.DE,PAH3.DE,CBK.DE,PUM.DE,MTX.DE".split(",")
CAC40="OR.PA,AIR.PA,MC.PA,KER.PA,RMS.PA,EL.PA,SAN.PA,BNP.PA,TTE.PA,CS.PA,DG.PA,BN.PA,SU.PA,VIE.PA,STLAP.PA,ACA.PA,ML.PA,GLE.PA,SGO.PA,AI.PA".split(",")
CRYPTO="BTC-USD,ETH-USD,BNB-USD,SOL-USD,XRP-USD,ADA-USD,DOGE-USD,AVAX-USD,DOT-USD,TRX-USD".split(",")
ESTOXX="ASML.AS,SAP.DE,AIR.PA,SIE.DE,LVMH.PA,TTE.PA,MC.PA,SAN.PA,DTE.DE,IBE.MC,PRX.AS,INGA.AS,BN.PA,SU.PA,ADYEN.AS,PHIA.AS,ITX.MC,AD.AS,BBVA.MC,CS.PA,ALV.DE,BNP.PA,ABI.BR,EL.PA,DG.PA,VIE.PA,BAYN.DE,ADS.DE,FP.PA,RMS.PA".split(",")
NIKKEI="7203.T,6758.T,9984.T,6861.T,8306.T,9433.T,4063.T,6981.T,4502.T,4503.T,8316.T,7974.T,6702.T,8031.T,6501.T,9432.T,4568.T,4507.T,8035.T,2914.T,8001.T,8766.T,4151.T,4188.T,9983.T,6367.T,8058.T,6273.T,4911.T,5108.T".split(",")

MARKETS={
    "S&P 500":SP500,
    "NASDAQ 100":NASDAQ,
    "RUSSELL 2000":RUSSELL,
    "FTSE MIB":FTSE,
    "DAX 40":DAX,
    "CAC 40":CAC40,
    "EUROSTOXX 50":ESTOXX,
    "NIKKEI 225":NIKKEI,
    "CRYPTO":CRYPTO,
    "ALL MARKETS":SP500+NASDAQ+RUSSELL+FTSE+DAX+CAC40+ESTOXX+NIKKEI+CRYPTO
}

# PANNELLO PARAMETRI CENTRALE
st.markdown("""
<div style="background: #1a1a1a; padding: 15px; border-left: 5px solid #00ff41; margin: 20px 0;">
    <h3 style="margin:0;">> PARAMETRI SCREENER</h3>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns([2,1,1,1])
with c1:
    market = st.selectbox("MERCATO", list(MARKETS.keys()))
    tickers = MARKETS[market]
with c2:
    lookback = st.slider("LOOKBACK (GG)", 1, 20, 5)
with c3:
    min_vol = st.number_input("VOL. MIN", value=500000, step=100000, format="%d")
with c4:
    period = st.selectbox("STORICO", ["3mo","6mo","1y","2y"], index=1)

st.markdown(f"""
<div style="background: #0d1117; padding: 10px; border: 1px dashed #00ff41; font-family: monospace; font-size: 0.85rem;">
    MERCATO: <span style="color:#00ff41">{market}</span> | 
    TICKER: <span style="color:#00ff41">{len(tickers)}</span> | 
    LOOKBACK: <span style="color:#00ff41">{lookback}D</span> | 
    TIMEFRAME: <span style="color:#00ff41">DAILY 1D</span>
</div>
""", unsafe_allow_html=True)

run = st.button("[ ESEGUI SCREENER ]")

# INDICATORI
def hma(s,l):
    h=int(l/2);sq=int(np.sqrt(l))
    return (2*s.rolling(h).mean()-s.rolling(l).mean()).rolling(sq).mean()

def supertrend(h,l,c,length,mult):
    hl2=(h+l)/2
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    atr=tr.rolling(int(length)).mean()
    up=hl2+mult*atr
    low=hl2-mult*atr
    d=pd.Series(1,index=c.index)
    for i in range(1,len(c)):
        if c.iloc[i]>up.iloc[i-1]: d.iloc[i]=1
        elif c.iloc[i]<low.iloc[i-1]: d.iloc[i]=-1
        else: d.iloc[i]=d.iloc[i-1]
    return d, (up if d.iloc[-1]==-1 else low)

@st.cache_data(ttl=3600)
def get_data(t,p):
    try:
        d=yf.download(t,period=p,interval="1d",progress=False)
        if len(d)<50: return None
        return d
    except: return None

def to_csv(df): return df.to_csv(index=False).encode('utf-8')

if run:
    res_ich, res_st, res_hma, res_all = [],[],[],[]
    ticker_list = sorted(list(set(tickers)))
    prog = st.progress(0)
    status_msg = st.empty()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    for i, t in enumerate(ticker_list):
        status_msg.markdown(f"⚡ ANALISI: {t}")
        df=get_data(t,period)
        prog.progress((i+1)/len(ticker_list))
        if df is None: continue
        
        try:
            if float(df["Volume"].iloc[-20:].mean()) < min_vol: continue
            
            cl = df["Close"]
            # Ichimoku cloud breakout
            hi = df["High"].rolling(9).mean()
            lo = df["Low"].rolling(9).mean()
            tenkan = (hi+lo)/2
            hi2 = df["High"].rolling(26).mean()
            lo2 = df["Low"].rolling(26).mean()
            kijun = (hi2+lo2)/2
            senkou_a = ((tenkan+kijun)/2).shift(26)
            hi3 = df["High"].rolling(52).mean()
            lo3 = df["Low"].rolling(52).mean()
            senkou_b = ((hi3+lo3)/2).shift(26)
            
            s_ich = any(cl.iloc[j-1] < max(senkou_a.iloc[j-1], senkou_b.iloc[j-1]) and 
                        cl.iloc[j] > max(senkou_a.iloc[j], senkou_b.iloc[j]) for j in range(-lookback,0))
            
            # SuperTrend reversal
            d,_ = supertrend(df["High"],df["Low"],df["Close"],10,3)
            s_st = any(d.iloc[j-1] == -1 and d.iloc[j] == 1 for j in range(-lookback,0))
            
            # HMA trend
            hv = hma(df["Close"],14)
            s_hma = float(df["Close"].iloc[-1]) > float(hv.iloc[-1]) and float(hv.iloc[-1]) > float(hv.iloc[-2])
            
            last_close = round(float(df["Close"].iloc[-1]),2)
            vol_avg = int(df["Volume"].iloc[-20:].mean())
            base = {"TICKER":t,"CLOSE":last_close,"VOL_20GG":vol_avg,"SCAN":ts}
            
            if s_ich: res_ich.append(base)
            if s_st: res_st.append(base)
            if s_hma: res_hma.append(base)
            if s_ich and s_st and s_hma: res_all.append(base)
        except: continue

    prog.empty()
    status_msg.empty()
    
    st.markdown(f"""
    <div style="background: #00ff41; color: #0a0a0a; padding: 10px; font-weight: bold; margin: 20px 0;">
        > SCAN COMPLETATO — {ts} — {len(ticker_list)} TICKER — ICH:{len(res_ich)} ST:{len(res_st)} HMA:{len(res_hma)} COMBO:{len(res_all)}
    </div>
    """,unsafe_allow_html=True)

    df_ich=pd.DataFrame(res_ich); df_st=pd.DataFrame(res_st); df_hma=pd.DataFrame(res_hma); df_all=pd.DataFrame(res_all)
    
    tab1,tab2,tab3,tab4=st.tabs(["1 ICHIMOKU","2 SUPERTREND","3 HULL MA","4 ALL SIGNALS"])
    
    with tab1:
        st.markdown(f"### > ICHIMOKU BREAKOUT NUVOLA [N={lookback}gg] — {len(res_ich)} SEGNALI")
        if not df_ich.empty:
            st.table(df_ich)
            st.download_button("[ EXPORT CSV ]",data=to_csv(df_ich),file_name=f"ichimoku_{ts[:10]}.csv",mime="text/csv", key="d1")
        else: st.markdown("> NO SIGNALS DETECTED")

    with tab2:
        st.markdown(f"### > SUPERTREND REVERSAL BULLISH [N={lookback}gg] — {len(res_st)} SEGNALI")
        if not df_st.empty:
            st.table(df_st)
            st.download_button("[ EXPORT CSV ]",data=to_csv(df_st),file_name=f"supertrend_{ts[:10]}.csv",mime="text/csv", key="d2")
        else: st.markdown("> NO SIGNALS DETECTED")

    with tab3:
        st.markdown(f"### > HULL MA BULLISH [CLOSE > HMA, SLOPE+] — {len(res_hma)} SEGNALI")
        if not df_hma.empty:
            st.table(df_hma)
            st.download_button("[ EXPORT CSV ]",data=to_csv(df_hma),file_name=f"hullma_{ts[:10]}.csv",mime="text/csv", key="d3")
        else: st.markdown("> NO SIGNALS DETECTED")

    with tab4:
        st.markdown(f"### > ALL 3 SIGNALS ACTIVE — {len(res_all)} TICKER")
        if not df_all.empty:
            st.table(df_all)
            st.download_button("[ EXPORT CSV ]",data=to_csv(df_all),file_name=f"all_signals_{ts[:10]}.csv",mime="text/csv", key="d4")
        else: st.markdown("> NO TICKER WITH ALL 3 SIGNALS")

    # TRADINGVIEW INTEGRATION
    st.markdown("<hr style='border: 1px solid #00ff41;'>", unsafe_allow_html=True)
    st.markdown("### > ANALISI GRAFICA TRADINGVIEW", unsafe_allow_html=True)
    
    all_found = list(set(df_ich['TICKER'].tolist() + df_st['TICKER'].tolist() + df_hma['TICKER'].tolist())) if not df_ich.empty or not df_st.empty or not df_hma.empty else []
    
    if all_found:
        sel_ticker = st.selectbox("DETTAGLIO TICKER", sorted(all_found))
        tv_s = sel_ticker
        if ".MI" in tv_s: tv_s = "MIL:" + tv_s.replace(".MI","")
        elif ".DE" in tv_s: tv_s = "XETR:" + tv_s.replace(".DE","")
        elif ".PA" in tv_s: tv_s = "EURONEXT:" + tv_s.replace(".PA","")
        elif "-USD" in tv_s: tv_s = "BINANCE:" + tv_s.replace("-USD","") + "USDT"
        
        components.html(f"""
            <div id="tv"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
              "width": "100%",
              "height": 500,
              "symbol": "{tv_s}",
              "interval": "D",
              "timezone": "Etc/UTC",
              "theme": "dark",
              "style": "1",
              "locale": "it",
              "toolbar_bg": "#f1f3f6",
              "enable_publishing": false,
              "hide_top_toolbar": false,
              "save_image": false,
              "container_id": "tv"
            }});
            </script>
        """, height=520)
else:
    st.markdown("""
    <div style="border: 1px solid #00ff41; padding: 40px; text-align: center; margin-top: 50px;">
        <h2 style="color: #00ff41;">███████████████</h2>
        <p style="font-size: 1.2rem;">> SELEZIONA PARAMETRI E PREMI [ ESEGUI SCREENER ]</p>
        <p style="color: #00ff41; opacity: 0.6;">ICHIMOKU BREAKOUT • SUPERTREND REVERSAL • HULL MA BULLISH</p>
        <h2 style="color: #00ff41;">███████████████</h2>
    </div>
    """, unsafe_allow_html=True)
