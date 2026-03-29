#!/bin/bash
# Ensure pip, setuptools, wheel are up-to-date
python -m pip install --upgrade pip setuptools wheel

# Install all packages from requirements.txt into the Render virtual environment
pip install -r requirements.txt