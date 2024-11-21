import streamlit as st
import yfinance as yf
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as pc

@st.cache_data
def fetch_info(ticker):
    ticker = yf.Ticker(ticker)
    info = ticker.info
    if "quoteType" in ticker.info:
        return info
    else:
        return None
        #st.warning("Invalid ticker")
        #st.stop()

@st.cache_data
def fetch_history(ticker, period="3mo", interval="1d"):
    ticker = yf.Ticker(ticker)
    hist = ticker.history(
        period=period,
        interval=interval
    )
    return hist

@st.cache_data
def fetch_balance(ticker, tp="Annual"):
    ticker = yf.Ticker(ticker)
    if tp == "Annual":
        bs = ticker.balance_sheet
    else:
        bs = ticker.quarterly_balance_sheet
    return bs

@st.cache_data
def fetch_income(ticker, tp="Annual"):
    ticker = yf.Ticker(ticker)
    if tp == "Annual":
        ins = ticker.income_stmt
    else:
        ins = ticker.quarterly_income_stmt
    return ins

@st.cache_data
def fetch_cash(ticker, tp="Annually"):
    ticker = yf.Ticker(ticker)
    if tp == "Annually":
        cf = ticker.cashflow
    else:
        cf = ticker.quarterly_cashflow
    return cf

@st.cache_data
def fetch_splits(ticker):
    ticker = yf.Ticker(ticker)
    return ticker.splits

@st.cache_data
def fetch_table(url):
    df = pd.read_html(url)
    return df[0]


def format_value(value):
    # Split the string at the first space
    base_value, change = value.split(' ', 1)

    # Determine the color based on the sign of the change
    if change.startswith('+'):
        color = 'green'
    else:
        color = 'red'

    # Create the formatted string
    return f"{base_value}<br><span style='color: {color};'>{change}</span>"


def top_table(df):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='lightgrey',
                    align='center'),
        cells=dict(values=[df[col] for col in df.columns],
                   fill_color='white',
                   align=['left', 'right']),
        columnwidth=[0.6, 0.4]
    )])

    fig.update_layout(height=270, margin=dict(t=0, b=0, l=0, r=0))

    return fig

def info_table(info):

    TYPE = info['quoteType']
    if TYPE == "EQUITY":
        data = {
            'Market Exchange': info['exchange'],
            'Sector': info['sector'],
            'Industry': info['industry'],
            'Market Capitalization': str(info['marketCap']),
            'Quote currency': info['currency'],
            'Beta': str(info['beta'])
        }
        PRICE = info['currentPrice']


    elif TYPE == "ETF":
        data = {
            'Market Exchange': info['exchange'],
            'Fund Family': info['fundFamily'],
            'Category': info['category'],
            'Total Assets': info['totalAssets'],
            'Quote currency': info['currency'],
            'Beta': info['beta3Year']
        }
        PRICE = info['navPrice']

    elif TYPE == "FUTURE":
        PRICE = info['open']

    df = pd.DataFrame([data]).T

    return df, PRICE


def plot_gauge(df, ticker):
    df = df[df['Ticker'] == ticker]

    initial_price = df['Close'].iloc[0]
    last_price = df['Close'].iloc[-1]
    last_pct = df['Pct_change'].iloc[-1] * 100
    color_pct = 'green' if last_pct > 0 else 'red'

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=last_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': ticker},
        number={'font': {'color': color_pct}},
        gauge={
            'axis': {'range': [-50, 50]},
            'bar': {'thickness': 0},
            'steps': [
                {'range': [0, last_pct], 'color': color_pct, 'thickness': 0.8},
            ],
        },
    ))

    fig.update_layout(height=150, margin=dict(t=50, b=0, l=0, r=0))

    return fig

