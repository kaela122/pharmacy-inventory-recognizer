@echo off
cd /d "%~dp0"
echo ============================================================
echo  MedIQ setup - installs backend + frontend dependencies
echo ============================================================
echo.
echo [1/2] Backend (Python)...
cd backend
python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
call deactivate
cd ..
echo.
echo [2/2] Frontend (Node.js)...
cd frontend
call npm install
cd ..
echo.
echo ============================================================
echo  Setup complete!  Now double-click  start.bat
echo ============================================================
pause
