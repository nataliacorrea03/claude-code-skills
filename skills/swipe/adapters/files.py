import argparse, json, os, sys

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".heic", ".webp", ".tiff", ".tif", ".bmp"}
TEXT_EXTS = {".txt", ".text", ".md", ".markdown", ".csv", ".tsv", ".log", ".json",
             ".yaml", ".yml", ".xml", ".html", ".htm", ".css", ".js", ".jsx", ".ts",
             ".tsx", ".py", ".sh", ".rb", ".go", ".rs", ".ini", ".conf", ".toml",
             ".rtf", ".srt", ".vtt"}
# Types QuickLook (qlmanage) can render a real thumbnail for on macOS - first
# page of a PDF, a poster frame from video, first slide/page of Office docs,
# a rasterized SVG. Without this these all fell back to a bare 📄 icon.
QL_EXTS = {".pdf", ".mov", ".mp4", ".m4v", ".avi", ".key", ".pptx", ".ppt",
           ".docx", ".doc", ".pages", ".numbers", ".xlsx", ".xls", ".svg",
           ".ai", ".eps", ".psd"}
PREVIEW_CHARS = 1200
ZIP_LIST_CAP = 40
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def read_preview(path):
    try:
        with open(path, "r", errors="replace") as f:
            text = f.read(PREVIEW_CHARS)
    except OSError:
        return None
    text = text.strip()
    return text or None

def zip_preview(path):
    import zipfile
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
    except Exception:
        return None
    lines = [f"{len(names)} item{'s' if len(names) != 1 else ''}:"] + names[:ZIP_LIST_CAP]
    if len(names) > ZIP_LIST_CAP:
        lines.append(f"... +{len(names) - ZIP_LIST_CAP} more")
    return "\n".join(lines)

def human_size(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024.0

def short_date(epoch):
    import time
    t = time.localtime(epoch)
    return f"{MONTHS[t.tm_mon - 1]} {t.tm_mday}"

def build(folder, cap, sort):
    entries = []
    for name in os.listdir(folder):
        if name.startswith("."):
            continue
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            continue
        st = os.stat(path)
        entries.append((path, name, st.st_size, st.st_mtime))
    if sort == "largest":
        entries.sort(key=lambda e: e[2], reverse=True)
    else:  # oldest
        entries.sort(key=lambda e: e[3])
    entries = entries[:cap]
    items = []
    for idx, (path, name, size, mtime) in enumerate(entries):
        ext = os.path.splitext(name)[1].lower()
        is_img = ext in IMAGE_EXTS
        item = {
            "id": str(idx),
            "type": "image" if is_img else "file",
            "label": name,
            "sub": f"{human_size(size)} · {short_date(mtime)}",
            "path": os.path.abspath(path),
            "thumb": is_img or ext in QL_EXTS,
        }
        if not is_img:
            if ext in TEXT_EXTS:
                pv = read_preview(path)
                if pv:
                    item["preview"] = pv
            elif ext == ".zip":
                pv = zip_preview(path)
                if pv:
                    item["preview"] = pv
        items.append(item)
    return {
        "source": "files",
        "title": f"{os.path.basename(os.path.abspath(folder)) or '/'} cleanup",
        "left":  {"label": "Trash", "kind": "trash"},
        "right": {"label": "Keep",  "kind": "keep"},
        "reply": False,
        "items": items,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--cap", type=int, default=75)
    ap.add_argument("--sort", choices=["oldest", "largest"], default="oldest")
    args = ap.parse_args()
    if not os.path.isdir(args.folder):
        sys.exit(f"not a folder: {args.folder}")
    print(json.dumps(build(args.folder, args.cap, args.sort)))

if __name__ == "__main__":
    main()
