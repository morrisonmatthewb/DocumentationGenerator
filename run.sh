#!/bin/bash
# Simple script to run the setup script with Python

# Ensure Python 3 is available
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    # Check if this is Python 3
    VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d '.' -f 1)
    if [ "$VERSION" -eq 3 ]; then
        PYTHON="python"
    else
        echo "Error: Python 3 is required but not found."
        exit 1
    fi
else
    echo "Error: Python 3 is required but not found."
    exit 1
fi

# Give execute permission to the setup script
chmod +x setup.py

# Run the setup script
"$PYTHON" setup.py "$@"