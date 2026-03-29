import streamlit as st

# # Inject CSS for button shapes
# st.markdown("""
#     <style>
#     .square-btn { width:60px; height:60px; border-radius:8px; background:#ddeeef;}
#     .rectangle-btn { width:100px; height:60px; border-radius:8px; background:#eeddee;}
#     .circle-btn { width:60px; height:60px; border-radius:50%; background:#ffeedd;}
#     .table-btn { display:inline-block; margin:10px; text-align:center; line-height:60px; font-weight:bold;}
#     </style>
# """, unsafe_allow_html=True)

# # Render buttons as clickable divs, and track clicks using Streamlit's session state
# st.markdown('<div class="table-btn square-btn">Table 1</div>', unsafe_allow_html=True)
# st.markdown('<div class="table-btn rectangle-btn">Table 2</div>', unsafe_allow_html=True)
# st.markdown('<div class="table-btn circle-btn">Table 3</div>', unsafe_allow_html=True)

import streamlit as st

# Page configuration
st.set_page_config(page_title="Table Allocations", page_icon="🌊", layout="wide")
st.title("🍽️ Table Allocations")
st.markdown("---")

# User input for grid size
n = st.number_input("Grid size (n x n)", min_value=2, max_value=10, value=4)

# Inject CSS for square, rectangle, circle shapes
st.markdown("""
    <style>
    .square-btn { width:60px; height:60px; border-radius:8px; background:#dceeef;}
    .rectangle-btn { width:100px; height:60px; border-radius:8px; background:#eeddee;}
    .circle-btn { width:60px; height:60px; border-radius:50%; background:#ffeedd;}
    .table-btn { display:inline-block; margin:7px; text-align:center; font-weight:bold; vertical-align:middle;}
    </style>
""", unsafe_allow_html=True)

# Button shape allocation function based on row,col or another mapping logic
def get_shape(row, col):
    if (row + col) % 3 == 0:
        return "square-btn"
    elif (row + col) % 3 == 1:
        return "rectangle-btn"
    else:
        return "circle-btn"

# Render nxn grid of custom shape buttons
for row in range(n):
    cols = st.columns(n)
    for col in range(n):
        shape_class = get_shape(row, col)
        table_id = f"Table {row * n + col + 1}"
        btn_html = f'<div class="table-btn {shape_class}">{table_id}</div>'
        cols[col].markdown(btn_html, unsafe_allow_html=True)