def plot_candles_stick_bar(df, title=""):

    rows = 1
    row_heights = [7]
    for col_name in df.columns:
        if col_name in ['Volume', 'MACD', 'ATR', 'RSI']:
            rows += 1
            row_heights.append(3)

    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.01,
                        subplot_titles=None,
                        row_heights=row_heights
                        )

    fig.update_xaxes(title_text="Date", row=rows, col=1)

    row = 1
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['Open'],
                                 high=df['High'],
                                 low=df['Low'],
                                 close=df['Close'],
                                 name="OHVC"
                                 ),
                  row=1, col=1)

    for col_name in df.columns:

        if 'SMA' in col_name or 'EMA' in col_name:
            fig.add_trace(go.Scatter(x=df.index,
                                     y=df[col_name],
                                     mode='lines',
                                     line=dict(
                                         #color='black',
                                         width=2
                                     ),
                                     name=col_name),
                          row=1, col=1)

        elif 'Crossover' in col_name:

            first_period = col_name.split('_')[1].split('/')[0]

            for i, v in df[col_name].items():

                if v == 1.0:  # Buy signal

                    fig.add_annotation(x=df.index[i], y=df[f'SMA_{first_period}'][i],
                                       text="Golden cross",
                                       showarrow=True,
                                       arrowhead=1,
                                       arrowsize=1,
                                       ay=60
                                       )

                if v == -1.0:  # Sell signal

                    fig.add_annotation(x=df.index[i], y=df[f'SMA_{first_period}'][i],
                                       text="Death cross",
                                       showarrow=True,
                                       arrowhead=1,
                                       arrowsize=1,
                                       ay=-60
                                       )

        if col_name == 'Volume':
            row += 1

            volume_colors = ['green' if df['Close'].iloc[i] > df['Open'].iloc[i] else 'red' for i in range(len(df))]

            fig.add_trace(go.Bar(x=df.index,
                                 y=df[col_name],
                                 name=col_name,
                                 marker_color=volume_colors),
                          row=row, col=1)

            fig.update_yaxes(title_text="Volume", row=row, col=1)

        elif col_name == 'MACD':
            row += 1

            fig.add_trace(go.Scatter(x=df.index,
                                     y=df[col_name],
                                     name=col_name,
                                     ),
                          row=row, col=1)

            fig.update_yaxes(title_text="MACD", row=row, col=1)

            if 'Signal' in df.columns:
                fig.add_trace(go.Scatter(x=df.index,
                                         y=df['Signal'],
                                         name='Signal',
                                         ),
                              row=row, col=1)

            if 'MACD_Hist' in df.columns:
                MACD_colors = ['green' if df['MACD_Hist'][i] > 0 else 'red' for i in range(len(df))]

                fig.add_trace(go.Bar(x=df.index,
                                     y=df['MACD_Hist'],
                                     name='MACD_Hist',
                                     marker_color=MACD_colors),
                              row=row, col=1)

        elif col_name == 'ATR':
            row += 1

            fig.add_trace(go.Scatter(x=df.index,
                                     y=df[col_name],
                                     name=col_name,
                                     ),
                          row=row, col=1)

            fig.update_yaxes(title_text="ATR", row=row, col=1)

        elif col_name == 'RSI':
            row += 1

            fig.add_trace(go.Scatter(x=df.index,
                                     y=df[col_name],
                                     name=col_name,
                                     ),
                          row=row, col=1)

            fig.update_yaxes(title_text="RSI", row=row, col=1)

            fig.add_hline(y=70, line_dash="dash", annotation_text='top', row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", annotation_text='bottom', row=2, col=1)
            fig.add_hrect(y0=30, y1=70, fillcolor="blue", opacity=0.25, line_width=0, row=2, col=1)

    fig.update_layout(
        title=title,
        # xaxis_title='Date',
        yaxis_title='Price',
        # xaxis2_title='Date',
        # yaxis2_title='Volume',
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="top",  # Aligns the legend vertically to the top
            y=-0.15,  # Positions the legend below the subplots
            xanchor="center",  # Aligns the legend horizontally to the center
            x=0.5  # Centers the legend horizontally
        ),
        showlegend=True,
        xaxis_rangeslider_visible=False,
        height=800
    )

    return fig


