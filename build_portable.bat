@echo off
REM ===========================================================================
REM  Build a PORTABLE copy of this app, for someone who has no Python.
REM
REM  Run this ONCE on your own computer, with internet.
REM  It downloads a private copy of Python, installs the packages into it,
REM  copies the app, and zips the lot onto your Desktop.
REM
REM  The person you send it to just unzips the folder and double-clicks a
REM  launcher. They install nothing.
REM
REM  Works for Windows 64-bit. The finished zip is roughly 150 MB, so send it
REM  by Google Drive, OneDrive, WeTransfer or a flash disk, not WhatsApp.
REM
REM  This file also works inside the todo_dashboard folder: copy it there and
REM  The same file sits in the Loan Desk folder and builds that one.
REM ===========================================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Building a portable copy

REM ---- name things after the folder this script sits in -------------------
for %%I in ("%~dp0.") do set APPDIRNAME=%%~nxI
set "APPNAME=Option Desk"
set "ICONFILE=option_desk.ico"
set "SAFENAME=%APPNAME: =%"
set PYVER=3.11.9
set BUILD=%USERPROFILE%\Desktop\%SAFENAME%_portable
set OUTZIP=%USERPROFILE%\Desktop\%SAFENAME%_portable.zip

echo.
echo   Building a portable %APPNAME%
echo   Destination: %BUILD%
echo   This takes 5 to 15 minutes and downloads about 250 MB.
echo.
pause

if exist "%BUILD%" (
  echo Removing the previous build...
  rmdir /s /q "%BUILD%"
)
mkdir "%BUILD%\python" 2>nul
mkdir "%BUILD%\app" 2>nul

REM ---- 1. a private copy of Python ---------------------------------------
echo [1/6] Downloading Python %PYVER% (embeddable)...
powershell -NoProfile -Command ^
  "$ErrorActionPreference='Stop';" ^
  "Invoke-WebRequest 'https://www.python.org/ftp/python/%PYVER%/python-%PYVER%-embed-amd64.zip' -OutFile '%TEMP%\pyembed.zip'"
if errorlevel 1 goto :failed

echo       Unpacking...
powershell -NoProfile -Command ^
  "Expand-Archive -Path '%TEMP%\pyembed.zip' -DestinationPath '%BUILD%\python' -Force"
if errorlevel 1 goto :failed
del "%TEMP%\pyembed.zip" >nul 2>nul

REM  let this Python see installed packages
powershell -NoProfile -Command ^
  "$p = Get-ChildItem '%BUILD%\python\python*._pth' | Select-Object -First 1;" ^
  "(Get-Content $p) -replace '^#\s*import site','import site' | Set-Content $p"

REM ---- 2. pip -------------------------------------------------------------
echo [2/6] Adding pip...
powershell -NoProfile -Command ^
  "$ErrorActionPreference='Stop';" ^
  "Invoke-WebRequest 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%BUILD%\python\get-pip.py'"
if errorlevel 1 goto :failed
"%BUILD%\python\python.exe" "%BUILD%\python\get-pip.py" --no-warn-script-location -q
if errorlevel 1 goto :failed
del "%BUILD%\python\get-pip.py" >nul 2>nul

REM ---- 3. the packages ----------------------------------------------------
echo [3/6] Installing the packages. This is the slow part...
"%BUILD%\python\python.exe" -m pip install --no-warn-script-location -q -r "%~dp0requirements.txt"
if errorlevel 1 goto :failed

REM ---- 4. the app ---------------------------------------------------------
echo [4/6] Copying the app (your records in "data" are left out)...
robocopy "%~dp0." "%BUILD%\app" /e /xd data __pycache__ .git /xf *.pyc build_portable.bat share_app.bat >nul

REM ---- 5. launchers and instructions --------------------------------------
echo [5/6] Writing the launchers...

