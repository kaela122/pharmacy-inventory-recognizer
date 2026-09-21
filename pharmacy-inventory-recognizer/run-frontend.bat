@echo off
cd /d "%~dp0frontend"
echo ============================================================
echo  MedIQ frontend  -  http://localhost:5173
echo  (first run installs Node packages, this can take a minute)
echo ============================================================
call npm install
call npm run dev
pause
