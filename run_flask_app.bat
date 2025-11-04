@echo off
echo Starting Flask App...
cd app
python -m venv venv
call venv\Scripts\activate
pip install -r ..\requirements.txt
python main.py
pause
