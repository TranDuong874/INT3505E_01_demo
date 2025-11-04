#!/bin/bash
echo "Starting Flask App..."
cd app
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
python main.py
