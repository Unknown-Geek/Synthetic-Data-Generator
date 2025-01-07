@echo off
start cmd /k "cd backend && python -m venv venv && venv\Scripts\activate && python.exe -m pip install --upgrade pip && pip install -r requirements.txt && python app.py"
start "" cmd /k "cd frontend && npm i && npm start"