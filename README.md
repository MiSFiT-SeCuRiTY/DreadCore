# 🩸 DREAD CORE
<img width="1344" height="768" alt="dread-core-logo png" src="https://github.com/user-attachments/assets/ad9e6bf5-e386-40a0-ad76-a80092f9a707" />

### 🔐 Permission-Based Browser Security Testing Toolkit

**Dread Core** is a professional browser security testing toolkit built for **authorized security assessments, privacy testing, and browser permission testing**.

It provides a terminal-driven workflow with a Flask web interface for testing browser-controlled permissions such as:

- 📷 Camera
- 🎙️ Microphone
- 📍 Location
- 💻 Device information
- 🌐 Network information
- 📊 Session results
- 📦 Result exporting
- ☁️ Public HTTPS testing through Cloudflare Quick Tunnel

Dread Core is designed for **authorized testing environments** such as labs, demonstrations, personal devices, security research, and penetration-testing engagements where the participant has consented.

---

## ✨ Features

### 🖥️ Professional Terminal Interface

Dread Core uses a colorful interactive terminal menu instead of requiring users to remember multiple commands.

Current menu:

```text
╔══════════════════════════════════════════════════════════╗
║                       DREAD CORE                          ║
╚══════════════════════════════════════════════════════════╝

[1]  🚀 Start Localhost Server
[2]  🌐 Open Localhost
[3]  ☁️  Start Cloudflare Tunnel
[4]  🛑 Stop Cloudflare Tunnel
[5]  📊 Server Status
[6]  📁 View Saved Results
[7]  📦 Export Results (ZIP)
[8]  🔗 Share Permission Links
[9]  🔄 Clear Screen / Redraw
[10] 🚪 Exit
```

---

# 🌐 Browser Permission Testing

Dread Core provides dedicated participant pages for browser permission testing.

### 📷 Camera

The participant can explicitly continue into a camera test.

The browser displays its normal native camera permission prompt.

If permission is granted:

- Camera preview becomes available.
- A test snapshot can be taken.
- The snapshot can be saved to the authorized test session.

If permission is denied:

- The camera workspace remains locked.
- No camera functionality is available.

---

### 🎙️ Microphone

The microphone test uses the browser's native microphone permission system.

After explicit participation:

```text
CONTINUE
     ↓
Browser microphone permission
     ↓
Permission granted
     ↓
Audio test workspace
```

If permission is denied, the test remains locked.

---

### 📍 Location

The location test uses the browser's native Geolocation API.

After the participant explicitly continues:

- Browser location permission is requested.
- Latitude is displayed after successful authorization.
- Longitude is displayed.
- Accuracy is displayed.
- A Google Maps location link can be generated.
- The result is saved to the authorized session.

If permission is denied, the location functionality remains unavailable.

---

# 🔐 Consent & Security Model

Dread Core is designed around **browser-controlled permissions**.

It does **not** bypass browser permission systems.

The participant must explicitly interact with the page and the browser decides whether camera, microphone, or location access is allowed.

### Important

Dread Core should only be used when you have authorization to perform the security test.

Do not use it to:

- ❌ Trick people into granting permissions
- ❌ Bypass browser security
- ❌ Collect information without authorization
- ❌ Capture credentials
- ❌ Perform covert surveillance
- ❌ Impersonate legitimate services
- ❌ Deploy against people without consent

---

# ☁️ Cloudflare Quick Tunnel

Dread Core can expose the local Flask server through a temporary HTTPS URL using **Cloudflare Quick Tunnel**.

Example:

```text
https://example-random-name.trycloudflare.com
```

This is useful when testing browser permissions because browsers can enforce different security requirements for camera, microphone, and geolocation access.

### Start the tunnel

From the Dread Core menu:

```text
[3] Start Cloudflare Tunnel
```

Dread Core launches:

```bash
cloudflared tunnel --url http://localhost:8080
```

A temporary public URL is generated.

### ⚠️ Important

Cloudflare Quick Tunnel URLs are temporary.

