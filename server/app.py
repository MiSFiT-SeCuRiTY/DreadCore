from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from functools import wraps
from pathlib import Path
from datetime import datetime
import json, io, zipfile, secrets, uuid

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
SESSIONS, CAPTURES = DATA/"sessions", DATA/"captures"
SESSIONS.mkdir(parents=True, exist_ok=True)
CAPTURES.mkdir(parents=True, exist_ok=True)
(SESSIONS/".gitkeep").touch(exist_ok=True)
(CAPTURES/".gitkeep").touch(exist_ok=True)
SHARE_TOKENS = {m: secrets.token_urlsafe(18) for m in ("camera", "microphone", "location")}
PORTAL_TOKEN = secrets.token_urlsafe(18)

CONFIG = json.loads((BASE/"config.json").read_text(encoding="utf-8"))
app = Flask(__name__, template_folder=str(BASE/"web/templates"), static_folder=str(BASE/"web/static"))
app.secret_key = secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = CONFIG.get("max_upload_mb",25) * 1024 * 1024

def auth(fn):
    @wraps(fn)
    def wrapped(*a, **kw):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return fn(*a, **kw)
    return wrapped

@app.context_processor
def context():
    return {"app_name":CONFIG["app_name"], "version":CONFIG["version"]}

@app.route("/")
def index():
    return redirect("/dashboard" if session.get("authenticated") else "/login")

@app.route("/login", methods=["GET","POST"])
def login():
    error=None
    if request.method=="POST":
        if request.form.get("username")==CONFIG["username"] and request.form.get("password")==CONFIG["password"]:
            session["authenticated"]=True
            return redirect("/dashboard")
        error="Invalid credentials"
    return render_template("login.html", error=error)

@app.get("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.get("/share")
def share_home():
    return render_template(
        "share.html",
        portal=url_for("participant_portal", token=PORTAL_TOKEN, _external=True),
        links={m: url_for("share_module", module=m, token=SHARE_TOKENS[m], _external=True) for m in SHARE_TOKENS}
    )

@app.get("/test/<token>")
def participant_portal(token):
    if not secrets.compare_digest(token, PORTAL_TOKEN):
        return "Invalid or expired test link", 404
    return render_template(
        "participant_portal.html",
        links={m: url_for("share_module", module=m, token=SHARE_TOKENS[m], _external=True) for m in SHARE_TOKENS}
    )

@app.get("/share/<module>/<token>")
def share_module(module, token):
    if module not in SHARE_TOKENS or not secrets.compare_digest(token, SHARE_TOKENS[module]):
        return "Invalid or expired share link", 404
    return render_template(f"share_{module}.html", module=module)

def valid_share(module, token):
    return module in SHARE_TOKENS and secrets.compare_digest(token, SHARE_TOKENS[module])

@app.post("/share/<module>/<token>/session")
def share_session(module, token):
    if not valid_share(module, token): return jsonify({"ok":False,"error":"Invalid share link"}),404
    data=request.get_json(silent=True) or {}
    sid=datetime.now().strftime("%Y%m%d-%H%M%S")+"-"+uuid.uuid4().hex[:8]
    data.update({"session_id":sid,"created_at":datetime.now().isoformat(timespec="seconds"),"module":module,"server_remote_address":request.remote_addr})
    (SESSIONS/f"{sid}.json").write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")
    return jsonify({"ok":True,"session_id":sid})

@app.post("/share/<module>/<token>/upload")
def share_upload(module, token):
    if not valid_share(module, token): return jsonify({"ok":False,"error":"Invalid share link"}),404
    f=request.files.get("file")
    if not f or not f.filename: return jsonify({"ok":False,"error":"No file supplied"}),400
    name=safe_name(f.filename)
    if name.lower().endswith((".exe",".dll",".bat",".cmd",".ps1",".sh")):
        return jsonify({"ok":False,"error":"File type is not accepted"}),400
    dest=CAPTURES/f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}-{module}-{name}"
    f.save(dest)
    return jsonify({"ok":True,"file":dest.name})

PAGE_MAP={
 "dashboard":"dashboard.html","sessions":"sessions.html","device":"device.html",
 "location":"location.html","camera":"camera.html","microphone":"microphone.html",
 "network":"network.html","reports":"reports.html","settings":"settings.html"
}
for endpoint, template in PAGE_MAP.items():
    app.add_url_rule("/"+endpoint, endpoint=endpoint,
        view_func=auth(lambda t=template: render_template(t)))

