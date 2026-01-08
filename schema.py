"""
WWTP Equipment Tool - Database Schema
SQLite schema definition for equipment management system
"""

import sqlite3
import os

def create_database(db_path='database/wwtp_equipment.db'):
    """
    Create SQLite database with all tables and indexes.
    
    Args:
        db_path: Path to database file (will be created if doesn't exist)
    
    Returns:
        sqlite3.Connection object
    """
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to database (creates file if doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # ========================================
    # TABLE 1: PROJECTS
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            client TEXT,
            job_number TEXT UNIQUE,
            phase TEXT CHECK(phase IN ('Design', 'Bid', 'Construction', 'Closeout')),
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    """)
    
    # ========================================
    # TABLE 2: EQUIPMENT MASTER
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment_master (
            equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer TEXT NOT NULL,
            model TEXT NOT NULL,
            equipment_type TEXT NOT NULL,
            equipment_subtype TEXT,
            
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
            
            -- Other specifications
            material TEXT,
            connection_size TEXT,
            weight_lbs REAL,
            
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(manufacturer, model)
        )
    """)
    
    # ========================================
    # TABLE 3: PROJECT EQUIPMENT INSTANCES
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_equipment (
            instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            equipment_id INTEGER NOT NULL,
            
            pid_tag TEXT,
            status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('existing', 'new', 'replace', 'remove', 'TBD')),
            quantity INTEGER DEFAULT 1,
            location TEXT,
            notes TEXT,
            
            selected_quote_id INTEGER,
            
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
            FOREIGN KEY (equipment_id) REFERENCES equipment_master(equipment_id) ON DELETE RESTRICT,
            FOREIGN KEY (selected_quote_id) REFERENCES quotes(quote_id) ON DELETE SET NULL,
            
            UNIQUE(project_id, pid_tag)
        )
    """)
    
    # ========================================
    # TABLE 4: QUOTES / PRICING
    # ========================================
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
            quote_file_path TEXT,
            
            is_current BOOLEAN DEFAULT 1,
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (equipment_id) REFERENCES equipment_master(equipment_id) ON DELETE CASCADE
        )
    """)
    
    # ========================================
    # TABLE 5: DOCUMENTS
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            document_id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_id INTEGER NOT NULL,
            
            document_type TEXT NOT NULL CHECK(document_type IN ('cutsheet', 'spec', 'submittal', 'quote', 'manual', 'other')),
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size_kb INTEGER,
            version TEXT,
            document_date DATE,
            
            notes TEXT,
            uploaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (equipment_id) REFERENCES equipment_master(equipment_id) ON DELETE CASCADE
        )
    """)
    
    # ========================================
    # INDEXES FOR PERFORMANCE
    # ========================================
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_equipment ON project_equipment(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipment_quotes ON quotes(equipment_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipment_docs ON documents(equipment_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_current_quotes ON quotes(equipment_id, is_current) WHERE is_current = 1")
    
    conn.commit()
    
    print(f"✅ Database created successfully at: {db_path}")
    print(f"📊 Tables created: projects, equipment_master, project_equipment, quotes, documents")
    
    return conn


def reset_database(db_path='database/wwtp_equipment.db'):
    """
    Drop all tables and recreate database (WARNING: deletes all data)
    
    Args:
        db_path: Path to database file
    """
    
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop all tables
        cursor.execute("DROP TABLE IF EXISTS documents")
        cursor.execute("DROP TABLE IF EXISTS quotes")
        cursor.execute("DROP TABLE IF EXISTS project_equipment")
        cursor.execute("DROP TABLE IF EXISTS equipment_master")
        cursor.execute("DROP TABLE IF EXISTS projects")
        
        conn.commit()
        conn.close()
        
        print("⚠️  All tables dropped")
    
    # Recreate database
    return create_database(db_path)


if __name__ == "__main__":
    # Test database creation
    conn = create_database()
    
    # Verify tables exist
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n📋 Tables in database:")
    for table in tables:
        print(f"   - {table[0]}")
    
    conn.close()
