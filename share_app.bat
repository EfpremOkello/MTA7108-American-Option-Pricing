@echo off
REM ---------------------------------------------------------------------------
REM  Makes a clean copy of Option Desk to send to someone else.
REM  Your client records (the "data" folder) are left out on purpose.
REM  The zip lands on your Desktop as  OptionDesk_share.zip
REM ---------------------------------------------------------------------------
cd /d "%~dp0"
title Package Option Desk for sharing

set SRC=%TEMP%\OptionDesk_share\MTA7108-American-Option-Pricing
set OUT=%USERPROFILE%\Desktop\OptionDesk_share.zip

if exist "%TEMP%\OptionDesk_share" rmdir /s /q "%TEMP%\OptionDesk_share"
mkdir "%SRC%"

echo Copying the app files (leaving out your records)...
robocopy "%~dp0." "%SRC%" /e /xd data __pycache__ .git /xf *.pyc >nul

if exist "%OUT%" del "%OUT%"
echo Zipping...
powershell -NoProfile -Command "Compress-Archive -Path '%SRC%' -DestinationPath '%OUT%' -Force"

rmdir /s /q "%TEMP%\OptionDesk_share"

echo.
echo  Done. Send this file:
echo     %OUT%
echo.
echo  Tell them to unzip it, then double-click install.bat inside the folder.
echo  README_FIRST.txt in the folder explains the rest.
pause
