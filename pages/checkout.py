import streamlit as st
import sqlite3
from datetime import datetime

# Custom CSS for checkout styling
def load_css():
    st.markdown("""
    <style>
    .main > div {
        padding: 1rem;
    }
    
    /* Order Cart Styling */
    .order-cart {
        border: 2px solid #bdc3c7;
        border-radius: 8px;
        margin: 0.5rem 0;
        background-color: white;
    }
    
    .order-header {
        background-color: #2c3e50;
        color: white;
        padding: 0.8rem;
        font-weight: bold;
        text-align: center;
        margin: 0;
    }
    
    .cart-table {
        width: 100%;
        border-collapse: collapse;
        margin: 0;
    }
    
    .cart-header {
        background-color: #ecf0f1;
        padding: 0.5rem;
        font-weight: bold;
        text-align: center;
        border-bottom: 1px solid #bdc3c7;
    }
    
    .cart-row {
        padding: 0.5rem;
        text-align: center;
        border-bottom: 1px solid #ecf0f1;
    }
    
    /* Payment Section */
    .payment-header {
        background-color: #2c3e50;
        color: white;
        padding: 0.8rem;
        font-weight: bold;
        text-align: center;
        border-radius: 8px 8px 0 0;
        margin: 0;
    }
    
    .payment-table {
        width: 100%;
        border-collapse: collapse;
        border: 2px solid #bdc3c7;
        border-top: none;
        border-radius: 0 0 8px 8px;
    }
    
    .payment-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 1rem;
        border-bottom: 1px solid #ecf0f1;
        background-color: #f8f9fa;
    }
    
    .payment-row:last-child {
        border-bottom: none;
        font-weight: bold;
        background-color: #e9ecef;
    }
    
    /* Calculator Buttons */
    .calc-button {
        background-color: #3498db !important;
        color: white !important;
        border: 2px solid #2980b9 !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 60px !important;
        margin: 0.1rem !important;
        border-radius: 4px !important;
    }
    
    .calc-button:hover {
        background-color: #2980b9 !important;
        border-color: #1f4788 !important;
    }
    
    .special-button {
        background-color: #95a5a6 !important;
        border-color: #7f8c8d !important;
    }
    
    .special-button:hover {
        background-color: #7f8c8d !important;
        border-color: #5d6d7e !important;
    }
    
    .settle-button {
        background-color: #e74c3c !important;
        border-color: #c0392b !important;
        font-size: 1.4rem !important;
    }
    
    .settle-button:hover {
        background-color: #c0392b !important;
        border-color: #a93226 !important;
    }
    
    /* Balance Display */
    .balance-header {
        background-color: #2c3e50;
        color: white;
        padding: 0.5rem;
        text-align: center;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .balance-amount {
        background-color: #2c3e50;
        color: white;
        padding: 0.8rem;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    /* Payment Method Buttons */
    .payment-method {
        background-color: #2c3e50 !important;
        color: white !important;
        border: 2px solid #34495e !important;
        font-weight: bold !important;
        width: 100% !important;
        margin: 0.1rem 0 !important;
        padding: 0.8rem !important;
    }
    
    /* Split Section */
    .split-section {
        background-color: #f8f9fa;
        border: 2px solid #bdc3c7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .split-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .split-amounts {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .split-amount {
        background-color: #e9ecef;
        padding: 0.5rem;
        text-align: right;
        font-weight: bold;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('pos.db')
    conn.row_factory = sqlite3.Row
    return conn

# Format price from integer to dollar format
def format_price(price_cents):
    if price_cents is None:
        return "$ 0.00"
    return f"$ {abs(price_cents) / 100:.2f}"

# Initialize database and session state
def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Order_Cart (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_status INTEGER NOT NULL DEFAULT 0,
            service_area_id INTEGER NOT NULL,
            customer_id INTEGER,
            subtotal INTEGER NOT NULL DEFAULT 0,
            charged INTEGER NOT NULL DEFAULT 0,
            special_request TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (service_area_id) REFERENCES Service_Area(service_area_id),
            FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Service_Area (
            service_area_id INTEGER PRIMARY KEY, 
            description TEXT,
            status INTEGER DEFAULT 0,
            timestamp DATETIME 
        )
    """)
    
    # Insert sample data for testing if needed
    cursor.execute("SELECT COUNT(*) FROM Order_Cart WHERE order_status = 2")
    if cursor.fetchone()[0] == 0:
        # Create sample confirmed order
        cursor.execute("""
            INSERT INTO Order_Cart (order_id, order_status, service_area_id, subtotal)
            VALUES (123, 2, 7, 2197)
        """)
        cursor.execute("""
            INSERT INTO Order_Cart (order_id, order_status, service_area_id, subtotal)
            VALUES (456, 2, 7, 799)
        """)
    
    conn.commit()
    conn.close()

