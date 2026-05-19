import streamlit as st
import sqlite3
import pandas as pd

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('layout.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Service_Area (
        service_area_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        description TEXT,
        table_type TEXT, 
        capacity INTEGER, 
        row_idx INTEGER, 
        col_idx INTEGER,    
        status INTEGER DEFAULT 0,
        timestamp DATETIME DEFAULT (datetime('now', 'localtime'))
    );''')
    conn.commit()
    conn.close()

def save_layout(layout_data):
    conn = sqlite3.connect('layout.db')
    c = conn.cursor()
    c.execute("DELETE FROM Service_Area") 
    for item in layout_data:
        c.execute("INSERT INTO Service_Area (table_type, capacity, row_idx, col_idx) VALUES (?, ?, ?, ?)", 
                  (item['type'], item['capacity'], item['row'], item['col']))
    conn.commit()
    conn.close()

def load_layout():
    conn = sqlite3.connect('layout.db')
    df = pd.read_sql_query("SELECT * FROM Service_Area", conn)
    conn.close()
    return df

# --- UI STYLING FOR VISUAL LAYOUT ---
def render_table_shape(table_type, capacity):
    """Returns a styled HTML div representing the table shape"""
    colors = {"Square": "#ADD8E6", "Circle": "#FFB6C1", "Rectangular": "#90EE90"}
    radius = "50%" if table_type == "Circle" else "4px"
    width = "80px" if table_type == "Rectangular" else "60px"
    height = "60px"
    
    style = f"""
    <div style="
        width: {width}; 
        height: {height}; 
        background-color: {colors.get(table_type, '#EEE')}; 
        border: 2px solid #333; 
        border-radius: {radius}; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 12px; 
        font-weight: bold;
        margin: auto;
    ">
        {capacity}
    </div>
    """
    return style

# --- MAIN APP ---
def main():
    st.set_page_config(page_title="Restaurant Layout Designer", layout="wide")
    init_db()

    st.title("🍽️ Restaurant Table Layout Designer")
    
    # Sidebar Configuration
    st.sidebar.header("Configuration")
    grid_rows = st.sidebar.number_input("Grid Rows", min_value=1, max_value=20, value=6)
    grid_cols = st.sidebar.number_input("Grid Columns", min_value=1, max_value=20, value=8)
    
    st.sidebar.subheader("Add Table")
    selected_type = st.sidebar.selectbox("Table Type", ["Square", "Circle", "Rectangular"])
    capacity = st.sidebar.number_input("Capacity", min_value=1, max_value=20, value=2)
    
    if 'layout' not in st.session_state:
        st.session_state.layout = {}

    def toggle_table(r, c):
        if (r, c) in st.session_state.layout:
            del st.session_state.layout[(r, c)]
        else:
            st.session_state.layout[(r, c)] = {"type": selected_type, "capacity": capacity}

    # Grid Editor Workspace
    st.subheader("Edit Floor Plan")
    st.info("Click a cell to place the selected table type. Click an existing table to remove it.")
    
    for r in range(grid_rows):
        cols = st.columns(grid_cols)
        for c in range(grid_cols):
            with cols[c]:
                table_data = st.session_state.layout.get((r, c))
                if table_data:
                    btn_label = f"{table_data['type']}\n({table_data['capacity']})"
                    if st.button(btn_label, key=f"btn_{r}_{c}"):
                        toggle_table(r, c)
                        st.rerun()
                else:
                    if st.button("[ + ]", key=f"empty_{r}_{c}"):
                        toggle_table(r, c)
                        st.rerun()

    st.divider()

    # Action Row: Save and Show Layout Toggle
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("💾 Save Layout", type="primary"):
            data = [{"row": r, "col": c, "type": v['type'], "capacity": v['capacity']} 
                    for (r, c), v in st.session_state.layout.items()]
            save_layout(data)
            st.success("Saved successfully!")
    
    with col2:
        show_layout = st.toggle("👀 Show Layout Preview", value=False)

    # VISUAL LAYOUT PREVIEW PANEL
    if show_layout:
        st.subheader("Visual Layout Preview")
        for r in range(grid_rows):
            cols = st.columns(grid_cols)
            for c in range(grid_cols):
                with cols[c]:
                    table_data = st.session_state.layout.get((r, c))
                    if table_data:
                        st.markdown(render_table_shape(table_data['type'], table_data['capacity']), unsafe_allow_html=True)
                    else:
                        st.write("") 

    if st.checkbox("Show Database Table"):
        st.table(load_layout())

if __name__ == "__main__":
    main()