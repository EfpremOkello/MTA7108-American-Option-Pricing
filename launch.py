"""
Option Desk launcher.

    python launch.py                  desktop window (default)
    python launch.py --mode web       web dashboard in your browser, this computer only
    python launch.py --mode web --network
                                      web dashboard other devices on your network can open

The desktop mode starts the dashboard server in the background and shows it in its
own window (pywebview, using Microsoft Edge WebView2). Closing the window stops it.
The web mode keeps a console window open that shows the address; close it to stop.
"""

import argparse
import os
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

BASE = Path(__file__).resolve().parent
APP = BASE / "app.py"
ICON = BASE / "assets" / "option_desk.ico"
LOG_DIR = BASE / "data"
APP_NAME = "Option Desk"


def free_port(preferred=None):
    if preferred:
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", preferred)) != 0:
                return preferred
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def lan_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def python_console_exe():
    """python.exe even when launched with pythonw.exe (streamlit needs a normal interpreter)."""
    exe = Path(sys.executable)
    if exe.name.lower() == "pythonw.exe" and (exe.parent / "python.exe").exists():
        return str(exe.parent / "python.exe")
    return sys.executable


def start_server(port, address, mode, quiet):
    cmd = [python_console_exe(), "-m", "streamlit", "run", str(APP),
           "--server.port", str(port), "--server.address", address,
           "--server.headless", "true", "--browser.gatherUsageStats", "false"]
    env = dict(os.environ, OPTIONDESK_MODE=mode)
    kwargs = {"cwd": str(BASE), "env": env}
    if quiet:
        LOG_DIR.mkdir(exist_ok=True)
        log = open(LOG_DIR / "app.log", "w", encoding="utf-8")
        kwargs.update(stdout=log, stderr=subprocess.STDOUT)
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return subprocess.Popen(cmd, **kwargs)


def wait_until_ready(port, proc, timeout=90):
    url = f"http://127.0.0.1:{port}/_stcore/health"
    end = time.time() + timeout
    while time.time() < end:
        if proc.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return True
        except OSError:
            pass
        time.sleep(0.4)
    return False


LOADING_HTML = """<!doctype html><html><head><style>
html,body{margin:0;height:100%;background:#0B0F17;color:#E6E9EF;
font-family:'Segoe UI',system-ui,sans-serif;display:grid;place-items:center}
.box{text-align:center}.spin{width:34px;height:34px;border:3px solid #232B3B;
border-top-color:#3B82F6;border-radius:50%;animation:s 0.9s linear infinite;margin:0 auto 18px}
@keyframes s{to{transform:rotate(360deg)}}p{color:#8B93A7;font-size:13px;margin:6px 0 0}
</style></head><body><div class="box"><div class="spin"></div>
<div style="font-size:18px;font-weight:600">Option Desk</div><p>Starting the dashboard...</p>
</div></body></html>"""


def run_desktop():
    try:
        import webview
    except ImportError:
        print("pywebview is not installed. Run:  python -m pip install pywebview")
        print("Opening the web dashboard instead.")
        return run_web(network=False)

    if os.name == "nt":
        try:  # own taskbar icon instead of the Python one
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("OptionDesk.Dashboard")
        except Exception:
            pass

    port = free_port()
    proc = start_server(port, "127.0.0.1", "desktop", quiet=True)
    window = webview.create_window(APP_NAME, html=LOADING_HTML, width=1440, height=920,
                                   min_size=(1024, 680), background_color="#0B0F17",
                                   text_select=True)

    def boot():
        if wait_until_ready(port, proc):
            window.load_url(f"http://127.0.0.1:{port}")
        else:
            window.load_html(LOADING_HTML.replace(
                "Starting the dashboard...",
                f"The dashboard could not start. See {LOG_DIR / 'app.log'}"))

    webview.settings["ALLOW_DOWNLOADS"] = True
    try:
        webview.start(boot, icon=str(ICON) if ICON.exists() else None)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def run_web(network=False):
    port = free_port(8501)
    address = "0.0.0.0" if network else "127.0.0.1"
    proc = start_server(port, address, "web", quiet=False)
    print(f"\n  {APP_NAME} is starting...")
    if not wait_until_ready(port, proc):
        print("  The dashboard could not start. Check the messages above.")
        proc.wait()
        return
    local = f"http://localhost:{port}"
    print(f"\n  {APP_NAME} web dashboard is running")
    print(f"    On this computer:     {local}")
    if network:
        print(f"    On your network:      http://{lan_ip()}:{port}")
        print("    (Allow Python through Windows Firewall if asked.)")
    print("\n  Close this window or press Ctrl+C to stop.\n")
    webbrowser.open(local)
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Start Option Desk")
    ap.add_argument("--mode", choices=["desktop", "web"], default="desktop")
    ap.add_argument("--network", action="store_true",
                    help="web mode: let other devices on your network open the dashboard")
    a = ap.parse_args()
    if a.mode == "web":
        run_web(a.network)
    else:
        run_desktop()
