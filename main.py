#!/usr/bin/env python3
"""Dread Core 1.0.9 terminal launcher.

Authorized security-lab console. Browser camera, microphone and location
features remain permission-based and require explicit user interaction.
"""
import os
import re
import shutil
import subprocess
import threading
import time
import webbrowser
import socket
from urllib.request import urlopen
from werkzeug.serving import make_server

from server.app import app, CONFIG, PORTAL_TOKEN, SHARE_TOKENS

# ANSI colors
RESET="\033[0m"; BOLD="\033[1m"
PURPLE="\033[38;5;141m"; MAGENTA="\033[38;5;207m"; CYAN="\033[38;5;51m"
GREEN="\033[38;5;82m"; YELLOW="\033[38;5;220m"; RED="\033[38;5;203m"; WHITE="\033[97m"; DIM="\033[2m"

SERVER_THREAD=None
SERVER_STARTED=False
SERVER_INSTANCE=None
TUNNEL_PROCESS=None
TUNNEL_URL=None

ASCII_ART=r'''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠖⠉⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣀⣀⣀⣀⣀⡠⣤⣴⣾⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣶⣠⣤⡤⠤⠀⠀⠀
⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⠀⠀⠀⠀⠀
⠀⢀⣠⣼⣟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀
⠈⠀⠀⠈⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢳⣄⣀⠀⠀
⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠁⠀⠀⠀
⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⠿⠾⢧⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⠀⣀⣤⣯⣧⠀⠀⣀⡀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⢀⡿⠿⠟⠻⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⢰⣿⠃⢿⣯⣵⡿⠿⠿⠆⠀⣨⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢿⡭⡄⠀⠀⠀⠀
⠀⠀⢀⠂⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡄⠀⠀⠀⠀⠸⣿⣧⢸⣿⡹⣇⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⣄⡀⠀⠘⣿⣗⢿⣿⣿⡀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣴⣴⣿⣿⣾⣿⣿⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠋⠀⠀⠿⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⢿⡍⠉⠛⠿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡤⠤⣤⣀⠀⠀⠀⠀⠀⢁⣴⣿⣿⣿⣿⣿⣟⡿⣿⣿⣿⠄⠀⠁⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⠋⠠⣤⣬⣿⣷⠛⠛⠻⣶⣿⣿⢟⣽⣿⣿⣿⣏⠀⢠⣿⣿⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠿⣿⣿⣿⣿⠿⠿⠿⣻⣿⠉⠉⠀⠀⠈⢿⣧⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠒⠯⠿⠖⠀⠀⠀⠀⠘⠛⠙⠛⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀'''


def clear_screen():
    os.system("clear")


def cprint(text="", color=WHITE, bold=False):
    print((BOLD if bold else "") + color + text + RESET)


def draw_banner():
    print(PURPLE + ASCII_ART + RESET)
    cprint("", WHITE)
    cprint("╔══════════════════════════════════════════════════════════════════════╗", PURPLE, True)
    cprint("║                 D R E A D   C O R E   //   1.0.5                  ║", MAGENTA, True)
    cprint("║                   AUTHORIZED SECURITY LAB                          ║", CYAN, True)
    cprint("╚══════════════════════════════════════════════════════════════════════╝", PURPLE, True)


def local_url():
    return f"http://127.0.0.1:{CONFIG['port']}"


def server_is_running():
    global SERVER_STARTED
    if SERVER_INSTANCE is not None and SERVER_THREAD is not None and SERVER_THREAD.is_alive():
        SERVER_STARTED = True
        return True
    # Also recognize a Dread Core server that was started earlier.
    try:
        with socket.create_connection((CONFIG["host"], int(CONFIG["port"])), timeout=0.35):
            SERVER_STARTED = True
            return True
    except OSError:
        SERVER_STARTED = False
        return False


def run_server():
    global SERVER_INSTANCE
    SERVER_INSTANCE = make_server(CONFIG["host"], int(CONFIG["port"]), app, threaded=True)
    SERVER_INSTANCE.serve_forever()


