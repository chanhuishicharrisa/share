import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ==========================================
# CONFIG
# ==========================================
st.set_page_config(
    page_title="Real-Time Stock Tracker",
    page_icon="📈",
    layout="wide"
)

# Auto refresh every 10 seconds
st_autorefresh(interval=10000, key="refresh")

# ==========================================
# HEADER
# ==========================================
st.title("📈 Real-Time Stock Tracker")
st.write("Monitor your favourite stocks in real time.")

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.header("Stock Watchlist")

symbols = st.sidebar.text_input(
    "Enter stock symbols (comma separated)",
    "AAPL,MSFT,NVDA,GOOGL,TSLA"
)

watchlist = [
    symbol.strip().upper()
    for symbol in symbols.split(",")
    if symbol.strip()
]

# ==========================================
# TOP METRICS
# ==========================================
st.subheader("Market Snapshot")

if watchlist:

    cols = st.columns(min(len(watchlist), 5))

    for i, ticker in enumerate(watchlist):

        try:
            stock = yf.Ticker(ticker)
            info = stock.fast_info

            current_price = info.get("lastPrice", 0)
            previous_close = info.get("previousClose", 0)

            change_pct = 0
            if previous_close:
                change_pct = (
                    (current_price - previous_close)
                    / previous_close
                ) * 100

            cols[i % len(cols)].metric(
                ticker,
                f"${current_price:,.2f}",
                f"{change_pct:.2f}%"
            )

        except Exception:
            cols[i % len(cols)].error(f"{ticker} unavailable")

st.divider()

# ==========================================
# CHARTS
# ==========================================
for ticker in watchlist:

    try:
        stock = yf.Ticker(ticker)

        data = stock.history(
            period="1d",
            interval="1m"
        )

        if data.empty:
            st.warning(f"No data available for {ticker}")
            continue

        current_price = data["Close"].iloc[-1]
        day_high = data["High"].max()
        day_low = data["Low"].min()
        volume = int(data["Volume"].sum())

        st.subheader(f"{ticker}")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Current", f"${current_price:,.2f}")
        c2.metric("High", f"${day_high:,.2f}")
        c3.metric("Low", f"${day_low:,.2f}")
        c4.metric("Volume", f"{volume:,}")

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Close"],
                mode="lines",
                name=ticker,
                line=dict(width=2)
            )
        )

        fig.update_layout(
            title=f"{ticker} Intraday Price",
            xaxis_title="Time",
            yaxis_title="Price",
            template="plotly_white",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()

    except Exception as e:
        st.error(f"{ticker}: {e}")

# ==========================================
# FOOTER
# ==========================================
st.caption("Live market data powered by Yahoo Finance • Refreshes every 10 seconds")
