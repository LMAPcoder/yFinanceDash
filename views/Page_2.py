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
    page_title="Forex", # The page title, shown in the browser tab.
    page_icon=":moneybag:", # The page favicon.
    layout="wide", # How the page content should be laid out.
    initial_sidebar_state="auto", # How the sidebar should start out.
    menu_items={ # Configure the menu that appears on the top-right side of this app.
        "Get help": "https://github.com/LMAPcoder" # The URL this menu item should point to.
    }
)


# ---- SIDEBAR ----
with st.sidebar:

    currencies_1 = {
        'United States Dollar': 'USD',
        'Euro': 'EUR',
        'Japanese Yen': 'JPY',
        'British Pound Sterling': 'GBP',
        'Chinese Yuan': 'CNY',
        'Argentine Peso': 'ARS',
        'Bitcoin': 'BTC',
        'Ethereum': 'ETH'
    }
    currencies_2 = {
        'United States Dollar': 'USD',
        'Euro': 'EUR',
        'Japanese Yen': 'JPY',
        'British Pound Sterling': 'GBP',
        'Chinese Yuan': 'CNY',
        'Argentine Peso': 'ARS'
    }

    option1 = st.selectbox(
        label="Base currency",
        options=list(currencies_1.keys()),
        index=0,
        placeholder="Select origin currency...",
    )

    CURRENCY_1 = currencies_1[option1]

    st.write(CURRENCY_1)

    if option1 in currencies_2:
        currencies_2.pop(option1)

    option2 = st.selectbox(
        label="Counter currency",
        options=list(currencies_2.keys()),
        index=0,
        placeholder="Select destination currency...",
    )

    CURRENCY_2 = currencies_2[option2]

    st.write(currencies_2[option2])

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

st.title("Forex Market")

col1, col2, col3 = st.columns(3, gap="medium")

if CURRENCY_1 in ["BTC", "ETH", "USTD"]:
    TICKER = f'{CURRENCY_1}-{CURRENCY_2}'
else:
    TICKER = f'{CURRENCY_1}{CURRENCY_2}=X'

info = fetch_info(TICKER)

EXCHANGE_RATE = info['previousClose']
BID_PRICE = info['dayLow']
ASK_PRICE = info['dayHigh']

col1.metric(
    "Exchange Rate",
    value=f'{EXCHANGE_RATE:.4f}'
    )

col2.metric(
    "Bid Price",
    value=f'{BID_PRICE:.4f}'
)

col3.metric(
    "Ask Price",
    value=f'{ASK_PRICE:.4f}'
)

hist = fetch_history(TICKER, period=PERIOD, interval=INTERVAL)

TITLE = f'Currencies: {CURRENCY_1}/{CURRENCY_1}'

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