# Initialize session state
def init_session_state():
    if 'selected_service_area' not in st.session_state:
        st.session_state.selected_service_area = 7
    
    if 'tips_amount' not in st.session_state:
        st.session_state.tips_amount = 0
    
    if 'amount_tendered' not in st.session_state:
        st.session_state.amount_tendered = 0
    
    if 'current_input' not in st.session_state:
        st.session_state.current_input = ""
    
    if 'split_count' not in st.session_state:
        st.session_state.split_count = 1
    
    if 'split_amounts' not in st.session_state:
        st.session_state.split_amounts = []

# Get order details
def get_order_details():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get orders for the selected service area with status 2
    cursor.execute("""
        SELECT 
            oc.order_id,
            oc.service_area_id,
            oc.subtotal,
            op.product_id,
            pi.description,
            op.option,
            op.product_quantity,
            pi.price
        FROM Order_Cart oc
        LEFT JOIN Order_Product op ON oc.order_id = op.order_id
        LEFT JOIN Product_Item pi ON op.product_id = pi.product_id
        WHERE oc.service_area_id = ? AND oc.order_status = 2
        ORDER BY oc.order_id, pi.description
    """, (st.session_state.selected_service_area,))
    
    results = cursor.fetchall()
    conn.close()
    return results

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

# Update order status and service area
def settle_order(order_ids, total_charged):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Update order status to 3 (settled) and set charged amount
        for order_id in order_ids:
            cursor.execute("""
                UPDATE Order_Cart 
                SET order_status = 3, charged = ?
                WHERE order_id = ?
            """, (total_charged, order_id))
        
        # Update service area status to 0 (available)
        cursor.execute("""
            UPDATE Service_Area 
            SET status = 0 
            WHERE service_area_id = ?
        """, (st.session_state.selected_service_area,))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error settling order: {e}")
        return False
    finally:
        conn.close()

