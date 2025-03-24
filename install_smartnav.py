import os
import subprocess
from pathlib import Path

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

if __name__ == "__main__":
    setup_shell()