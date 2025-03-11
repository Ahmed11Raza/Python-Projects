import streamlit as st
import random

# Set page title and description
st.title("Random Quote Generator")
st.write("Click the button below to display a random inspirational quote.")

# Quotes list
quotes = [
    {
        "quote": "The only way to do great work is to love what you do.",
        "author": "Steve Jobs"
    },
    {
        "quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "author": "Winston Churchill"
    },
    {
        "quote": "The future belongs to those who believe in the beauty of their dreams.",
        "author": "Eleanor Roosevelt"
    },
    {
        "quote": "Don't watch the clock; do what it does. Keep going.",
        "author": "Sam Levenson"
    },
    {
        "quote": "The only limit to our realization of tomorrow will be our doubts of today.",
        "author": "Franklin D. Roosevelt"
    },
    {
        "quote": "Believe you can and you're halfway there.",
        "author": "Theodore Roosevelt"
    },
    {
        "quote": "Your time is limited, don't waste it living someone else's life.",
        "author": "Steve Jobs"
    }
]

# Initialize session state
if 'current_quote' not in st.session_state:
    st.session_state.current_quote = random.choice(quotes)

def get_random_quote():
    st.session_state.current_quote = random.choice(quotes)

# Create a card-like container for the quote
with st.container():
    st.subheader(f'"{st.session_state.current_quote["quote"]}"')
    st.caption(f"- {st.session_state.current_quote['author']}")

# Add some spacing
st.write("")

# New quote button
st.button("New Quote", on_click=get_random_quote)