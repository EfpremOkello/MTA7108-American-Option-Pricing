"""
Creates Option Desk shortcuts (with the app icon) on your Desktop and in the Start menu:

    Option Desk              opens the desktop app window
    Option Desk (Web)        opens the web dashboard in your browser (this computer)
    Option Desk (Network)    web dashboard that phones/other PCs on your network can open

Run once:  python install_shortcuts.py
Windows only (uses PowerShell to write the .lnk files).
"""

import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ICON = BASE / "assets" / "option_desk.ico"
LAUNCH = BASE / "launch.py"


def exe(windowless):
    p = Path(sys.executable)
    if windowless and (p.parent / "pythonw.exe").exists():
        return str(p.parent / "pythonw.exe")
    if not windowless and p.name.lower() == "pythonw.exe":
        return str(p.parent / "python.exe")
    return str(p)


SHORTCUTS = [
    ("Option Desk", exe(True), f'"{LAUNCH}" --mode desktop', "Loan amortization and portfolio (desktop)"),
    ("Option Desk (Web)", exe(False), f'"{LAUNCH}" --mode web', "Option Desk web dashboard"),
    ("Option Desk (Network)", exe(False), f'"{LAUNCH}" --mode web --network',
     "Option Desk web dashboard for devices on your network"),
]


def ps_quote(s):
    return "'" + str(s).replace("'", "''") + "'"


def main():
    if sys.platform != "win32":
        print("Shortcuts are created on Windows only. Start the app with: python launch.py")
        return
    lines = [
        "$ws = New-Object -ComObject WScript.Shell",
        "$desk = [Environment]::GetFolderPath('Desktop')",
        "$menu = Join-Path ([Environment]::GetFolderPath('Programs')) 'Option Desk'",
        "New-Item -ItemType Directory -Force -Path $menu | Out-Null",
    ]
    for name, target, args, desc in SHORTCUTS:
        for folder in ("$desk", "$menu"):
            if folder == "$desk" and name == "Option Desk (Network)":
                continue  # keep the Desktop tidy; this one lives in the Start menu
            lines += [
                f"$s = $ws.CreateShortcut((Join-Path {folder} {ps_quote(name + '.lnk')}))",
                f"$s.TargetPath = {ps_quote(target)}",
                f"$s.Arguments = {ps_quote(args)}",
                f"$s.WorkingDirectory = {ps_quote(BASE)}",
                f"$s.IconLocation = {ps_quote(str(ICON) + ',0')}",
                f"$s.Description = {ps_quote(desc)}",
                "$s.Save()",
            ]
    lines.append("Write-Output $desk")
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-Command", "; ".join(lines)], capture_output=True, text=True)
    if r.returncode != 0:
        print("Could not create shortcuts:\n", r.stderr)
        sys.exit(1)
    print(f"Shortcuts created on your Desktop ({r.stdout.strip()}) and in Start menu > Option Desk:")
    for name, *_ in SHORTCUTS:
        print("  -", name)


if __name__ == "__main__":
    main()
