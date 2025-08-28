import sqlite3

# Database connection
def get_db_connection():
    conn = sqlite3.connect('pos.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

# Initialize checkout database  
def initialize_database():
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
    

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Product_Item (
            product_id INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            product_group_id INTEGER,
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

    # Insert sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM Order_Cart WHERE order_status = 2")
    if cursor.fetchone()[0] == 0:
        # Create sample confirmed order
        cursor.execute("""
            INSERT INTO Order_Cart (order_id, order_status, service_area_id, subtotal)
            VALUES (223, 2, 7, 2197)
        """)
        cursor.execute("""
            INSERT INTO Order_Cart (order_id, order_status, service_area_id, subtotal)
            VALUES (135, 2, 7, 799)
        """)
       
    
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
    
    # Check if table is empty and populate with initial data
    cursor.execute('SELECT COUNT(*) FROM Service_Area')
    if cursor.fetchone()[0] == 0:
        service_areas = [
            (1, 'buffet tables for eight'),
            (2, 'square table for two'),
            (3, 'rectangular table for four'),
            (4, 'round table for six'),
            (5, 'VIP booth'),
            (6, 'outdoor patio table'),
            (7, 'bar counter seat'),
            (8, 'window-side table for two')
        ]
        cursor.executemany('INSERT INTO Service_Area (service_area_id, description) VALUES (?, ?)', service_areas)
        conn.commit()
    
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
        print(f"Error creating sample data: {e}")
    finally:
        conn.close()
