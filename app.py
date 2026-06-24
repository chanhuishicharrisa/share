import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ----------------------------------
# PAGE SETTINGS
# ----------------------------------
st.set_page_config(
    page_title="Real-Time Stock Tracker",
    page_icon="📈",
    layout="wide"
)

# Auto refresh every 10 seconds
st_autorefresh(interval=10000, key="stock_refresh")

# ----------------------------------
# HEADER
# ----------------------------------
st.title("📈 Real-Time Stock Tracker")
st.markdown("Track your favourite stocks with live market data from Yahoo Finance.")

# ----------------------------------
# SIDEBAR
# ----------------------------------
st.sidebar.header("Watchlist")

default_symbols = "AAPL,MSFT,NVDA,GOOGL,TSLA"

symbols = st.sidebar.text_input(
    "Enter stock symbols (comma separated)",
    default_symbols
)

refresh_rate = st.sidebar.slider(
    "Refresh interval (seconds)",
    min_value=5,
    max_value=60,
    value=10
)

# Apply chosen refresh interval
st_autorefresh(interval=refresh_rate * 1000, key="custom_refresh")

watchlist = [
    symbol.strip().upper()
    for symbol in symbols.split(",")
    if symbol.strip()
]

# ----------------------------------
# SUMMARY METRICS
# ----------------------------------
st.subheader("Market Overview")

if watchlist:

    cols = st.columns(min(len(watchlist), 5))

    for i, ticker in enumerate(watchlist):

        try:
            stock = yf.Ticker(ticker)
            info = stock.fast_info

            current_price = info.get("lastPrice")
            previous_close = info.get("previousClose")
            volume = info.get("lastVolume")

            if current_price and previous_close:
                pct_change = (
                    (current_price - previous_close)
                    / previous_close
                ) * 100
            else:
                pct_change = 0

            cols[i % len(cols)].metric(
                label=ticker,
                value=f"${current_price:,.2f}",
                delta=f"{pct_change:.2f}%"
            )

        except Exception:
            cols[i % len(cols)].error(f"{ticker} unavailable")

st.divider()

# ----------------------------------
# DETAILED CHARTS
# ----------------------------------
for ticker in watchlist:

    try:
        stock = yf.Ticker(ticker)

        data = stock.history(
            period="1d",
            interval="1m"
        )

        if data.empty:
            st.warning(f"No market data found for {ticker}")
            continue

        latest_price = data["Close"].iloc[-1]
        open_price = data["Open"].iloc[0]
        high_price = data["High"].max()
        low_price = data["Low"].min()
        total_volume = int(data["Volume"].sum())

        st.subheader(f"📊 {ticker}")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Current",
            f"${latest_price:,.2f}"
        )

        c2.metric(
            "Open",
            f"${open_price:,.2f}"
        )

        c3.metric(
            "High",
            f"${high_price:,.2f}"
        )

        c4.metric(
            "Low",
            f"${low_price:,.2f}"
        )

        st.write(f"**Volume:** {total_volume:,}")

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
            yaxis_title="Price (USD)",
            template="plotly_white",
            height=450,
            margin=dict(l=20, r=20, t=50, b=20)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()

    except Exception as e:
        st.error(f"{ticker}: {e}")

# ----------------------------------
# FOOTER
# ----------------------------------
st.caption(
    f"Auto-refreshing every {refresh_rate} seconds | Powered by Yahoo Finance"
)
