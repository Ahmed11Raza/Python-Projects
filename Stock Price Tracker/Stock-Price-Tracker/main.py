import streamlit as st
import yfinance as yf
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Stock Price Tracker",
    layout="wide",
    page_icon="📈"
)

# Sidebar for user input
st.sidebar.header("User Input Parameters")
ticker_symbol = st.sidebar.text_input(
    "Enter Stock Ticker Symbol (e.g., AAPL):",
    value="AAPL",
    max_chars=10
)

start_date = st.sidebar.date_input(
    "Start date:",
    value=pd.to_datetime("2020-01-01").date()
)
end_date = st.sidebar.date_input(
    "End date:",
    value=pd.to_datetime("today").date()
)

# Add moving average selection
ma_days = st.sidebar.multiselect(
    "Select Moving Average Days:",
    [50, 100, 200],
    default=[50, 200]
)

# Main app content
st.title(f"Stock Price Tracker - {ticker_symbol}")

@st.cache_data
def load_data(ticker, start, end):
    data = yf.download(ticker, start, end)
    return data

try:
    df = load_data(ticker_symbol, start_date, end_date)
    
    if df.empty:
        st.error("No data found for this ticker symbol. Please check the symbol and try again.")
    else:
        # Calculate moving averages
        for days in ma_days:
            df[f'MA_{days}'] = df['Adj Close'].rolling(window=days).mean()

        # Display recent price metrics
        col1, col2, col3, col4 = st.columns(4)
        current_price = df['Adj Close'].iloc[-1]
        period_high = df['High'].max()
        period_low = df['Low'].min()
        volume = df['Volume'].mean()
        
        col1.metric("Current Price", f"${current_price:.2f}")
        col2.metric("Period High", f"${period_high:.2f}")
        col3.metric("Period Low", f"${period_low:.2f}")
        col4.metric("Avg Volume", f"{volume:,.0f}")

        # Display price chart
        st.subheader("Price Chart with Moving Averages")
        chart_data = df[['Adj Close'] + [f'MA_{days}' for days in ma_days if f'MA_{days}' in df]]
        st.line_chart(chart_data)

        # Display raw data
        st.subheader("Recent Data")
        st.dataframe(df.tail(10).style.format({
            'Open': '{:.2f}',
            'High': '{:.2f}',
            'Low': '{:.2f}',
            'Close': '{:.2f}',
            'Adj Close': '{:.2f}',
            'Volume': '{:,}'
        }))

except Exception as e:
    st.error(f"Error fetching data: {str(e)}")

