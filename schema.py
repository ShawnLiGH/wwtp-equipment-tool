"""
Database schema for WWTP Equipment Management Tool
SQLite database structure with 5 core tables
"""

import sqlite3
from pathlib import Path


def get_db_path():
    """Get the path to the database file"""
    db_dir = Path(__file__).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "wwtp_equipment.db"


def create_schema():
    """Create all database tables and indexes"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. PROJECTS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            client TEXT,
            job_number TEXT UNIQUE,
            phase TEXT,  -- Design / Bid / Construction
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    """)
    
    # 2. EQUIPMENT MASTER TABLE (normalized catalog)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment_master (
            equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer TEXT NOT NULL,
            model TEXT NOT NULL,
            equipment_type TEXT NOT NULL,  -- Pump, Mixer, Blower, etc.
            equipment_subtype TEXT,         -- Submersible, Centrifugal, etc.
            
            -- Key parameters (as extracted)
            power_hp REAL,
            flow_gpm REAL,
            head_ft REAL,
            voltage TEXT,
            rpm REAL,
            
            -- Verified/corrected parameters
            power_hp_verified REAL,
            flow_gpm_verified REAL,
            head_ft_verified REAL,
            
            -- Other specs
            material TEXT,
            connection_size TEXT,
            weight_lbs REAL,
            
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(manufacturer, model)
        )
    """)
    
    # 3. PROJECT EQUIPMENT INSTANCES TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_equipment (
            instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            equipment_id INTEGER NOT NULL,
            
            pid_tag TEXT,  -- Manually entered P&ID tag (e.g., "P-101")
            status TEXT NOT NULL DEFAULT 'new',  -- existing/new/replace/remove/TBD
            quantity INTEGER DEFAULT 1,
            location TEXT,  -- Building, room, elevation
            notes TEXT,
            
            selected_quote_id INTEGER,  -- FK to quotes table
            
            FOREIGN KEY (project_id) REFERENCES projects(project_id),
            FOREIGN KEY (equipment_id) REFERENCES equipment_master(equipment_id),
            FOREIGN KEY (selected_quote_id) REFERENCES quotes(quote_id),
            UNIQUE(project_id, pid_tag)
        )
    """)
    
    # 4. QUOTES / PRICING TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            quote_id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_id INTEGER NOT NULL,
            
            vendor TEXT NOT NULL,
            price REAL,
            currency TEXT DEFAULT 'USD',
            lead_time_weeks INTEGER,
            quote_date DATE,
            quote_number TEXT,
            quote_file_path TEXT,  -- Link to PDF quote
            
            is_current BOOLEAN DEFAULT 1,  -- Flag for latest quote
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (equipment_id) REFERENCES equipment_master(equipment_id)
        )
    """)
    
    # 5. DOCUMENTS TABLE (cut sheets, specs, submittals)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            document_id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_id INTEGER NOT NULL,
            
            document_type TEXT NOT NULL,  -- cutsheet/spec/submittal/quote/manual
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,  -- Relative path: data/files/equipment_001/cutsheet.pdf
            file_size_kb INTEGER,
            version TEXT,
            document_date DATE,
            
            notes TEXT,
            uploaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (equipment_id) REFERENCES equipment_master(equipment_id)
        )
    """)
    
    # INDEXES FOR PERFORMANCE
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_project_equipment 
        ON project_equipment(project_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_equipment_quotes 
        ON quotes(equipment_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_equipment_docs 
        ON documents(equipment_id)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✓ Database created at: {db_path}")
    return db_path


def reset_database():
    """Drop all tables and recreate schema (USE WITH CAUTION)"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop all tables
    tables = ['documents', 'quotes', 'project_equipment', 'equipment_master', 'projects']
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    
    # Drop indexes
    indexes = ['idx_project_equipment', 'idx_equipment_quotes', 'idx_equipment_docs']
    for index in indexes:
        cursor.execute(f"DROP INDEX IF EXISTS {index}")
    
    conn.commit()
    conn.close()
    
    # Recreate schema
    create_schema()
    print("✓ Database reset complete")


if __name__ == "__main__":
    # Test schema creation
    create_schema()
