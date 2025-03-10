import streamlit as st
import requests

st.title("🔒 Password Strength Checker")
st.write("Check how strong your password is!")

password = st.text_input("Enter your password:", type="password")

if st.button("Check Strength"):
    if password:
        try:
            response = requests.post(
                "http://localhost:8000/check-password/",
                json={"password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Display individual messages
                for msg in data["messages"]:
                    st.error(msg)
                
                # Display final result with appropriate styling
                if data["strength"] == "strong":
                    st.success(data["result"])
                elif data["strength"] == "moderate":
                    st.warning(data["result"])
                else:
                    st.error(data["result"])
            else:
                st.error("Error connecting to the API service")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the API. Make sure the backend is running.")
    else:
        st.warning("Please enter a password to check")