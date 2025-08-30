import streamlit as st
from datetime import datetime
from utils.util import format_price
from utils.database import  get_db_connection
from utils.style import load_css


# Set selected_service_area 7
if 'selected_service_area' not in st.session_state:
    st.session_state.selected_service_area = 7

# Initialize session state for cart
if 'cart' not in st.session_state:
    st.session_state.cart = []

if 'order_id' not in st.session_state:
    st.session_state.order_id = None

def get_product_groups():
    """Get all product groups"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_group_id, description FROM Product_Group ORDER BY product_group_id")
    groups = cursor.fetchall()
    conn.close()
    return groups

def get_product_items(group_id):
    """Get product items for a specific group"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT product_id, description, price 
        FROM Product_Item 
        WHERE product_group_id = ?
        ORDER BY product_id
    ''', (group_id,))
    items = cursor.fetchall()
    conn.close()
    return items

def get_product_options(product_id):
    """Get product options for a specific product item"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT option FROM Product_Option 
        WHERE product_id = ?
    ''', (product_id,))
    options = cursor.fetchall()
    conn.close()
    return options

def add_to_cart(product_id, product_name, price, option):
    """Add item to cart or update quantity if already exists"""
    # Check if item with same product and option already exists
    for item in st.session_state.cart:
        if item['product_id'] == product_id and item['option'] == option:
            item['quantity'] += 1
            return
    
    # Add new item
    st.session_state.cart.append({
        'product_id': product_id,
        'product_name': product_name,
        'price': price,
        'option': option,
        'quantity': 1
    })

def update_quantity(index, delta):
    """Update quantity of cart item"""
    if 0 <= index < len(st.session_state.cart):
        st.session_state.cart[index]['quantity'] += delta
        if st.session_state.cart[index]['quantity'] <= 0:
            st.session_state.cart.pop(index)

def calculate_subtotal():
    """Calculate cart subtotal"""
    return sum(item['price'] * item['quantity'] for item in st.session_state.cart)

def create_order():
    """Create order and insert into database"""
    if not st.session_state.cart:
        return False
    
    # Check if service area is selected
    if not st.session_state.get('selected_service_area'):
        st.error("Select a service area to continue.")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create order in Order_Cart
        cursor.execute('''
            INSERT INTO Order_Cart (service_area_id, order_status)
            VALUES (?, 1)
        ''', (st.session_state.selected_service_area,))
        
        order_id = cursor.lastrowid
        st.session_state.order_id = order_id
        
        # Insert items into Order_Product
        for item in st.session_state.cart:
            cursor.execute('''
                INSERT INTO Order_Product (order_id, product_id, option, product_quantity)
                VALUES (?, ?, ?, ?)
            ''', (order_id, item['product_id'], item['option'], item['quantity']))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        # Check if the error is related to service_area_id NOT NULL constraint
        error_message = str(e)
        if "NOT NULL constraint failed: Order_Cart.service_area_id" in error_message:
            st.error("Select a service area to continue.")
        else:
            st.error(f"Error creating order: {e}")
        return False
    finally:
        conn.close()
 
def show_order_page():

    # Page layout
    st.set_page_config(
        page_title="Order Cart",    
        page_icon="🛒",
        layout="wide"
    )
    
    load_css()

    st.title("🛒 Order Cart")
    
    # Check if service area is selected and display appropriate message
    service_area_display = st.session_state.get('selected_service_area', 'Not Selected')
    if not st.session_state.get('selected_service_area'):
        st.warning("⚠️ No service area selected. Please select a service area first.")
        st.caption(f"Service area: {service_area_display} | Order #{st.session_state.order_id or 'New'}")
        
        # Add button to go back to service area selection
        if st.button("🔙 Go to Service Area Selection", type="primary"):
            st.switch_page("pages/1_Service_Area.py")
    else:
        st.caption(f"Service area: {service_area_display} | Order #{st.session_state.order_id or 'New'}")
    
    st.markdown("---")

    # Create two columns
    col_cart, col_menu = st.columns([1, 2])

    # Left column - Cart
    with col_cart:
        st.subheader("Order Cart")
        
        if st.session_state.cart:
            # Display cart items
            for i, item in enumerate(st.session_state.cart):
                with st.container():
                    cart_col1, cart_col2, cart_col3 = st.columns([3, 2, 2])
                    
                    with cart_col1:
                        st.write(f"**{item['product_name']}**")
                        if item['option']:
                            st.caption(f"Option: {item['option']}")
                    
                    with cart_col2:
                        quantity_col1, quantity_col2, quantity_col3 = st.columns([1, 1, 1])
                        with quantity_col1:
                            if st.button("➖", key=f"dec_{i}", help="Decrease quantity"):
                                update_quantity(i, -1)
                                st.rerun()
                        with quantity_col2:
                            st.write(f"{item['quantity']}")
                        with quantity_col3:
                            if st.button("➕", key=f"inc_{i}", help="Increase quantity"):
                                update_quantity(i, 1)
                                st.rerun()
                    
                    with cart_col3:
                        st.write(format_price(item['price']))
                    
                    st.divider()
        else:
            st.info("Cart is empty")
        
        # Subtotal
        st.divider()
        subtotal = calculate_subtotal()
        st.subheader(f"Subtotal: {format_price(subtotal)}")
        
        # Checkout button - disabled if no service area selected or cart is empty
        checkout_disabled = (
            len(st.session_state.cart) == 0 or 
            not st.session_state.get('selected_service_area')
        )
        
        if st.button("Checkout", type="primary", use_container_width=True, disabled=checkout_disabled):
            if create_order():
                st.success("Order created successfully!")
                # Clear cart after successful order
                st.session_state.cart = []
                # Navigate to checkout
                st.switch_page("pages/4_Checkout.py")

    # Right column - Menu
    with col_menu:
        st.subheader("Menu")
        
        # Get product groups
        product_groups = get_product_groups()
        
        # Create tabs for product groups
        if product_groups:
            group_names = [group[1] for group in product_groups]
            tabs = st.tabs(group_names)
            
            for i, (group_id, group_name) in enumerate(product_groups):
                with tabs[i]:
                    # Get product items for this group
                    product_items = get_product_items(group_id)
                    
                    # Display product items
                    for product_id, product_name, price in product_items:
                        with st.container():
                            item_col1, item_col2 = st.columns([3, 1])
                            
                            with item_col1:
                                st.write(f"**{product_name}**")
                                st.write(format_price(price))
                            
                            with item_col2:
                                # Product options
                                options = get_product_options(product_id)
                                option_list = ["No option"] + [opt[0] for opt in options]

                                
                                # Create unique key for each product's selectbox
                                selected_option = st.selectbox(
                                    "Option",
                                    option_list,
                                    key=f"option_{product_id}",
                                    label_visibility="collapsed"
                                )
                                
                                if st.button("Add", key=f"add_{product_id}", type="primary"):
                                    option_value = None if selected_option == "No option" else selected_option
                                    add_to_cart(product_id, product_name, price, option_value)
                                    st.rerun()
                            
                            st.divider()

# Run the page
if __name__ == "__main__":
    show_order_page()