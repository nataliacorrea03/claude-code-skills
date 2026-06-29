import argparse, json, os, shutil, subprocess, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(ROOT, ".run")
THUMBS = os.path.join(RUN, "thumbs")

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

def thumb_for(manifest, item_id):
    item = next((i for i in manifest["items"] if i["id"] == item_id), None)
    if not item or not item.get("thumb"):
        return None
    os.makedirs(THUMBS, exist_ok=True)
    out = os.path.join(THUMBS, f"{item_id}.jpg")
    if not os.path.exists(out):
        subprocess.run(["sips", "-Z", "600", "-s", "format", "jpeg", item["path"], "--out", out],
                       capture_output=True)
    return out if os.path.exists(out) else None

def make_handler(manifest, deck_html):
    marker = "/*__MANIFEST__*/null/*__END__*/"
    if marker not in deck_html:
        raise ValueError("deck.html is missing the manifest injection marker: " + marker)
    page = deck_html.replace(marker, json.dumps(manifest))
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
                t = thumb_for(manifest, self.path.split("/thumb/", 1)[1])
                if t:
                    with open(t, "rb") as f:
                        self._send(200, f.read(), "image/jpeg")
                else:
                    self._send(404, b"no thumb", "text/plain")
            elif self.path == "/vendor/qrcode.js":
                with open(os.path.join(ROOT, "vendor", "qrcode.js"), "rb") as f:
                    self._send(200, f.read(), "application/javascript")
            elif self.path == "/qr":
                with open(os.path.join(RUN, "server-info.json")) as f:
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
                os.makedirs(RUN, exist_ok=True)
                with open(os.path.join(RUN, "decisions.json"), "wb") as f:
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
    args = ap.parse_args()
    manifest = load_manifest(args.manifest)
    with open(os.path.join(ROOT, "deck.html")) as f:
        deck_html = f.read()
    httpd = ThreadingHTTPServer(("0.0.0.0", args.port), make_handler(manifest, deck_html))
    port = httpd.server_address[1]
    host = lan_ip() if args.host == "AUTO" else args.host
    os.makedirs(RUN, exist_ok=True)
    shutil.rmtree(THUMBS, ignore_errors=True)  # fresh thumbnails per run; never serve a stale cached thumb
    url = f"http://{host}:{port}/"
    with open(os.path.join(RUN, "server-info.json"), "w") as f:
        json.dump({"port": port, "pid": os.getpid(), "url": url}, f)
    print(url, flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
