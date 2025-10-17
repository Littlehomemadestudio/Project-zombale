"""
Database utilities and schema for BalletBot: Outbreak Dominion
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager
import threading

from config import DATABASE_PATH

logger = logging.getLogger(__name__)

# Thread-local storage for database connections
local = threading.local()

class DatabaseManager:
    """Manages SQLite database connections and operations"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database file and tables if they don't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with self.get_connection() as conn:
            conn.executescript(self._get_schema_sql())
            conn.commit()
    
    def _get_schema_sql(self) -> str:
        """Get the complete database schema SQL"""
        return """
        -- Players table
        CREATE TABLE IF NOT EXISTS players (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            group_code TEXT NOT NULL,
            class TEXT NOT NULL,
            hp INTEGER DEFAULT 100,
            stamina INTEGER DEFAULT 100,
            hunger INTEGER DEFAULT 0,
            infection INTEGER DEFAULT 0,
            intelligence INTEGER DEFAULT 0,
            location TEXT DEFAULT 'Forest:Camp:Area1',
            shelter_id TEXT,
            status TEXT DEFAULT 'alive',
            offline_mode TEXT DEFAULT 'none',
            last_active INTEGER DEFAULT 0,
            last_actions TEXT DEFAULT '[]',
            created_at INTEGER DEFAULT 0
        );
        
        -- Inventories table
        CREATE TABLE IF NOT EXISTS inventories (
            player_id TEXT,
            item_id TEXT,
            qty INTEGER DEFAULT 0,
            PRIMARY KEY (player_id, item_id),
            FOREIGN KEY (player_id) REFERENCES players(id)
        );
        
        -- Items table
        CREATE TABLE IF NOT EXISTS items (
            item_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            properties TEXT DEFAULT '{}'
        );
        
        -- World regions table
        CREATE TABLE IF NOT EXISTS world_regions (
            name TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            danger INTEGER DEFAULT 0,
            zombies INTEGER DEFAULT 0,
            connected TEXT DEFAULT '[]',
            buildings TEXT DEFAULT '[]',
            properties TEXT DEFAULT '{}'
        );
        
        -- Buildings table
        CREATE TABLE IF NOT EXISTS buildings (
            id TEXT PRIMARY KEY,
            region TEXT NOT NULL,
            name TEXT NOT NULL,
            floors TEXT DEFAULT '[]',
            cleared_by TEXT DEFAULT '{}',
            last_checked INTEGER DEFAULT 0
        );
        
        -- Vehicles table
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id TEXT PRIMARY KEY,
            owner_id TEXT,
            type TEXT NOT NULL,
            condition INTEGER DEFAULT 100,
            fuel INTEGER DEFAULT 100,
            storage INTEGER DEFAULT 0,
            location TEXT NOT NULL,
            properties TEXT DEFAULT '{}'
        );
        
        -- Pending actions table
        CREATE TABLE IF NOT EXISTS pending_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            payload TEXT DEFAULT '{}',
            expire_at INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        );
        
        -- Construction table
        CREATE TABLE IF NOT EXISTS construction (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id TEXT NOT NULL,
            structure_type TEXT NOT NULL,
            start_time INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            resources TEXT DEFAULT '{}',
            status TEXT DEFAULT 'in_progress',
            location TEXT NOT NULL
        );
        
        -- Events table
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time INTEGER NOT NULL,
            type TEXT NOT NULL,
            payload TEXT DEFAULT '{}'
        );
        
        -- Logs table
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time INTEGER NOT NULL,
            level TEXT NOT NULL,
            message TEXT NOT NULL
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_players_group_code ON players(group_code);
        CREATE INDEX IF NOT EXISTS idx_players_status ON players(status);
        CREATE INDEX IF NOT EXISTS idx_players_location ON players(location);
        CREATE INDEX IF NOT EXISTS idx_inventories_player_id ON inventories(player_id);
        CREATE INDEX IF NOT EXISTS idx_pending_actions_expire ON pending_actions(expire_at);
        CREATE INDEX IF NOT EXISTS idx_events_time ON events(time);
        CREATE INDEX IF NOT EXISTS idx_logs_time ON logs(time);
        """
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with proper cleanup"""
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def execute_one(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a SELECT query and return single result as dict"""
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Execute a query multiple times with different parameters"""
        with self.get_connection() as conn:
            cursor = conn.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
    
    def execute_script(self, script: str) -> None:
        """Execute multiple SQL statements"""
        with self.get_connection() as conn:
            conn.executescript(script)
            conn.commit()
    
    def begin_transaction(self):
        """Begin a transaction (use with commit_transaction or rollback_transaction)"""
        if not hasattr(local, 'connection'):
            local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            local.connection.row_factory = sqlite3.Row
        local.connection.execute("BEGIN TRANSACTION")
    
    def commit_transaction(self):
        """Commit the current transaction"""
        if hasattr(local, 'connection'):
            local.connection.commit()
            local.connection.close()
            delattr(local, 'connection')
    
    def rollback_transaction(self):
        """Rollback the current transaction"""
        if hasattr(local, 'connection'):
            local.connection.rollback()
            local.connection.close()
            delattr(local, 'connection')
    
    def get_connection_in_transaction(self):
        """Get connection for use within a transaction"""
        if not hasattr(local, 'connection'):
            raise RuntimeError("No active transaction. Call begin_transaction() first.")
        return local.connection

# Global database manager instance
db = DatabaseManager()

# Helper functions for common operations
def get_player(player_id: str) -> Optional[Dict[str, Any]]:
    """Get player by ID"""
    return db.execute_one("SELECT * FROM players WHERE id = ?", (player_id,))

def get_player_by_username(username: str, group_code: str) -> Optional[Dict[str, Any]]:
    """Get player by username and group code"""
    return db.execute_one(
        "SELECT * FROM players WHERE username = ? AND group_code = ?",
        (username, group_code)
    )

def create_player(player_data: Dict[str, Any]) -> bool:
    """Create a new player"""
    try:
        db.execute_update("""
            INSERT INTO players (id, username, group_code, class, hp, stamina, 
                               hunger, infection, intelligence, location, 
                               shelter_id, status, offline_mode, last_active, 
                               last_actions, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_data['id'],
            player_data['username'],
            player_data['group_code'],
            player_data['class'],
            player_data.get('hp', 100),
            player_data.get('stamina', 100),
            player_data.get('hunger', 0),
            player_data.get('infection', 0),
            player_data.get('intelligence', 0),
            player_data.get('location', 'Forest:Camp:Area1'),
            player_data.get('shelter_id'),
            player_data.get('status', 'alive'),
            player_data.get('offline_mode', 'none'),
            player_data.get('last_active', 0),
            json.dumps(player_data.get('last_actions', [])),
            player_data.get('created_at', 0)
        ))
        return True
    except Exception as e:
        logger.error(f"Failed to create player: {e}")
        return False