def start_localhost():
    global SERVER_THREAD, SERVER_STARTED
    if server_is_running():
        cprint(f"\n  ● LOCALHOST SERVER: ALREADY ONLINE", YELLOW, True)
        cprint(f"  → {local_url()}", CYAN, True)
        return
    cprint("\n  ◈ Starting localhost server...", CYAN)
    SERVER_STARTED = False
    SERVER_THREAD = threading.Thread(target=run_server, daemon=True, name="dread-core-server")
    SERVER_THREAD.start()
    deadline = time.time() + 3.0
    while time.time() < deadline:
        if SERVER_INSTANCE is not None and server_is_running():
            SERVER_STARTED = True
            cprint("  ● LOCALHOST SERVER: ONLINE", GREEN, True)
            cprint(f"  → {local_url()}", CYAN, True)
            return
        time.sleep(0.1)
    if server_is_running():
        SERVER_STARTED = True
        cprint("  ● LOCALHOST SERVER: ONLINE", GREEN, True)
        cprint(f"  → {local_url()}", CYAN, True)
    else:
        cprint("  ● LOCALHOST SERVER: FAILED TO START", RED, True)
        cprint(f"  Port {CONFIG['port']} may already be occupied by another program.", YELLOW)


def open_localhost():
    if not server_is_running():
        cprint("\n  ● Localhost is not running. Select [1] first.", YELLOW)
        return
    url=local_url()
    cprint(f"\n  ◈ Opening {url}", CYAN)
    try: webbrowser.open(url)
    except Exception: cprint(f"  Open manually: {url}", YELLOW)


