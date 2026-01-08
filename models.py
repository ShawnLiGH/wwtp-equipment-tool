"""
Database models and CRUD operations for WWTP Equipment Tool
"""

import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
from .schema import get_db_path


class DatabaseManager:
    """Main database interface class"""
    
    def __init__(self):
        self.db_path = get_db_path()
    
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute SELECT query and return results as list of dicts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE and return affected rows or last row id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id


# ============================================================================
# PROJECTS
# ============================================================================

class ProjectManager(DatabaseManager):
    """Manage projects"""
    
    def create_project(self, name: str, client: str = None, job_number: str = None, 
                      phase: str = None, notes: str = None) -> int:
        """Create new project"""
        query = """
            INSERT INTO projects (name, client, job_number, phase, notes)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (name, client, job_number, phase, notes))
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects"""
        query = "SELECT * FROM projects ORDER BY created_date DESC"
        return self.execute_query(query)
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get project by ID"""
        query = "SELECT * FROM projects WHERE project_id = ?"
        results = self.execute_query(query, (project_id,))
        return results[0] if results else None
    
    def update_project(self, project_id: int, **kwargs) -> None:
        """Update project fields"""
        allowed_fields = ['name', 'client', 'job_number', 'phase', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE projects SET {set_clause} WHERE project_id = ?"
        params = tuple(updates.values()) + (project_id,)
        
        self.execute_update(query, params)
    
    def delete_project(self, project_id: int) -> None:
        """Delete project and all associated equipment instances"""
        # First delete project equipment
        self.execute_update("DELETE FROM project_equipment WHERE project_id = ?", (project_id,))
        # Then delete project
        self.execute_update("DELETE FROM projects WHERE project_id = ?", (project_id,))


# ============================================================================
# EQUIPMENT MASTER
# ============================================================================

class EquipmentManager(DatabaseManager):
    """Manage equipment master catalog"""
    
    def create_equipment(self, manufacturer: str, model: str, equipment_type: str, **kwargs) -> int:
        """Create new equipment in master catalog"""
        allowed_fields = [
            'equipment_subtype', 'power_hp', 'flow_gpm', 'head_ft', 'voltage', 'rpm',
            'power_hp_verified', 'flow_gpm_verified', 'head_ft_verified',
            'material', 'connection_size', 'weight_lbs', 'notes'
        ]
        
        # Build dynamic INSERT
        fields = ['manufacturer', 'model', 'equipment_type']
        values = [manufacturer, model, equipment_type]
        
        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                fields.append(field)
                values.append(kwargs[field])
        
        placeholders = ", ".join(["?"] * len(fields))
        query = f"INSERT INTO equipment_master ({', '.join(fields)}) VALUES ({placeholders})"
        
        return self.execute_update(query, tuple(values))
    
    def get_all_equipment(self, equipment_type: str = None) -> List[Dict]:
        """Get all equipment, optionally filtered by type"""
        if equipment_type:
            query = "SELECT * FROM equipment_master WHERE equipment_type = ? ORDER BY manufacturer, model"
            return self.execute_query(query, (equipment_type,))
        else:
            query = "SELECT * FROM equipment_master ORDER BY manufacturer, model"
            return self.execute_query(query)
    
    def get_equipment(self, equipment_id: int) -> Optional[Dict]:
        """Get equipment by ID"""
        query = "SELECT * FROM equipment_master WHERE equipment_id = ?"
        results = self.execute_query(query, (equipment_id,))
        return results[0] if results else None
    
    def search_equipment(self, search_term: str) -> List[Dict]:
        """Search equipment by manufacturer, model, or type"""
        query = """
            SELECT * FROM equipment_master 
            WHERE manufacturer LIKE ? OR model LIKE ? OR equipment_type LIKE ?
            ORDER BY manufacturer, model
        """
        search_pattern = f"%{search_term}%"
        return self.execute_query(query, (search_pattern, search_pattern, search_pattern))
    
    def update_equipment(self, equipment_id: int, **kwargs) -> None:
        """Update equipment fields"""
        allowed_fields = [
            'manufacturer', 'model', 'equipment_type', 'equipment_subtype',
            'power_hp', 'flow_gpm', 'head_ft', 'voltage', 'rpm',
            'power_hp_verified', 'flow_gpm_verified', 'head_ft_verified',
            'material', 'connection_size', 'weight_lbs', 'notes'
        ]
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE equipment_master SET {set_clause} WHERE equipment_id = ?"
        params = tuple(updates.values()) + (equipment_id,)
        
        self.execute_update(query, params)
    
    def delete_equipment(self, equipment_id: int) -> None:
        """Delete equipment (will fail if referenced in project_equipment)"""
        self.execute_update("DELETE FROM equipment_master WHERE equipment_id = ?", (equipment_id,))
    
    def get_equipment_types(self) -> List[str]:
        """Get list of unique equipment types"""
        query = "SELECT DISTINCT equipment_type FROM equipment_master ORDER BY equipment_type"
        results = self.execute_query(query)
        return [r['equipment_type'] for r in results]


# ============================================================================
# PROJECT EQUIPMENT INSTANCES
# ============================================================================

class ProjectEquipmentManager(DatabaseManager):
    """Manage equipment instances within projects"""
    
    def add_equipment_to_project(self, project_id: int, equipment_id: int, 
                                 pid_tag: str = None, status: str = 'new',
                                 quantity: int = 1, location: str = None,
                                 notes: str = None, selected_quote_id: int = None) -> int:
        """Add equipment instance to project"""
        query = """
            INSERT INTO project_equipment 
            (project_id, equipment_id, pid_tag, status, quantity, location, notes, selected_quote_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (project_id, equipment_id, pid_tag, status, 
                                           quantity, location, notes, selected_quote_id))
    
    def get_project_equipment(self, project_id: int) -> List[Dict]:
        """Get all equipment for a project with full details"""
        query = """
            SELECT 
                pe.*,
                em.manufacturer,
                em.model,
                em.equipment_type,
                em.equipment_subtype,
                em.power_hp,
                em.flow_gpm,
                em.head_ft,
                q.vendor,
                q.price,
                q.currency,
                q.lead_time_weeks
            FROM project_equipment pe
            LEFT JOIN equipment_master em ON pe.equipment_id = em.equipment_id
            LEFT JOIN quotes q ON pe.selected_quote_id = q.quote_id
            WHERE pe.project_id = ?
            ORDER BY pe.pid_tag
        """
        return self.execute_query(query, (project_id,))
    
    def update_project_equipment(self, instance_id: int, **kwargs) -> None:
        """Update project equipment instance"""
        allowed_fields = ['pid_tag', 'status', 'quantity', 'location', 'notes', 'selected_quote_id']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE project_equipment SET {set_clause} WHERE instance_id = ?"
        params = tuple(updates.values()) + (instance_id,)
        
        self.execute_update(query, params)
    
    def delete_project_equipment(self, instance_id: int) -> None:
        """Remove equipment instance from project"""
        self.execute_update("DELETE FROM project_equipment WHERE instance_id = ?", (instance_id,))


