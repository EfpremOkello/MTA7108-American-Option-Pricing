LOAN DESK
=========
Loan amortization schedules, client PDFs and a loan portfolio dashboard.
Runs on your own computer. Nothing is sent anywhere.


SETTING IT UP (about 10 minutes, once)
--------------------------------------
1. Unzip this folder somewhere you will keep it, for example the Desktop.
   Right-click the zip file > Extract All.

2. Install Python, if the computer does not already have it:
   - Go to  https://www.python.org/downloads/
   - Download Python for Windows and run the installer.
   - IMPORTANT: on the first screen tick "Add python.exe to PATH",
     then click "Install Now".

3. Open the unzipped "MTA7108-American-Option-Pricing" folder and double-click  install.bat
   It installs what the app needs and puts shortcuts on the Desktop.
   If Windows shows a blue "Windows protected your PC" box, click
   "More info" then "Run anyway".


RUNNING IT
----------
Double-click one of the Desktop shortcuts:

  Option Desk            the app in its own window
  Option Desk (Web)      the app in your web browser, this computer only
  Option Desk (Network)  in the browser, and other devices on the same
                       network can open the address it prints

Or from the folder: double-click  run_dashboard.bat


USING IT
--------
New schedule   Enter the client's details and the loan terms (amount, interest
               rate, period, repayment frequency). The repayment table appears
               as you type. Click "Generate PDF" to issue the client's schedule:
               it gets a serial number like LN-2026-000001, is saved in
               data\generated_pdfs, and the client is added to the register.

Portfolio      How the loans are performing on any date: outstanding balance,
               portfolio at risk (PAR 30), collection rate, arrears, expected
               collections, and a loan book you can search and download.

Repayments     Record money received from a client. Each payment gets a receipt
               number and updates the portfolio figures.

Client register  Every schedule issued, with a CSV download.


WHERE THE RECORDS ARE KEPT
--------------------------
Everything is in the "data" folder inside MTA7108-American-Option-Pricing:

  data\client_register.csv   one line per schedule issued
  data\repayments.csv        one line per repayment received
  data\generated_pdfs\       a copy of every client PDF
  data\serials.json          the last serial number used

Copy that "data" folder to back it up. To move the app to another computer,
copy the whole MTA7108-American-Option-Pricing folder, then run install.bat there.


IF SOMETHING DOES NOT WORK
--------------------------
"python is not recognized"
    Python is not installed, or "Add python.exe to PATH" was not ticked during
    installation. Reinstall Python with that box ticked.

The window opens and closes immediately
    Open the folder, then look in  data\app.log  for the error.

Nothing happens when you double-click the shortcut
    Open Command Prompt, then type these two lines:
        cd /d "%USERPROFILE%\Desktop\MTA7108-American-Option-Pricing"
        python launch.py --mode web
    The browser version will open and any error message will be visible.

The Network mode is not reachable from a phone
    Allow Python through Windows Firewall when it asks, and make sure both
    devices are on the same Wi-Fi.
