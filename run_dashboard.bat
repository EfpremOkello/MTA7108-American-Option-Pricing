@echo off
REM Starts Option Desk. Double-click for the desktop window.
REM   run_dashboard.bat web       web dashboard in your browser
REM   run_dashboard.bat network   web dashboard other devices on your network can open
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (set PY=python& set PYW=pythonw) else (set PY=py& set PYW=pyw)

if /i "%1"=="web" (
  %PY% launch.py --mode web
) else if /i "%1"=="network" (
  %PY% launch.py --mode web --network
) else (
  start "" %PYW% launch.py --mode desktop
)
