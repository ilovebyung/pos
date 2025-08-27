import streamlit as st
import sqlite3
from datetime import datetime

# Custom CSS for KDS styling
def load_css():
    st.markdown("""
    <style>
    .main > div {
        padding: 1rem;
    }
    
    /* Order Card Styling */
    .order-card {
        border: 3px solid #27ae60;
        border-radius: 8px;
        margin: 1rem;
        background-color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    
    .order-header {
        background-color: #3498db;
        color: white;
        padding: 0.8rem;
        font-weight: bold;
        font-size: 1.1rem;
        text-align: center;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .order-content {
        padding: 0;
    }
    
    .product-table {
        width: 100%;
        border-collapse: collapse;
        margin: 0;
    }
    
    .table-header {
        background-color: #ecf0f1;
        border-bottom: 2px solid #bdc3c7;
        padding: 0.8rem;
        font-weight: bold;
        text-align: left;
    }
    
    .product-row {
        border-bottom: 1px solid #ecf0f1;
        padding: 1rem;
        vertical-align: top;
    }
    
    .product-name {
        font-weight: bold;
        color: #2c3e50;
        padding: 1rem;
        border-bottom: 1px solid #ecf0f1;
    }
    
    .quantity-cell {
        text-align: center;
        font-weight: bold;
        color: #27ae60;
        font-size: 1.2rem;
        padding: 1rem;
        border-bottom: 1px solid #ecf0f1;
        border-left: 1px solid #ecf0f1;
    }
    
    .confirm-button {
        background-color: #ecf0f1 !important;
        color: #2c3e50 !important;
        border: 2px solid #bdc3c7 !important;
        font-weight: bold !important;
        width: 100% !important;
        padding: 0.8rem !important;
        margin: 0 !important;
        border-radius: 0 !important;
        font-size: 1.1rem !important;
    }
    
    .confirm-button:hover {
        background-color: #d5dbdb !important;
        border-color: #95a5a6 !important;
    }
    
    .kds-title {
        text-align: center;
        color: #2c3e50;
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 2rem;
        padding: 1rem;
        background-color: #ecf0f1;
        border-radius: 8px;
    }
    
    .no-orders {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.5rem;
        padding: 3rem;
        background-color: #f8f9fa;
        border-radius: 8px;
        margin: 2rem;
    }
    
    /* Responsive grid */
    .order-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('pos.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database tables if they don't exist
def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Order_Cart (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_area_id INTEGER,
            order_status INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Product_Item (
            product_id INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            product_group_id INTEGER,
            product_id INTEGER,
            price INTEGER NOT NULL,
            tax INTEGER NOT NULL,
            FOREIGN KEY (product_group_id) REFERENCES Product_Group(product_group_id),
            FOREIGN KEY (product_id) REFERENCES Product_Option(product_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Order_Product (
            order_id INTEGER,
            product_id INTEGER,
            option TEXT,
            product_quantity INTEGER NOT NULL,
            PRIMARY KEY (order_id, product_id),
            FOREIGN KEY (order_id) REFERENCES Order_Cart(order_id),
            FOREIGN KEY (product_id) REFERENCES Product_Item(product_id)
        )
    """)
    
    conn.commit()
    conn.close()

# Get all open orders (order_status = 1)
def get_open_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT 
            oc.order_id,
            oc.service_area_id,
            oc.order_status,
            oc.created_at
        FROM Order_Cart oc
        INNER JOIN Order_Product op ON oc.order_id = op.order_id
        WHERE oc.order_status = 1
        ORDER BY oc.created_at ASC
    """)
    
    orders = cursor.fetchall()
    conn.close()
    return orders

# Get order items for a specific order
def get_order_items(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            op.order_id,
            op.product_id,
            pi.description as product_name,
            op.option,
            op.product_quantity
        FROM Order_Product op
        INNER JOIN Product_Item pi ON op.product_id = pi.product_id
        INNER JOIN Order_Cart oc ON op.order_id = oc.order_id
        WHERE op.order_id = ? AND oc.order_status = 1
        ORDER BY pi.description
    """, (order_id,))
    
    items = cursor.fetchall()
    conn.close()
    return items

