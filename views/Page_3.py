import streamlit as st
import pandas as pd

from functions import plot_candles_stick
#from functions import fetch_info
#from functions import fetch_history

@st.cache_data
def fetch_info(ticker):
    ticker = yf.Ticker(ticker)
    info = ticker.info
    if "quoteType" in ticker.info:
        return info
    else:
        st.warning("Invalid ticker")
        st.stop()

@st.cache_data
def fetch_history(ticker, period="3mo", interval="1d"):
    ticker = yf.Ticker(ticker)
    hist = ticker.history(
        period=period,
        interval=interval
    )
    return hist

st.set_page_config(
    page_title="Commodities", # The page title, shown in the browser tab.
    page_icon=":mountain:", # The page favicon.
    layout="wide", # How the page content should be laid out.
    initial_sidebar_state="auto", # How the sidebar should start out.
    menu_items={ # Configure the menu that appears on the top-right side of this app.
        "Get help": "https://github.com/LMAPcoder" # The URL this menu item should point to.
    }
)

# ---- SIDEBAR ----
with st.sidebar:
    commodities = {
        'West Texas Intermediate': 'CL=F',
        'Brent': 'BZ=F',
        'Natural Gas': 'NG=F',
        'Copper': 'HG=F',
        #'Aluminum': 'ALUMINUM',
        'Wheat': 'KE=F',
        'Corn': 'ZC=F',
        'Cotton': 'CT=F',
        'Sugar': 'SB=F',
        'Coffee': 'KC=F'
    }

    option = st.selectbox(
        label="Commodity",
        options=list(commodities.keys()),
        index=0,
        placeholder="Select commodity...",
    )

    COMMODITY = commodities[option]

    st.write(COMMODITY)

    periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

    PERIOD = st.selectbox(
        label="Period",
        options=periods,
        index=3,
        placeholder="Select period...",
    )

    intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

    if PERIOD in intervals:
        idx = intervals.index(PERIOD)
        intervals = intervals[:idx]

    INTERVAL = st.selectbox(
        label="Interval",
        options=intervals,
        index=len(intervals) - 4,
        placeholder="Select interval...",
    )

    INDICATORS = st.multiselect(
        label="Technical indicators:",
        options=['SMA', 'EMA']
    )
    TIME_SPAN = None
    if INDICATORS:
        TIME_SPAN = st.slider(
            label="Select time span:",
            min_value=1,  # The minimum permitted value.
            max_value=20,  # The maximum permitted value.
            value=10  # The value of the slider when it first renders.
        )

    st.sidebar.markdown("Made with ❤️ by Leonardo")


# ---- MAINPAGE ----

st.title("Commodity Market")

info = fetch_info(COMMODITY)

TITLE = f'Commodity: {option}'

hist = fetch_history(COMMODITY, period=PERIOD, interval=INTERVAL)

if "SMA" in INDICATORS:
    hist['SMA'] = hist['Close'].rolling(window=TIME_SPAN, min_periods=1).mean()
if "EMA" in INDICATORS:
    hist['EMA'] = hist['Close'].ewm(span=TIME_SPAN, adjust=False, min_periods=1).mean()

fig = plot_candles_stick(hist, TITLE, TIME_SPAN)

st.plotly_chart(fig, use_container_width=True)

with st.expander("Show data"):
    st.dataframe(
        data=hist.reset_index(),
        hide_index=True
    )