import streamlit as st
import pandas as pd
from utils.database import get_db_connection

# --- DATABASE FUNCTIONS ---
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

    if 'layout' not in st.session_state:
        st.session_state.layout = {}

    st.sidebar.header("Configuration")
    grid_rows = st.sidebar.slider("Grid Rows", min_value=1, max_value=20, value=5)
    grid_cols = st.sidebar.slider("Grid Columns", min_value=1, max_value=20, value=5)

    st.sidebar.subheader("Add Table")
    selected_shape = st.sidebar.selectbox("Table Shape", ["Rectangular", "Circle"])
    selected_capacity = st.sidebar.number_input("Capacity", min_value=1, max_value=10, value=2)
    selected_description = st.sidebar.text_input("Description", "")

    def toggle_table(r, c):
        if (r, c) in st.session_state.layout:
            del st.session_state.layout[(r, c)]
        else:
            st.session_state.layout[(r, c)] = {
                "table_shape": selected_shape,
                "capacity": selected_capacity,
                "description": selected_description
            }

    st.info("Click a cell to place the selected table shape. Click again to remove it.")  
    
    for r in range(grid_rows):
        cols = st.columns(grid_cols)
        for c in range(grid_cols):
            with cols[c]:
                table_data = st.session_state.layout.get((r, c))
                if table_data:
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
    col_load, col_save, col_preview = st.columns([1,1, 5])
    with col_load:
        if st.button("Load Layout"):
            loaded_df = load_layout()
            
            # FIX 1: Use .empty to check if the DataFrame has records
            if not loaded_df.empty:
                # FIX 2: Convert DataFrame rows back into the dictionary format expected by the app
                parsed_layout = {}
                for _, row in loaded_df.iterrows():
                    r, c = int(row['row_idx']), int(row['col_idx'])
                    parsed_layout[(r, c)] = {
                        "table_shape": row['table_shape'],
                        "capacity": int(row['capacity']),
                        "description": row['description']
                    }
                
                st.session_state.layout = parsed_layout
                st.success("Layout Loaded!")
                st.rerun()  # Force rerun to show updated layout instantly
            else:
                st.warning("No layout found in Service_Area table.")

    with col_save:
        if st.button("Save Layout"):
            save_layout(st.session_state.layout)
            st.success("Layout Saved!")

    with col_preview:
        show_layout = st.toggle("Show Layout Preview")

    if show_layout:
        st.subheader("Visual Layout Preview")
        for r in range(grid_rows):
            cols = st.columns(grid_cols)
            for c in range(grid_cols):
                with cols[c]:
                    table_data = st.session_state.layout.get((r, c))
                    if table_data:
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

if __name__ == "__main__":
    main()