def start_cloudflare_tunnel():
    global TUNNEL_PROCESS, TUNNEL_URL
    if not server_is_running():
        cprint("\n  ● Start localhost with [1] before creating a tunnel.", YELLOW)
        return
    if TUNNEL_PROCESS and TUNNEL_PROCESS.poll() is None:
        cprint(f"\n  ● Tunnel already running: {TUNNEL_URL or 'starting...'}", YELLOW)
        return
    if not shutil.which("cloudflared"):
        cprint("\n  ● cloudflared is not installed or not in PATH.", RED, True)
        cprint("  Install it on Kali, then select [3] again.", YELLOW)
        return
    cprint("\n  ◈ Starting Cloudflare Quick Tunnel...", CYAN, True)
    try:
        TUNNEL_PROCESS=subprocess.Popen(["cloudflared","tunnel","--url",local_url(),"--no-autoupdate"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
    except OSError as exc:
        cprint(f"  ● Failed to start cloudflared: {exc}", RED); return
    pattern=re.compile(r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com")
    deadline=time.time()+30
    captured=[]
    while time.time()<deadline:
        if TUNNEL_PROCESS.poll() is not None: break
        line=TUNNEL_PROCESS.stdout.readline()
        if line:
            captured.append(line.rstrip())
            match=pattern.search(line)
            if match:
                TUNNEL_URL=match.group(0)
                cprint("\n  ╔════════════════════════════════════════════════════════════════╗", GREEN, True)
                cprint("  ║                  PUBLIC TUNNEL READY                          ║", GREEN, True)
                cprint("  ╚════════════════════════════════════════════════════════════════╝", GREEN, True)
                cprint(f"  SHARE URL → {TUNNEL_URL}", CYAN, True)
                cprint("  Authorized testing only; browser permissions still apply.", YELLOW)
                try: webbrowser.open(TUNNEL_URL)
                except Exception: pass
                return
        else: time.sleep(.1)
    cprint("\n  ● No public Cloudflare URL was detected.", RED, True)
    if captured: cprint("\n"+"\n".join(captured[-8:]), DIM)
    if TUNNEL_PROCESS and TUNNEL_PROCESS.poll() is None: TUNNEL_PROCESS.terminate()
    TUNNEL_PROCESS=None; TUNNEL_URL=None


def stop_cloudflare_tunnel():
    global TUNNEL_PROCESS, TUNNEL_URL
    if TUNNEL_PROCESS and TUNNEL_PROCESS.poll() is None:
        TUNNEL_PROCESS.terminate()
        try: TUNNEL_PROCESS.wait(timeout=3)
        except subprocess.TimeoutExpired: TUNNEL_PROCESS.kill()
        cprint("\n  ● Cloudflare tunnel stopped.", GREEN)
    else: cprint("\n  ● No active Cloudflare tunnel.", YELLOW)
    TUNNEL_PROCESS=None; TUNNEL_URL=None


def show_status():
    cprint("\n  ┌──────────────────────── SERVER STATUS ────────────────────────┐", PURPLE, True)
    cprint(f"  │ Localhost : {'ONLINE' if server_is_running() else 'OFFLINE'}", GREEN if server_is_running() else RED)
    cprint(f"  │ Local URL : {local_url()}", CYAN)
    tunnel_live=bool(TUNNEL_PROCESS and TUNNEL_PROCESS.poll() is None)
    cprint(f"  │ Tunnel    : {'ONLINE' if tunnel_live else 'OFFLINE'}", GREEN if tunnel_live else RED)
    if TUNNEL_URL: cprint(f"  │ Share URL : {TUNNEL_URL}", CYAN)
    cprint("  └──────────────────────────────────────────────────────────────┘", PURPLE, True)


def list_saved_results():
    base = Path(__file__).resolve().parent / "data"
    sessions = base / "sessions"
    captures = base / "captures"
    session_files = sorted([p for p in sessions.glob("*.json") if p.is_file()], reverse=True)
    capture_files = sorted([p for p in captures.iterdir() if p.is_file() and p.name != ".gitkeep"], reverse=True)

    cprint("\n  ┌──────────────────────── SAVED RESULTS ───────────────────────┐", PURPLE, True)
    cprint(f"  │ Sessions : {len(session_files):<48}│", CYAN)
    cprint(f"  │ Evidence : {len(capture_files):<47}│", CYAN)
    cprint("  └──────────────────────────────────────────────────────────────┘", PURPLE, True)

    if session_files:
        cprint("\n  ◈ SESSIONS", MAGENTA, True)
        for p in session_files[:20]:
            try:
                data=json.loads(p.read_text(encoding="utf-8"))
                sid=data.get("session_id", p.stem)
                created=data.get("created_at", "unknown")
                cprint(f"    • {sid}  [{created}]", WHITE)
            except Exception:
                cprint(f"    • {p.name}", WHITE)
        if len(session_files) > 20:
            cprint(f"    … and {len(session_files)-20} more", DIM)
    else:
        cprint("\n  ◈ SESSIONS: none saved yet", YELLOW)

    if capture_files:
        cprint("\n  ◈ EVIDENCE / CAPTURES", MAGENTA, True)
        for p in capture_files[:20]:
            size=p.stat().st_size
            cprint(f"    • {p.name}  [{size:,} bytes]", WHITE)
        if len(capture_files) > 20:
            cprint(f"    … and {len(capture_files)-20} more", DIM)
    else:
        cprint("\n  ◈ EVIDENCE / CAPTURES: none saved yet", YELLOW)


def export_saved_results():
    base=Path(__file__).resolve().parent / "data"
    output_dir=base / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp=time.strftime("%Y%m%d-%H%M%S")
    output=output_dir / f"dread-core-results-{stamp}.zip"
    files=[]
    for folder in (base/"sessions", base/"captures"):
        if folder.exists():
            files.extend([p for p in folder.iterdir() if p.is_file() and p.name != ".gitkeep"])
    if not files:
        cprint("\n  ● No saved results to export.", YELLOW, True)
        return
    import zipfile
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f"{f.parent.name}/{f.name}")
    cprint("\n  ● RESULTS EXPORT CREATED", GREEN, True)
    cprint(f"  → {output}", CYAN, True)
    cprint(f"  → {len(files)} file(s) included", WHITE)


def draw_menu():
    cprint("\n╔══════════════════════════════════════════════════════════════════════╗", PURPLE, True)
    cprint("║                         CONTROL MENU                               ║", MAGENTA, True)
    cprint("╚══════════════════════════════════════════════════════════════════════╝", PURPLE, True)
    cprint("  [1]  Start Localhost Server", CYAN)
    cprint("  [2]  Open Localhost", CYAN)
    cprint("  [3]  Start Cloudflare Tunnel", MAGENTA)
    cprint("  [4]  Stop Cloudflare Tunnel", MAGENTA)
    cprint("  [5]  Server Status", YELLOW)
    cprint("  [6]  View Saved Results", MAGENTA)
    cprint("  [7]  Export Results (ZIP)", MAGENTA)
    cprint("  [8]  Share Permission Links", GREEN)
    cprint("  [9]  Clear Screen / Redraw", PURPLE)
    cprint("  [10] Exit", RED)
    cprint("──────────────────────────────────────────────────────────────────────", PURPLE)


def show_share_links():
    if not TUNNEL_URL:
        cprint("\n  ● Start the Cloudflare Tunnel first with option [3].", YELLOW, True)
        return
    base = TUNNEL_URL.rstrip("/")
    portal = f"{base}/test/{PORTAL_TOKEN}"
    cprint("\n  ╔══════════════════════════════════════════════════════════════╗", PURPLE, True)
    cprint("  ║              AUTHORIZED TEST / SHARE LINKS                ║", MAGENTA, True)
    cprint("  ╚══════════════════════════════════════════════════════════════╝", PURPLE, True)
    cprint("\n  PARTICIPANT PORTAL — SHARE THIS LINK", GREEN, True)
    cprint(f"  → {portal}", WHITE, True)
    cprint("\n  CAMERA PERMISSION TEST", CYAN, True)
    cprint(f"  → {base}/share/camera/{SHARE_TOKENS['camera']}", WHITE)
    cprint("\n  MICROPHONE PERMISSION TEST", CYAN, True)
    cprint(f"  → {base}/share/microphone/{SHARE_TOKENS['microphone']}", WHITE)
    cprint("\n  LOCATION PERMISSION TEST", CYAN, True)
    cprint(f"  → {base}/share/location/{SHARE_TOKENS['location']}", WHITE)
    cprint("\n  The PARTICIPANT PORTAL is the recommended public link.", DIM)
    cprint("  Permissions require explicit user interaction in the browser.", DIM)
    try:
        webbrowser.open(portal)
        cprint("  ● Participant portal opened in your browser.", GREEN)
    except Exception:
        pass


def pause():
    try: input(f"\n  {DIM}Press Enter to return to menu...{RESET}")
    except (KeyboardInterrupt,EOFError): pass


def redraw():
    clear_screen(); draw_banner()
    cprint(f"  LOCAL  → {local_url()}", CYAN)
    cprint(f"  STATUS → {'ONLINE' if server_is_running() else 'OFFLINE'}", GREEN if server_is_running() else YELLOW)
    if TUNNEL_URL: cprint(f"  SHARE  → {TUNNEL_URL}", CYAN, True)


def stop_localhost():
    global SERVER_INSTANCE, SERVER_STARTED
    if SERVER_INSTANCE is not None:
        try:
            SERVER_INSTANCE.shutdown()
        except Exception:
            pass
        SERVER_INSTANCE = None
    SERVER_STARTED = False


def shutdown():
    stop_cloudflare_tunnel()
    stop_localhost()
    clear_screen()
    cprint("Dread Core stopped.", PURPLE, True)


def main():
    redraw()
    cprint("\n  Login: admin / admin", WHITE)
    cprint("  Select [1] to start the local web console.", YELLOW)
    while True:
        draw_menu()
        try: choice=input(f"  {MAGENTA}{BOLD}dread-core > {RESET}").strip().lower()
        except (KeyboardInterrupt,EOFError): shutdown(); break
        if choice=="1": start_localhost(); pause()
        elif choice=="2": open_localhost(); pause()
        elif choice=="3": start_cloudflare_tunnel(); pause()
        elif choice=="4": stop_cloudflare_tunnel(); pause()
        elif choice=="5": show_status(); pause()
        elif choice=="6": list_saved_results(); pause()
        elif choice=="7": export_saved_results(); pause()
        elif choice=="8": show_share_links(); pause()
        elif choice=="9": redraw()
        elif choice in {"10","q","quit","exit"}: shutdown(); break
        else: cprint("\n  ● Invalid option. Choose 1-10.", RED); time.sleep(.8)

if __name__=="__main__": main()
