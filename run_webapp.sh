
#!/bin/bash

# This script installs dependencies and runs the CalMind web application.

# Exit immediately if a command exits with a non-zero status.
set -e

# Get the directory of the script
SCRIPT_DIR=$(dirname "$0")

# Change to the script's directory to ensure correct relative paths
cd "$SCRIPT_DIR"

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping dependency installation."
fi

# Run the web application
echo "Starting the CalMind web application..."
python3 -m calmind.webapp
