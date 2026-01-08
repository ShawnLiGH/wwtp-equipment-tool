"""
WWTP Equipment Tool - Main Application
Streamlit web interface for wastewater treatment plant equipment management
"""

import streamlit as st
import os
from database import create_database, Database
from database import models

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="WWTP Equipment Tool",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# INITIALIZE DATABASE
# ============================================
DB_PATH = 'database/wwtp_equipment.db'

@st.cache_resource
def init_database():
    """Initialize database connection (cached)"""
    if not os.path.exists(DB_PATH):
        create_database(DB_PATH)
    db = Database(DB_PATH)
    db.connect()
    return db

db = init_database()

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'active_project_id' not in st.session_state:
    st.session_state.active_project_id = None

if 'active_project_name' not in st.session_state:
    st.session_state.active_project_name = None

# ============================================
# SIDEBAR - PROJECT SELECTOR
# ============================================
with st.sidebar:
    st.title("🏭 WWTP Equipment Tool")
    st.markdown("---")
    
    # Active Project Display
    st.subheader("Active Project")
    
    projects = models.get_all_projects(db)
    
    if projects:
        project_options = {f"{p['name']} ({p['job_number'] or 'No Job #'})": p['project_id'] 
                          for p in projects}
        project_options = {"[No Project Selected]": None, **project_options}
        
        # Get current selection index
        current_selection = "[No Project Selected]"
        if st.session_state.active_project_id:
            for key, value in project_options.items():
                if value == st.session_state.active_project_id:
                    current_selection = key
                    break
        
        selected_project = st.selectbox(
            "Select Project:",
            options=list(project_options.keys()),
            index=list(project_options.keys()).index(current_selection),
            key="project_selector"
        )
        
        st.session_state.active_project_id = project_options[selected_project]
        
        if st.session_state.active_project_id:
            project = models.get_project(db, st.session_state.active_project_id)
            st.session_state.active_project_name = project['name']
            
            st.success(f"✅ **{project['name']}**")
            st.caption(f"Client: {project['client'] or 'N/A'}")
            st.caption(f"Phase: {project['phase']}")
        else:
            st.session_state.active_project_name = None
            st.info("No project selected")
    else:
        st.session_state.active_project_id = None
        st.session_state.active_project_name = None
        st.info("No projects created yet")
    
    st.markdown("---")
    
    # Database Stats
    st.subheader("📊 Database Stats")
    stats = models.get_database_stats(db)
    st.metric("Equipment Items", stats['equipment_master'])
    st.metric("Total Projects", stats['projects'])
    st.metric("Total Quotes", stats['quotes'])
    st.metric("Documents", stats['documents'])

# ============================================
# MAIN CONTENT - TABS
# ============================================
st.title("🏭 Wastewater Treatment Plant Equipment Tool")

tabs = st.tabs([
    "📦 Equipment Master",
    "🏗️ Projects",
    "📋 Equipment List Builder",
    "💰 Cost Estimate",
    "📄 Submittal Generator",
    "⚙️ Settings"
])

