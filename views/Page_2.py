import streamlit as st
import pandas as pd

from functions import plot_candles_stick
from functions import *
from contact import contact_form

@st.dialog("Contact Me")
def show_contact_form():
    contact_form()

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

    indicator_list = ['SMA_20', 'SMA_50', 'SMA_200', 'SMA_X', 'EMA_20', 'EMA_50', 'EMA_200', 'EMA_X', 'ATR', 'MACD', 'RSI']

    INDICATORS = st.multiselect(
        label="Technical indicators:",
        options=indicator_list
    )

    if 'SMA_X' in INDICATORS or 'EMA_X' in INDICATORS:
        TIME_SPAN = st.slider(
            label="Select time span:",
            min_value=10,  # The minimum permitted value.
            max_value=200,  # The maximum permitted value.
            value=30  # The value of the slider when it first renders.
        )
        INDICATORS = [indicator.replace("X", str(TIME_SPAN)) if '_X' in indicator else indicator for indicator in INDICATORS]

    st.sidebar.markdown("Made with ❤️ by Leonardo")

    button = st.button("✉️ Contact Me", key="contact")

    if button:
        show_contact_form()


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
df = hist.copy()
df = df.drop(columns=['Volume'], axis=1)

TITLE = f'Currencies: {CURRENCY_1}/{CURRENCY_1}'

for INDICATOR in INDICATORS:
    if "SMA" in INDICATOR:
        window = int(INDICATOR.split("_")[1])
        df[INDICATOR] = df['Close'].rolling(window=window, min_periods=1).mean()
    if "EMA" in INDICATOR:
        window = int(INDICATOR.split("_")[1])
        df[INDICATOR] = df['Close'].ewm(span=window, adjust=False, min_periods=1).mean()

if "ATR" in INDICATORS:

    Prev_Close = df['Close'].shift(1)
    High_Low = df['High'] - df['Low']
    High_PrevClose = abs(df['High'] - Prev_Close)
    Low_PrevClose = abs(df['Low'] - Prev_Close)

    df['TR'] = pd.concat([High_Low, High_PrevClose, Low_PrevClose], axis=1).max(axis=1)

    df['ATR'] = df['TR'].rolling(window=14, min_periods=1).mean()

    df = df.drop(columns=['TR'], axis=1)

if "MACD" in INDICATORS:

    ema_short = df['Close'].ewm(span=12, adjust=False, min_periods=1).mean()
    ema_long = df['Close'].ewm(span=26, adjust=False, min_periods=1).mean()
    df['MACD'] = ema_short - ema_long
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False, min_periods=1).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']

if "RSI" in INDICATORS:

    # delta = df['Close'].diff()
    delta = df['Close'].pct_change(periods=1) * 100

    # Separate gains and losses
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()

    # Calculate the relative strength (RS)
    rs = gain / loss

    df['RSI'] = 100 - (100 / (1 + rs))

fig = plot_candles_stick_bar(df, TITLE)

st.plotly_chart(fig, use_container_width=True)

with st.expander("Show data"):
    st.dataframe(
        data=df.reset_index(),
        hide_index=True
    )