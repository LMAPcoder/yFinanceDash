import streamlit as st
import pandas as pd

from functions import *
from contact import contact_form

@st.dialog("Contact Me")
def show_contact_form():
    contact_form()

st.set_page_config(
    page_title="Stock", # The page title, shown in the browser tab.
    page_icon=":chart:", # The page favicon.
    layout="wide", # How the page content should be laid out.
    initial_sidebar_state="auto", # How the sidebar should start out.
    menu_items={ # Configure the menu that appears on the top-right side of this app.
        "Get help": "https://github.com/LMAPcoder" # The URL this menu item should point to.
    }
)

# ----SESSION STATE -----


# ---- SIDEBAR ----
with st.sidebar:

    TICKERS = st.text_input(
        label="Securities:",
        value='MSFT'
    )

    TICKERS = [item.strip() for item in TICKERS.split(",") if item.strip() != ""]

    TICKERS = list(set(TICKERS))

    TICKERS = TICKERS[:10]

    TICKERS = [TICKER for TICKER in TICKERS if fetch_info(TICKER) is not None]

    st.write("eg.: MSFT, QQQ, SPY (max 10)")

    period_list = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

    PERIOD = st.selectbox(
        label="Period",
        options=period_list,
        index=3,
        placeholder="Select period...",
    )

    interval_list = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

    if PERIOD in interval_list:
        idx = interval_list.index(PERIOD)
        interval_list = interval_list[:idx]

    INTERVAL = st.selectbox(
        label="Interval",
        options=interval_list,
        index=len(interval_list) - 4,
        placeholder="Select interval...",
    )

    if len(TICKERS) == 1:

        TOGGLE_VOL = st.toggle(
            label="Volume",
            value=True
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

    button = st.button("Refresh All", key="refresh_security")
    if button:
        #fetch_info.clear()
        st.cache_data.clear()

    st.markdown("Made with ❤️ by Leonardo")

    button = st.button("✉️ Contact Me", key="contact")

    if button:
        show_contact_form()


# ---- MAINPAGE ----


#----FIRST SECTION----
st.title("Stock Market")


col1, col2, col3 = st.columns(3, gap="small")

with col1:
    st.subheader("Indices")

    URL = "https://finance.yahoo.com/markets/world-indices/"

    df = fetch_table(URL)
    df['Symbol'] = df['Symbol'] + ' ' + df['Name']
    df['Symbol'] = df['Symbol'].apply(lambda x: x.replace(" ", "<br>", 1))
    df['Price'] = df['Price'].apply(format_value)
    df = df[['Symbol', 'Price']]
    df = df.iloc[:10]

    fig = top_table(df)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top Gainers")

    URL = "https://finance.yahoo.com/markets/stocks/gainers/"

    df = fetch_table(URL)
    df['Symbol'] = df['Symbol'] + ' ' + df['Name']
    df['Symbol'] = df['Symbol'].apply(lambda x: x.replace(" ", "<br>", 1))
    df['Price'] = df['Price'].apply(format_value)
    df = df[['Symbol', 'Price']]
    df = df.iloc[:10]

    fig = top_table(df)
    st.plotly_chart(fig, use_container_width=False)

with col3:
    st.subheader("Top Losers")

    URL = "https://finance.yahoo.com/markets/stocks/losers/"

    df = fetch_table(URL)
    df['Symbol'] = df['Symbol'] + ' ' + df['Name']
    df['Symbol'] = df['Symbol'].apply(lambda x: x.replace(" ", "<br>", 1))
    df['Price'] = df['Price'].apply(format_value)
    df = df[['Symbol', 'Price']]
    df = df.iloc[:10]

    fig = top_table(df)
    st.plotly_chart(fig, use_container_width=False)


#----SECOND SECTION----

if len(TICKERS) == 1:

    TICKER = TICKERS[0]

    info = fetch_info(TICKER)

    NAME = info['shortName']

    st.header(f"Security: {TICKER}")
    st.write(NAME)

    #----INFORMATION----
    with st.expander("More info"):
        df, PRICE = info_table(info)
        df = df.reset_index()
        df = df.rename(columns={"index": "Feature", 0: "Value"})

        st.dataframe(
            data=df,
            hide_index=True
        )


    #----METRICS----

    PREVIOUS_PRICE = info['previousClose']
    CHANGE = PRICE - PREVIOUS_PRICE
    CHANGE_PER = (CHANGE/PREVIOUS_PRICE)*100
    HIGH = info['dayHigh']
    LOW = info['dayLow']
    VOLUME = info['volume']

    st.metric(
        "Latest Price",
        value=f'{PRICE:.1f} USD',
        delta=f'{CHANGE:.1f} ({CHANGE_PER:.2f}%)'
        )


    col1, col2, col3 = st.columns(3, gap="medium")

    col1.metric(
        "High",
        value=f'{HIGH:.1f} USD'
        )

    col2.metric(
        "Low",
        value=f'{LOW:.1f} USD'
    )

    col3.metric(
        "Volume",
        value=f'{VOLUME}'
    )

    #----CANDLESTICK CHART----
    hist = fetch_history(TICKER, period=PERIOD, interval=INTERVAL)

    df = hist.copy()

    if not TOGGLE_VOL:
        df = df.drop(columns=['Volume'], axis=1)

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

    fig = plot_candles_stick_bar(df, "Candlestick Chart")

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show data"):

        st.markdown("Daily prices")
        st.dataframe(
            data=df.reset_index(),
            hide_index=False
        )

else:

    TITLE = ", ".join(TICKERS)

    st.header(f"Securities: {TITLE}")

    dfs_hist = list()
    dfs_info = list()

    for TICKER in TICKERS:
        info = fetch_info(TICKER)
        df, PRICE = info_table(info)
        df = df.rename(columns={0: TICKER})
        dfs_info.append(df)

        hist = fetch_history(TICKER, period=PERIOD, interval=INTERVAL)

        hist.insert(0, 'Ticker', TICKER)

        hist['Pct_change'] = ((hist['Close'] - hist['Close'].iloc[0]) / hist['Close'].iloc[0])

        dfs_hist.append(hist)

    df = pd.concat(dfs_info, axis=1, join='inner')
    df = df.reset_index()
    df = df.rename(columns={"index": "Feature"})

    # ----INFORMATION----
    with st.expander("More info"):

        st.dataframe(
            data=df,
            hide_index=True
        )

    # ----GAUGES----

    df = pd.concat(dfs_hist, ignore_index=False)

    if len(TICKERS) <= 5:

        cols = st.columns(5, gap="small")

        for i, TICKER in enumerate(TICKERS):

            fig = plot_gauge(df, TICKER)

            cols[i].plotly_chart(fig, use_container_width=True)

    # ----LINE CHART----

    fig = plot_candles_stick_bar_multiple(df, "Percent Change Line Chart")

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show data"):

        st.markdown("Daily prices")
        st.dataframe(
            data=df.reset_index(),
            hide_index=False
        )