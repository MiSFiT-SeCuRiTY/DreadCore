# Dread Core

**Dread Core 1.0.3** is a modern purple browser-based security testing console for Kali Linux and authorized security labs.

## Included in this release

- Modern responsive purple cyberpunk web UI
- Local authenticated control console
- Device/browser intelligence collection
- Automatic device-class detection for iPhone, iPad, Android, Windows, macOS and Linux browsers
- Browser geolocation request and session storage
- Camera permission request, live preview and user-triggered JPEG snapshot upload
- Microphone permission request, MediaRecorder recording and user-triggered WebM upload
- Browser network information
- Session archive
- Evidence file archive
- Individual downloads
- ZIP export
- Configurable upload limit
- GitHub-ready `.gitignore`
- MIT License
- Cloudflare Tunnel compatible local service

## Kali Linux

```bash
sudo apt update
sudo apt install -y python3 python3-venv
cd Dread-Core
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Open `http://127.0.0.1:8080`.

Initial local demo login:

```text
Username: admin
Password: admin
```

## Important browser security model

Camera, microphone and geolocation are protected by modern browsers. Dread Core **does not bypass or suppress those permission controls**. A module requests access only after the user performs the relevant action, and the browser decides whether access is granted.

Camera snapshots and microphone recordings are sent to the local evidence store only when the operator explicitly chooses the save action.

## Evidence

Generated evidence is stored locally under:

```text
data/sessions/
data/captures/
```

These directories are ignored by Git so personal test data is not accidentally published.

## Cloudflare Tunnel

For an authorized lab, a locally running instance can be exposed using `cloudflared`:

```bash
cloudflared tunnel --url http://127.0.0.1:8080
```

Use an authenticated Cloudflare setup for real deployments. Never expose this project publicly with `admin/admin`.

## GitHub

```bash
git init
git add .
git commit -m "Dread Core 1.0.3"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/Dread-Core.git
git push -u origin main
```

## Safety

Use Dread Core only against devices, browsers, networks and accounts that you own or are explicitly authorized to test. This project is not designed to defeat operating-system/browser permissions, steal credentials or tokens, or provide covert surveillance.

## License

MIT License.


## Terminal workflow

Run `python3 main.py` to open the Dread Core terminal interface. The launcher clears the screen and presents an ASCII-art control menu.

1. **Start Localhost Server** — starts the Flask console on `127.0.0.1:8080`.
2. **Open Localhost** — opens the local console in the default browser.
3. **Start Cloudflare Tunnel** — creates an authorized Quick Tunnel to the local console and prints the public share URL.
4. **Stop Cloudflare Tunnel** — stops the active tunnel.
5. **Server Status** — shows localhost and tunnel status.
6. **Clear Screen / Redraw** — clears the terminal and redraws the ASCII interface.
7. **Exit** — stops the tunnel and exits.

The public tunnel is intended for authorized security-lab use. Browser camera, microphone, and location access remains permission-based.
