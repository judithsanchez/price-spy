#!/usr/bin/env python3
"""
Price Spy Database Manager
Handles SQL dumps and restores for production data environment.
"""

import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Configure paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "pricespy.db"
DUMP_PATH = BASE_DIR / "data" / "pricespy_dump.sql"

# Constants
MIN_ARGS_GLOBAL = 2
MIN_ARGS_QUERY = 3

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("db_manager")


def dump():
    """Create a SQL dump of the current database using python's sqlite3 module."""
    logger.info("Creating SQL dump of %s...", DB_PATH)
    if not DB_PATH.exists():
        logger.error("Error: Database file not found.")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        with DUMP_PATH.open("w") as f:
            f.writelines(f"{line}\n" for line in conn.iterdump())
        conn.close()
    except Exception:
        logger.exception("Error during dump:")
        return False
    return True


def restore():
    """Restore the database from the SQL dump."""
    logger.info("Restoring database from %s...", DUMP_PATH)
    if not DUMP_PATH.exists():
        logger.error("Error: SQL dump file not found.")
        return False

    # Create a backup of current DB if it exists
    backup_name = None
    if DB_PATH.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = DB_PATH.parent / f"{DB_PATH.name}.bak_{timestamp}"
        logger.info("Backing up current database to %s...", backup_name)
        DB_PATH.rename(backup_name)

    try:
        conn = sqlite3.connect(DB_PATH)
        # Use read_text if file is small enough.
        # executescript needs the full script. Dumps can be large but
        # usually fit in memory.
        sql = DUMP_PATH.read_text()
        conn.executescript(sql)
        conn.close()
    except Exception:
        logger.exception("Error during restore:")
        # Restore the backup if it existed and we failed
        if backup_name and backup_name.exists():
            if DB_PATH.exists():
                DB_PATH.unlink()
            backup_name.rename(DB_PATH)
            logger.info("Restored from backup after failure.")
        return False
    logger.info("Successfully restored database from %s", DUMP_PATH)
    return True


def query(sql):
    """Execute a query and print results in a formatted table."""
    if not DB_PATH.exists():
        logger.error("Error: Database file not found.")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql)

        rows = cursor.fetchall()
        if not rows:
            if cursor.description:
                logger.info("No results found.")
            else:
                logger.info("Command executed successfully.")
            conn.commit()
            conn.close()
            return True

        # Calculate column widths
        headers = rows[0].keys()
        widths = {h: len(str(h)) for h in headers}
        for row in rows:
            for h in headers:
                widths[h] = max(widths[h], len(str(row[h])))

        # Print header
        header_row = " | ".join(str(h).ljust(widths[h]) for h in headers)
        print(header_row)
        print("-" * len(header_row))

        # Print rows
        for row in rows:
            print(" | ".join(str(row[h]).ljust(widths[h]) for h in headers))

        # Commit changes in case of INSERT/UPDATE/DELETE
        conn.commit()
        conn.close()
    except Exception:
        logger.exception("Error during query:")
        return False
    return True


def cleanup():
    """Remove backup database files (.bak or .backup_) from the data directory."""
    logger.info("Cleaning up backup files in %s...", DB_PATH.parent)
    count = 0
    patterns = ["*.bak", "*.bak_*", "*.backup_*"]

    for pattern in patterns:
        for backup_file in DB_PATH.parent.glob(pattern):
            try:
                logger.info("  - Removing %s", backup_file.name)
                backup_file.unlink()
                count += 1
            except Exception:
                logger.exception("  - Failed to remove %s", backup_file.name)

    logger.info("Done. Removed %d files.", count)
    return True


def migrate():
    """Run pending migrations from the migrations directory."""
    migrations_dir = BASE_DIR / "migrations"
    migrations_dir.mkdir(exist_ok=True)

    logger.info("Checking for pending migrations in %s...", migrations_dir)

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS _migrations (
                name TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        applied = {
            row[0] for row in conn.execute("SELECT name FROM _migrations").fetchall()
        }
        files = sorted(migrations_dir.glob("*.sql"))

        count = 0
        for sql_file in files:
            if sql_file.name not in applied:
                logger.info("  - Applying %s...", sql_file.name)
                conn.executescript(sql_file.read_text())
                conn.execute(
                    "INSERT INTO _migrations (name) VALUES (?)", (sql_file.name,)
                )
                conn.commit()
                count += 1

        logger.info("Done. Applied %d new migrations.", count)
        conn.close()
    except Exception:
        logger.exception("Migration failed:")
        return False
    return True


def main():
    """Execute the database manager utility."""
    commands = {
        "dump": dump,
        "restore": restore,
        "cleanup": cleanup,
        "migrate": migrate,
    }

    if len(sys.argv) < MIN_ARGS_GLOBAL:
        cmds = "|".join(commands.keys())
        print(f"Usage: python scripts/db_manager.py [{cmds}|query] [sql_if_query]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "query":
        if len(sys.argv) < MIN_ARGS_QUERY:
            print('Usage: python scripts/db_manager.py query "SQL_QUERY"')
            sys.exit(1)
        if query(sys.argv[2]):
            sys.exit(0)
    elif command in commands:
        if commands[command]():
            sys.exit(0)
    else:
        cmds = "|".join(commands.keys())
        print(f"Unknown command: {command}")
        print(f"Usage: python scripts/db_manager.py [{cmds}|query]")
        sys.exit(1)

    sys.exit(1)


if __name__ == "__main__":
    main()
