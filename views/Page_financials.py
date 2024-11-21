from functions import *

st.set_page_config(
    page_title="Financials", # The page title, shown in the browser tab.
    page_icon=":material/finance:",
    layout="wide", # How the page content should be laid out.
    initial_sidebar_state="auto", # How the sidebar should start out.
    menu_items={ # Configure the menu that appears on the top-right side of this app.
        "Get help": "https://github.com/LMAPcoder" # The URL this menu item should point to.
    }
)


# ---- SIDEBAR ----
with st.sidebar:

    TICKER = st.text_input(
        label="Securities:",
        value='MSFT'
    )

    TIME_PERIOD = st.radio(
        label="Time Period:",
        options=["Annual", "Quarterly"]
    )

    st.markdown("Made with ❤️ by Leonardo")

    button = st.button("✉️ Contact Me", key="contact")

    if button:
        show_contact_form()

# ---- MAINPAGE ----

st.title("Financials")

#----FIRST SECTION----

st.header("Balance Sheet")

info = fetch_info(TICKER)

CURRENCY = info["financialCurrency"]

bs = fetch_balance(TICKER, tp=TIME_PERIOD)
df = bs.copy()
df = df.loc[:, df.isna().mean() < 0.5]

fig = plot_balance(df[df.columns[::-1]], ticker=TICKER, currency=CURRENCY)

st.plotly_chart(fig, use_container_width=True)

with st.expander("Show data"):
    st.dataframe(
        data=df.reset_index(),
        hide_index=True
    )

tab1, tab2, tab3 = st.tabs(["Assets", "Liabilities", "Equity"])

with tab1:
    fig = plot_assets(df, ticker=TICKER, currency=CURRENCY)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = plot_liabilities(df, ticker=TICKER, currency=CURRENCY)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = plot_equity(df, ticker=TICKER, currency=CURRENCY)
    st.plotly_chart(fig, use_container_width=True)

#----SECOND SECTION----

st.header("Income Statement")

ist = fetch_income(TICKER, tp=TIME_PERIOD)
df = ist.copy()
df = df.loc[:, df.isna().mean() < 0.5]

fig = plot_income(df, ticker=TICKER, currency=CURRENCY)

st.plotly_chart(fig, use_container_width=True)

with st.expander("Show data"):
    st.dataframe(
        data=df.reset_index(),
        hide_index=True
    )

#----THIRD SECTION----

st.header("Cash Flow")

cf = fetch_cash(TICKER, tp=TIME_PERIOD)
df = cf.copy()
df = df.loc[:, df.isna().mean() < 0.5]

fig = plot_cash(df, ticker=TICKER, currency=CURRENCY)

st.plotly_chart(fig, use_container_width=True)

with st.expander("Show data"):
    st.dataframe(
        data=df.reset_index(),
        hide_index=True
    )