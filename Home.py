import streamlit as st
import os

# Set page config
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
st.title("🏠 Welcome to POS Home ")
st.markdown("---")

# Navigation hint
st.markdown("👉 Use the sidebar to navigate to the service area page.")


# Add vertical space to push the caption down
for _ in range(20):
    st.write("")

# Caption at the bottom
st.caption("Built with ❤️ by BADA & I4U") 
