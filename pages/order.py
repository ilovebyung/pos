import streamlit as st
import sqlite3
from datetime import datetime

# Set selected_service_area 7
if 'selected_service_area' not in st.session_state:
    st.session_state.selected_service_area = 7

# Initialize session state for cart
if 'cart' not in st.session_state:
    st.session_state.cart = []

if 'order_id' not in st.session_state:
    st.session_state.order_id = None

def get_connection():
    """Create a connection to the SQLite database"""
    return sqlite3.connect('pos.db')

def initialize_database():
    """Initialize the database with all required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Product_Group (
            product_group_id INTEGER PRIMARY KEY,
            description TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Product_Option (
            product_option_id INTEGER PRIMARY KEY,
            description TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Product_Item (
            product_id INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            product_group_id INTEGER,
            product_option_id INTEGER,
            price INTEGER NOT NULL,
            tax INTEGER NOT NULL,
            FOREIGN KEY (product_group_id) REFERENCES Product_Group(product_group_id),
            FOREIGN KEY (product_option_id) REFERENCES Product_Option(product_option_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Order_Cart (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_area_id INTEGER,
            order_status INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (service_area_id) REFERENCES Service_Area(service_area_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Order_Product (
            order_id INTEGER,
            product_id INTEGER,
            option TEXT,
            product_quantity INTEGER NOT NULL,
            PRIMARY KEY (order_id, product_id, option),
            FOREIGN KEY (order_id) REFERENCES Order_Cart(order_id),
            FOREIGN KEY (product_id) REFERENCES Product_Item(product_id)
        )
    ''')
    
    # Insert initial data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM Product_Group")
    if cursor.fetchone()[0] == 0:
        # Insert Product Groups
        cursor.executemany('''
            INSERT INTO Product_Group (product_group_id, description) VALUES (?, ?)
        ''', [
            (1, 'Burgers and Sandwiches'),
            (2, 'Fried Chicken'),
            (3, 'Salads and Wraps'),
            (4, 'Sides')
        ])
        
        # Insert Product Items
        cursor.executemany('''
            INSERT INTO Product_Item (product_id, description, product_group_id, price, tax) VALUES (?, ?, ?, ?, ?)
        ''', [
            (1, 'Classic Cheeseburger', 1, 599, 60),
            (2, 'Grilled Chicken Club', 1, 799, 80),
            (3, 'Veggie Burger', 1, 699, 70),
            (5, 'Crispy Chicken Tenders (6 pcs)', 2, 699, 70),
            (6, 'Chicken Bucket (8 pcs)', 2, 1299, 130),
            (7, 'Spicy Fried Chicken Sandwich', 2, 679, 68),
            (8, 'Grilled Chicken Caesar Salad', 3, 749, 75),
            (9, 'Southwest Chicken Wrap', 3, 699, 70),
            (10, 'Garden Salad', 3, 599, 60),
            (11, 'French Fries (Small)', 4, 249, 25),
            (12, 'French Fries (Large)', 4, 349, 35)
        ])
        
        # Insert Product Options
        cursor.executemany('''
            INSERT INTO Product_Option (product_option_id, description) VALUES (?, ?)
        ''', [
            (1, 'Sweet'),
            (2, 'Spicy'),
            (3, 'No tomato')
        ])
    
    conn.commit()
    conn.close()

def format_price(price):
    """Format price from integer cents to dollar string"""
    return f"$ {price/100:.2f}"

def get_product_groups():
    """Get all product groups"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_group_id, description FROM Product_Group ORDER BY product_group_id")
    groups = cursor.fetchall()
    conn.close()
    return groups

def get_product_items(group_id):
    """Get product items for a specific group"""
    conn = get_connection()
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
    conn = get_connection()
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
    
    conn = get_connection()
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
        st.error(f"Error creating order: {e}")
        return False
    finally:
        conn.close()

# Initialize database
initialize_database()

# Page layout
st.set_page_config(layout="wide")

# Header
st.title("Order Cart")
st.caption(f"Service area: {st.session_state.selected_service_area} | Order #{st.session_state.order_id or 'New'}")

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
    
    # Checkout button
    if st.button("Checkout", type="primary", use_container_width=True, disabled=len(st.session_state.cart) == 0):
        if create_order():
            st.success("Order created successfully!")
            # Clear cart after successful order
            st.session_state.cart = []
            # Navigate to checkout
            st.switch_page("pages/checkout.py")

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