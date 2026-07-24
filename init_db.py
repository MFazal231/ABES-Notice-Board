import sqlite3
import os

DB_PATH = "database/notice.db"
SCHEMA_PATH = "database/schema.sql"

# Create database directory if it doesn't exist
os.makedirs("database", exist_ok=True)

# Connect to SQLite (creates the database if it doesn't exist)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Execute schema.sql
with open(SCHEMA_PATH, "r", encoding="utf-8") as schema:
    cursor.executescript(schema.read())

conn.commit()
conn.close()

print("✅ Database initialized successfully!")