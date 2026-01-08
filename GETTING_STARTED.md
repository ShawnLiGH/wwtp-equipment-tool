# 🚀 GETTING STARTED - WWTP Equipment Tool

## What You Just Received

✅ **Complete Phase 1 implementation** - Foundation ready to use!

**Project Structure:**
```
wwtp-equipment-tool/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Dependencies list
├── README.md                   # Full documentation
├── test_database.py           # Database test script
├── .gitignore                 # Git configuration
│
├── database/
│   ├── schema.py              # Database schema (5 tables)
│   ├── models.py              # CRUD operations
│   └── wwtp_equipment.db      # Database file (created)
│
├── modules/                    # Future business logic
├── data/files/                # PDF storage
└── exports/                   # Generated outputs
```

## 🏃 Quick Start (5 minutes)

### Step 1: Open Terminal/Command Prompt
Navigate to the project folder:
```bash
cd wwtp-equipment-tool
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the App
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📝 What Works Right Now (Phase 1)

### ✅ Equipment Master Tab
- Add equipment with full specifications
- Search and filter equipment
- View equipment catalog

**Try this:**
1. Go to "Equipment Master" tab
2. Fill in the form on the right:
   - Manufacturer: "Wilo"
   - Model: "EMU KPR 150"
   - Type: "Pump"
   - Power: 15 HP
   - Flow: 750 GPM
3. Click "Add Equipment"

### ✅ Projects Tab
- Create new projects
- Track client, job number, phase
- Set active project

**Try this:**
1. Go to "Projects" tab
2. Create a project:
   - Name: "Rio Del Oro WWTP Upgrade"
   - Client: "City of Sacramento"
   - Job Number: "2026-001"
   - Phase: "Design"
3. Click "Create Project"

### ✅ Equipment List Builder Tab
- Add equipment to projects
- Assign P&ID tags
- Set status (new/existing/replace)
- Track quantities and locations

**Try this:**
1. Make sure a project is active (check sidebar)
2. Go to "Equipment List Builder" tab
3. Add equipment:
   - Select equipment from dropdown
   - P&ID Tag: "P-101"
   - Status: "new"
   - Quantity: 2
   - Location: "Pump Station A"
4. Click "Add to Project"

## 🎯 Test It Out (2 minutes)

The project includes a test script that already ran successfully:
```bash
python test_database.py
```

This verifies:
- ✓ Equipment can be added
- ✓ Projects can be created
- ✓ Equipment can be assigned to projects
- ✓ Database queries work correctly

## 📊 Database Overview

**5 Core Tables:**
1. **projects** - Your WWTP projects
2. **equipment_master** - Equipment catalog
3. **project_equipment** - Equipment assigned to projects
4. **quotes** - Equipment pricing (ready for Phase 4)
5. **documents** - Document management (ready for Phase 4)

**Database File:** `database/wwtp_equipment.db`
- SQLite format (no server needed)
- Portable (copy the whole folder)
- Backed up with the project

## 🔄 What's Coming Next

### Phase 2 (Next Week)
- Document upload functionality
- Quote management interface
- Enhanced equipment editing

### Phase 4 (Week 4)
- 💰 **Cost Estimate Generator** → Excel with pricing
- 📄 **Submittal Package Creator** → Combined PDFs
- 📊 **Professional Excel Exports** → Formatted lists

## 🛠️ Common Tasks

### Reset Database (Start Fresh)
```python
# In Python console
from database import reset_database
reset_database()
```

### Backup Your Data
Just copy the entire `wwtp-equipment-tool/` folder!

### Use Different Port
```bash
streamlit run app.py --server.port 8502
```

## 🐛 Troubleshooting

**Can't import modules?**
- Make sure you're in the `wwtp-equipment-tool` directory
- Run: `pip install -r requirements.txt`

**Port already in use?**
- Try: `streamlit run app.py --server.port 8502`

**Database errors?**
- Delete `database/wwtp_equipment.db`
- Restart the app (it will recreate it)

## 📖 Next Steps

1. **Familiarize yourself** - Click through all tabs
2. **Add your first equipment** - Use real data from your projects
3. **Create a test project** - Practice the workflow
4. **Read the full README.md** - Complete documentation

## 💡 Pro Tips

- **Active Project** in sidebar tracks which project you're working on
- **Search** in Equipment Master filters in real-time
- **P&ID Tags** must be unique per project
- **Status field** helps filter for cost estimates later

## 🎉 You're Ready!

The foundation is solid. Phase 1 gives you:
- ✅ Working database with proper schema
- ✅ Clean, professional UI
- ✅ Core CRUD operations
- ✅ Project and equipment tracking
- ✅ Ready for Phase 2 enhancements

**Questions?** Check the README.md for detailed documentation.

---

**Built for:** Wastewater Engineering
**Phase:** 1 - Foundation ✅
**Status:** Production Ready
