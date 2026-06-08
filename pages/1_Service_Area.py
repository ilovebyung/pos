import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database import get_db_connection
from utils.style import load_css 

# Page configuration
st.set_page_config(
    # page_title="Service Area - POS System",
    # page_icon="🍽️",
    layout="wide"
)

# --- DATABASE FUNCTIONS ---
def get_service_area_layout():
    """Fetch the full service area grid layout from the database"""
    conn = get_db_connection()
    # Fetching all columns including positional grid data
    df = pd.read_sql_query("SELECT * FROM Service_Area", conn)
    conn.close()
    return df

def update_service_area_status(service_area_id):
    """Update service area status to occupied (1)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute(
        'UPDATE Service_Area SET status = 1, timestamp = ? WHERE service_area_id = ?',
        (timestamp, service_area_id)
    )
    conn.commit()
    conn.close()

def reset_specific_service_area(service_area_id):
    """Reset specific service area status to available (0)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Service_Area SET status = 0, timestamp = NULL WHERE service_area_id = ?', (service_area_id,))
    conn.commit()
    conn.close()

# --- UI RENDERING FOR PREVIEW ---
def render_table_shape(table_shape, capacity, description, status):
    """Generates custom HTML styling reflecting table shapes and occupancy status"""
    # Dynamic coloring depending on availability vs occupancy
    if status == 1:
        color = "#FF4B4B"  # Soft Red for Occupied
        text_color = "white"
    else:
        colors = {"Square": "#ADD8E6", "Circle": "#90EE90", "Rectangular": "#FFB6C1"}
        color = colors.get(table_shape, "#E6E6E6")
        text_color = "black"
        
    radius = "50%" if table_shape == "Circle" else "10px"
    
    return f"""
    <div style="background-color: {color}; border-radius: {radius}; 
                border: 2px solid #333333; padding: 5px; text-align: center; 
                width: 85px; height: 85px; display: flex; flex-direction: column; 
                justify-content: center; align-items: center; font-family: sans-serif; 
                font-size: 11px; color: {text_color}; font-weight: bold; margin: auto;">
        <span>{description if description else f"Table"}</span>
        <span style="font-size: 9px; opacity: 0.8;">Cap: {capacity}</span>
        <span style="font-size: 9px;">{'(OCCUPIED)' if status == 1 else '(Vacant)'}</span>
    </div>
    """

# --- MAIN APP ---
load_css()
# st.title("🍽️ Service Area Selection")
# st.markdown("### Please select an available table or seating area")

# Load configuration grid metadata
layout_df = get_service_area_layout()

if not layout_df.empty:
    # Safely determine the required dimensions of our grid
    grid_rows = int(layout_df['row_idx'].max() + 1)
    grid_cols = int(layout_df['col_idx'].max() + 1)
    
    # Map coordinates to fast lookup dictionaries
    layout_dict = {}
    occupied_areas = []
    available_count = 0
    occupied_count = 0
    
    for _, row in layout_df.iterrows():
        r, c = int(row['row_idx']), int(row['col_idx'])
        layout_dict[(r, c)] = row
        
        # Track statistics & tracking lists
        if row['status'] == 1:
            occupied_areas.append(row)
            occupied_count += 1
        else:
            available_count += 1

    # --- GRID LAYOUT GENERATION ---
    for r in range(grid_rows):
        cols = st.columns(grid_cols)
        for c in range(grid_cols):
            with cols[c]:
                table_data = layout_dict.get((r, c))
                if table_data is not None:
                    # Render CSS Mockup HTML above the execution button
                    st.markdown(
                        render_table_shape(
                            table_data['table_shape'], 
                            int(table_data['capacity']), 
                            table_data['description'],
                            int(table_data['status'])
                        ), 
                        unsafe_allow_html=True
                    )
                    
                    service_area_id = table_data['service_area_id']
                    
                    # Add execution buttons beneath the custom styled preview shapes
                    if int(table_data['status']) == 0:
                        if st.button("🪑 Seat", key=f"seat_{r}_{c}", use_container_width=True, type="secondary"):
                            update_service_area_status(service_area_id)
                            st.session_state.selected_service_area = service_area_id
                            st.switch_page("pages/2_Order.py")
                    else:
                        st.button("🔴 Busy", key=f"busy_{r}_{c}", disabled=True, use_container_width=True)
                else:
                    st.write("") # Keep layout alignment intact for empty structural grid elements
else:
    st.warning("No configuration layout found. Use the layout builder page to initialize tables.")
    available_count, occupied_count = 0, 0
    occupied_areas = []

st.markdown("---")

# --- RESET CONSOLE COMPONENT ---
col_legend, col_reset = st.columns([3, 1])

with col_legend:
        st.markdown(f"**Summary:** {available_count} available, {occupied_count} occupied")

with col_reset:
    # st.markdown("#### Select Service Area to Reset:")
    
    if occupied_areas:
        dropdown_options = {}
        dropdown_display = []
        
        for area in occupied_areas:
            display_text = f"ID {area['service_area_id']} - {area['description'] if area['description'] else 'Table'}"
            dropdown_display.append(display_text)
            dropdown_options[display_text] = area['service_area_id']
        
        selected_option = st.selectbox(
            "Choose a service area to reset:",
            [None] + dropdown_display,
            format_func=lambda x: "Select..." if x is None else x,
            key="reset_dropdown"
        )
        
        if selected_option:
            if st.button("⭕ Confirm Reset", type="primary", use_container_width=True):
                selected_id = dropdown_options[selected_option]
                reset_specific_service_area(selected_id)
                st.success(f"Service area {selected_id} has been reset!")
                st.rerun()
    else:
        st.info("No occupied service areas to reset.")


