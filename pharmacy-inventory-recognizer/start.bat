@echo off
cd /d "%~dp0"
echo Starting MedIQ (backend :8000 and frontend :5173)...
start "MedIQ Backend" cmd /k "cd /d %~dp0backend ^&^& (if exist .venv\Scripts\python.exe (.venv\Scripts\python.exe -m uvicorn app.main:app --reload) else (python -m uvicorn app.main:app --reload))"
timeout /t 4 >nul
start "MedIQ Frontend" cmd /k "cd /d %~dp0frontend ^&^& npm run dev"
timeout /t 5 >nul
start "" http://localhost:5173
echo.
echo Two windows opened. Close them to stop the app.
echo Frontend: http://localhost:5173    Backend docs: http://localhost:8000/docs