def plot_candles_stick(df, title="", time_span=None):

    fig = go.Figure()


    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['Open'],
                                 high=df['High'],
                                 low=df['Low'],
                                 close=df['Close'],
                                 name="OHVC")
                  )

    if 'SMA' in df.columns:
        fig.add_trace(go.Scatter(x=df.index,
                                 y=df['SMA'],
                                 mode='lines',
                                 line=dict(color='black', width=2),
                                 name=f'{time_span}SMA')
                      )
    if 'EMA' in df.columns:
        fig.add_trace(go.Scatter(x=df.index,
                                 y=df['EMA'],
                                 mode='lines',
                                 line=dict(color='blue', width=2),
                                 name=f'{time_span}EMA')
                      )

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Price',
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="top",  # Aligns the legend vertically to the top
            y=-0.3,  # Positions the legend below the subplots
            xanchor="center",  # Aligns the legend horizontally to the center
            x=0.5  # Centers the legend horizontally
        ),
        showlegend=True,
        xaxis_rangeslider_visible=False,
    )

    return fig

def plot_candles_stick_bar_multiple(df, title=""):
    fig = go.Figure()

    dfs = df.groupby('Ticker')

    for df_name, df in dfs:
        fig.add_trace(go.Scatter(x=df.index,
                                 y=df['Pct_change'],
                                 mode='lines',
                                 name=f'{df_name}',
                                 meta=df_name,
                                 hovertemplate='%{meta}: %{y:.2f}<br><extra></extra>', )
                      )

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Percentage change',
        hovermode='x',
        xaxis=dict(
            showspikes=True,  # Enable vertical spikes
            spikemode='across',  # Draw spikes across the entire plot
            spikesnap='cursor',  # Snap spikes to the cursor position
            showline=True,  # Show axis line
            showgrid=True,  # Show grid lines
            spikecolor='black',  # Custom color for spikes
            spikethickness=1,  # Custom thickness for spikes
            rangeslider=dict(
                visible=True,
                thickness=0.1
            ),
        ),
        yaxis=dict(
            tickformat='.0%',
            showspikes=True,  # Enable horizontal spikes
            spikemode='across',  # Draw spikes across the entire plot
            spikesnap='cursor',  # Snap spikes to the cursor position
            showline=True,  # Show axis line
            showgrid=True,  # Show grid lines
            spikecolor='black',  # Custom color for spikes
            spikethickness=1,  # Custom thickness for spikes
            side='right'  # Move the y-axis ticks to the right side
        ),
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="top",  # Aligns the legend vertically to the top
            y=-0.3,  # Positions the legend below the subplots
            xanchor="center",  # Aligns the legend horizontally to the center
            x=0.5  # Centers the legend horizontally
        ),
        showlegend=True,
        # xaxis_rangeslider_visible=True,
        height=800
    )

    return fig

def plot_balance(df, ticker="", currency=""):
    df.columns = pd.to_datetime(df.columns).strftime('%b %d, %Y')
    components = {
        'Total Assets': {
            'color': 'forestgreen'
        },
        'Stockholders Equity': {
            'color': 'CornflowerBlue'  # http://davidbau.com/colors/
        },
        'Total Liabilities Net Minority Interest': {
            'color': 'tomato'
        },
    }
    fig = go.Figure()

    for component in components:
        if component == 'Total Assets':
            fig.add_trace(go.Bar(
                x=[df.columns, ['Assets'] * len(df.columns)],
                y=df.loc[component],
                name=component,
                marker=dict(color=components[component]['color'])
            ))
        else:

            fig.add_trace(go.Bar(
                x=[df.columns, ['L+E'] * len(df.columns)],
                y=df.loc[component],
                name=component,
                marker=dict(color=components[component]['color'])
            ))

        offset = 0.03 * df.loc['Total Assets'].max()

        for i, date in enumerate(df.columns):
            fig.add_annotation(
                x=[date, "Assets"],
                y=df.loc['Total Assets', date] + offset,
                text=str(round(df.loc['Total Assets', date] / 1e9, 1)) + 'B',  # Format as text
                showarrow=False,
                font=dict(size=12, color="black"),
                align="center"
            )

        fig.update_layout(
            barmode='stack',
            title=f'Accounting Balance: {ticker}',
            xaxis_title='Year',
            yaxis_title=f'Amount (in {currency})',
            legend_title='Balance components',
        )

    return fig

