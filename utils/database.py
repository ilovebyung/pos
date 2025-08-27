import sqlite3

# Database connection
def get_db_connection():
    conn = sqlite3.connect('pos.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database and create table if not exists
def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Service_Area(
            service_area_id INTEGER PRIMARY KEY, 
            description TEXT,
            status INTEGER DEFAULT 0,
            timestamp DATETIME 
        )
    """)
    
    # Check if table is empty and insert initial data
    cursor.execute("SELECT COUNT(*) FROM Service_Area")
    count = cursor.fetchone()[0]
    
    if count == 0:
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
        
        cursor.executemany(
            "INSERT INTO Service_Area (service_area_id, description) VALUES (?, ?)",
            service_areas
        )
    
    conn.commit()
    conn.close()
