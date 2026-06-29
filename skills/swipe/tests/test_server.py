import base64, json, socket, subprocess, sys, tempfile, time, unittest, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "server.py"
RUN = ROOT / ".run"

# 1x1 PNG so sips has a real image to downscale
PNG_1x1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

def start(manifest_path, port):
    proc = subprocess.Popen([sys.executable, str(SERVER), str(manifest_path),
                             "--port", str(port), "--host", "127.0.0.1"])
    for _ in range(50):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1); return proc
        except Exception:
            time.sleep(0.1)
    proc.kill(); raise RuntimeError("server did not start")

class ServerTest(unittest.TestCase):
    def test_serves_deck_and_captures_decisions(self):
        tmp = Path(tempfile.mkdtemp())
        img = tmp / "p.png"; img.write_bytes(PNG_1x1)
        manifest = {"source": "files", "title": "t",
                    "left": {"label": "Trash", "kind": "trash"},
                    "right": {"label": "Keep", "kind": "keep"}, "reply": False,
                    "items": [{"id": "0", "type": "image", "label": "p.png",
                               "sub": "1 B", "path": str(img), "thumb": True}]}
        mpath = tmp / "m.json"; mpath.write_text(json.dumps(manifest))
        port = free_port()
        proc = start(mpath, port)
        try:
            base = f"http://127.0.0.1:{port}"
            html = urllib.request.urlopen(base + "/").read().decode()
            assert "p.png" in html  # manifest injected into the page
            info = json.loads((RUN / "server-info.json").read_text())
            assert info["port"] == port and info["url"].endswith(f":{port}/")
            thumb = urllib.request.urlopen(base + "/thumb/0").read()
            assert thumb[:3] == b"\xff\xd8\xff"  # JPEG magic
            decisions = {"done": True, "decisions": [{"id": "0", "dir": "left", "reply": None}]}
            req = urllib.request.Request(base + "/decisions", data=json.dumps(decisions).encode(),
                                         headers={"Content-Type": "application/json"}, method="POST")
            assert urllib.request.urlopen(req).status == 200
            written = json.loads((RUN / "decisions.json").read_text())
            assert written["done"] is True and written["decisions"][0]["dir"] == "left"
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()

if __name__ == "__main__":
    unittest.main()
