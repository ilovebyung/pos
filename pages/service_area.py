import streamlit as st
import sqlite3
import pandas as pd

def init_database():
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect('pos.db')
    conn.execute('PRAGMA journal_mode=WAL;')  # Enable WAL mode
    cursor = conn.cursor()
    
    # Create Service_Area table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Service_Area (
            service_area_id INTEGER PRIMARY KEY,
            description TEXT
        )
    ''')
    
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

def load_service_areas():
    """Load service areas from database with WAL mode enabled"""
    conn = sqlite3.connect('pos.db')
    conn.execute('PRAGMA journal_mode=WAL;')  # Enable WAL mode
    df = pd.read_sql_query('SELECT * FROM Service_Area ORDER BY service_area_id', conn)
    conn.close()
    return df

def initialize_session_state(service_areas_df):
    """Initialize session state for service areas if empty"""
    if 'service_area_status' not in st.session_state:
        st.session_state.service_area_status = {}
        for _, row in service_areas_df.iterrows():
            st.session_state.service_area_status[row['service_area_id']] = 0

def reset_all_tables():
    """Reset all service area statuses to 0"""
    if 'service_area_status' in st.session_state:
        for area_id in st.session_state.service_area_status.keys():
            st.session_state.service_area_status[area_id] = 0
    st.rerun()

def select_service_area(area_id):
    """Set selected service area status to 1 and navigate to order page"""
    st.session_state.service_area_status[area_id] = 1
    st.session_state.selected_service_area = area_id
    st.switch_page("pages/order.py")

def main():
    st.set_page_config(
        page_title="Service Area Selection",
        page_icon="🍽️",
        layout="wide"
    )
    
    st.title("🍽️ Service Area Selection")
    st.markdown("---")
    
    # Initialize database
    init_database()
    
    # Load service areas
    service_areas_df = load_service_areas()
    
    # Initialize session state
    initialize_session_state(service_areas_df)
    
    # Create grid layout for service areas
    cols = st.columns(3)
    
    for idx, (_, row) in enumerate(service_areas_df.iterrows()):
        area_id = row['service_area_id']
        description = row['description']
        status = st.session_state.service_area_status[area_id]
        
        col_idx = idx % 3
        
        with cols[col_idx]:
            # Determine button style based on status
            if status == 0:  # Available
                button_type = "primary"
                button_text = f"**{area_id}**\n\n{description}"
                disabled = False
            else:  # Occupied
                button_type = "secondary"
                button_text = f"**{area_id}** 🔴\n\n{description}\n\n*OCCUPIED*"
                disabled = True
            
            # Create button for each service area
            if st.button(
                button_text,
                key=f"area_{area_id}",
                disabled=disabled,
                use_container_width=True,
                type=button_type
            ):
                select_service_area(area_id)
    
    st.markdown("---")
    
    # Reset and status section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔄 Reset Table", use_container_width=True, type="secondary"):
            reset_all_tables()
    
    # Display current status
    st.markdown("### Current Status")
    status_cols = st.columns(3)
    
    available_count = sum(1 for status in st.session_state.service_area_status.values() if status == 0)
    occupied_count = sum(1 for status in st.session_state.service_area_status.values() if status == 1)
    total_count = len(st.session_state.service_area_status)
    
    with status_cols[0]:
        st.metric("Available", available_count, delta=None)
    
    with status_cols[1]:
        st.metric("Occupied", occupied_count, delta=None)
    
    with status_cols[2]:
        st.metric("Total Tables", total_count, delta=None)

if __name__ == "__main__":
    main()
