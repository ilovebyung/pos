import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- DATABASE FUNCTIONS ---
def get_db_connection():
    return sqlite3.connect('pos_database.db')

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Service_Area (
            service_area_id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            table_shape TEXT,
            capacity INTEGER,
            row_idx INTEGER,
            col_idx INTEGER,    
            status INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT (datetime('now', 'localtime'))
        )
    ''')
    conn.commit()
    conn.close()

def save_layout(layout_dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Service_Area") # Reset layout
    for (r, c), data in layout_dict.items():
        cursor.execute("""
            INSERT INTO Service_Area (description, table_shape, capacity, row_idx, col_idx)
            VALUES (?, ?, ?, ?, ?)
        """, (data['description'], data['table_shape'], data['capacity'], r, c))
    conn.commit()
    conn.close()

def load_layout():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM Service_Area", conn)
    conn.close()
    return df

# --- UI RENDERING ---
def render_table_shape(table_shape, capacity, description=""):
    # Color mapping based on shape
    colors = {"Square": "#ADD8E6", "Circle": "#90EE90", "Rectangular": "#FFB6C1"}
    color = colors.get(table_shape, "gray")
    radius = "50%" if table_shape == "Circle" else "10px"
    
    return f"""
    <div style="background-color: {color}; border-radius: {radius}; 
                border: 1px solid black; padding: 5px; text-align: center; 
                width: 70px; height: 70px; display: flex; flex-direction: column; 
                justify-content: center; align-items: center; font-family: sans-serif; font-size: 10px;">
        <b>Cap: {capacity}</b><br>{description}
    </div>
    """

# --- MAIN APP ---
def main():
    st.set_page_config(layout="wide")
    init_db()

    if 'layout' not in st.session_state:
        st.session_state.layout = {}

    # grid_rows, grid_cols = 5, 5
    st.sidebar.header("Configuration")
    # Changed from number_input to slider and value to 5
    grid_rows = st.sidebar.slider("Grid Rows", min_value=1, max_value=20, value=5)
    grid_cols = st.sidebar.slider("Grid Columns", min_value=1, max_value=20, value=5)

    # SIDEBAR: Add Table
    st.sidebar.subheader("Add Table")
    selected_shape = st.sidebar.selectbox("Table Shape", ["Rectangular", "Circle"])
    # selected_capacity = st.sidebar.number_input("Capacity", min_value=1, value=2)
    selected_capacity = st.sidebar.number_input("Capacity", min_value=1, max_value=10, value=2)
    selected_description = st.sidebar.text_input("Description", "") # Requirement: description field

    def toggle_table(r, c):
        if (r, c) in st.session_state.layout:
            del st.session_state.layout[(r, c)]
        else:
            # Fix: Now saving description to session state to prevent KeyError
            st.session_state.layout[(r, c)] = {
                "table_shape": selected_shape,
                "capacity": selected_capacity,
                "description": selected_description
            }

    # Grid Editor Workspace
    # st.subheader("Edit Floor Plan")
    st.info("Click a cell to place the selected table shape. Click again to remove it.")  
    
    for r in range(grid_rows):
        cols = st.columns(grid_cols)
        for c in range(grid_cols):
            with cols[c]:
                table_data = st.session_state.layout.get((r, c))
                if table_data:
                    # Display shape and capacity on the button [1]
                    btn_label = f"{table_data['table_shape']}\n({table_data['capacity']})"
                    if st.button(btn_label, key=f"btn_{r}_{c}"):
                        toggle_table(r, c)
                        st.rerun()
                else:
                    if st.button("[ + ]", key=f"empty_{r}_{c}"):
                        toggle_table(r, c)
                        st.rerun()  
    st.divider()

    # Save and Preview Controls
    col_save, col_preview = st.columns([1, 5])
    with col_save:
        if st.button("Save Layout"):
            save_layout(st.session_state.layout)
            st.success("Layout Saved!")

    with col_preview:
        show_layout = st.toggle("Show Layout Preview")

    # VISUAL LAYOUT PREVIEW PANEL
    if show_layout:
        st.subheader("Visual Layout Preview")
        for r in range(grid_rows):
            cols = st.columns(grid_cols)
            for c in range(grid_cols):
                with cols[c]:
                    table_data = st.session_state.layout.get((r, c))
                    if table_data:
                        # Fix: Pass description to the render function [1]
                        st.markdown(
                            render_table_shape(
                                table_data['table_shape'], 
                                table_data['capacity'], 
                                table_data.get('description', '')
                            ), 
                            unsafe_allow_html=True
                        )
                    else:
                        st.write("")  

    # if st.checkbox("Show Database Table"):
    #     st.table(load_layout())

if __name__ == "__main__":
    main()