# Confirm order (set order_status to 2)
def confirm_order(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE Order_Cart 
            SET order_status = 2 
            WHERE order_id = ?
        """, (order_id,))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error confirming order: {e}")
        return False
    finally:
        conn.close()

# Create sample data for testing
def create_sample_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if sample data already exists
    cursor.execute("SELECT COUNT(*) FROM Order_Cart WHERE order_status = 1")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    try:
        # Insert sample product items
        sample_items = [
            (1, 'Classic Cheeseburger', 1, None, 599, 60),
            (2, 'Grilled Chicken Club', 1, None, 799, 80),
            (3, 'Veggie Burger', 1, None, 699, 70),
            (5, 'Crispy Chicken Tenders (6 pcs)', 2, None, 699, 70)
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO Product_Item 
            (product_id, description, product_group_id, product_id, price, tax)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_items)
        
        # Insert sample orders
        cursor.execute("""
            INSERT INTO Order_Cart (order_id, service_area_id, order_status)
            VALUES (123, 7, 1)
        """)
        
        cursor.execute("""
            INSERT INTO Order_Cart (order_id, service_area_id, order_status)
            VALUES (456, 7, 1)
        """)
        
        # Insert sample order products
        cursor.execute("""
            INSERT INTO Order_Product (order_id, product_id, option, product_quantity)
            VALUES (123, 1, NULL, 1)
        """)
        
        cursor.execute("""
            INSERT INTO Order_Product (order_id, product_id, option, product_quantity)
            VALUES (456, 2, 'No tomato', 2)
        """)
        
        conn.commit()
    except Exception as e:
        st.error(f"Error creating sample data: {e}")
    finally:
        conn.close()

# Display individual order card
def display_order_card(order, items):
    with st.container():
        # Order header
        st.markdown(f"""
        <div class="order-card">
            <div class="order-header">
                <span>service_area:{order['service_area_id']}</span>
                <span>Order: {order['order_id']}</span>
            </div>
            <div class="order-content">
                <table class="product-table">
                    <tr>
                        <th class="table-header">product_Item</th>
                        <th class="table-header" style="width: 100px; text-align: center;">quantity</th>
                    </tr>
        """, unsafe_allow_html=True)
        
        # Display each product item
        for item in items:
            product_display = item['product_name']
            if item['option']:
                product_display += f" ({item['option']})"
            
            st.markdown(f"""
                    <tr>
                        <td class="product-name">{product_display}</td>
                        <td class="quantity-cell">{item['product_quantity']}</td>
                    </tr>
            """, unsafe_allow_html=True)
        
        st.markdown("""
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Confirm button
        if st.button("Confirm", key=f"confirm_{order['order_id']}", use_container_width=True):
            if confirm_order(order['order_id']):
                st.success(f"Order {order['order_id']} confirmed!")
                st.rerun()

# Main KDS page
def show_kds_page():
    load_css()
    init_database()
    
    # Create sample data for demonstration
    create_sample_data()
    
    # Page title
    st.markdown("""
    <div class="kds-title">
        🍳 Kitchen Display System
    </div>
    """, unsafe_allow_html=True)
    
    # Get open orders
    orders = get_open_orders()
    
    if not orders:
        st.markdown("""
        <div class="no-orders">
            📋 No pending orders<br>
            <small>All caught up! 🎉</small>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display orders in columns
    # Calculate number of columns based on number of orders
    num_orders = len(orders)
    if num_orders == 1:
        cols = [st.columns(1)[0]]
    elif num_orders == 2:
        cols = st.columns(2)
    else:
        cols = st.columns(min(3, num_orders))  # Maximum 3 columns
    
    for i, order in enumerate(orders):
        col_index = i % len(cols)
        
        with cols[col_index]:
            # Get items for this order
            items = get_order_items(order['order_id'])
            
            if items:  # Only display if order has items
                display_order_card(order, items)
    
    # Auto-refresh every 30 seconds
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=False):
            st.rerun()
    
    # Auto-refresh (uncomment for production)
    # import time
    # time.sleep(30)
    # st.rerun()

# Run the page
if __name__ == "__main__":
    show_kds_page()
else:
    show_kds_page()