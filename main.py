import streamlit as st

# --- PAGE SETUP ---

page_price = st.Page(
    "views/Page_price.py",
    title="Stock Market",
    icon=":material/stacked_line_chart:", # from Material Design by Google
    default=True,
)

page_financials = st.Page(
    "views/Page_financials.py",
    title="Financials",
    icon=":material/finance:", # from https://fonts.google.com/icons
)

page_forex = st.Page(
    "views/Page_forex.py",
    title="Forex Market",
    icon=":material/currency_exchange:",
)

page_commodity = st.Page(
    "views/Page_commodity.py",
    title="Commodity Market",
    icon=":material/oil_barrel:",
)

pg = st.navigation(pages=[page_price, page_financials, page_forex, page_commodity])

# --- SHARED ON ALL PAGES ---
st.logo("imgs/logo.png")

# --- RUN NAVIGATION ---
pg.run()