> "%BUILD%\%APPNAME% (Window).bat" echo @echo off
>>"%BUILD%\%APPNAME% (Window).bat" echo cd /d "%%~dp0"
>>"%BUILD%\%APPNAME% (Window).bat" echo start "" "%%~dp0python\pythonw.exe" "%%~dp0app\launch.py" --mode desktop

> "%BUILD%\%APPNAME% (Browser).bat" echo @echo off
>>"%BUILD%\%APPNAME% (Browser).bat" echo cd /d "%%~dp0"
>>"%BUILD%\%APPNAME% (Browser).bat" echo "%%~dp0python\python.exe" "%%~dp0app\launch.py" --mode web

> "%BUILD%\Create Desktop shortcut.bat" echo @echo off
>>"%BUILD%\Create Desktop shortcut.bat" echo powershell -NoProfile -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) '%APPNAME%.lnk')); $s.TargetPath=(Join-Path '%%~dp0' '%APPNAME% (Window).bat'); $s.WorkingDirectory='%%~dp0'; $s.IconLocation=(Join-Path '%%~dp0' 'app\assets\%ICONFILE%'); $s.Save()"
>>"%BUILD%\Create Desktop shortcut.bat" echo echo Shortcut created on the Desktop.
>>"%BUILD%\Create Desktop shortcut.bat" echo pause

> "%BUILD%\READ ME FIRST.txt" echo %APPNAME% - portable copy
>>"%BUILD%\READ ME FIRST.txt" echo ==============================
>>"%BUILD%\READ ME FIRST.txt" echo.
>>"%BUILD%\READ ME FIRST.txt" echo Nothing needs to be installed. Python is already inside this folder.
>>"%BUILD%\READ ME FIRST.txt" echo.
>>"%BUILD%\READ ME FIRST.txt" echo 1. Unzip this folder somewhere you will keep it, for example the Desktop.
>>"%BUILD%\READ ME FIRST.txt" echo    Do not run it from inside the zip file.
>>"%BUILD%\READ ME FIRST.txt" echo 2. Double-click  "%APPNAME% (Window).bat"
>>"%BUILD%\READ ME FIRST.txt" echo    If nothing appears after a minute, use "%APPNAME% (Browser).bat"
>>"%BUILD%\READ ME FIRST.txt" echo    instead: it opens in your web browser.
>>"%BUILD%\READ ME FIRST.txt" echo 3. If Windows shows "Windows protected your PC", click More info,
>>"%BUILD%\READ ME FIRST.txt" echo    then Run anyway.
>>"%BUILD%\READ ME FIRST.txt" echo.
>>"%BUILD%\READ ME FIRST.txt" echo Optional: double-click "Create Desktop shortcut.bat" to put an icon
>>"%BUILD%\READ ME FIRST.txt" echo on the Desktop.
>>"%BUILD%\READ ME FIRST.txt" echo.
>>"%BUILD%\READ ME FIRST.txt" echo The first start takes longer than the rest. Everything you enter is
>>"%BUILD%\READ ME FIRST.txt" echo saved in the "app\data" folder inside this folder. Copy that folder
>>"%BUILD%\READ ME FIRST.txt" echo to back your records up.

REM ---- 6. zip -------------------------------------------------------------
echo [6/6] Zipping (this also takes a while)...
if exist "%OUTZIP%" del "%OUTZIP%"
powershell -NoProfile -Command ^
  "Compress-Archive -Path '%BUILD%' -DestinationPath '%OUTZIP%' -Force"
if errorlevel 1 goto :failed

echo.
echo   Done.
echo.
echo   Send this file:   %OUTZIP%
echo   Built folder:     %BUILD%
echo.
echo   Test it first: open the built folder and double-click
echo   "%APPNAME% (Window).bat".
echo.
pause
exit /b 0

:failed
echo.
echo   The build failed at the step above.
echo   Check your internet connection and run this file again.
echo.
pause
exit /b 1
