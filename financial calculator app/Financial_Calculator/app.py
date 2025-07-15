import streamlit as st
import numpy as np
import numpy_financial as npf

# Set page configuration for a professional look
st.set_page_config(page_title="Financial Calculator", layout="wide", page_icon="💰")

# Custom CSS for enhanced styling
st.markdown(
    """
    <style>
    .main {background-color: #f5f7fa;}
    .stButton>button {
        background-color: #1e3a8a;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #3b82f6;
        color: white;
    }
    .stNumberInput, .stSelectbox {
        background-color: #ffffff;
        border-radius: 5px;
        padding: 5px;
    }
    h1 {color: #1e3a8a; font-weight: bold;}
    h2, h3 {color: #374151;}
    .result-box {
        background-color: #e5e7eb;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# App title and description
st.title("📊 Professional Financial Calculator")
st.markdown("Perform advanced financial calculations including compound interest, loan payments, and investment returns with ease.")

# Sidebar for calculator selection
st.sidebar.header("Select Calculator")
calculator = st.sidebar.selectbox(
    "Choose a calculation type",
    ["Compound Interest", "Loan Payment", "Investment Return (FV)", "Net Present Value (NPV)"]
)

# Function to format currency
def format_currency(value):
    return f"${value:,.2f}"

# Compound Interest Calculator
if calculator == "Compound Interest":
    st.header("Compound Interest Calculator")
    st.markdown("Calculate the future value of an investment with compound interest.")
    
    col1, col2 = st.columns(2)
    with col1:
        principal = st.number_input("Initial Investment ($)", min_value=0.0, value=1000.0, step=100.0)
        rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=5.0, step=0.1)
    with col2:
        years = st.number_input("Time (Years)", min_value=1, value=10, step=1)
        compounds_per_year = st.selectbox("Compounding Frequency", 
                                         ["Annually", "Semi-Annually", "Quarterly", "Monthly"],
                                         index=3)
    
    # Map compounding frequency to number of periods
    freq_map = {"Annually": 1, "Semi-Annually": 2, "Quarterly": 4, "Monthly": 12}
    n = freq_map[compounds_per_year]
    
    if st.button("Calculate Compound Interest"):
        rate_decimal = rate / 100
        future_value = principal * (1 + rate_decimal / n) ** (n * years)
        interest_earned = future_value - principal
        
        st.markdown("### Results")
        st.markdown(
            f"""
            <div class="result-box">
                <b>Future Value:</b> {format_currency(future_value)}<br>
                <b>Interest Earned:</b> {format_currency(interest_earned)}<br>
                <b>Initial Investment:</b> {format_currency(principal)}
            </div>
            """,
            unsafe_allow_html=True
        )

# Loan Payment Calculator
elif calculator == "Loan Payment":
    st.header("Loan Payment Calculator")
    st.markdown("Calculate monthly loan payments and total interest paid.")
    
    col1, col2 = st.columns(2)
    with col1:
        loan_amount = st.number_input("Loan Amount ($)", min_value=0.0, value=10000.0, step=1000.0)
        rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=4.5, step=0.1)
    with col2:
        years = st.number_input("Loan Term (Years)", min_value=1, value=5, step=1)
    
    if st.button("Calculate Loan Payment"):
        monthly_rate = rate / 100 / 12
        months = years * 12
        monthly_payment = npf.pmt(monthly_rate, months, -loan_amount)
        total_paid = monthly_payment * months
        total_interest = total_paid - loan_amount
        
        st.markdown("### Results")
        st.markdown(
            f"""
            <div class="result-box">
                <b>Monthly Payment:</b> {format_currency(monthly_payment)}<br>
                <b>Total Paid:</b> {format_currency(total_paid)}<br>
                <b>Total Interest:</b> {format_currency(total_interest)}<br>
                <b>Loan Amount:</b> {format_currency(loan_amount)}
            </div>
            """,
            unsafe_allow_html=True
        )

# Investment Return (Future Value) Calculator
elif calculator == "Investment Return (FV)":
    st.header("Investment Return Calculator")
    st.markdown("Calculate the future value of a series of cash flows.")
    
    col1, col2 = st.columns(2)
    with col1:
        periodic_payment = st.number_input("Periodic Investment ($)", min_value=0.0, value=100.0, step=10.0)
        rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=5.0, step=0.1)
    with col2:
        years = st.number_input("Time (Years)", min_value=1, value=10, step=1)
        compounds_per_year = st.selectbox("Compounding Frequency", 
                                         ["Annually", "Semi-Annually", "Quarterly", "Monthly"],
                                         index=3)
    
    if st.button("Calculate Future Value"):
        freq_map = {"Annually": 1, "Semi-Annually": 2, "Quarterly": 4, "Monthly": 12}
        n = freq_map[compounds_per_year]
        monthly_rate = rate / 100 / n
        periods = years * n
        future_value = npf.fv(monthly_rate, periods, -periodic_payment, 0, when='end')
        
        st.markdown("### Results")
        st.markdown(
            f"""
            <div class="result-box">
                <b>Future Value:</b> {format_currency(future_value)}<br>
                <b>Total Invested:</b> {format_currency(periodic_payment * periods)}<br>
                <b>Interest Earned:</b> {format_currency(future_value - periodic_payment * periods)}
            </div>
            """,
            unsafe_allow_html=True
        )

# Net Present Value (NPV) Calculator
elif calculator == "Net Present Value (NPV)":
    st.header("Net Present Value (NPV) Calculator")
    st.markdown("Calculate the NPV of a series of cash flows.")
    
    col1, col2 = st.columns(2)
    with col1:
        rate = st.number_input("Discount Rate (%)", min_value=0.0, value=5.0, step=0.1)
    with col2:
        cash_flows = st.text_area("Cash Flows (comma-separated, e.g., -1000, 300, 400, 500)", value="-1000, 300, 400, 500")
    
    if st.button("Calculate NPV"):
        try:
            cash_flows = [float(x.strip()) for x in cash_flows.split(",")]
            npv_value = npf.npv(rate / 100, cash_flows)
            
            st.markdown("### Results")
            st.markdown(
                f"""
                <div class="result-box">
                    <b>Net Present Value (NPV):</b> {format_currency(npv_value)}<br>
                    <b>Recommendation:</b> {'Positive NPV, consider investment.' if npv_value > 0 else 'Negative NPV, reconsider investment.'}
                </div>
                """,
                unsafe_allow_html=True
            )
        except ValueError:
            st.error("Please enter valid comma-separated cash flows (e.g., -1000, 300, 400, 500).")

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit | © 2025 Financial Calculator App")