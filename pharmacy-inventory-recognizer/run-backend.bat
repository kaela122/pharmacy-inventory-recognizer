@echo off
cd /d "%~dp0backend"
echo ============================================================
echo  MedIQ backend  -  http://localhost:8000
echo  (first run installs Python packages, this can take a minute)
echo ============================================================
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
pause
