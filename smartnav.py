import os
import sys
import sqlite3
import subprocess
from pathlib import Path
from thefuzz import process

#Creating Table in the database to store the directories
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

#Adding directory to the table
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


#To automatically track the directory whenever the user changes it
def auto_track_directory():
    current_path = os.getcwd()
    add_directory(current_path)

#Finding the best match for the given directory
def find_best_match(query, current_path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT path, access_count, last_access FROM dirs")
    paths = c.fetchall()
    conn.close()
    
    if not paths:
        return None
    
    all_paths = [row[0] for row in paths]
    
    # Exact match first
    exact_matches = [p for p in all_paths if query.lower() == os.path.basename(p).lower()]
    if exact_matches:
        return sorted(exact_matches, key=lambda p: -p.count(os.sep))[0]
    
    # Fuzzy match with weighted ranking
    best_match = process.extractOne(query, all_paths, scorer=process.fuzz.partial_ratio)
    return best_match[0] if best_match else None

def jump_to_directory(query):
    best_match = find_best_match(query, os.getcwd())
    if best_match:
        print(best_match)
    else:
        print("No matching directory found.")

#Listing Tracked Directories
def list_tracked():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT path, access_count FROM dirs ORDER BY access_count DESC, last_access DESC")
    rows = c.fetchall()
    conn.close()
    for row in rows:
        print(f"{row[1]:<5} {row[0]}")

#Removing Directory from tracking
def remove_directory(path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM dirs WHERE path = ?", (os.path.abspath(path),))
    conn.commit()
    conn.close()

#Clear Database
def clear_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM dirs")
    conn.commit()
    conn.close()

#Setting up Shell

def setup_windows():
    """Setup SmartNav for Windows PowerShell."""
    profile_path = Path.home() / "Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1"
    python_cmd = "python3" if subprocess.run("python3 --version", shell=True, stdout=subprocess.PIPE).returncode == 0 else "python"

    with open(profile_path, "a") as f:
        f.write(f"\nfunction smartnav {{ & {python_cmd} {Path(__file__).resolve()} $args }}\n")
    print("SmartNav has been added to PowerShell. Restart your terminal.")

def setup_unix():
    """Setup SmartNav for Bash, Zsh, or Fish."""
    shell_config = {
        "bash": "~/.bashrc" if not os.path.exists(os.path.expanduser("~/.bash_profile")) else "~/.bash_profile",
        "zsh": "~/.zshrc",
        "fish": "~/.config/fish/config.fish"
    }
    shell = subprocess.run("ps -p $$ -o comm=", shell=True, capture_output=True, text=True).stdout.strip()
    script_path = str(Path(__file__).resolve())

    if shell in shell_config:
        config_path = os.path.expanduser(shell_config[shell])
        with open(config_path, "a") as f:
            if shell == "fish":
                f.write(f"\nfunction smartnav; python3 {script_path} $argv; end\n")
            else:
                f.write(f"\nalias smartnav='python3 {script_path}'\n")
        print(f"SmartNav has been added to {shell}. Restart your terminal.")
    else:
        print("Unsupported shell. Manually add SmartNav alias.")

def setup_shell():
    """Detect OS and call the correct setup function."""
    if os.name == "nt":
        setup_windows()
    else:
        setup_unix()


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
    elif command == "auto-track":
        auto_track_directory()
    elif command == "setup-shell":
        setup_shell()
    else:
        print("Invalid command or missing arguments.")

if __name__ == "__main__":
    init_db()
    main()