When the tunnel is stopped or restarted, the URL can change.

Therefore, generate new permission links whenever a new tunnel URL is created.

---

# 🔗 Permission Sharing

Dread Core generates tokenized permission-testing URLs.

From the terminal:

```text
[8] Share Permission Links
```

The interface provides:

```text
🌐 Participant Portal
📷 Camera Permission
🎙️ Microphone Permission
📍 Location Permission
```

Example structure:

```text
https://YOUR-TUNNEL.trycloudflare.com/test/TOKEN
```

Camera:

```text
https://YOUR-TUNNEL.trycloudflare.com/share/camera/TOKEN
```

Microphone:

```text
https://YOUR-TUNNEL.trycloudflare.com/share/microphone/TOKEN
```

Location:

```text
https://YOUR-TUNNEL.trycloudflare.com/share/location/TOKEN
```

The tokens are generated automatically when the server starts.

---

# 🧑‍💻 Participant Portal

The participant portal provides a centralized interface for authorized browser testing.

It contains separate modules for:

```text
📷 Camera Session
🎙️ Audio Session
📍 Location Session
```

Each module opens its own secure testing page.

The participant UI is intentionally separated from the administrator dashboard.

---

# 🎨 Participant UI

The participant-facing interface can be customized independently.

Main participant templates:

```text
web/templates/
├── participant_portal.html
├── share.html
├── share_camera.html
├── share_microphone.html
└── share_location.html
```

### 🎨 Camera UI

Edit:

```text
web/templates/share_camera.html
```

You can customize:

- Logo
- Title
- Colors
- Buttons
- Instructions
- Cards
- Animations
- Camera workspace
- Permission messaging

---

### 🎙️ Microphone UI

Edit:

```text
web/templates/share_microphone.html
```

You can customize:

- Branding
- Colors
- Text
- Audio workspace
- Buttons
- Instructions
- Animations

---

### 📍 Location UI

Edit:

```text
web/templates/share_location.html
```

You can customize:

- Branding
- Colors
- Location information
- Permission instructions
- Map button
- Animations
- Layout

---

# ⚠️ Important: Do Not Change Routes Accidentally

The visual HTML can be changed without changing the generated URLs.

For example, you can redesign:

```text
share_camera.html
```

without changing:

```text
/share/camera/<token>
```

The URL structure is controlled by:

```text
server/app.py
```

Therefore:

### Safe to modify

```text
HTML
CSS
JavaScript
Colors
Fonts
Animations
Branding
Text
Layout
```

### Be careful modifying

```text
Flask routes
Token validation
Session endpoints
Upload endpoints
Authentication
```

Changing those can break the existing permission links.

---

# 🖥️ Administrator Dashboard

The administrator interface is separate from the participant interface.

The dashboard provides access to authorized test results and modules such as:

```text
📊 Dashboard
📁 Sessions
💻 Device
📍 Location
📷 Camera
🎙️ Microphone
🌐 Network
📑 Reports
⚙️ Settings
```

Changing the participant pages does **not** automatically change the administrator dashboard.

---

# 📁 Project Structure

```text
Dread-Core/
│
├── config.json
├── LICENSE
├── README.md
├── main.py
├── requirements.txt
│
├── server/
│   ├── __init__.py
│   └── app.py
│
└── web/
    ├── static/
    │   ├── css/
    │   ├── js/
    │   └── assets/
    │
    └── templates/
        ├── login.html
        ├── dashboard.html
        ├── sessions.html
        ├── device.html
        ├── location.html
        ├── camera.html
        ├── microphone.html
        ├── network.html
        ├── reports.html
        ├── settings.html
        │
        ├── participant_portal.html
        ├── share.html
        ├── share_camera.html
        ├── share_microphone.html
        └── share_location.html
```

Runtime data is automatically created when Dread Core runs:

```text
data/
├── captures/
├── exports/
└── sessions/
```

You do **not** need to manually create the `data` directory.

---

# 🐍 Requirements

