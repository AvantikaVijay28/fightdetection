#!/bin/bash

# Upgrade pip, setuptools, wheel first
python -m pip install --upgrade pip setuptools wheel

# Then install requirements
pip install -r requirements.txt