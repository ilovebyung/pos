import streamlit as st
import sqlite3
from datetime import datetime
from utils.util import format_price
from utils.database import  get_db_connection 
from utils.style import load_css 



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

# Display individual order card


def display_order_card(order, items):
    with st.container():
        # Single card with header and content together
        st.markdown(f"""
        <div class="order-card">
            <div class="order-header">
                <span>Service Area: {order['service_area_id']}</span>
                <span>Order: {order['order_id']}</span>
            </div>
            <div class="order-content">
                <table class="product-table">

        """, unsafe_allow_html=True)
        
        # Display each product item within the same HTML block
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
        
        # Close the table and card in one block
        st.markdown("""
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Confirm button outside the card
        if st.button("Confirm", key=f"confirm_{order['order_id']}", width='stretch'):
            if confirm_order(order['order_id']):
                st.success(f"Order {order['order_id']} confirmed!")
                st.rerun()

# Main KDS page
def show_kds_page():
    st.set_page_config(
        page_title="Kitchen Display System",
        page_icon="🍳",
        layout="wide"
    )
    
    load_css()
    
    st.title("🍳 Kitchen Display System")
    st.markdown("---")

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
    
    # Display orders in three fixed columns
    cols = st.columns(3)
    
    for i, order in enumerate(orders):
        col_index = i % 3
        
        with cols[col_index]:
            # Get items for this order
            items = get_order_items(order['order_id'])
            
            if items:  # Only display if order has items
                display_order_card(order, items)
    
    # Auto-refresh every 30 seconds
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔀 Refresh", type="primary", width='stretch'):
            st.rerun()


# Run the page
if __name__ == "__main__":
    show_kds_page()