Dread Core requires:

- 🐍 Python 3
- 🌐 Flask
- ☁️ Cloudflared (optional, for public HTTPS testing)
- 💻 Linux/Kali Linux recommended

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/MiSFiT-SeCuRiTY/DreadCore.git
```

Enter the directory:

```bash
cd DreadCore
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

For Kali Linux, you may prefer:

```bash
python3 -m pip install -r requirements.txt
```

---

# ☁️ Install Cloudflared

Cloudflare Tunnel is optional.

If you want public HTTPS permission testing, install:

```text
cloudflared
```

Verify:

```bash
cloudflared --version
```

If Cloudflare is not installed, Dread Core can still be used locally.

---

# 🚀 Starting Dread Core

Run:

```bash
python3 main.py
```

The Dread Core interface will appear.

Start the local server:

```text
[1] Start Localhost Server
```

Then open it:

```text
[2] Open Localhost
```

The local application will normally be available at:

```text
http://127.0.0.1:8080
```

---

# 🌐 Public HTTPS Testing

For authorized remote browser testing:

### 1. Start the server

```text
[1] Start Localhost Server
```

### 2. Start Cloudflare

```text
[3] Start Cloudflare Tunnel
```

### 3. Share permission links

```text
[8] Share Permission Links
```

Dread Core will display the generated URLs.

Use the participant portal for a centralized testing experience.

---

# 📊 Server Status

Use:

```text
[5] Server Status
```

to check the current server state.

This helps verify whether:

- Flask is running
- Cloudflare is running
- A public URL exists

---

# 📁 Saved Results

Use:

```text
[6] View Saved Results
```

to inspect stored authorized testing results.

Results are stored inside:

```text
data/
```

---

# 📦 Export Results

Use:

```text
[7] Export Results (ZIP)
```

Dread Core packages available test results into a ZIP archive.

Exports are stored in:

```text
data/exports/
```

---

# 🧹 Runtime Data

Dread Core automatically creates:

```text
data/captures/
data/exports/
data/sessions/
```

These directories contain runtime information generated during testing.

For GitHub repositories, do not commit private test data.

---

# ⚙️ Configuration

The main configuration file is:

```text
config.json
```

It can contain application settings such as:

- Application name
- Version
- Host
- Port
- Session settings
- Feature configuration

Always review configuration before deploying the project in a testing environment.

---

# 🔑 Authentication

The administrator interface uses an authentication layer.

The participant permission pages are separate from the administrator dashboard.

This separation allows:

```text
Administrator
      │
      ▼
Admin Dashboard
      │
      └── Test Results
           
Participant
      │
      ▼
Permission Testing Page
```

---

# 🎨 Branding

Dread Core can be rebranded for authorized internal security assessments.

Common customization locations include:

```text
web/templates/
web/static/
config.json
```

You can customize:

- 🩸 Dread Core branding
- 🎨 Colors
- 🖼️ Logos
- 🔤 Fonts
- ✨ Animations
- 📝 Text
- 🔘 Buttons
- 🧩 Cards
- 📐 Layout

---

# 🧩 Adding New Testing Modules

Dread Core uses a modular Flask structure.

A new module generally consists of:

```text
Flask route
     ↓
HTML template
     ↓
JavaScript interaction
     ↓
Session/result endpoint
     ↓
Stored result
```

For example:

```text
web/templates/
    new_module.html
```

and a corresponding route in:

```text
server/app.py
```

---

# 🛠️ Troubleshooting

## ❌ Localhost Does Not Open

Check whether the server is running:

```text
[5] Server Status
```

You can also test:

```bash
curl -I http://127.0.0.1:8080
```

If Flask is not running, start:

```text
[1] Start Localhost Server
```

---

## ❌ Cloudflare URL Does Not Open

First verify localhost:

```bash
curl -I http://127.0.0.1:8080
```

Then verify Cloudflare:

```bash
ps aux | grep cloudflared
```

You can also run:

```bash
cloudflared tunnel diag
```

