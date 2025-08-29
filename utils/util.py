# Custom CSS for styling
import streamlit as st
import datetime

def load_css():
    st.markdown("""
    <style>
    .main > div {
        padding: 2rem 1rem;
    }
    
    .service-area-button {
        width: 100%;
        padding: 2rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 3px solid;
    }
    
    .service-area-active {
        background-color: #17a2b8;
        color: white;
        border-color: #17a2b8;
    }
    
    .service-area-available {
        background-color: white;
        color: #333;
        border-color: #28a745;
    }
    
    .service-area-button:hover {
        opacity: 0.8;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .running-time {
        font-size: 1rem;
        font-weight: normal;
        margin-top: 0.5rem;
    }
    
    .refresh-btn {
        background-color: #333 !important;
        color: white !important;
        border: none !important;
        padding: 1rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border-radius: 4px !important;
        width: 200px !important;
        margin: 2rem auto !important;
        display: block !important;
    }
    
    div.stButton > button:first-child {
        width: 100%;
        height: auto;
        min-height: 120px;
        white-space: pre-line;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 8px;
        border: 3px solid;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .active-button {
        background-color: #17a2b8 !important;
        color: white !important;
        border-color: #17a2b8 !important;
    }
    
    .available-button {
        background-color: white !important;
        color: #333 !important;
        border-color: #28a745 !important;
    }
    
    .refresh-button {
        background-color: #333 !important;
        color: white !important;
        border: none !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        padding: 0.8rem 2rem !important;
        min-height: 50px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Format price from integer to dollar format
def format_price(price_cents):
    if price_cents is None:
        return "$ 0.00"
    return f"$ {abs(price_cents) / 100:.2f}"

def format_timestamp(timestamp_str):
    """Format timestamp for better display"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str
    
# Calculate split amounts
def calculate_split_amounts(total_amount, split_count):
    if split_count <= 1:
        return [total_amount]
    
    base_amount = total_amount // split_count
    remainder = total_amount % split_count
    
    amounts = [base_amount] * split_count
    
    # Distribute remainder starting from the last amounts
    for i in range(remainder):
        amounts[-(i+1)] += 1
    
    return amounts