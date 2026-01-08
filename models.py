"""
WWTP Equipment Tool - Database Models
CRUD operations for all database tables
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd


class Database:
    """Database connection and operations manager"""
    
    def __init__(self, db_path='database/wwtp_equipment.db'):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute query and return cursor"""
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor
    
    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Execute query and return single row as dict"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetchall(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute query and return all rows as list of dicts"""
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# ============================================
# PROJECT OPERATIONS
# ============================================

def create_project(db: Database, name: str, client: str = None, 
                   job_number: str = None, phase: str = 'Design', 
                   notes: str = None) -> int:
    """Create new project"""
    query = """
        INSERT INTO projects (name, client, job_number, phase, notes)
        VALUES (?, ?, ?, ?, ?)
    """
    cursor = db.execute(query, (name, client, job_number, phase, notes))
    return cursor.lastrowid


def get_project(db: Database, project_id: int) -> Optional[Dict]:
    """Get project by ID"""
    query = "SELECT * FROM projects WHERE project_id = ?"
    return db.fetchone(query, (project_id,))


def get_all_projects(db: Database) -> List[Dict]:
    """Get all projects"""
    query = "SELECT * FROM projects ORDER BY created_date DESC"
    return db.fetchall(query)


def update_project(db: Database, project_id: int, **kwargs) -> bool:
    """Update project fields"""
    allowed_fields = ['name', 'client', 'job_number', 'phase', 'notes']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return False
    
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    query = f"UPDATE projects SET {set_clause} WHERE project_id = ?"
    
    db.execute(query, tuple(updates.values()) + (project_id,))
    return True


def delete_project(db: Database, project_id: int) -> bool:
    """Delete project (cascades to project_equipment)"""
    query = "DELETE FROM projects WHERE project_id = ?"
    cursor = db.execute(query, (project_id,))
    return cursor.rowcount > 0


# ============================================
# EQUIPMENT MASTER OPERATIONS
# ============================================

def create_equipment(db: Database, manufacturer: str, model: str, 
                     equipment_type: str, **kwargs) -> int:
    """Create new equipment in master catalog"""
    
    # Build dynamic insert based on provided kwargs
    base_fields = ['manufacturer', 'model', 'equipment_type']
    optional_fields = ['equipment_subtype', 'power_hp', 'flow_gpm', 'head_ft', 
                       'voltage', 'rpm', 'power_hp_verified', 'flow_gpm_verified', 
                       'head_ft_verified', 'material', 'connection_size', 
                       'weight_lbs', 'notes']
    
    fields = base_fields.copy()
    values = [manufacturer, model, equipment_type]
    
    for field in optional_fields:
        if field in kwargs:
            fields.append(field)
            values.append(kwargs[field])
    
    placeholders = ", ".join(["?" for _ in fields])
    query = f"""
        INSERT INTO equipment_master ({", ".join(fields)})
        VALUES ({placeholders})
    """
    
    cursor = db.execute(query, tuple(values))
    return cursor.lastrowid


def get_equipment(db: Database, equipment_id: int) -> Optional[Dict]:
    """Get equipment by ID"""
    query = "SELECT * FROM equipment_master WHERE equipment_id = ?"
    return db.fetchone(query, (equipment_id,))


def get_all_equipment(db: Database, equipment_type: str = None) -> List[Dict]:
    """Get all equipment, optionally filtered by type"""
    if equipment_type:
        query = "SELECT * FROM equipment_master WHERE equipment_type = ? ORDER BY manufacturer, model"
        return db.fetchall(query, (equipment_type,))
    else:
        query = "SELECT * FROM equipment_master ORDER BY manufacturer, model"
        return db.fetchall(query)


def search_equipment(db: Database, search_term: str) -> List[Dict]:
    """Search equipment by manufacturer, model, or type"""
    query = """
        SELECT * FROM equipment_master 
        WHERE manufacturer LIKE ? 
           OR model LIKE ? 
           OR equipment_type LIKE ?
        ORDER BY manufacturer, model
    """
    pattern = f"%{search_term}%"
    return db.fetchall(query, (pattern, pattern, pattern))


def update_equipment(db: Database, equipment_id: int, **kwargs) -> bool:
    """Update equipment fields"""
    allowed_fields = ['manufacturer', 'model', 'equipment_type', 'equipment_subtype',
                      'power_hp', 'flow_gpm', 'head_ft', 'voltage', 'rpm',
                      'power_hp_verified', 'flow_gpm_verified', 'head_ft_verified',
                      'material', 'connection_size', 'weight_lbs', 'notes']
    
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return False
    
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    query = f"UPDATE equipment_master SET {set_clause} WHERE equipment_id = ?"
    
    db.execute(query, tuple(updates.values()) + (equipment_id,))
    return True


def delete_equipment(db: Database, equipment_id: int) -> bool:
    """Delete equipment (restricted if used in projects)"""
    query = "DELETE FROM equipment_master WHERE equipment_id = ?"
    try:
        cursor = db.execute(query, (equipment_id,))
        return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        return False  # Cannot delete if referenced in project_equipment


# ============================================
# PROJECT EQUIPMENT OPERATIONS
# ============================================