def safe_name(name, fallback="capture"):
    name = Path(name or fallback).name
    return "".join(c for c in name if c.isalnum() or c in "._-")[:100] or fallback

@app.get("/api/status")
@auth
def api_status():
    return jsonify({
        "online":True, "host":CONFIG["host"], "port":CONFIG["port"],
        "version":CONFIG["version"],
        "sessions":len(list(SESSIONS.glob("*.json"))),
        "captures":len([p for p in CAPTURES.iterdir() if p.is_file() and p.name!=".gitkeep"])
    })

@app.post("/api/session")
@auth
def api_session():
    data=request.get_json(silent=True) or {}
    sid=datetime.now().strftime("%Y%m%d-%H%M%S")+"-"+uuid.uuid4().hex[:8]
    data["session_id"]=sid
    data["created_at"]=datetime.now().isoformat(timespec="seconds")
    data["server_remote_address"]=request.remote_addr
    (SESSIONS/f"{sid}.json").write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")
    return jsonify({"ok":True,"session_id":sid})

@app.get("/api/sessions")
@auth
def api_sessions():
    out=[]
    for p in sorted(SESSIONS.glob("*.json"), reverse=True):
        try: out.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception: pass
    return jsonify(out)

@app.post("/api/upload")
@auth
def api_upload():
    f=request.files.get("file")
    if not f or not f.filename:
        return jsonify({"ok":False,"error":"No file supplied"}),400
    name=safe_name(f.filename)
    if name.lower().endswith((".exe",".dll",".bat",".cmd",".ps1",".sh")):
        return jsonify({"ok":False,"error":"Executable files are not accepted"}),400
    stamp=datetime.now().strftime("%Y%m%d-%H%M%S")
    dest=CAPTURES/f"{stamp}-{uuid.uuid4().hex[:6]}-{name}"
    f.save(dest)
    return jsonify({"ok":True,"file":dest.name})

@app.post("/api/save-json")
@auth
def api_save_json():
    data=request.get_json(silent=True) or {}
    name=safe_name(data.get("name"),"evidence.json")
    if not name.endswith(".json"): name+=".json"
    dest=CAPTURES/f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}-{name}"
    dest.write_text(json.dumps(data.get("data",{}),indent=2,ensure_ascii=False),encoding="utf-8")
    return jsonify({"ok":True,"file":dest.name})

@app.get("/api/files")
@auth
def api_files():
    return jsonify([{"name":p.name,"size":p.stat().st_size,"modified":datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds")}
                    for p in sorted(CAPTURES.iterdir(),reverse=True) if p.is_file() and p.name!=".gitkeep"])

@app.get("/download/<path:name>")
@auth
def download(name):
    p=CAPTURES/Path(name).name
    return send_file(p,as_attachment=True) if p.exists() else ("Not found",404)

@app.get("/download-all")
@auth
def download_all():
    fs=[p for p in CAPTURES.iterdir() if p.is_file() and p.name!=".gitkeep"]
    if not fs: return "No evidence files",404
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        for p in fs: z.write(p,p.name)
    buf.seek(0)
    return send_file(buf,mimetype="application/zip",as_attachment=True,download_name="dread-core-evidence.zip")

@app.get("/api/browser-info")
@auth
def browser_info():
    return jsonify({"user_agent":request.headers.get("User-Agent",""),
                    "language":request.headers.get("Accept-Language",""),
                    "remote_address":request.remote_addr})

@app.errorhandler(413)
def too_large(e):
    return jsonify({"ok":False,"error":"File exceeds configured upload limit"}),413

def run():
    print("\n"+"="*62)
    print("  DREAD CORE 1.0.0  |  AUTHORIZED SECURITY LAB")
    print("="*62)
    print(f"  Web console : http://{CONFIG['host']}:{CONFIG['port']}")
    print(f"  Login       : {CONFIG['username']} / {CONFIG['password']}")
    print("  Stop        : Ctrl+C")
    print("="*62+"\n")
    app.run(host=CONFIG["host"],port=CONFIG["port"],threaded=True,debug=False)

if __name__=="__main__":
    run()
