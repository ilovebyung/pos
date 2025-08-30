import streamlit as st

def load_css():
    st.markdown("""
    <style>
    /* Global styling */
    .main > div {
        padding: 2rem 1rem;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Service Area Button Styling */
    .service-area-button {
        width: 100%;
        padding: 2rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 3px solid;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .service-area-active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
    
    .service-area-available {
        background: white;
        color: #333;
        border-color: #28a745;
    }
    
    .service-area-button:hover {
        opacity: 0.9;
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    }
    
    .running-time {
        font-size: 1rem;
        font-weight: normal;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* Streamlit Button Override for Service Areas */
    div.stButton > button:first-child {
        width: 100%;
        height: auto;
        min-height: 120px;
        white-space: pre-line;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 12px;
        border: 3px solid;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    }
    
    .active-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: #667eea !important;
    }
    
    .available-button {
        background: white !important;
        color: #333 !important;
        border-color: #28a745 !important;
    }
    
    /* Order Card Styling */
    .order-card {
        background: white;
        border: 2px solid #e1e5e9;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        overflow: hidden;
    }
    
    .order-card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    /* Order header styling */
    .order-header {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 600;
        font-size: 14px;
    }
    
    .order-header span {
        padding: 4px 8px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 6px;
        font-size: 12px;
    }
    
    /* Order content area */
    .order-content {
        padding: 16px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Product table styling */
    .product-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 12px;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        overflow: hidden;
    }
    
    .table-header {
        background-color: #f8f9fa;
        color: #495057;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 10px 12px;
        border-bottom: 2px solid #dee2e6;
        text-align: left;
    }
    
    .product-name {
        padding: 12px;
        border-bottom: 1px solid #f1f3f4;
        font-size: 14px;
        color: #2c3e50;
        line-height: 1.4;
    }
    
    .quantity-cell {
        padding: 12px;
        border-bottom: 1px solid #f1f3f4;
        text-align: center;
        font-weight: 600;
        font-size: 16px;
        color: #e74c3c;
        background-color: #fef9f9;
        width: 100px;
    }
    
    /* Table row hover effects */
    .product-table tr:hover .product-name,
    .product-table tr:hover .quantity-cell {
        background-color: #f8f9fa;
    }
    
    /* No orders message */
    .no-orders {
        text-align: center;
        padding: 60px 20px;
        color: #6c757d;
        font-size: 18px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        margin: 20px 0;
    }
    
    .no-orders small {
        display: block;
        margin-top: 10px;
        font-size: 14px;
        color: #adb5bd;
    }
    
    /* Confirm Button Styling */
    .stButton > button {
        background: #ff5a5f;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 6px 16px;
        font-weight: 500;
        font-size: 12px;
        min-height: 28px;
        transition: all 0.3s ease;
        margin-top: 8px;
    }
    
    .stButton > button:hover {
        background: #e04146;
        transform: translateY(-1px);
        box-shadow: 0 3px 8px rgba(255, 90, 95, 0.3);
    }
    
    /* Refresh Button Styling */
    .refresh-btn, .refresh-button {
        background: linear-gradient(135deg, #333 0%, #555 100%) !important;
        color: white !important;
        border: none !important;
        padding: 1rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        width: 200px !important;
        margin: 2rem auto !important;
        display: block !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    .refresh-btn:hover, .refresh-button:hover {
        background: linear-gradient(135deg, #222 0%, #444 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Status indicators */
    .order-header::before {
        content: "🔥";
        margin-right: 8px;
        font-size: 16px;
    }
    
    /* Animation for new orders */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .order-card {
        animation: slideIn 0.5s ease-out;
    }
    
    /* Success message styling */
    .stSuccess {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        border-radius: 8px;
    }
    
    /* Responsive design for smaller screens */
    @media (max-width: 768px) {
        .main > div {
            padding: 1rem 0.5rem;
        }
        
        .service-area-button {
            padding: 1.5rem;
            font-size: 1rem;
        }
        
        div.stButton > button:first-child {
            min-height: 100px;
            font-size: 1rem;
        }
        
        .order-card {
            margin-bottom: 15px;
        }
        
        .order-header {
            padding: 10px 12px;
            font-size: 12px;
        }
        
        .order-header span {
            font-size: 10px;
            padding: 3px 6px;
        }
        
        .product-name {
            font-size: 13px;
            padding: 10px;
        }
        
        .quantity-cell {
            font-size: 14px;
            padding: 10px;
            width: 80px;
        }
        
        .table-header {
            font-size: 11px;
            padding: 8px 10px;
        }
        
        .running-time {
            font-size: 0.9rem;
        }
    }
    
    /* Medium screen adjustments */
    @media (max-width: 1024px) and (min-width: 769px) {
        .service-area-button {
            padding: 1.8rem;
            font-size: 1.1rem;
        }
        
        .order-header {
            font-size: 13px;
        }
    }
    </style>
    """, unsafe_allow_html=True)