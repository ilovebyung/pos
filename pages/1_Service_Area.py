import streamlit as st
from datetime import datetime
from utils.database import get_db_connection
from utils.style import load_css 

# Page configuration
st.set_page_config(
    page_title="Service Area - POS System",
    page_icon="🍽️",
    layout="wide"
)

# Function to get all service areas
def get_service_areas():
    """Fetch all service areas from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT service_area_id, description, status FROM Service_Area ORDER BY service_area_id')
    areas = cursor.fetchall()
    conn.close()
    return areas

# Function to update service area status
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

# Function to reset specific service area status
def reset_specific_service_area(service_area_id):
    """Reset specific service area status to available (0)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Service_Area SET status = 0, timestamp = NULL WHERE service_area_id = ?', (service_area_id,))
    conn.commit()
    conn.close()

# Function to reset all statuses (for the refresh all button)
def reset_all_statuses():
    """Reset all service area statuses to available (0)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Service_Area SET status = 0, timestamp = NULL')
    conn.commit()
    conn.close()

# Initialize session state for showing dropdown
if 'show_refresh_dropdown' not in st.session_state:
    st.session_state.show_refresh_dropdown = False

# Main page content
load_css()
st.title("🍽️ Service Area Selection")
st.markdown("### Please select a table or seating area")

# Get service areas
service_areas = get_service_areas()

# Create a grid layout for buttons
col1, col2, col3 = st.columns(3)

# Display service area buttons in a grid
for i, area in enumerate(service_areas):
    service_area_id = area['service_area_id']
    description = area['description']
    status = area['status']
    
    # Determine button color based on status
    button_type = "secondary" if status == 0 else "primary"
    button_label = f"{service_area_id} - {description}"
    
    # Distribute buttons across columns
    with [col1, col2, col3][i % 3]:
        # Create button with conditional styling
        if status == 0:  # Available - Blue
            if st.button(
                button_label,
                key=f"area_{service_area_id}",
                type="secondary",
                use_container_width=True
            ):
                # Update status to occupied
                update_service_area_status(service_area_id)
                
                # Store selected service area in session state
                st.session_state.selected_service_area = service_area_id
                
                # Navigate to Order page
                st.switch_page("pages/2_Order.py")
        else:  # Occupied - Different styling
            st.button(
                f"🔴 {service_area_id} - {description} (Occupied)",
                key=f"occupied_area_{service_area_id}",
                disabled=True,
                use_container_width=True
            )

# Add some spacing
st.markdown("---")

# Refresh section
col_refresh1, col_refresh2, col_refresh3 = st.columns([1, 1, 1])
with col_refresh2:
    # Main refresh button
    if st.button("🔁 Reset", type="primary", use_container_width=True):
        st.session_state.show_refresh_dropdown = True
        st.rerun()
    # Show dropdown if refresh button was clicked
    if st.session_state.show_refresh_dropdown:
        st.markdown("#### Select Service Area to Reset:")
        
        # Create options for dropdown
        occupied_areas = [area for area in service_areas if area['status'] == 1]
        
        if occupied_areas:
            # Create dropdown options
            dropdown_options = {}
            dropdown_display = []
            
            # Add "Reset All" option
            dropdown_display.append("Reset All Service Areas")
            dropdown_options["Reset All Service Areas"] = "all"
            
            # Add individual service areas (only occupied ones)
            for area in occupied_areas:
                display_text = f"{area['service_area_id']} - {area['description']}"
                dropdown_display.append(display_text)
                dropdown_options[display_text] = area['service_area_id']
            
            # Create selectbox
            selected_option = st.selectbox(
                "Choose an option:",
                dropdown_display,
                key="refresh_dropdown"
            )
            
            # Create action buttons
            col_action1, col_action2 = st.columns(2)
            
            with col_action1:
                if st.button("⭕ Confirm Reset", type="primary", use_container_width=True):
                    selected_id = dropdown_options[selected_option]
                    
                    if selected_id == "all":
                        reset_all_statuses()
                        st.success("All service areas have been reset!")
                    else:
                        reset_specific_service_area(selected_id)
                        st.success(f"Service area {selected_id} has been reset!")
                    
                    # Hide dropdown and refresh
                    st.session_state.show_refresh_dropdown = False
                    st.rerun()
            
            with col_action2:
                if st.button("❌ Cancel", type="primary", use_container_width=True):
                    st.session_state.show_refresh_dropdown = False
                    st.rerun()
        else:
            st.info("No occupied service areas to reset.")
            if st.button("❌ Close", use_container_width=True):
                st.session_state.show_refresh_dropdown = False
                st.rerun()

# Display status information
st.markdown("### Status Legend")
col_legend1, col_legend2 = st.columns(2)
with col_legend1:
    st.markdown("🟦 **Available** - Ready for seating")
with col_legend2:
    st.markdown("🔴 **Occupied** - Currently in use")

# Optional: Display current status summary
available_count = sum(1 for area in service_areas if area['status'] == 0)
occupied_count = len(service_areas) - available_count
st.markdown(f"**Summary:** {available_count} available, {occupied_count} occupied")