def add_equipment_to_project(db: Database, project_id: int, equipment_id: int,
                             pid_tag: str = None, status: str = 'new',
                             quantity: int = 1, location: str = None,
                             notes: str = None, selected_quote_id: int = None) -> int:
    """Add equipment instance to project"""
    query = """
        INSERT INTO project_equipment 
        (project_id, equipment_id, pid_tag, status, quantity, location, notes, selected_quote_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor = db.execute(query, (project_id, equipment_id, pid_tag, status, 
                                  quantity, location, notes, selected_quote_id))
    return cursor.lastrowid


def get_project_equipment_list(db: Database, project_id: int) -> List[Dict]:
    """Get all equipment for a project with details"""
    query = """
        SELECT 
            pe.instance_id,
            pe.project_id,
            pe.equipment_id,
            pe.pid_tag,
            pe.status,
            pe.quantity,
            pe.location,
            pe.notes as instance_notes,
            pe.selected_quote_id,
            em.manufacturer,
            em.model,
            em.equipment_type,
            em.equipment_subtype,
            em.power_hp,
            em.flow_gpm,
            em.head_ft,
            em.voltage,
            q.vendor,
            q.price,
            q.currency,
            q.lead_time_weeks
        FROM project_equipment pe
        JOIN equipment_master em ON pe.equipment_id = em.equipment_id
        LEFT JOIN quotes q ON pe.selected_quote_id = q.quote_id
        WHERE pe.project_id = ?
        ORDER BY pe.pid_tag
    """
    return db.fetchall(query, (project_id,))


def update_project_equipment(db: Database, instance_id: int, **kwargs) -> bool:
    """Update project equipment instance"""
    allowed_fields = ['pid_tag', 'status', 'quantity', 'location', 'notes', 'selected_quote_id']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return False
    
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    query = f"UPDATE project_equipment SET {set_clause} WHERE instance_id = ?"
    
    db.execute(query, tuple(updates.values()) + (instance_id,))
    return True


def remove_equipment_from_project(db: Database, instance_id: int) -> bool:
    """Remove equipment from project"""
    query = "DELETE FROM project_equipment WHERE instance_id = ?"
    cursor = db.execute(query, (instance_id,))
    return cursor.rowcount > 0


# ============================================
# QUOTE OPERATIONS
# ============================================

def create_quote(db: Database, equipment_id: int, vendor: str,
                 price: float = None, currency: str = 'USD',
                 lead_time_weeks: int = None, quote_date: str = None,
                 quote_number: str = None, quote_file_path: str = None,
                 is_current: bool = True, notes: str = None) -> int:
    """Create new quote for equipment"""
    query = """
        INSERT INTO quotes 
        (equipment_id, vendor, price, currency, lead_time_weeks, quote_date, 
         quote_number, quote_file_path, is_current, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor = db.execute(query, (equipment_id, vendor, price, currency, 
                                  lead_time_weeks, quote_date, quote_number,
                                  quote_file_path, is_current, notes))
    return cursor.lastrowid


def get_equipment_quotes(db: Database, equipment_id: int, 
                         current_only: bool = False) -> List[Dict]:
    """Get all quotes for equipment"""
    if current_only:
        query = "SELECT * FROM quotes WHERE equipment_id = ? AND is_current = 1 ORDER BY quote_date DESC"
    else:
        query = "SELECT * FROM quotes WHERE equipment_id = ? ORDER BY quote_date DESC"
    return db.fetchall(query, (equipment_id,))


def update_quote(db: Database, quote_id: int, **kwargs) -> bool:
    """Update quote fields"""
    allowed_fields = ['vendor', 'price', 'currency', 'lead_time_weeks', 
                      'quote_date', 'quote_number', 'quote_file_path', 
                      'is_current', 'notes']
    
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return False
    
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    query = f"UPDATE quotes SET {set_clause} WHERE quote_id = ?"
    
    db.execute(query, tuple(updates.values()) + (quote_id,))
    return True


def delete_quote(db: Database, quote_id: int) -> bool:
    """Delete quote"""
    query = "DELETE FROM quotes WHERE quote_id = ?"
    cursor = db.execute(query, (quote_id,))
    return cursor.rowcount > 0


# ============================================
# DOCUMENT OPERATIONS
# ============================================

def create_document(db: Database, equipment_id: int, document_type: str,
                    file_name: str, file_path: str, file_size_kb: int = None,
                    version: str = None, document_date: str = None,
                    notes: str = None) -> int:
    """Create document record for equipment"""
    query = """
        INSERT INTO documents 
        (equipment_id, document_type, file_name, file_path, file_size_kb, 
         version, document_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor = db.execute(query, (equipment_id, document_type, file_name, 
                                  file_path, file_size_kb, version, 
                                  document_date, notes))
    return cursor.lastrowid


def get_equipment_documents(db: Database, equipment_id: int, 
                            document_type: str = None) -> List[Dict]:
    """Get documents for equipment, optionally filtered by type"""
    if document_type:
        query = "SELECT * FROM documents WHERE equipment_id = ? AND document_type = ? ORDER BY uploaded_date DESC"
        return db.fetchall(query, (equipment_id, document_type))
    else:
        query = "SELECT * FROM documents WHERE equipment_id = ? ORDER BY uploaded_date DESC"
        return db.fetchall(query, (equipment_id,))


def delete_document(db: Database, document_id: int) -> bool:
    """Delete document record"""
    query = "DELETE FROM documents WHERE document_id = ?"
    cursor = db.execute(query, (document_id,))
    return cursor.rowcount > 0


# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_database_stats(db: Database) -> Dict[str, int]:
    """Get count of records in each table"""
    stats = {}
    tables = ['projects', 'equipment_master', 'project_equipment', 'quotes', 'documents']
    
    for table in tables:
        query = f"SELECT COUNT(*) as count FROM {table}"
        result = db.fetchone(query)
        stats[table] = result['count']
    
    return stats


def export_to_dataframe(db: Database, query: str, params: tuple = ()) -> pd.DataFrame:
    """Execute query and return results as pandas DataFrame"""
    if not db.conn:
        db.connect()
    return pd.read_sql_query(query, db.conn, params=params)
