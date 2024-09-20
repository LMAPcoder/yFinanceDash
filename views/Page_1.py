import streamlit as st
import pandas as pd

from functions import plot_candles_stick_bar
from functions import fetch_info
from functions import fetch_history
from functions import fetch_splits
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

# ---- SIDEBAR ----
with st.sidebar:

    TICKER = st.text_input(
        label="Security",
        value='MSFT',
        placeholder="Input security ticker"
    )
    st.write("eg: MSFT, QQQ, SPY")

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
        index=len(intervals)-4,
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

    button = st.button("✉️ Contact Me", key="contact")

    if button:
        show_contact_form()



# ---- MAINPAGE ----


#----FIRST SECTION----
st.title("Stock Market")

#----SECOND SECTION----

info = fetch_info(TICKER)

TYPE = info['quoteType']
NAME = info['longName']

st.header(f"Stock: {TICKER}")
st.write(NAME)

button = st.button("Refresh", key="refresh_security")
if button:
    fetch_info.clear()

#----INFORMATION----
with st.expander("More info"):
    if TYPE == "EQUITY":
        data = {
            'Country': info['country'],
            'Market Exchange': info['exchange'],
            'Sector': info['sector'],
            'Industry': info['industry'],
            'Market Capitalization': info['marketCap'],
            'EBITDA': info['ebitda'],
            'Beta': info['beta']
        }
        PRICE = info['currentPrice']
        df = pd.DataFrame([data]).T
        df.index.name = 'Feature'
        st.dataframe(
            data=df.reset_index(),
            hide_index=True
        )
    elif TYPE == "ETF":
        PRICE = info['navPrice']
        st.write(TYPE)

#----METRICS----

# hist = fetch_history(ticker)

# hist['Daily_change'] = hist['Close'].pct_change()

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

TITLE = f'{TYPE}: {TICKER}'

if "SMA" in INDICATORS:
    hist['SMA'] = hist['Close'].rolling(window=TIME_SPAN, min_periods=1).mean()
if "EMA" in INDICATORS:
    hist['EMA'] = hist['Close'].ewm(span=TIME_SPAN, adjust=False, min_periods=1).mean()

fig = plot_candles_stick_bar(hist, TITLE, TIME_SPAN)

st.plotly_chart(fig, use_container_width=True)

with st.expander("Show data"):

    col1, col2 = st.columns([0.6, 0.4], gap="medium")

    col1.markdown("Daily prices")
    col1.dataframe(
        data=hist.reset_index(),
        hide_index=False
    )

    col2.markdown("Historical split events")
    splits = fetch_splits(TICKER)
    col2.dataframe(
        data=splits.reset_index(),
        hide_index=True
    )