# Handle calculator button clicks
def handle_calculator_input(value):
    if value == "delete":
        st.session_state.current_input = st.session_state.current_input[:-1]
    elif value == "enter":
        if st.session_state.current_input:
            st.session_state.amount_tendered = int(float(st.session_state.current_input) * 100)
            st.session_state.current_input = ""
    elif value in ["00", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        st.session_state.current_input += value
    elif value.startswith("$"):
        # Quick amount buttons
        amount = value[1:]
        st.session_state.amount_tendered = int(float(amount) * 100)

# Main checkout page
def show_checkout_page():
    load_css()
    init_database()
    init_session_state()
    
    # Get order data
    order_data = get_order_details()
    
    if not order_data:
        st.error("No confirmed orders found for this service area.")
        return
    
    # Process order data
    orders = {}
    subtotal = 0
    
    for row in order_data:
        order_id = row['order_id']
        if order_id not in orders:
            orders[order_id] = []
        
        if row['product_id']:  # Check if product exists
            orders[order_id].append({
                'description': row['description'],
                'op.option': row['option'],
                'quantity': row['product_quantity'],
                'price': row['price']
            })
            subtotal += row['price'] * row['product_quantity']
    
    # Constants
    TAX = 203  # $2.03
    
    # Calculate totals
    total_tips = st.session_state.tips_amount
    balance_due = subtotal + TAX + total_tips
    remaining_balance = balance_due - st.session_state.amount_tendered
    
    # Layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Order Cart
        st.markdown(f"""
        <div class="order-cart">
            <div class="order-header">
                Order Cart<br>
                service_area: {st.session_state.selected_service_area} &nbsp;&nbsp; Order_id {', '.join(map(str, orders.keys()))}
            </div>
            <table class="cart-table">
                <tr>
                    <th class="cart-header">product_Item</th>
                    <th class="cart-header">quantity</th>
                    <th class="cart-header">price</th>
                </tr>
        """, unsafe_allow_html=True)
        
        for order_id, items in orders.items():
            for item in items:
                item_display = item['description']
                if item['op.option']:
                    item_display += f"<br>({item['op.option']})"
                
                st.markdown(f"""
                    <tr>
                        <td class="cart-row">{item_display}</td>
                        <td class="cart-row">{item['quantity']}</td>
                        <td class="cart-row">{format_price(item['price'] * item['quantity'])}</td>
                    </tr>
                """, unsafe_allow_html=True)
        
        st.markdown("</table></div>", unsafe_allow_html=True)
        
        # Payment Section
        st.markdown('<div class="payment-header">Payment</div>', unsafe_allow_html=True)
        
        payment_items = [
            ("Subtotal", subtotal),
            ("Tax", TAX),
            ("Tips", total_tips),
            ("Balance due", balance_due)
        ]
        
        for label, amount in payment_items:
            st.markdown(f"""
            <div class="payment-row">
                <span>{label}</span>
                <span>{format_price(amount)}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Top row - Balance and Payment Methods
        top_col1, top_col2, top_col3 = st.columns([2, 1, 1])
        
        with top_col1:
            st.markdown(f"""
            <div class="balance-header">Remaining Balance / Change Due</div>
            <div class="balance-amount">{format_price(remaining_balance)}</div>
            """, unsafe_allow_html=True)
        
        with top_col2:
            if st.button("Credit", key="credit", use_container_width=True, type="secondary"):
                pass
        
        with top_col3:
            if st.button("Cash", key="cash", use_container_width=True, type="secondary"):
                pass
        
        # Amount Tendered
        st.markdown(f"""
        <div class="balance-header">Amount Tendered {format_price(st.session_state.amount_tendered)}</div>
        """, unsafe_allow_html=True)
        
        # Calculator Grid
        calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)
        
        # Row 1
        with calc_col1:
            if st.button("7", key="calc_7", use_container_width=True):
                handle_calculator_input("7")
                st.rerun()
        with calc_col2:
            if st.button("8", key="calc_8", use_container_width=True):
                handle_calculator_input("8")
                st.rerun()
        with calc_col3:
            if st.button("9", key="calc_9", use_container_width=True):
                handle_calculator_input("9")
                st.rerun()
        with calc_col4:
            if st.button("$20", key="quick_20", use_container_width=True):
                handle_calculator_input("$20")
                st.rerun()
        
        # Row 2
        with calc_col1:
            if st.button("4", key="calc_4", use_container_width=True):
                handle_calculator_input("4")
                st.rerun()
        with calc_col2:
            if st.button("5", key="calc_5", use_container_width=True):
                handle_calculator_input("5")
                st.rerun()
        with calc_col3:
            if st.button("6", key="calc_6", use_container_width=True):
                handle_calculator_input("6")
                st.rerun()
        with calc_col4:
            if st.button("$10", key="quick_10", use_container_width=True):
                handle_calculator_input("$10")
                st.rerun()
        
        # Row 3
        with calc_col1:
            if st.button("1", key="calc_1", use_container_width=True):
                handle_calculator_input("1")
                st.rerun()
        with calc_col2:
            if st.button("2", key="calc_2", use_container_width=True):
                handle_calculator_input("2")
                st.rerun()
        with calc_col3:
            if st.button("3", key="calc_3", use_container_width=True):
                handle_calculator_input("3")
                st.rerun()
        with calc_col4:
            if st.button("$5", key="quick_5", use_container_width=True):
                handle_calculator_input("$5")
                st.rerun()
        
        # Row 4
        with calc_col1:
            if st.button("0", key="calc_0", use_container_width=True):
                handle_calculator_input("0")
                st.rerun()
        with calc_col2:
            if st.button("00", key="calc_00", use_container_width=True):
                handle_calculator_input("00")
                st.rerun()
        with calc_col3:
            if st.button("delete", key="calc_delete", use_container_width=True):
                handle_calculator_input("delete")
                st.rerun()
        with calc_col4:
            if st.button("enter", key="calc_enter", use_container_width=True):
                handle_calculator_input("enter")
                st.rerun()
        
        # Tips Section
        st.markdown("### Tips")
        tips_col1, tips_col2 = st.columns([3, 1])
        
        with tips_col1:
            if st.button("Tips", key="tips_button", use_container_width=True, type="secondary"):
                # Use current input as tips if available
                if st.session_state.current_input:
                    st.session_state.tips_amount = int(float(st.session_state.current_input) * 100)
                    st.session_state.current_input = ""
                    st.rerun()
        
        # Split Evenly Section
        st.markdown("### Split evenly")
        split_col1, split_col2, split_col3 = st.columns([1, 2, 1])
        
        with split_col1:
            if st.button("➖", key="split_minus"):
                if st.session_state.split_count > 1:
                    st.session_state.split_count -= 1
                    st.rerun()
        
        with split_col2:
            st.markdown(f"<div style='text-align: center; padding: 0.5rem; background: #f0f0f0; border-radius: 4px;'>{st.session_state.split_count}</div>", unsafe_allow_html=True)
        
        with split_col3:
            if st.button("➕", key="split_plus"):
                st.session_state.split_count += 1
                st.rerun()
        
        # Calculate and display split amounts
        if st.session_state.split_count > 1:
            split_amounts = calculate_split_amounts(balance_due, st.session_state.split_count)
            st.markdown("**Split amounts:**")
            for i, amount in enumerate(split_amounts):
                st.markdown(f"<div class='split-amount'>{format_price(amount)}</div>", unsafe_allow_html=True)
        
        # Display current input
        if st.session_state.current_input:
            st.markdown(f"**Current input:** ${st.session_state.current_input}")
        
        # Settle Button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("settle", key="settle", use_container_width=True, type="primary"):
            # Calculate total charged (subtotal + tax + tips)
            total_charged = subtotal + TAX + total_tips
            
            if settle_order(list(orders.keys()), total_charged):
                # Clear session state
                st.session_state.selected_service_area = None
                st.session_state.tips_amount = 0
                st.session_state.amount_tendered = 0
                st.session_state.current_input = ""
                st.session_state.split_count = 1
                
                st.success("Order settled successfully!")
                st.switch_page("pages/service_area.py")

# Run the page
if __name__ == "__main__":
    show_checkout_page()
else:
    show_checkout_page()