def update_player(player_id: str, updates: Dict[str, Any]) -> bool:
    """Update player data"""
    try:
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key == 'last_actions':
                value = json.dumps(value)
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        values.append(player_id)
        
        query = f"UPDATE players SET {', '.join(set_clauses)} WHERE id = ?"
        db.execute_update(query, tuple(values))
        return True
    except Exception as e:
        logger.error(f"Failed to update player: {e}")
        return False

def get_player_inventory(player_id: str) -> List[Dict[str, Any]]:
    """Get player's inventory"""
    return db.execute_query("""
        SELECT i.*, inv.qty 
        FROM inventories inv
        JOIN items i ON inv.item_id = i.item_id
        WHERE inv.player_id = ? AND inv.qty > 0
        ORDER BY i.name
    """, (player_id,))

def add_item_to_inventory(player_id: str, item_id: str, quantity: int) -> bool:
    """Add item to player inventory"""
    try:
        # Check if item already exists
        existing = db.execute_one(
            "SELECT qty FROM inventories WHERE player_id = ? AND item_id = ?",
            (player_id, item_id)
        )
        
        if existing:
            # Update existing quantity
            new_qty = existing['qty'] + quantity
            db.execute_update(
                "UPDATE inventories SET qty = ? WHERE player_id = ? AND item_id = ?",
                (new_qty, player_id, item_id)
            )
        else:
            # Insert new item
            db.execute_update(
                "INSERT INTO inventories (player_id, item_id, qty) VALUES (?, ?, ?)",
                (player_id, item_id, quantity)
            )
        return True
    except Exception as e:
        logger.error(f"Failed to add item to inventory: {e}")
        return False

def remove_item_from_inventory(player_id: str, item_id: str, quantity: int) -> bool:
    """Remove item from player inventory"""
    try:
        # Check current quantity
        current = db.execute_one(
            "SELECT qty FROM inventories WHERE player_id = ? AND item_id = ?",
            (player_id, item_id)
        )
        
        if not current or current['qty'] < quantity:
            return False
        
        new_qty = current['qty'] - quantity
        if new_qty <= 0:
            # Remove item completely
            db.execute_update(
                "DELETE FROM inventories WHERE player_id = ? AND item_id = ?",
                (player_id, item_id)
            )
        else:
            # Update quantity
            db.execute_update(
                "UPDATE inventories SET qty = ? WHERE player_id = ? AND item_id = ?",
                (new_qty, player_id, item_id)
            )
        return True
    except Exception as e:
        logger.error(f"Failed to remove item from inventory: {e}")
        return False

def log_event(event_type: str, payload: Dict[str, Any]) -> None:
    """Log an event to the database"""
    import time
    db.execute_update(
        "INSERT INTO events (time, type, payload) VALUES (?, ?, ?)",
        (int(time.time()), event_type, json.dumps(payload))
    )

def log_message(level: str, message: str) -> None:
    """Log a message to the database"""
    import time
    db.execute_update(
        "INSERT INTO logs (time, level, message) VALUES (?, ?, ?)",
        (int(time.time()), level, message)
    )