def plot_assets(df, ticker="", currency=""):
    assests = {
        'Current Assets': {
            'Cash Cash Equivalents And Short Term Investments': {},
            'Receivables': {},
            'Inventory': {},
            'Hedging Assets Current': None,
            'Other Current Assets': None
        },
        'Total Non Current Assets': {
            'Net PPE': {},
            'Goodwill And Other Intangible Assets': {},
            'Investments And Advances': {},
            'Other Non Current Assets': None
        }
    }

    fig = make_subplots(
        rows=1, cols=2,
        shared_yaxes=True,  # Share x-axis for both subplots
        horizontal_spacing=0.05,  # Adjust the space between the subplots
        subplot_titles=['Current Assets', 'Non-Current Assets']  # Titles for the subplots
    )

    colors = pc.sequential.Blugrn[::-1]
    i = 0

    for component in assests['Current Assets']:
        fig.add_trace(go.Bar(
            x=df.columns,
            y=df.loc[component],
            name=component,
            marker=dict(
                color=colors[i]  # Assign a color from the green color scale
            ),
            legendgroup='Current Assets',
            showlegend=True
        ), row=1, col=1)
        i += 1

    colors = pc.sequential.Purp[::-1]
    i = 0

    for component in assests['Total Non Current Assets']:
        fig.add_trace(go.Bar(
            x=df.columns,
            y=df.loc[component],
            name=component,
            marker=dict(
                color=colors[i]  # Assign a color from the green color scale
            ),
            legendgroup='Non-current Assets',
            showlegend=True
        ), row=1, col=2)
        i += 1

    offset = 0.03 * max(df.loc['Current Assets'].max(), df.loc['Total Non Current Assets'].max())

    for i, date in enumerate(df.columns):
        fig.add_annotation(
            x=date,
            y=df.loc['Current Assets', date] + offset,
            text=str(round(df.loc['Current Assets', date] / 1e9, 1)) + 'B',  # Format as text
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center",
            row=1, col=1
        )
        fig.add_annotation(
            x=date,
            y=df.loc['Total Non Current Assets', date] + offset,
            text=str(round(df.loc['Total Non Current Assets', date] / 1e9, 1)) + 'B',  # Format as text
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center",
            row=1, col=2
        )

    # Update layout to stack bars and set titles
    fig.update_layout(
        barmode='stack',
        title=f'Assets: {ticker}',
        #xaxis1_title='Year',
        #xaxis2_title='Year',
        xaxis1=dict(
            title='Date',
            type='date',  # Ensure the x-axis is treated as a date/time axis
            tickvals=df.columns
        ),
        xaxis2=dict(
            title='Date',
            type='date',  # Ensure the x-axis is treated as a date/time axis
            tickvals=df.columns
        ),
        yaxis_title=f'Amount (in {currency})',
        # yaxis2_title=f'Amount (in {currency})',
        legend_title='Asset Components',
        # height=800
    )

    return fig

