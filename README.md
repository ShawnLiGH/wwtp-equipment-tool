# WWTP Equipment Tool

A Streamlit-based web application for managing wastewater treatment plant (WWTP) equipment databases, project equipment lists, cost estimates, and submittal packages.

## Features

- **📦 Equipment Master Catalog**: Centralized database of pumps, mixers, blowers, and other WWTP equipment
- **🏗️ Project Management**: Create and manage multiple WWTP projects
- **📋 Equipment List Builder**: Build project-specific equipment lists with P&ID tags
- **💰 Cost Estimates**: Generate cost summaries based on equipment quotes (Coming in Phase 4)
- **📄 Submittal Packages**: Create submittal document packages (Coming in Phase 4)

## Tech Stack

- **Frontend**: Streamlit
- **Database**: SQLite
- **Data Processing**: pandas
- **Document Generation**: openpyxl, PyPDF2, python-docx

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd wwtp-equipment-tool
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create required directories**
```bash
mkdir -p data/files exports database
```

5. **Initialize database**
```bash
python database/schema.py
```

## Running the Application

### Local Development

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy!

## Project Structure

```
wwtp-equipment-tool/
│
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
│
├── database/
│   ├── __init__.py                 # Package init
│   ├── schema.py                   # SQLite schema definition
│   ├── models.py                   # Database CRUD operations
│   └── wwtp_equipment.db           # SQLite database (auto-created)
│
├── modules/                        # Future: Business logic modules
│   ├── __init__.py
│   ├── equipment_master.py         # Equipment operations
│   ├── project_manager.py          # Project operations
│   ├── cost_estimator.py           # Cost calculations
│   ├── submittal_generator.py      # PDF generation
│   └── utils.py                    # Helper functions
│
├── data/
│   └── files/                      # PDF storage (gitignored)
│       └── equipment_XXX/          # Equipment-specific folders
│           ├── cutsheet.pdf
│           └── submittal.pdf
│
└── exports/                        # Generated deliverables (gitignored)
    ├── equipment_lists/
    ├── cost_estimates/
    └── submittals/
```

## Database Schema

The application uses SQLite with 5 main tables:

1. **projects** - WWTP projects (client, job number, phase)
2. **equipment_master** - Equipment catalog (manufacturer, model, specs)
3. **project_equipment** - Project-specific equipment instances (P&ID tags, status)
4. **quotes** - Equipment pricing and quotes
5. **documents** - File metadata for PDFs (cut sheets, specs, submittals)

## Usage

### 1. Add Equipment to Master Catalog

1. Go to **Equipment Master** tab
2. Fill in equipment details (manufacturer, model, type, specs)
3. Click "Add Equipment"

### 2. Create a Project

1. Go to **Projects** tab
2. Enter project details (name, client, job number, phase)
3. Click "Create Project"

### 3. Build Equipment List

1. Select your project from the sidebar
2. Go to **Equipment List Builder** tab
3. Select equipment from master catalog
4. Assign P&ID tag and status (new/existing/replace/remove)
5. Set quantity and location
6. Link to a quote if available
7. Click "Add to Project"

### 4. Generate Cost Estimate (Coming in Phase 4)

1. Select project
2. Go to **Cost Estimate** tab
3. Configure filters and options
4. Export to Excel

### 5. Create Submittal Package (Coming in Phase 4)

1. Select project
2. Go to **Submittal Generator** tab
3. Select equipment and document types
4. Generate PDF package

## Development Roadmap

### ✅ Phase 1: Foundation (Week 1)
- [x] Database schema and models
- [x] Basic Streamlit UI with tabs
- [x] Project and equipment CRUD operations

### 🔄 Phase 2: Equipment Master (Week 2)
- [ ] File upload functionality for PDFs
- [ ] Quote management interface
- [ ] Equipment search and filtering
- [ ] Edit/delete operations

### ⏳ Phase 3: Project Management (Week 3)
- [ ] Enhanced project equipment interface
- [ ] Quote linking and selection
- [ ] Data validation and error handling

### ⏳ Phase 4: Deliverable Generation (Week 4)
- [ ] Equipment list Excel export
- [ ] Cost estimate calculations and formatting
- [ ] PDF submittal package generation
- [ ] Transmittal cover sheet

### ⏳ Phase 5: Polish (Week 5)
- [ ] Professional Excel templates
- [ ] Database backup/restore
- [ ] Enhanced UI/UX
- [ ] Documentation and testing

## Contributing

This is an internal tool for single-user demonstration purposes. For questions or suggestions, contact the development team.

## License

Internal use only - not for public distribution.

## Support

For issues or feature requests, please contact:
- Email: [your-email]
- GitHub Issues: [repo-url]/issues

---

**Version**: 0.1.0 (Phase 1 - Foundation)  
**Last Updated**: January 2026