# ============================================================================
# QUOTES
# ============================================================================

class QuoteManager(DatabaseManager):
    """Manage equipment quotes"""
    
    def create_quote(self, equipment_id: int, vendor: str, price: float = None,
                    currency: str = 'USD', lead_time_weeks: int = None,
                    quote_date: str = None, quote_number: str = None,
                    quote_file_path: str = None, is_current: bool = True,
                    notes: str = None) -> int:
        """Create new quote for equipment"""
        query = """
            INSERT INTO quotes 
            (equipment_id, vendor, price, currency, lead_time_weeks, 
             quote_date, quote_number, quote_file_path, is_current, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (equipment_id, vendor, price, currency, 
                                           lead_time_weeks, quote_date, quote_number,
                                           quote_file_path, is_current, notes))
    
    def get_equipment_quotes(self, equipment_id: int) -> List[Dict]:
        """Get all quotes for equipment"""
        query = "SELECT * FROM quotes WHERE equipment_id = ? ORDER BY quote_date DESC"
        return self.execute_query(query, (equipment_id,))
    
    def get_current_quote(self, equipment_id: int) -> Optional[Dict]:
        """Get current quote for equipment"""
        query = "SELECT * FROM quotes WHERE equipment_id = ? AND is_current = 1 LIMIT 1"
        results = self.execute_query(query, (equipment_id,))
        return results[0] if results else None
    
    def update_quote(self, quote_id: int, **kwargs) -> None:
        """Update quote fields"""
        allowed_fields = ['vendor', 'price', 'currency', 'lead_time_weeks', 
                         'quote_date', 'quote_number', 'quote_file_path', 
                         'is_current', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE quotes SET {set_clause} WHERE quote_id = ?"
        params = tuple(updates.values()) + (quote_id,)
        
        self.execute_update(query, params)
    
    def delete_quote(self, quote_id: int) -> None:
        """Delete quote"""
        self.execute_update("DELETE FROM quotes WHERE quote_id = ?", (quote_id,))


# ============================================================================
# DOCUMENTS
# ============================================================================

class DocumentManager(DatabaseManager):
    """Manage equipment documents"""
    
    def create_document(self, equipment_id: int, document_type: str, 
                       file_name: str, file_path: str,
                       file_size_kb: int = None, version: str = None,
                       document_date: str = None, notes: str = None) -> int:
        """Register new document for equipment"""
        query = """
            INSERT INTO documents 
            (equipment_id, document_type, file_name, file_path, 
             file_size_kb, version, document_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (equipment_id, document_type, file_name, 
                                           file_path, file_size_kb, version, 
                                           document_date, notes))
    
    def get_equipment_documents(self, equipment_id: int, document_type: str = None) -> List[Dict]:
        """Get all documents for equipment, optionally filtered by type"""
        if document_type:
            query = """
                SELECT * FROM documents 
                WHERE equipment_id = ? AND document_type = ?
                ORDER BY uploaded_date DESC
            """
            return self.execute_query(query, (equipment_id, document_type))
        else:
            query = "SELECT * FROM documents WHERE equipment_id = ? ORDER BY uploaded_date DESC"
            return self.execute_query(query, (equipment_id,))
    
    def update_document(self, document_id: int, **kwargs) -> None:
        """Update document metadata"""
        allowed_fields = ['document_type', 'file_name', 'file_path', 
                         'file_size_kb', 'version', 'document_date', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE documents SET {set_clause} WHERE document_id = ?"
        params = tuple(updates.values()) + (document_id,)
        
        self.execute_update(query, params)
    
    def delete_document(self, document_id: int) -> None:
        """Delete document record"""
        self.execute_update("DELETE FROM documents WHERE document_id = ?", (document_id,))
