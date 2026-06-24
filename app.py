import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Live Stock Tracker",
    page_icon="📈",
    layout="wide"
)

# Auto refresh every 10 seconds
st_autorefresh(interval=10000, key="refresh")

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
st.sidebar.title("📊 Stock Watchlist")

default_stocks = "AAPL,MSFT,GOOGL,NVDA,TSLA"

symbols = st.sidebar.text_input(
    "Enter stock symbols (comma separated)",
    default_stocks
)

stock_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.title("📈 Real-Time Stock Price Dashboard")

st.markdown(
    """
    Track your favourite stocks with live market data.
    Data source: Yahoo Finance
    """
)

# ---------------------------------------------------
# METRICS SECTION
# ---------------------------------------------------
cols = st.columns(min(len(stock_list), 4))

for idx, ticker in enumerate(stock_list):

    try:
        stock = yf.Ticker(ticker)

        info = stock.fast_info

        current_price = info.get("lastPrice")
        previous_close = info.get("previousClose")
        volume = info.get("lastVolume")

        if current_price and previous_close:
            change = current_price - previous_close
            pct_change = (change / previous_close) * 100
        else:
            change = 0
            pct_change = 0

        with cols[idx % len(cols)]:
            st.metric(
                label=ticker,
                value=f"${current_price:,.2f}",
                delta=f"{pct_change:.2f}%"
            )

    except Exception:
        with cols[idx % len(cols)]:
            st.error(f"{ticker}: Data unavailable")

st.divider()

# ---------------------------------------------------
# CHARTS
# ---------------------------------------------------
for ticker in stock_list:

    try:
        st.subheader(f"📈 {ticker}")

        stock = yf.Ticker(ticker)

        hist = stock.history(
            period="1d",
            interval="1m"
        )

        if hist.empty:
            st.warning(f"No data for {ticker}")
            continue

        latest = hist.iloc[-1]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Current Price",
            f"${latest['Close']:.2f}"
        )

        col2.metric(
            "Day High",
            f"${hist['High'].max():.2f}"
        )

        col3.metric(
            "Volume",
            f"{int(hist['Volume'].sum()):,}"
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist["Close"],
                mode="lines",
                name=ticker,
                line=dict(width=2)
            )
        )

        fig.update_layout(
            height=400,
            xaxis_title="Time",
            yaxis_title="Price",
            template="plotly_white",
            margin=dict(l=20, r=20, t=30, b=20)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Error loading {ticker}: {e}")

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.caption(
    "Auto-refresh every 10 seconds • Powered by Streamlit + Yahoo Finance"
)
