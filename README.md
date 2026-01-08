# WWTP Equipment Management Tool

A Streamlit-based application for managing wastewater treatment plant equipment specifications, project tracking, cost estimates, and submittal generation.

## 🎯 Features

### Phase 1 - Foundation (Current)
- ✅ **Equipment Master Catalog** - Centralized database of equipment with specifications
- ✅ **Project Management** - Track multiple WWTP projects
- ✅ **Equipment List Builder** - Assign equipment to projects with P&ID tags
- ✅ **SQLite Database** - Lightweight, file-based storage
- ✅ **Search & Filter** - Find equipment quickly

### Upcoming Phases
- 📋 **Cost Estimation** - Generate formatted cost estimates (Phase 4)
- 📄 **Submittal Generator** - Create equipment submittal packages (Phase 4)
- 📊 **Professional Excel Exports** - Formatted equipment lists and estimates
- 📦 **PDF Management** - Store and organize cut sheets and specifications

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <your-repo-url>
   cd wwtp-equipment-tool
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Activate on Windows:
   venv\Scripts\activate
   
   # Activate on Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**
   - The app will automatically open at `http://localhost:8501`
   - If not, navigate to that URL manually

## 📖 User Guide

### 1. Equipment Master Tab
Add equipment to your master catalog:

**Adding Equipment:**
1. Fill in manufacturer and model (required)
2. Select equipment type (Pump, Mixer, Blower, etc.)
3. Enter specifications (HP, flow, head, voltage)
4. Add any notes
5. Click "Add Equipment"

**Searching:**
- Use the search box to filter by manufacturer, model, or type
- Results update in real-time

### 2. Projects Tab
Manage your WWTP projects:

**Creating a Project:**
1. Enter project name (required)
2. Add client, job number, and phase
3. Add project notes
4. Click "Create Project"

**Setting Active Project:**
- Click "Set as Active Project" on any project
- Active project appears in the sidebar

### 3. Equipment List Builder Tab
Build equipment lists for your active project:

**Adding Equipment to Project:**
1. Ensure a project is active (check sidebar)
2. Select equipment from the master catalog
3. Assign a P&ID tag (e.g., "P-101")
4. Set status (new/existing/replace/remove)
5. Enter quantity and location
6. Click "Add to Project"

**Equipment Status Options:**
- **new** - New equipment to be installed
- **existing** - Equipment already in place
- **replace** - Replacement of existing equipment
- **remove** - Equipment to be removed
- **TBD** - Status to be determined

### 4. Cost Estimate Tab
*Coming in Phase 4* - Will generate formatted cost estimates

### 5. Submittal Generator Tab
*Coming in Phase 4* - Will create submittal packages

### 6. Settings Tab
View database information and statistics

## 🗂️ Project Structure

```
wwtp-equipment-tool/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── database/
│   ├── __init__.py            # Package initialization
│   ├── schema.py              # Database schema definition
│   ├── models.py              # Database CRUD operations
│   └── wwtp_equipment.db      # SQLite database (created on first run)
│
├── modules/
│   └── __init__.py            # Future business logic modules
│
├── data/
│   └── files/                 # PDF storage (organized by equipment ID)
│
└── exports/                   # Generated deliverables
    ├── equipment_lists/
    ├── cost_estimates/
    └── submittals/
```

## 💾 Database Schema

The application uses SQLite with 5 main tables:

1. **projects** - Project information (name, client, job number, phase)
2. **equipment_master** - Equipment catalog (specs, manufacturers, models)
3. **project_equipment** - Equipment instances in projects (P&ID tags, status, quantities)
4. **quotes** - Pricing information for equipment
5. **documents** - Document management (cut sheets, specs, submittals)

## 🔧 Technical Details

### Tech Stack
- **Streamlit** - Web application framework
- **SQLite** - Embedded database
- **pandas** - Data manipulation
- **openpyxl** - Excel file generation

### Database Location
- Database file: `database/wwtp_equipment.db`
- Created automatically on first run
- File-based (no server required)

### Data Storage
- PDF files: `data/files/equipment_<id>/`
- Exports: `exports/` directory
- Organized by equipment ID and document type

## 🐛 Troubleshooting

### Database Issues
If you encounter database errors:
```bash
# Delete the database file to start fresh
rm database/wwtp_equipment.db

# Restart the application
streamlit run app.py
```

### Import Errors
If modules can't be found:
```bash
# Ensure you're in the project directory
cd wwtp-equipment-tool

# Verify requirements are installed
pip install -r requirements.txt
```

### Port Already in Use
If port 8501 is busy:
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

## 📋 Development Roadmap

- [x] **Phase 1** - Foundation (database, basic UI)
- [x] **Phase 2** - Equipment Master (CRUD operations)
- [x] **Phase 3** - Project Management (equipment lists)
- [ ] **Phase 4** - Deliverable Generation (cost estimates, submittals)
- [ ] **Phase 5** - Polish & Enhancements (formatting, validation)

## 🤝 Contributing

This is a custom tool for internal use. For questions or suggestions, contact the project maintainer.

## 📄 License

Internal use only - proprietary software

## 🔗 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [pandas Documentation](https://pandas.pydata.org/docs/)

---

**Version:** 1.0 (Phase 1 - Foundation)  
**Last Updated:** January 2026
