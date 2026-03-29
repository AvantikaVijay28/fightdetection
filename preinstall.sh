#!/bin/bash
# Exit immediately if a command fails
set -e

# Activate Render's virtual environment
source .venv/bin/activate

# Upgrade core Python packaging tools
python -m pip install --upgrade pip setuptools wheel

# Install all packages from requirements.txt
pip install -r requirements.txt

# Ensure Gunicorn is installed
pip install gunicorn