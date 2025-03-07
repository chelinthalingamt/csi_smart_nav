#!/bin/bash

smartnav() {
    if [[ "$1" == "jump" ]]; then
        dest=$(python3 /path/to/smartnav.py jump "$2")
        if [[ -d "$dest" ]]; then
            cd "$dest" || echo "Failed to change directory."
        else
            echo "No matching directory found."
        fi
    elif [[ "$1" == "auto-track" ]]; then
        python3 /path/to/smartnav.py auto-track
    else
        python3 /path/to/smartnav.py "$@"
    fi
}

# Auto-track `cd` changes
cd() {
    builtin cd "$@" || return
    smartnav auto-track
}

alias sn="smartnav"