# ============================================
# TAB 1: EQUIPMENT MASTER
# ============================================
with tabs[0]:
    st.header("📦 Equipment Master Catalog")
    st.markdown("Manage your equipment database: add, search, edit equipment and attach documents.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Equipment List")
        
        # Search bar
        search_term = st.text_input("🔍 Search Equipment", placeholder="Search by manufacturer, model, or type...")
        
        if search_term:
            equipment_list = models.search_equipment(db, search_term)
        else:
            equipment_list = models.get_all_equipment(db)
        
        if equipment_list:
            st.write(f"**{len(equipment_list)} equipment items found**")
            
            for eq in equipment_list:
                with st.expander(f"**{eq['manufacturer']} {eq['model']}** - {eq['equipment_type']}"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write(f"**Type:** {eq['equipment_type']}")
                        if eq['equipment_subtype']:
                            st.write(f"**Subtype:** {eq['equipment_subtype']}")
                        st.write(f"**Power:** {eq['power_hp']} HP" if eq['power_hp'] else "**Power:** N/A")
                        st.write(f"**Flow:** {eq['flow_gpm']} GPM" if eq['flow_gpm'] else "**Flow:** N/A")
                    
                    with col_b:
                        st.write(f"**Head:** {eq['head_ft']} ft" if eq['head_ft'] else "**Head:** N/A")
                        st.write(f"**Voltage:** {eq['voltage']}" if eq['voltage'] else "**Voltage:** N/A")
                        st.write(f"**RPM:** {eq['rpm']}" if eq['rpm'] else "**RPM:** N/A")
                    
                    if eq['notes']:
                        st.info(f"📝 {eq['notes']}")
                    
                    # Show documents count
                    docs = models.get_equipment_documents(db, eq['equipment_id'])
                    quotes = models.get_equipment_quotes(db, eq['equipment_id'])
                    st.caption(f"📄 {len(docs)} documents | 💰 {len(quotes)} quotes")
        else:
            st.info("No equipment found. Add your first equipment item!")
    
    with col2:
        st.subheader("➕ Add New Equipment")
        
        with st.form("add_equipment_form", clear_on_submit=True):
            manufacturer = st.text_input("Manufacturer*", placeholder="e.g., Wilo")
            model = st.text_input("Model*", placeholder="e.g., EMU FA 10.37-252")
            equipment_type = st.selectbox("Equipment Type*", 
                                         ["Pump", "Mixer", "Blower", "Screen", "Valve", 
                                          "Instrumentation", "Other"])
            equipment_subtype = st.text_input("Subtype", placeholder="e.g., Submersible")
            
            col_x, col_y = st.columns(2)
            with col_x:
                power_hp = st.number_input("Power (HP)", min_value=0.0, step=0.1, format="%.2f")
                flow_gpm = st.number_input("Flow (GPM)", min_value=0.0, step=1.0, format="%.1f")
                voltage = st.text_input("Voltage", placeholder="e.g., 460V")
            
            with col_y:
                head_ft = st.number_input("Head (ft)", min_value=0.0, step=1.0, format="%.1f")
                rpm = st.number_input("RPM", min_value=0.0, step=1.0, format="%.0f")
            
            notes = st.text_area("Notes", placeholder="Additional specifications or notes...")
            
            submit = st.form_submit_button("Add Equipment", type="primary")
            
            if submit:
                if not manufacturer or not model or not equipment_type:
                    st.error("Please fill in all required fields (*)")
                else:
                    try:
                        eq_id = models.create_equipment(
                            db, manufacturer, model, equipment_type,
                            equipment_subtype=equipment_subtype if equipment_subtype else None,
                            power_hp=power_hp if power_hp > 0 else None,
                            flow_gpm=flow_gpm if flow_gpm > 0 else None,
                            head_ft=head_ft if head_ft > 0 else None,
                            voltage=voltage if voltage else None,
                            rpm=rpm if rpm > 0 else None,
                            notes=notes if notes else None
                        )
                        st.success(f"✅ Equipment added successfully! (ID: {eq_id})")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding equipment: {e}")

# ============================================
# TAB 2: PROJECTS
# ============================================
with tabs[1]:
    st.header("🏗️ Project Management")
    st.markdown("Create and manage wastewater treatment plant projects.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Existing Projects")
        
        if projects:
            for proj in projects:
                with st.expander(f"**{proj['name']}** - {proj['phase']}", expanded=False):
                    st.write(f"**Client:** {proj['client'] or 'N/A'}")
                    st.write(f"**Job Number:** {proj['job_number'] or 'N/A'}")
                    st.write(f"**Phase:** {proj['phase']}")
                    st.write(f"**Created:** {proj['created_date']}")
                    
                    if proj['notes']:
                        st.info(f"📝 {proj['notes']}")
                    
                    # Show project equipment count
                    eq_list = models.get_project_equipment_list(db, proj['project_id'])
                    st.caption(f"📋 {len(eq_list)} equipment items in this project")
        else:
            st.info("No projects created yet. Create your first project!")
    
    with col2:
        st.subheader("➕ Create New Project")
        
        with st.form("create_project_form", clear_on_submit=True):
            name = st.text_input("Project Name*", placeholder="e.g., Rio Del Oro WWTP Upgrade")
            client = st.text_input("Client", placeholder="e.g., City of Sacramento")
            job_number = st.text_input("Job Number", placeholder="e.g., 2024-1234")
            phase = st.selectbox("Phase", ["Design", "Bid", "Construction", "Closeout"])
            notes = st.text_area("Notes", placeholder="Project description or notes...")
            
            submit = st.form_submit_button("Create Project", type="primary")
            
            if submit:
                if not name:
                    st.error("Project name is required")
                else:
                    try:
                        proj_id = models.create_project(
                            db, name, client if client else None,
                            job_number if job_number else None,
                            phase, notes if notes else None
                        )
                        st.success(f"✅ Project created successfully! (ID: {proj_id})")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating project: {e}")

# ============================================
# TAB 3: EQUIPMENT LIST BUILDER
# ============================================
with tabs[2]:
    st.header("📋 Equipment List Builder")
    
    if not st.session_state.active_project_id:
        st.warning("⚠️ Please select a project from the sidebar first.")
    else:
        st.markdown(f"**Building equipment list for:** {st.session_state.active_project_name}")
        
        # Show current project equipment
        project_equipment = models.get_project_equipment_list(db, st.session_state.active_project_id)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Project Equipment List")
            
            if project_equipment:
                st.write(f"**{len(project_equipment)} equipment items**")
                
                for pe in project_equipment:
                    status_emoji = {
                        'new': '🆕',
                        'existing': '📦',
                        'replace': '🔄',
                        'remove': '🗑️',
                        'TBD': '❓'
                    }
                    
                    with st.expander(f"{status_emoji.get(pe['status'], '📌')} **{pe['pid_tag'] or 'No Tag'}** - {pe['manufacturer']} {pe['model']}"):
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.write(f"**Status:** {pe['status']}")
                            st.write(f"**Quantity:** {pe['quantity']}")
                            st.write(f"**Location:** {pe['location'] or 'N/A'}")
                        
                        with col_b:
                            st.write(f"**Type:** {pe['equipment_type']}")
                            st.write(f"**Power:** {pe['power_hp']} HP" if pe['power_hp'] else "**Power:** N/A")
                            st.write(f"**Flow:** {pe['flow_gpm']} GPM" if pe['flow_gpm'] else "**Flow:** N/A")
                        
                        with col_c:
                            if pe['vendor']:
                                st.write(f"**Vendor:** {pe['vendor']}")
                                st.write(f"**Price:** ${pe['price']:,.2f}" if pe['price'] else "**Price:** N/A")
                                st.write(f"**Lead Time:** {pe['lead_time_weeks']} weeks" if pe['lead_time_weeks'] else "**Lead Time:** N/A")
                            else:
                                st.write("**Quote:** Not assigned")
                        
                        if pe['instance_notes']:
                            st.info(f"📝 {pe['instance_notes']}")
            else:
                st.info("No equipment added to this project yet. Add equipment from the master catalog!")
        
        with col2:
            st.subheader("➕ Add Equipment to Project")
            
            equipment_list = models.get_all_equipment(db)
            
            if equipment_list:
                with st.form("add_to_project_form", clear_on_submit=True):
                    # Equipment selector
                    eq_options = {f"{eq['manufacturer']} {eq['model']} ({eq['equipment_type']})": eq['equipment_id'] 
                                 for eq in equipment_list}
                    
                    selected_eq = st.selectbox("Select Equipment*", options=list(eq_options.keys()))
                    equipment_id = eq_options[selected_eq]
                    
                    # P&ID Tag
                    pid_tag = st.text_input("P&ID Tag*", placeholder="e.g., P-101")
                    
                    # Status
                    status = st.selectbox("Status*", ["new", "existing", "replace", "remove", "TBD"])
                    
                    # Quantity
                    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
                    
                    # Location
                    location = st.text_input("Location", placeholder="e.g., MBR Building")
                    
                    # Notes
                    notes = st.text_area("Notes", placeholder="Installation notes or special requirements...")
                    
                    # Quote selection (optional)
                    quotes = models.get_equipment_quotes(db, equipment_id)
                    if quotes:
                        quote_options = {f"{q['vendor']} - ${q['price']:,.2f}": q['quote_id'] 
                                        for q in quotes if q['price']}
                        quote_options = {"[No Quote Selected]": None, **quote_options}
                        selected_quote = st.selectbox("Select Quote", options=list(quote_options.keys()))
                        selected_quote_id = quote_options[selected_quote]
                    else:
                        st.caption("No quotes available for this equipment")
                        selected_quote_id = None
                    
                    submit = st.form_submit_button("Add to Project", type="primary")
                    
                    if submit:
                        if not pid_tag:
                            st.error("P&ID Tag is required")
                        else:
                            try:
                                instance_id = models.add_equipment_to_project(
                                    db, st.session_state.active_project_id, equipment_id,
                                    pid_tag, status, quantity,
                                    location if location else None,
                                    notes if notes else None,
                                    selected_quote_id
                                )
                                st.success(f"✅ Equipment added to project! (Instance ID: {instance_id})")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error adding equipment to project: {e}")
            else:
                st.warning("No equipment in master catalog. Add equipment first in the Equipment Master tab.")

# ============================================
# TAB 4: COST ESTIMATE
# ============================================
with tabs[3]:
    st.header("💰 Project Cost Estimate")
    
    if not st.session_state.active_project_id:
        st.warning("⚠️ Please select a project from the sidebar first.")
    else:
        st.markdown(f"**Cost estimate for:** {st.session_state.active_project_name}")
        
        st.info("🚧 Cost estimate generation will be implemented in Phase 4")
        st.markdown("""
        **Planned features:**
        - Summary by equipment type
        - Line items with unit price × quantity
        - Subtotals and grand total
        - Export to formatted Excel
        - Contingency calculations
        """)

# ============================================
# TAB 5: SUBMITTAL GENERATOR
# ============================================
with tabs[4]:
    st.header("📄 Submittal Package Generator")
    
    if not st.session_state.active_project_id:
        st.warning("⚠️ Please select a project from the sidebar first.")
    else:
        st.markdown(f"**Generate submittals for:** {st.session_state.active_project_name}")
        
        st.info("🚧 Submittal generation will be implemented in Phase 4")
        st.markdown("""
        **Planned features:**
        - Select equipment from project
        - Choose document types (cutsheet/submittal/spec)
        - Generate combined PDF or folder structure
        - Create transmittal cover sheet
        - Batch export capabilities
        """)

# ============================================
# TAB 6: SETTINGS
# ============================================
with tabs[5]:
    st.header("⚙️ Settings")
    
    st.subheader("Database Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Database Location:**")
        st.code(os.path.abspath(DB_PATH))
        
        st.write("**Database Size:**")
        if os.path.exists(DB_PATH):
            size_bytes = os.path.getsize(DB_PATH)
            size_kb = size_bytes / 1024
            st.write(f"{size_kb:.2f} KB")
    
    with col2:
        st.write("**Actions:**")
        
        if st.button("🔄 Reload Database Stats", type="secondary"):
            st.cache_resource.clear()
            st.rerun()
        
        st.warning("⚠️ Danger Zone")
        if st.button("🗑️ Reset Database (Delete All Data)", type="secondary"):
            st.error("This feature requires confirmation dialog (to be implemented)")
    
    st.markdown("---")
    
    st.subheader("File Storage")
    st.write("**PDF Storage Location:**")
    st.code("data/files/")
    
    st.write("**Export Location:**")
    st.code("exports/")
    
    st.markdown("---")
    
    st.subheader("About")
    st.write("**WWTP Equipment Tool** - Version 0.1.0")
    st.write("Internal engineering tool for wastewater treatment plant equipment management")
    st.caption("Built with Streamlit + SQLite")