def plot_liabilities(df, ticker="", currency=""):
    liabilities = {
        'Current Liabilities': {
            'Payables And Accrued Expenses': {},
            'Pensionand Other Post Retirement Benefit Plans Current': None,
            'Current Debt And Capital Lease Obligation': {},
            'Current Deferred Liabilities': {},
            'Other Current Liabilities': {}
        },
        'Total Non Current Liabilities Net Minority Interest': {
            'Long Term Debt And Capital Lease Obligation': {},
            'Non Current Deferred Liabilities': {},
            'Tradeand Other Payables Non Current': None,
            'Other Non Current Liabilities': None
        }
    }

    fig = make_subplots(
        rows=1, cols=2,
        shared_yaxes=True,  # Share x-axis for both subplots
        horizontal_spacing=0.05,  # Adjust the space between the subplots
        subplot_titles=['Current Liabilities', 'Non-Current Liabilities']  # Titles for the subplots
    )

    colors = pc.sequential.Oryel[::-1]
    i = 0

    for component in liabilities['Current Liabilities']:
        fig.add_trace(go.Bar(
            x=df.columns,
            y=df.loc[component],
            name=component,
            marker=dict(
                color=colors[i]  # Assign a color from the green color scale
            ),
            legendgroup='Current Liabilities',
            showlegend=True
        ), row=1, col=1)
        i += 1

    colors = pc.sequential.Brwnyl[::-1]
    i = 0

    for component in liabilities['Total Non Current Liabilities Net Minority Interest']:
        fig.add_trace(go.Bar(
            x=df.columns,
            y=df.loc[component],
            name=component,
            marker=dict(
                color=colors[i]  # Assign a color from the green color scale
            ),
            legendgroup='Non-current Liabilities',
            showlegend=True
        ), row=1, col=2)
        i += 1

    offset = 0.03 * max(df.loc['Current Liabilities'].max(),
                        df.loc['Total Non Current Liabilities Net Minority Interest'].max())

    for i, date in enumerate(df.columns):
        fig.add_annotation(
            x=date,
            y=df.loc['Current Liabilities', date] + offset,
            text=str(round(df.loc['Current Liabilities', date] / 1e9, 1)) + 'B',  # Format as text
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center",
            row=1, col=1
        )
        fig.add_annotation(
            x=date,
            y=df.loc['Total Non Current Liabilities Net Minority Interest', date] + offset,
            text=str(round(df.loc['Total Non Current Liabilities Net Minority Interest', date] / 1e9, 1)) + 'B',
            # Format as text
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center",
            row=1, col=2
        )

    # Update layout to stack bars and set titles
    fig.update_layout(
        barmode='stack',
        title=f'Liabilities: {ticker}',
        #xaxis1_title='Year',
        #xaxis2_title='Year',
        xaxis1=dict(
            title='Date',
            type='date',  # Ensure the x-axis is treated as a date/time axis
            tickvals=df.columns
        ),
        xaxis2=dict(
            title='Date',
            type='date',  # Ensure the x-axis is treated as a date/time axis
            tickvals=df.columns
        ),
        yaxis_title=f'Amount (in {currency})',
        # yaxis2_title=f'Amount (in {currency})',
        legend_title='Liability Components',
        # height=800
    )

    return fig

def plot_equity(df, ticker="", currency=""):
    equity = {
        'Stockholders Equity': {
            'Capital Stock': {},
            'Retained Earnings': None,
            'Gains Losses Not Affecting Retained Earnings': {},
        },
    }

    fig = go.Figure()

    colors = pc.sequential.Blues[::-1]
    i = 0

    for component in equity['Stockholders Equity']:
        fig.add_trace(go.Bar(
            x=df.columns,
            y=df.loc[component],
            name=component,
            marker=dict(
                color=colors[i]  # Assign a color from the green color scale
            ),
        ))
        i += 2

    offset = 0.05 * df.loc['Stockholders Equity'].max()

    for i, date in enumerate(df.columns):
        fig.add_annotation(
            x=date,
            y=df.loc['Stockholders Equity', date] + offset,
            text=str(round(df.loc['Stockholders Equity', date] / 1e9, 1)) + 'B',  # Format as text
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center"
        )

    # Update layout to stack bars and set titles
    fig.update_layout(
        barmode='relative',
        title=f'Equity: {ticker}',
        # xaxis_title='Year',
        xaxis=dict(
            title='Date',
            type='date',  # Ensure the x-axis is treated as a date/time axis
            # tickformat='%Y',
            # dtick='M12'
            tickvals=df.columns
        ),
        yaxis_title=f'Amount (in {currency})',
        legend_title='Equity Components',
    )

    return fig

