#!/bin/bash

# Check if Python 3.9+ is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Try cargo path first, then ~/.local/bin
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    elif [ -f "$HOME/.local/bin/uv" ]; then
        export PATH="$HOME/.local/bin:$PATH"
    fi
fi

# Create a virtual environment with uv
if [ ! -d ".venv" ]; then
    uv venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install requirements
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Install Jupyter and ipykernel if not already installed
echo "Installing Jupyter..."
uv pip install jupyter ipykernel
# Create Jupyter kernel from this environment
echo "Creating Jupyter kernel..."
python -m ipykernel install --user --name=hdcrs-school-2026 --display-name="HDCRS School 2026"

echo "Setup complete! Select 'HDCRS School 2026' kernel in Jupyter."