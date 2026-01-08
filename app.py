"""
WWTP Equipment Management Tool
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Import database managers
from database import (
    create_schema,
    ProjectManager,
    EquipmentManager,
    ProjectEquipmentManager,
    QuoteManager,
    DocumentManager
)

# Page configuration
st.set_page_config(
    page_title="WWTP Equipment Tool",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on first run
@st.cache_resource
def init_database():
    """Initialize database and return managers"""
    create_schema()
    return {
        'project': ProjectManager(),
        'equipment': EquipmentManager(),
        'project_equipment': ProjectEquipmentManager(),
        'quote': QuoteManager(),
        'document': DocumentManager()
    }

# Load database managers
db = init_database()

# Initialize session state
if 'active_project_id' not in st.session_state:
    st.session_state.active_project_id = None

# ============================================================================
# SIDEBAR - PROJECT SELECTOR
# ============================================================================

with st.sidebar:
    st.title("🏭 WWTP Equipment Tool")
    st.markdown("---")
    
    # Project selector
    st.subheader("Active Project")
    projects = db['project'].get_all_projects()
    
    if projects:
        project_options = {p['project_id']: f"{p['name']} ({p['job_number'] or 'No Job #'})" 
                          for p in projects}
        
        selected_project_id = st.selectbox(
            "Select Project",
            options=list(project_options.keys()),
            format_func=lambda x: project_options[x],
            index=list(project_options.keys()).index(st.session_state.active_project_id) 
                  if st.session_state.active_project_id in project_options else 0
        )
        
        if selected_project_id != st.session_state.active_project_id:
            st.session_state.active_project_id = selected_project_id
            st.rerun()
        
        # Display active project info
        if st.session_state.active_project_id:
            active_project = db['project'].get_project(st.session_state.active_project_id)
            st.success(f"**{active_project['name']}**")
            if active_project['client']:
                st.caption(f"Client: {active_project['client']}")
            if active_project['phase']:
                st.caption(f"Phase: {active_project['phase']}")
    else:
        st.info("No projects yet. Create one in the Projects tab.")
    
    st.markdown("---")
    
    # Quick stats
    if st.session_state.active_project_id:
        equipment_count = len(db['project_equipment'].get_project_equipment(
            st.session_state.active_project_id
        ))
        st.metric("Equipment Items", equipment_count)
    
    # Database info
    st.markdown("---")
    st.caption("**Database Status**")
    total_equipment = len(db['equipment'].get_all_equipment())
    st.caption(f"📦 Equipment Master: {total_equipment} items")
    st.caption(f"🏗️ Projects: {len(projects)} active")

# ============================================================================
# MAIN TABS
# ============================================================================

tabs = st.tabs([
    "📦 Equipment Master",
    "🏗️ Projects",
    "📋 Equipment List Builder",
    "💰 Cost Estimate",
    "📄 Submittal Generator",
    "⚙️ Settings"
])

# ============================================================================
# TAB 1: EQUIPMENT MASTER
# ============================================================================

with tabs[0]:
    st.header("📦 Equipment Master Catalog")
    st.markdown("Manage your equipment database with specifications, documents, and pricing.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Equipment List")
        
        # Search and filter
        search_term = st.text_input("🔍 Search equipment", placeholder="Enter manufacturer, model, or type...")
        
        if search_term:
            equipment_list = db['equipment'].search_equipment(search_term)
        else:
            equipment_list = db['equipment'].get_all_equipment()
        
        if equipment_list:
            # Convert to DataFrame for display
            df = pd.DataFrame(equipment_list)
            
            # Select key columns for display
            display_cols = ['equipment_id', 'manufacturer', 'model', 'equipment_type', 
                          'power_hp', 'flow_gpm', 'head_ft', 'voltage']
            display_df = df[[col for col in display_cols if col in df.columns]]
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "equipment_id": "ID",
                    "manufacturer": "Manufacturer",
                    "model": "Model",
                    "equipment_type": "Type",
                    "power_hp": st.column_config.NumberColumn("HP", format="%.1f"),
                    "flow_gpm": st.column_config.NumberColumn("Flow (GPM)", format="%.0f"),
                    "head_ft": st.column_config.NumberColumn("Head (ft)", format="%.1f"),
                    "voltage": "Voltage"
                }
            )
            
            st.caption(f"Showing {len(equipment_list)} equipment items")
        else:
            st.info("No equipment found. Add equipment using the form on the right.")
    
    with col2:
        st.subheader("Add New Equipment")
        
        with st.form("add_equipment_form"):
            manufacturer = st.text_input("Manufacturer*", placeholder="e.g., Wilo")
            model = st.text_input("Model*", placeholder="e.g., EMU KPR 100")
            
            equipment_type = st.selectbox(
                "Equipment Type*",
                options=["Pump", "Mixer", "Blower", "Screen", "Clarifier", "Filter", "Other"]
            )
            
            equipment_subtype = st.text_input("Subtype", placeholder="e.g., Submersible")
            
            st.markdown("**Specifications**")
            col_a, col_b = st.columns(2)
            with col_a:
                power_hp = st.number_input("Power (HP)", min_value=0.0, step=0.1, format="%.2f")
                flow_gpm = st.number_input("Flow (GPM)", min_value=0.0, step=1.0, format="%.0f")
                voltage = st.text_input("Voltage", placeholder="e.g., 480V 3Ph")
            
            with col_b:
                head_ft = st.number_input("Head (ft)", min_value=0.0, step=0.1, format="%.1f")
                rpm = st.number_input("RPM", min_value=0.0, step=1.0, format="%.0f")
                material = st.text_input("Material", placeholder="e.g., Cast Iron")
            
            notes = st.text_area("Notes", placeholder="Additional specifications or comments...")
            
            submit = st.form_submit_button("➕ Add Equipment", use_container_width=True)
            
            if submit:
                if not manufacturer or not model or not equipment_type:
                    st.error("Please fill in required fields (Manufacturer, Model, Type)")
                else:
                    try:
                        equipment_id = db['equipment'].create_equipment(
                            manufacturer=manufacturer,
                            model=model,
                            equipment_type=equipment_type,
                            equipment_subtype=equipment_subtype or None,
                            power_hp=power_hp if power_hp > 0 else None,
                            flow_gpm=flow_gpm if flow_gpm > 0 else None,
                            head_ft=head_ft if head_ft > 0 else None,
                            voltage=voltage or None,
                            rpm=rpm if rpm > 0 else None,
                            material=material or None,
                            notes=notes or None
                        )
                        st.success(f"✓ Equipment added (ID: {equipment_id})")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding equipment: {str(e)}")

# ============================================================================
# TAB 2: PROJECTS
# ============================================================================

with tabs[1]:
    st.header("🏗️ Project Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Projects")
        
        projects = db['project'].get_all_projects()
        
        if projects:
            for project in projects:
                with st.expander(f"**{project['name']}** ({project['job_number'] or 'No Job #'})", 
                               expanded=(project['project_id'] == st.session_state.active_project_id)):
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.caption("**Client**")
                        st.write(project['client'] or "—")
                    
                    with col_b:
                        st.caption("**Phase**")
                        st.write(project['phase'] or "—")
                    
                    with col_c:
                        st.caption("**Created**")
                        st.write(project['created_date'][:10] if project['created_date'] else "—")
                    
                    if project['notes']:
                        st.caption("**Notes**")
                        st.write(project['notes'])
                    
                    # Equipment count
                    eq_count = len(db['project_equipment'].get_project_equipment(project['project_id']))
                    st.info(f"📋 {eq_count} equipment items")
                    
                    # Actions
                    if st.button(f"Set as Active Project", key=f"activate_{project['project_id']}"):
                        st.session_state.active_project_id = project['project_id']
                        st.rerun()
        else:
            st.info("No projects yet. Create your first project using the form on the right.")
    
    with col2:
        st.subheader("Create New Project")
        
        with st.form("create_project_form"):
            name = st.text_input("Project Name*", placeholder="e.g., Rio Del Oro WWTP Upgrade")
            client = st.text_input("Client", placeholder="e.g., City of Sacramento")
            job_number = st.text_input("Job Number", placeholder="e.g., 2025-001")
            phase = st.selectbox("Phase", options=["Design", "Bid", "Construction", "Closeout"])
            notes = st.text_area("Notes", placeholder="Project description or special requirements...")
            
            submit = st.form_submit_button("➕ Create Project", use_container_width=True)
            
            if submit:
                if not name:
                    st.error("Please enter a project name")
                else:
                    try:
                        project_id = db['project'].create_project(
                            name=name,
                            client=client or None,
                            job_number=job_number or None,
                            phase=phase,
                            notes=notes or None
                        )
                        st.success(f"✓ Project created (ID: {project_id})")
                        st.session_state.active_project_id = project_id
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating project: {str(e)}")

# ============================================================================
# TAB 3: EQUIPMENT LIST BUILDER
# ============================================================================

with tabs[2]:
    st.header("📋 Equipment List Builder")
    
    if not st.session_state.active_project_id:
        st.warning("⚠️ Please select or create a project first (see Projects tab)")
    else:
        active_project = db['project'].get_project(st.session_state.active_project_id)
        st.info(f"Building equipment list for: **{active_project['name']}**")
        
        # Get current project equipment
        project_equipment = db['project_equipment'].get_project_equipment(
            st.session_state.active_project_id
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("Project Equipment")
            
            if project_equipment:
                df = pd.DataFrame(project_equipment)
                
                # Display key columns
                display_cols = ['pid_tag', 'manufacturer', 'model', 'equipment_type', 
                              'status', 'quantity', 'location', 'price']
                display_df = df[[col for col in display_cols if col in df.columns]]
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "pid_tag": "P&ID Tag",
                        "manufacturer": "Manufacturer",
                        "model": "Model",
                        "equipment_type": "Type",
                        "status": "Status",
                        "quantity": st.column_config.NumberColumn("Qty", format="%d"),
                        "location": "Location",
                        "price": st.column_config.NumberColumn("Unit Price", format="$%.2f")
                    }
                )
                
                st.caption(f"Total: {len(project_equipment)} equipment items")
            else:
                st.info("No equipment added yet. Use the form to add equipment from the master catalog.")
        
        with col2:
            st.subheader("Add Equipment")
            
            # Get equipment master list
            equipment_list = db['equipment'].get_all_equipment()
            
            if equipment_list:
                equipment_options = {
                    e['equipment_id']: f"{e['manufacturer']} {e['model']} ({e['equipment_type']})"
                    for e in equipment_list
                }
                
                with st.form("add_project_equipment"):
                    selected_equipment_id = st.selectbox(
                        "Select Equipment",
                        options=list(equipment_options.keys()),
                        format_func=lambda x: equipment_options[x]
                    )
                    
                    pid_tag = st.text_input("P&ID Tag*", placeholder="e.g., P-101")
                    
                    status = st.selectbox(
                        "Status",
                        options=["new", "existing", "replace", "remove", "TBD"]
                    )
                    
                    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
                    location = st.text_input("Location", placeholder="e.g., Pump Room A")
                    notes = st.text_area("Notes")
                    
                    submit = st.form_submit_button("➕ Add to Project", use_container_width=True)
                    
                    if submit:
                        if not pid_tag:
                            st.error("Please enter a P&ID tag")
                        else:
                            try:
                                instance_id = db['project_equipment'].add_equipment_to_project(
                                    project_id=st.session_state.active_project_id,
                                    equipment_id=selected_equipment_id,
                                    pid_tag=pid_tag,
                                    status=status,
                                    quantity=quantity,
                                    location=location or None,
                                    notes=notes or None
                                )
                                st.success(f"✓ Equipment added to project (ID: {instance_id})")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error adding equipment: {str(e)}")
            else:
                st.warning("No equipment in master catalog. Add equipment in the Equipment Master tab first.")

# ============================================================================
# TAB 4: COST ESTIMATE
# ============================================================================

with tabs[3]:
    st.header("💰 Cost Estimate")
    
    if not st.session_state.active_project_id:
        st.warning("⚠️ Please select a project first")
    else:
        st.info("📊 Cost estimation features coming in Phase 4")
        st.markdown("This tab will generate formatted cost estimates with:")
        st.markdown("- Equipment pricing by category")
        st.markdown("- Quantity × Unit Price calculations")
        st.markdown("- Subtotals and contingencies")
        st.markdown("- Export to formatted Excel")

# ============================================================================
# TAB 5: SUBMITTAL GENERATOR
# ============================================================================

with tabs[4]:
    st.header("📄 Submittal Package Generator")
    
    if not st.session_state.active_project_id:
        st.warning("⚠️ Please select a project first")
    else:
        st.info("📦 Submittal generation features coming in Phase 4")
        st.markdown("This tab will create submittal packages with:")
        st.markdown("- Equipment cut sheets and specifications")
        st.markdown("- Combined PDF or organized folders")
        st.markdown("- Transmittal cover sheets")
        st.markdown("- Automatic document assembly")

# ============================================================================
# TAB 6: SETTINGS
# ============================================================================

with tabs[5]:
    st.header("⚙️ Settings")
    
    st.subheader("Database Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Database Location**")
        from database import get_db_path
        db_path = get_db_path()
        st.code(str(db_path))
        
        st.markdown("**File Storage**")
        file_path = Path("data/files")
        st.code(str(file_path.absolute()))
    
    with col2:
        st.markdown("**Database Statistics**")
        total_projects = len(db['project'].get_all_projects())
        total_equipment = len(db['equipment'].get_all_equipment())
        
        st.metric("Projects", total_projects)
        st.metric("Equipment Master", total_equipment)
    
    st.markdown("---")
    
    st.subheader("Danger Zone")
    st.warning("⚠️ These actions cannot be undone!")
    
    if st.button("🗑️ Reset Database", type="secondary"):
        st.error("Database reset functionality disabled in this version. Use with caution in production.")
    
    st.markdown("---")
    st.caption("WWTP Equipment Tool v1.0 | Phase 1 - Foundation")