def plot_income(df, ticker="", currency=""):
    income_st = {
        'Total Revenue': {
            'name': 'Total Revenue',
            'value': df.loc['Total Revenue'],
            'base': None,
            'color': 'rgb(0,68,27)'
        },
        'Cost Of Revenue': {
            'name': 'Cost of Revenue',
            'value': -df.loc['Cost Of Revenue'],
            'base': df.loc['Total Revenue'],
            'color': 'rgb(165,15,21)'
        },
        'Gross Profit': {
            'name': 'Gross Profit',
            'value': df.loc['Gross Profit'],
            'base': None,
            'color': 'rgb(35,139,69)'
        },
        'Operating Expense': {
            'name': 'Operating Expense',
            'value': -df.loc['Operating Expense'],
            'base': df.loc['Gross Profit'],
            'color': 'rgb(239,59,44)'
        },
        'Operating Income': {
            'name': 'Operating Income',
            'value': df.loc['Operating Income'],
            'base': None,
            'color': 'rgb(116,196,118)'
        },
        'Net Non Operating Interest Income Expense': {
            'name': 'Net Non Operating I/E',
            'value': df.loc['Net Non Operating Interest Income Expense'],
            'base': df.loc['Operating Income'],
            'color': 'rgb(130, 109, 186)'
        },
        'Other Income Expense': {
            'name': 'Other Income Expense',
            'value': df.loc['Other Income Expense'],
            'base': df.loc['Operating Income'] + df.loc['Net Non Operating Interest Income Expense'],
            'color': 'rgb(185, 152, 221)'
        },
        'Pretax Income': {
            'name': 'Pretax Income',
            'value': df.loc['Pretax Income'],
            'base': None,
            'color': 'rgb(199,233,192)'
        },
        'Tax Provision': {
            'name': 'Tax Provision',
            'value': -df.loc['Tax Provision'],
            'base': df.loc['Pretax Income'],
            'color': 'rgb(252,146,114)'
        },
        'Net Income Common Stockholders': {
            'name': 'Net Income',
            'value': df.loc['Net Income Common Stockholders'],
            'base': None,
            'color': 'rgb(224, 253, 74)'
        }
    }

    # Create traces for stacked data
    traces = list()

    for component in income_st:
        trace = go.Bar(
            x=df.columns,
            y=income_st[component]['value'],
            name=income_st[component]['name'],
            base=income_st[component]['base'],
            marker=dict(
                color=income_st[component]['color']  # Assign a color from the green color scale
            ),
        )

        traces.append(trace)

    # Create the figure
    fig = go.Figure(data=traces)

    # Update layout to stack bars and set titles
    fig.update_layout(
        barmode='group',
        # barmode = 'overlay',
        title=f'Income Statement: {ticker}',
        # xaxis_title='Year',
        xaxis=dict(
            title='Date',
            type='date',  # Ensure the x-axis is treated as a date/time axis
            tickvals=df.columns
        ),
        yaxis_title=f'Amount (in {currency})',
        legend_title='I/E segregation',
    )

    return fig

def plot_cash(df, ticker="", currency=""):
    cashflow = {
        'Operating Cash Flow': {},
        'Investing Cash Flow': {},
        'Financing Cash Flow': {},
        'End Cash Position': {
            'Changes In Cash': None,
            'Effect Of Exchange Rate Changes': None,
            'Beginning Cash Position': None
        }
    }

    fig = go.Figure()

    colors = pc.sequential.Plotly3[::-1]
    i = 0

    for component in cashflow:
        if component == 'End Cash Position':
            for item in cashflow[component]:
                if item == 'Changes In Cash':
                    fig.add_trace(go.Scatter(
                        x=df.columns,
                        y=df.loc[item],
                        mode='lines',
                        line=dict(color='black', width=2, dash='dash'),
                        name=item,
                    ))
                else:
                    fig.add_trace(go.Bar(
                        x=df.columns,
                        y=df.loc[item],
                        name=item,
                        marker=dict(
                            color=colors[i]  # Assign a color from the green color scale
                        ),
                    ))
                    i += 2
            fig.add_trace(go.Scatter(
                x=df.columns,
                y=df.loc[component],
                mode='lines+markers',
                line=dict(color='black', width=3),
                name=component,
            ))
        else:
            fig.add_trace(go.Bar(
                x=df.columns,
                y=df.loc[component],
                name=component,
                marker=dict(
                    color=colors[i]  # Assign a color from the green color scale
                ),
            ))
            i += 2

    offset = 0.1 * df.loc['End Cash Position'].max()

    for i, date in enumerate(df.columns):
        fig.add_annotation(
            x=date,
            y=df.loc['End Cash Position', date] + offset,
            text=str(round(df.loc['End Cash Position', date] / 1e9, 1)) + 'B',  # Format as text
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center"
        )

    # Update layout to stack bars and set titles
    fig.update_layout(
        barmode='relative',
        title=f'Cash flow: {ticker}',
        # xaxis_title='Year',
        xaxis=dict(
            title='Date',
            type='date',  # Ensure the x-axis is treated as a date/time axis
            tickvals=df.columns
        ),
        yaxis_title=f'Amount (in {currency})',
        legend_title='Cash Flow Components',
    )

    return fig