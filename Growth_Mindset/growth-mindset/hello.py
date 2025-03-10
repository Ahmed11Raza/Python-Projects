import streamlit as st

# Title and Introduction
st.title("Growth Mindset Challenge")
st.markdown("""
Welcome to the **Growth Mindset Challenge**! 
This interactive tool is designed to help you reflect on your challenges, set personal growth goals, and plan actionable strategies.
""")

# Step 1: Reflection on a past challenge
st.header("Step 1: Reflect on a Challenge")
challenge = st.text_area(
    "Describe a challenge or setback you've experienced:",
    placeholder="For example, a time when you faced failure and learned from it."
)

# Step 2: Set a personal growth goal
st.header("Step 2: Set Your Growth Goal")
goal = st.text_input("What is one personal growth goal you'd like to achieve?")

# Step 3: Define a strategy
st.header("Step 3: Outline Your Strategy")
strategy = st.text_area(
    "How do you plan to overcome challenges and work towards your goal?",
    placeholder="E.g., practicing new skills daily, seeking feedback, etc."
)

# Submit button to process the challenge input
if st.button("Submit Challenge"):
    st.success("Your challenge has been submitted!")
    st.markdown("### Your Growth Mindset Challenge Summary")
    st.write("**Challenge Reflection:**", challenge)
    st.write("**Growth Goal:**", goal)
    st.write("**Strategy:**", strategy)
    st.info("Remember: Every setback is a setup for a comeback. Embrace the learning process and keep growing!")
