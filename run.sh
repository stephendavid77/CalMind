#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

# Check if virtual environment exists, if not, create it
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created."
fi

# Activate virtual environment
source "$VENV_DIR"/bin/activate

# Install dependencies
echo "Installing dependencies from $REQUIREMENTS_FILE..."
pip install -r "$REQUIREMENTS_FILE"
echo "Dependencies installed."

# Run the main application
echo "Running CalMind application..."
python -m calmind.main
