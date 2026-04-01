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

/* DATAFRAME FIX - Ensuring high contrast */
.stDataFrame { 
    border: 1px solid #00ff41 !important; 
}

/* Target streamlit's internal dataframe styling */
[data-testid="stDataFrame"] * { 
    color: #00ff41 !important; 
    background-color: #000000 !important; 
}

/* Ensure table headers and cell text are visible */
div[data-testid="stDataFrame"] div[role="gridcell"], 
div[data-testid="stDataFrame"] div[role="columnheader"] {
    color: #00ff41 !important;
    background-color: #0d1117 !important;
}

.stSuccess { background: transparent !important; border: 1px solid #00ff41 !important; color: #00ff41 !important; }
.stInfo { background: transparent !important; border: 1px solid #ffff00 !important; color: #ffff00 !important; }
.stWarning { background: transparent !important; border: 1px solid #ff6b00 !important; color: #ff6b00 !important; }

</style>
""", unsafe_allow_html=True)

# HEADER TERMINAL
now = datetime.now().strftime("%a, %b %d, %Y %H:%M:%S")
st.markdown(f"""
<div style='background:#0d1117; border:1px solid #00ff41; padding:12px 20px; margin-bottom:4px; display:flex; justify-content:space-between; align-items:center;'>
    <div style='color:#00ff41; font-size:1.4rem; font-weight:700; letter-spacing:3px;'>█ STOCK SCREENER TERMINAL</div>
    <div style='color:#555; font-size:0.75rem;'>DAILY (1D) &nbsp;|&nbsp; YAHOO FINANCE &nbsp;|&nbsp; ICHIMOKU • SUPERTREND • HULL MA</div>
    <div style='color:#00ff41; font-size:0.85rem;'>{now} ●</div>
</div>
""", unsafe_allow_html=True)

# LISTE MERCATI
SP500="AAPL,MSFT,GOOGL,AMZN,NVDA,META,TSLA,BRK-B,LLY,V,UNH,JPM,XOM,MA,JNJ,AVGO,WMT,PG,HD,CVX,MRK,COST,ABBV,KO,PEP,ADBE,NFLX,CRM,BAC,TMO,MCD,CSCO,AMD,ACN,DHR,ABT,TXN,WFC,CMCSA,DIS,PM,INTC,VZ,QCOM,NEE,HON,UNP,NKE,ORCL,IBM,RTX,UPS,LOW,BMY,LIN,COP,MS,SPGI,T,CAT,ELV,GE,AMGN,DE,BA,MDT,AXP,INTU,BLK,GS,PLD,ADI,SYK,SBUX,GILD,AMT,BKNG,TJX,ISRG,ADP,MDLZ,LRCX,MMC,VRTX,NOW,PFE,C,TMUS,REGN,CI,MO,CVS,ZTS,EOG,SO,CB,HCA,DUK,ETN,BDX,SCHW".split(",")
NASDAQ="AAPL,MSFT,GOOGL,GOOG,AMZN,NVDA,META,TSLA,AVGO,COST,NFLX,AMD,PEP,ADBE,CSCO,TMUS,CMCSA,INTC,TXN,QCOM,INTU,AMGN,HON,AMAT,SBUX,BKNG,ISRG,ADP,VRTX,GILD,REGN,ADI,MU,LRCX,MELI,PANW,KLAC,PYPL,MDLZ,SNPS,CDNS,ASML,MRVL,MAR,CTAS,AZN,ORLY,MNST,FTNT,CSX,ABNB,ADSK,DXCM,CHTR,PCAR,WDAY,NXPI,PAYX,CPRT,CRWD,AEP,ODFL,ROST,KDP,FAST,ON,VRSK,BKR,GEHC,EXC,TEAM,LULU,CSGP,DDOG,CTSH,XEL,IDXX,KHC,BIIB,CCEP,ANSS,ZS,TTD,CDW,WBD,MDB,ILMN,GFS".split(",")
RUSSELL="SMCI,KVUE,CELH,DOCS,DECK,IONQ,RBLX,HIMS,TPL,JXN,CCCS,FIVE,MNDY,CASY,MOD,FTAI,MATX,IBP,CHH,CNM,GPI,PLAB,COKE,INSM,NEOG,AIT,BCC,GMED,CBZ,AAON,CWEN,DIOD,HELE,CWST,CNX,HQY,CNXC,APAM,MCY,SKYW,TBBK,CRS,CW,VCTR,MWA,SHOO,SANM,POWL,NSP".split(",")
FTSE="ENI.MI,UCG.MI,ISP.MI,TIT.MI,ENEL.MI,STLAM.MI,STM.MI,G.MI,A2A.MI,AZM.MI,CPR.MI,FBK.MI,RACE.MI,BAMI.MI,BMED.MI,TEN.MI,LDO.MI,HER.MI,PST.MI,ATL.MI,SPM.MI,CNHI.MI,BGN.MI,BZU.MI,PRY.MI,MONC.MI,AMP.MI,IP.MI,SRG.MI,REC.MI".split(",")
DAX="SIE.DE,SAP.DE,ALV.DE,DTE.DE,VOW3.DE,MBG.DE,BMW.DE,BAYN.DE,ADS.DE,BAS.DE,MUV2.DE,DB1.DE,HEN3.DE,SHL.DE,IFX.DE,DHL.DE,CON.DE,1COV.DE,HNR1.DE,HEI.DE,VOW.DE,BNR.DE,ZAL.DE,RWE.DE,VNA.DE,QIA.DE,PAH3.DE,FRE.DE,P911.DE,HFG.DE".split(",")
ESTOXX="ASML.AS,SAP.DE,AIR.PA,SIE.DE,LVMH.PA,TTE.PA,MC.PA,SAN.PA,DTE.DE,IBE.MC,PRX.AS,INGA.AS,BN.PA,SU.PA,ADYEN.AS,PHIA.AS,ITX.MC,AD.AS,BBVA.MC,CS.PA,ALV.DE,BNP.PA,ABI.BR,EL.PA,DG.PA,VIE.PA,BAYN.DE,ADS.DE,FP.PA,RMS.PA".split(",")
NIKKEI="7203.T,6758.T,9984.T,6861.T,8306.T,9433.T,4063.T,6981.T,4502.T,4503.T,8316.T,7974.T,6702.T,8031.T,6501.T,9432.T,4568.T,4507.T,8035.T,2914.T,8001.T,8766.T,4151.T,4188.T,9983.T,6367.T,8058.T,6273.T,4911.T,5108.T".split(",")

MARKETS={"S&P 500":SP500,"NASDAQ 100":NASDAQ,"RUSSELL 2000":RUSSELL,"FTSE MIB":FTSE,"DAX 40":DAX,"EUROSTOXX 50":ESTOXX,"NIKKEI 225":NIKKEI,"ALL MARKETS":SP500+NASDAQ+RUSSELL+FTSE+DAX+ESTOXX+NIKKEI}

# PANNELLO PARAMETRI CENTRALE
st.markdown("""
<div style='background:#0d1117; border:1px solid #333; border-top:2px solid #00ff41; padding:1.5rem 2rem; margin-bottom:4px;'>
    <div style='color:#555; font-size:0.7rem; letter-spacing:2px; margin-bottom:1rem;'>> PARAMETRI SCREENER</div>
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
<div style='background:#0d1117; border:1px solid #1a1a1a; padding:8px 20px; margin-top:4px; margin-bottom:4px; display:flex; gap:2rem;'>
    <span style='color:#555; font-size:0.75rem;'>MERCATO: <span style='color:#00ff41;'>{market}</span></span>
    <span style='color:#555; font-size:0.75rem;'>TICKER: <span style='color:#00ff41;'>{len(tickers)}</span></span>
    <span style='color:#555; font-size:0.75rem;'>LOOKBACK: <span style='color:#00ff41;'>{lookback}D</span></span>
    <span style='color:#555; font-size:0.75rem;'>TIMEFRAME: <span style='color:#00ff41;'>DAILY 1D</span></span>
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
    
    # Vectorized check for direction change where possible or simple loop for logic clarity
    for i in range(1,len(c)):
        if c.iloc[i]>up.iloc[i-1]:
            d.iloc[i]=1
        elif c.iloc[i]<low.iloc[i-1]:
            d.iloc[i]=-1
        else:
            d.iloc[i]=d.iloc[i-1]
            
        if d.iloc[i]==1:
            low.iloc[i]=max(low.iloc[i],low.iloc[i-1])
        else:
            up.iloc[i]=min(up.iloc[i],up.iloc[i-1])
            
    return d,pd.Series(np.where(d==1,low,up),index=c.index)

def ichimoku(h,l,t,k,s):
    ta=(h.rolling(t).max()+l.rolling(t).min())/2
    ka=(h.rolling(k).max()+l.rolling(k).min())/2
    sa=((ta+ka)/2).shift(k)
    sb=((h.rolling(s).max()+l.rolling(s).min())/2).shift(k)
    return pd.concat([sa,sb],axis=1).max(axis=1)

@st.cache_data(ttl=3600)
def get_data(t,p):
    try:
        df=yf.download(t,period=p,interval="1d",auto_adjust=True,progress=False)
        if df.empty or len(df)<60:return None
        df.columns=[c[0] if isinstance(c,tuple) else c for c in df.columns]
        return df
    except:return None

def to_csv(df):
    buf=io.StringIO()
    df.to_csv(buf,index=False)
    return buf.getvalue()

# MAIN
if run:
    prog=st.progress(0)
    ts=datetime.now().strftime("%Y-%m-%d %H:%M")
    res_ich,res_st,res_hma,res_all=[],[],[],[]
    ticker_list=list(set(tickers))
    
    status_msg = st.empty()
    
    for i,t in enumerate(ticker_list):
        status_msg.markdown(f"<div style='color:#00ff41; font-size:0.75rem;'>⚡ ANALISI: {t}</div>", unsafe_allow_html=True)
        df=get_data(t,period)
        prog.progress((i+1)/len(ticker_list))
        
        if df is None:continue
        
        try:
            if float(df["Volume"].iloc[-20:].mean())<min_vol:continue
            
            # Ichimoku cloud breakout
            cl=ichimoku(df["High"],df["Low"],9,26,52)
            s_ich=any(df["Close"].iloc[j-1]<=cl.iloc[j-1] and df["Close"].iloc[j]>cl.iloc[j] for j in range(-lookback,0))
            
            # SuperTrend reversal
            d,_=supertrend(df["High"],df["Low"],df["Close"],10,3)
            s_st=any(d.iloc[j-1]==-1 and d.iloc[j]==1 for j in range(-lookback,0))
            
            # HMA trend
            hv=hma(df["Close"],14)
            s_hma=float(df["Close"].iloc[-1])>float(hv.iloc[-1]) and float(hv.iloc[-1])>float(hv.iloc[-2])
            
            last_close = round(float(df["Close"].iloc[-1]),2)
            vol_avg = int(df["Volume"].iloc[-20:].mean())
            
            base={"TICKER":t,"CLOSE":last_close,"VOL_20GG":vol_avg,"SCAN":ts}
            
            if s_ich: res_ich.append(base)
            if s_st: res_st.append(base)
            if s_hma: res_hma.append(base)
            if s_ich and s_st and s_hma: res_all.append(base)
            
        except Exception as e:
            continue
            
    prog.empty()
    status_msg.empty()
    
    st.markdown(f"<div style='background:#0d1117;border:1px solid #00ff41;padding:8px 20px;margin:4px 0;color:#00ff41;font-size:0.8rem;'>> SCAN COMPLETATO — {ts} — {len(ticker_list)} TICKER — ICH:{len(res_ich)} ST:{len(res_st)} HMA:{len(res_hma)} COMBO:{len(res_all)}</div>",unsafe_allow_html=True)
    
    df_ich=pd.DataFrame(res_ich);df_st=pd.DataFrame(res_st);df_hma=pd.DataFrame(res_hma);df_all=pd.DataFrame(res_all)
    
    tab1,tab2,tab3,tab4=st.tabs(["1 ICHIMOKU","2 SUPERTREND","3 HULL MA","4 ALL SIGNALS"])
    
    with tab1:
        st.markdown(f"<div style='color:#555;font-size:0.75rem;padding:4px 0;'>> ICHIMOKU BREAKOUT NUVOLA [N={lookback}gg] — {len(res_ich)} SEGNALI</div>",unsafe_allow_html=True)
        if not df_ich.empty:
            st.dataframe(df_ich,use_container_width=True,hide_index=True)
            st.download_button("[ EXPORT CSV ]",data=to_csv(df_ich),file_name=f"ichimoku_{ts[:10]}.csv",mime="text/csv", key="d1")
        else:st.markdown("<div style='color:#555;font-size:0.8rem;padding:1rem;'>> NO SIGNALS DETECTED</div>",unsafe_allow_html=True)
        
    with tab2:
        st.markdown(f"<div style='color:#555;font-size:0.75rem;padding:4px 0;'>> SUPERTREND REVERSAL BULLISH [N={lookback}gg] — {len(res_st)} SEGNALI</div>",unsafe_allow_html=True)
        if not df_st.empty:
            st.dataframe(df_st,use_container_width=True,hide_index=True)
            st.download_button("[ EXPORT CSV ]",data=to_csv(df_st),file_name=f"supertrend_{ts[:10]}.csv",mime="text/csv", key="d2")
        else:st.markdown("<div style='color:#555;font-size:0.8rem;padding:1rem;'>> NO SIGNALS DETECTED</div>",unsafe_allow_html=True)
        
    with tab3:
        st.markdown(f"<div style='color:#555;font-size:0.75rem;padding:4px 0;'>> HULL MA BULLISH [CLOSE > HMA, SLOPE+] — {len(res_hma)} SEGNALI</div>",unsafe_allow_html=True)
        if not df_hma.empty:
            st.dataframe(df_hma,use_container_width=True,hide_index=True)
            st.download_button("[ EXPORT CSV ]",data=to_csv(df_hma),file_name=f"hullma_{ts[:10]}.csv",mime="text/csv", key="d3")
        else:st.markdown("<div style='color:#555;font-size:0.8rem;padding:1rem;'>> NO SIGNALS DETECTED</div>",unsafe_allow_html=True)
        
    with tab4:
        st.markdown(f"<div style='color:#ffff00;font-size:0.75rem;padding:4px 0;'>> ALL 3 SIGNALS ACTIVE — {len(res_all)} TICKER</div>",unsafe_allow_html=True)
        if not df_all.empty:
            st.dataframe(df_all,use_container_width=True,hide_index=True)
            st.download_button("[ EXPORT CSV ]",data=to_csv(df_all),file_name=f"all_signals_{ts[:10]}.csv",mime="text/csv", key="d4")
        else:st.markdown("<div style='color:#555;font-size:0.8rem;padding:1rem;'>> NO TICKER WITH ALL 3 SIGNALS</div>",unsafe_allow_html=True)
else:
    st.markdown("""
    <div style='background:#0d1117; border:1px solid #1a1a1a; padding:3rem; text-align:center; margin-top:4px;'>
        <div style='color:#333; font-size:0.8rem; letter-spacing:3px;'>███████████████</div>
        <div style='color:#00ff41; font-size:1.1rem; letter-spacing:2px; margin:1rem 0;'>> SELEZIONA PARAMETRI E PREMI [ ESEGUI SCREENER ]</div>
        <div style='color:#333; font-size:0.75rem; margin-top:0.5rem;'>ICHIMOKU BREAKOUT &nbsp;•&nbsp; SUPERTREND REVERSAL &nbsp;•&nbsp; HULL MA BULLISH</div>
        <div style='color:#333; font-size:0.8rem; letter-spacing:3px; margin-top:1rem;'>███████████████</div>
    </div>
    """, unsafe_allow_html=True)
