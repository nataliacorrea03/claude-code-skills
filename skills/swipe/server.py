import argparse, json, os, shutil, subprocess, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RUN = os.path.join(ROOT, ".run")

def lan_ip():
    # The phone reaches the deck over the local network, so we want the LAN
    # address, not a VPN one. Try the common WiFi/Ethernet interfaces in order.
    for iface in ("en0", "en1", "en2"):
        try:
            out = subprocess.check_output(["ipconfig", "getifaddr", iface], text=True, timeout=5)
            ip = out.strip()
            if ip:
                return ip
        except Exception:
            continue
    return "127.0.0.1"

def load_manifest(path):
    with open(path) as f:
        return json.load(f)

def thumb_for(manifest, item_id, thumbs_dir):
    item = next((i for i in manifest["items"] if i["id"] == item_id), None)
    if not item or not item.get("thumb"):
        return None
    THUMBS = thumbs_dir
    os.makedirs(THUMBS, exist_ok=True)
    ext = os.path.splitext(item["path"])[1].lower()
    if ext == ".svg":
        # SVG is already a browser-renderable image; serve the bytes as-is.
        return (item["path"], "image/svg+xml") if os.path.exists(item["path"]) else None
    if item["type"] == "image":
        out = os.path.join(THUMBS, f"{item_id}.jpg")
        if not os.path.exists(out):
            subprocess.run(["sips", "-Z", "600", "-s", "format", "jpeg", item["path"], "--out", out],
                           capture_output=True)
        return (out, "image/jpeg") if os.path.exists(out) else None
    # Non-image types (PDF, video, Office docs, ...) get a QuickLook-rendered
    # thumbnail - first page / poster frame - instead of no preview at all.
    out_dir = os.path.join(THUMBS, item_id)
    marker = os.path.join(out_dir, ".done")
    if not os.path.exists(marker):
        os.makedirs(out_dir, exist_ok=True)
        try:
            subprocess.run(["qlmanage", "-t", "-s", "600", "-o", out_dir, item["path"]],
                           capture_output=True, timeout=15)
        except subprocess.TimeoutExpired:
            pass
        open(marker, "w").close()
    candidate = os.path.join(out_dir, os.path.basename(item["path"]) + ".png")
    return (candidate, "image/png") if os.path.exists(candidate) else None

def make_handler(manifest, deck_html, run_dir):
    marker = "/*__MANIFEST__*/null/*__END__*/"
    if marker not in deck_html:
        raise ValueError("deck.html is missing the manifest injection marker: " + marker)
    page = deck_html.replace(marker, json.dumps(manifest))
    thumbs_dir = os.path.join(run_dir, "thumbs")
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):  # quiet
            pass
        def _send(self, code, body, ctype):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def do_GET(self):
            if self.path == "/" or self.path.startswith("/?"):
                self._send(200, page.encode(), "text/html; charset=utf-8")
            elif self.path.startswith("/thumb/"):
                t = thumb_for(manifest, self.path.split("/thumb/", 1)[1], thumbs_dir)
                if t:
                    path, ctype = t
                    with open(path, "rb") as f:
                        self._send(200, f.read(), ctype)
                else:
                    self._send(404, b"no thumb", "text/plain")
            elif self.path == "/vendor/qrcode.js":
                with open(os.path.join(ROOT, "vendor", "qrcode.js"), "rb") as f:
                    self._send(200, f.read(), "application/javascript")
            elif self.path == "/qr":
                with open(os.path.join(run_dir, "server-info.json")) as f:
                    info = json.load(f)
                qr = ('<!doctype html><meta name=viewport content="width=device-width">'
                      '<body style="display:flex;flex-direction:column;align-items:center;'
                      'font-family:-apple-system;padding:24px"><h2>Scan to swipe</h2>'
                      '<div id=q></div><p>%s</p>'
                      '<script src="/vendor/qrcode.js"></script>'
                      '<script>new QRCode(document.getElementById("q"),'
                      '{text:"%s",width:280,height:280});</script>') % (info["url"], info["url"])
                self._send(200, qr.encode(), "text/html; charset=utf-8")
            else:
                self._send(404, b"not found", "text/plain")
        def do_POST(self):
            if self.path == "/decisions":
                n = int(self.headers.get("Content-Length", 0))
                data = self.rfile.read(n)
                os.makedirs(run_dir, exist_ok=True)
                with open(os.path.join(run_dir, "decisions.json"), "wb") as f:
                    f.write(data)
                self._send(200, b'{"ok":true}', "application/json")
            else:
                self._send(404, b"not found", "text/plain")
    return H

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--host", default="AUTO")
    ap.add_argument("--rundir", default=None,
                     help="Where to write server-info.json/decisions.json/thumbs (default: <skill>/.run). Tests should override this to avoid clobbering a live run.")
    args = ap.parse_args()
    run_dir = args.rundir or DEFAULT_RUN
    manifest = load_manifest(args.manifest)
    with open(os.path.join(ROOT, "deck.html")) as f:
        deck_html = f.read()
    httpd = ThreadingHTTPServer(("0.0.0.0", args.port), make_handler(manifest, deck_html, run_dir))
    port = httpd.server_address[1]
    host = lan_ip() if args.host == "AUTO" else args.host
    os.makedirs(run_dir, exist_ok=True)
    shutil.rmtree(os.path.join(run_dir, "thumbs"), ignore_errors=True)  # fresh thumbnails per run; never serve a stale cached thumb
    url = f"http://{host}:{port}/"
    with open(os.path.join(run_dir, "server-info.json"), "w") as f:
        json.dump({"port": port, "pid": os.getpid(), "url": url}, f)
    print(url, flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