Make sure the Cloudflare process is still running.

---

## ❌ Permission Prompt Does Not Appear

Check:

- 🌐 You are using HTTPS where required.
- 🔒 Browser permissions are not blocked.
- 📷 Camera permissions are allowed for the site.
- 🎙️ Microphone permissions are allowed for the site.
- 📍 Location permissions are allowed for the site.
- 🖥️ The operating system has not blocked the browser.

For Cloudflare Quick Tunnel, the generated URL should use:

```text
https://
```

---

## ❌ Old Cloudflare URL Stops Working

This is expected with Quick Tunnels.

Quick Tunnel URLs are temporary.

Start the tunnel again:

```text
[3] Start Cloudflare Tunnel
```

Then generate new links:

```text
[8] Share Permission Links
```

---

## ❌ `cloudflared` Command Not Found

Install Cloudflare Tunnel and verify:

```bash
cloudflared --version
```

Then restart Dread Core.

---

# 🔄 Updating Dread Core

When updating the project:

1. Stop Dread Core.
2. Replace the application files.
3. Keep your private runtime data backed up if required.
4. Start Dread Core again.
5. Generate fresh permission links if the server/tunnel has restarted.

---

# 🧹 GitHub Cleanup

Before pushing the project to GitHub, do **not** upload:

```text
__pycache__/
*.pyc
.venv/
venv/
data/captures/*
data/exports/*
data/sessions/*
*.log
```

Recommended `.gitignore`:

```gitignore
__pycache__/
*.py[cod]
*.pyo

.venv/
venv/
env/

data/captures/*
data/exports/*
data/sessions/*

*.log

.DS_Store
```

---

# 📌 Recommended GitHub Repository Contents

Your repository should contain:

```text
config.json
LICENSE
README.md
main.py
requirements.txt
server/
web/
.gitignore
```

Do not upload private testing results.

---

# 🧪 Version History

## 🩸 1.0.0

- 🎨 Unified professional participant UI
- 📷 Updated camera permission-testing page
- 🎙️ Updated microphone permission-testing page
- 📍 Updated location permission-testing page
- 🔐 Explicit browser permission workflow
- 🔒 Locked state when permission is denied
- 🌐 Cloudflare HTTPS support
- 🔗 Tokenized permission links
- 🧑‍💻 Participant portal
- 📊 Session result storage
- 📦 ZIP result export

---

# 🔐 Responsible Use

Dread Core is a security testing tool.

Use it only against:

- ✅ Your own devices
- ✅ Your own browser
- ✅ Authorized test environments
- ✅ Security labs
- ✅ Participants who have explicitly agreed to the test
- ✅ Systems where you have documented authorization

Do not use Dread Core for unauthorized surveillance, credential theft, deceptive phishing, or bypassing browser security controls.

The browser's native permission system must remain the authority over camera, microphone, and location access.

---

# 🛡️ Privacy

Dread Core is intended for controlled security testing.

Before running a test:

- Explain what is being tested.
- Obtain appropriate authorization.
- Avoid collecting unnecessary information.
- Protect stored results.
- Delete test data when it is no longer required.
- Never publish private participant data.

---

# 📜 License

See:

```text
LICENSE
```

for the license governing this project.

---

# ⚠️ Disclaimer

Dread Core is provided for **authorized security testing, research, education, and controlled laboratory environments**.

The developer is not responsible for misuse of this software.

You are responsible for ensuring that your use of Dread Core complies with applicable laws, policies, permissions, and organizational rules.

---

# 🩸 DREAD CORE

### Browser Security Testing • Permission Testing • Authorized Research

```text
██████╗ ██████╗ ███████╗ █████╗ ██████╗
██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗
██║  ██║██████╔╝█████╗  ███████║██║  ██║
██║  ██║██╔══██╗██╔══╝  ██╔══██║██║  ██║
██████╔╝██║  ██║███████╗██║  ██║██████╔╝
╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝
```

**Built for authorized browser security testing. 🔐🩸**
