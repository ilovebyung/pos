import streamlit as st

# Initialize session state variable if it doesn't exist
if 'customer' not in st.session_state:
    st.session_state.customer = ''

# Input field for customer
customer_input = st.text_input("Enter customer name:")

# Button to save customer to session state
if st.button("Save Name"):
    st.session_state.customer = customer_input
    st.success(f"Name '{st.session_state.customer}' saved!")



