@echo off
REM ---------------------------------------------------------------------------
REM  Option Desk setup.  Double-click this file once on a new computer.
REM  It checks that Python is installed, installs the packages Option Desk needs,
REM  and puts "Option Desk" shortcuts on the Desktop.
REM ---------------------------------------------------------------------------
cd /d "%~dp0"
title Option Desk setup

where python >nul 2>nul
if %errorlevel%==0 (set PY=python) else (set PY=py)

%PY% --version >nul 2>nul
if errorlevel 1 (
  echo.
  echo  Python is not installed on this computer.
  echo.
  echo  1. Go to  https://www.python.org/downloads/
  echo  2. Download Python for Windows and run the installer.
  echo  3. On the FIRST screen, tick "Add python.exe to PATH", then click Install Now.
  echo  4. When it finishes, double-click this file again.
  echo.
  pause
  exit /b 1
)

echo Installing the packages Option Desk needs. This takes a few minutes the first time...
%PY% -m pip install --upgrade -r requirements.txt
if errorlevel 1 (
  echo.
  echo  The installation failed. Check the internet connection and run this file again.
  pause
  exit /b 1
)

echo.
echo Creating shortcuts...
%PY% install_shortcuts.py

echo.
echo  Done. Open "Option Desk" from the Desktop.
pause
