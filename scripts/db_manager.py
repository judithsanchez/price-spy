#!/usr/bin/env python3
"""
Price Spy Database Manager
Handles SQL dumps and restores for production data environment.
"""

import os
import subprocess
import sys
from datetime import datetime

# Configure paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "pricespy.db")
DUMP_PATH = os.path.join(BASE_DIR, "data", "pricespy_dump.sql")

import sqlite3

def dump():
    """Create a SQL dump of the current database using python's sqlite3 module."""
    print(f"Creating SQL dump of {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print("Error: Database file not found.")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        with open(DUMP_PATH, 'w') as f:
            for line in conn.iterdump():
                f.write('%s\n' % line)
        conn.close()
        print(f"Successfully created dump at {DUMP_PATH}")
        return True
    except Exception as e:
        print(f"Error during dump: {e}")
        return False

def restore():
    """Restore the database from the SQL dump."""
    print(f"Restoring database from {DUMP_PATH}...")
    if not os.path.exists(DUMP_PATH):
        print("Error: SQL dump file not found.")
        return False
    
    # Create a backup of current DB if it exists
    backup_name = None
    if os.path.exists(DB_PATH):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{DB_PATH}.bak_{timestamp}"
        print(f"Backing up current database to {backup_name}...")
        os.rename(DB_PATH, backup_name)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        with open(DUMP_PATH, 'r') as f:
            sql = f.read()
            conn.executescript(sql)
        conn.close()
        print(f"Successfully restored database from {DUMP_PATH}")
        return True
    except Exception as e:
        print(f"Error during restore: {e}")
        # Restore the backup if it existed and we failed
        if backup_name and os.path.exists(backup_name):
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
            os.rename(backup_name, DB_PATH)
            print("Restored from backup after failure.")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/db_manager.py [dump|restore]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    if command == "dump":
        if dump():
            sys.exit(0)
    elif command == "restore":
        if restore():
            sys.exit(0)
    else:
        print(f"Unknown command: {command}")
        print("Usage: python scripts/db_manager.py [dump|restore]")
        sys.exit(1)
    
    sys.exit(1)

if __name__ == "__main__":
    main()
