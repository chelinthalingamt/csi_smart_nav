#!/bin/bash

SMARTNAV_DIR="$(cd "$(dirname "$0")" && pwd)"
SHELL_CONFIG=""

if [[ $SHELL == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ $SHELL == *"bash"* ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [[ $SHELL == *"fish"* ]]; then
    SHELL_CONFIG="$HOME/.config/fish/config.fish"
else
    echo "Unsupported shell. Add the alias manually."
    exit 1
fi

echo "alias smartnav='python3 $SMARTNAV_DIR/smartnav.py'" >> "$SHELL_CONFIG"
echo "SmartNav setup complete. Restart your terminal to use 'smartnav'."

