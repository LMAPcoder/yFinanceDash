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

# ----SESSION STATE -----
all_my_widget_keys_to_keep = {
    'tickers': "MSFT"
}

for key in all_my_widget_keys_to_keep:
    if key not in st.session_state:
        st.session_state[key] = all_my_widget_keys_to_keep[key]

for key in all_my_widget_keys_to_keep:
    st.session_state[key] = st.session_state[key]


# ---- SIDEBAR ----
with st.sidebar:

    TICKERS = st.text_input(
        label="Securities:",
        #value='MSFT',
        key='tickers'
    )

    TICKERS = [item.strip() for item in TICKERS.split(",") if item.strip() != ""]

    TICKERS = remove_duplicates(TICKERS)

    TICKERS = TICKERS[:10]

    TIME_PERIOD = st.radio(
        label="Time Period:",
        options=["Annual", "Quarterly"]
    )

    TICKERS = [TICKER for TICKER in TICKERS if fetch_info(TICKER) is not None]

    st.markdown("Made with ❤️ by Leonardo")

    button = st.button("✉️ Contact Me", key="contact")

    if button:
        show_contact_form()

# ---- MAINPAGE ----

st.title("Financials")

if len(TICKERS) == 1:

    TICKER = TICKERS[0]

    #----BALANCE SHEET----

    st.header("Balance Sheet")

    info = fetch_info(TICKER)

    CURRENCY = info["financialCurrency"]

    bs = fetch_balance(TICKER, tp=TIME_PERIOD)
    bs = bs.loc[:, bs.isna().mean() < 0.5]

    a_bs = fetch_balance(TICKER, tp='Annual')
    a_bs = a_bs.loc[:, a_bs.isna().mean() < 0.5]

    fig = plot_balance(bs[bs.columns[::-1]], ticker=TICKER, currency=CURRENCY)

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ratios"):
        tab1, tab2 = st.tabs(["Current Ratio", "Debt-to-Equity Ratio"])

        with tab1:
            fig = plot_current_ratio(bs, ticker=TICKER)
            st.plotly_chart(
                fig,
                use_container_width=True,
                #theme=None
            )

        with tab2:
            fig = plot_de_ratio(bs, ticker=TICKER)
            st.plotly_chart(
                fig,
                use_container_width=True
            )

    with st.expander("Show components"):

        tab1, tab2, tab3 = st.tabs(["Assets", "Liabilities", "Equity"])

        with tab1:
            fig = plot_assets(bs, ticker=TICKER, currency=CURRENCY)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig = plot_liabilities(bs, ticker=TICKER, currency=CURRENCY)
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            fig = plot_equity(bs, ticker=TICKER, currency=CURRENCY)
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show data"):
        st.dataframe(
            data=bs.reset_index(),
            hide_index=True
        )


    #----INCOME STATEMENT----

    st.header("Income Statement")

    ist = fetch_income(TICKER, tp=TIME_PERIOD)
    ist = ist.loc[:, ist.isna().mean() < 0.5]

    a_ist = fetch_income(TICKER, tp='Annual')
    a_ist = a_ist.loc[:, a_ist.isna().mean() < 0.5]

    fig = plot_income(ist, ticker=TICKER, currency=CURRENCY)

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ratios"):
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Net Margin", "Earnings Per Share (EPS)", "Price-to-Earnings (P/E) Ratio", "Return on Equity"]
        )

        with tab1:

            fig = plot_margins(ist, ticker=TICKER)
            st.plotly_chart(
                fig,
                use_container_width=True,
                #theme=None
            )

        with tab2:

            fig = plot_eps(ist, ticker=TICKER)
            st.plotly_chart(
                fig,
                use_container_width=True,
                #theme=None
            )

        with tab3:
            fig = plot_pe_ratio(a_ist, ticker=TICKER)
            st.plotly_chart(
                fig,
                use_container_width=True,
                # theme=None
            )

        with tab4:
            fig = plot_roe(a_ist, a_bs, ticker=TICKER)
            st.plotly_chart(
                fig,
                use_container_width=True,
                # theme=None
            )


    with st.expander("Show data"):
        st.dataframe(
            data=ist.reset_index(),
            hide_index=True
        )

    #----CASH FLOW----

    st.header("Cash Flow")

    cf = fetch_cash(TICKER, tp=TIME_PERIOD)
    cf = cf.loc[:, cf.isna().mean() < 0.5]

    a_cf = fetch_cash(TICKER, tp='Annual')
    a_cf = a_cf.loc[:, a_cf.isna().mean() < 0.5]

    fig = plot_cash(cf, ticker=TICKER, currency=CURRENCY)

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ratios"):
        tab1, tab2, tab3 = st.tabs(["FCF per share", "Operating Cash Flow Ratio", "Price-to-Cash Flow (P/CF) Ratio"])

        with tab2:
            fig = plot_ocf(a_cf, a_bs, ticker=TICKER)
            st.plotly_chart(
                fig,
                use_container_width=True,
                # theme=None
            )

    with st.expander("Show data"):
        st.dataframe(
            data=cf.reset_index(),
            hide_index=True
        )

else:
    # ----BALANCE SHEET----

    st.header("Balance Sheet")

    fig = plot_balance_multiple(TICKERS)

    st.plotly_chart(fig, use_container_width=True)