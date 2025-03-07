import os
import sys
import sqlite3
import subprocess
from pathlib import Path

DB_PATH = Path.home() / ".smart_nav.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dirs (
                    path TEXT PRIMARY KEY,
                    access_count INTEGER DEFAULT 1,
                    last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

def add_directory(path):
    path = os.path.abspath(path)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT access_count FROM dirs WHERE path = ?", (path,))
    row = c.fetchone()
    if row:
        c.execute("UPDATE dirs SET access_count = access_count + 1, last_access = CURRENT_TIMESTAMP WHERE path = ?", (path,))
    else:
        c.execute("INSERT INTO dirs (path) VALUES (?)", (path,))
    conn.commit()
    conn.close()

def find_best_match(query):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = f"%{query}%"
    c.execute("""
        SELECT path FROM dirs 
        WHERE path LIKE ? 
        ORDER BY access_count DESC, last_access DESC
        LIMIT 1
    """, (query,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def jump_to_directory(query):
    best_match = find_best_match(query)
    if best_match:
        print(best_match)
    else:
        print("No matching directory found.")

def list_tracked():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT path, access_count FROM dirs ORDER BY access_count DESC, last_access DESC")
    rows = c.fetchall()
    conn.close()
    for row in rows:
        print(f"{row[1]:<5} {row[0]}")

def remove_directory(path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM dirs WHERE path = ?", (os.path.abspath(path),))
    conn.commit()
    conn.close()

def clear_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM dirs")
    conn.commit()
    conn.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: smartnav <command> [arguments]")
        return
    
    command = sys.argv[1]
    if command == "add" and len(sys.argv) == 3:
        add_directory(sys.argv[2])
    elif command == "jump" and len(sys.argv) == 3:
        jump_to_directory(sys.argv[2])
    elif command == "list":
        list_tracked()
    elif command == "remove" and len(sys.argv) == 3:
        remove_directory(sys.argv[2])
    elif command == "clear":
        clear_db()
    else:
        print("Invalid command or missing arguments.")

if __name__ == "__main__":
    init_db()
    main()