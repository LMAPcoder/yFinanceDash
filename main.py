import streamlit as st

# --- PAGE SETUP ---

page_1 = st.Page(
    "views/Page_1.py",
    title="Stock Market",
    icon=":material/stacked_line_chart:", # from Material Design by Google
    default=True,
)

page_2 = st.Page(
    "views/Page_2.py",
    title="Forex Market",
    icon=":material/bar_chart:",
)

page_3 = st.Page(
    "views/Page_3.py",
    title="Commodity Market",
    icon=":material/landscape:",
)


pg = st.navigation(pages=[page_1, page_2, page_3])

# --- SHARED ON ALL PAGES ---
st.logo("imgs/logo.png")

# --- RUN NAVIGATION ---
pg.run()