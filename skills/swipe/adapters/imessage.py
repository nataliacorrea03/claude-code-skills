import argparse, json, os, shutil, sqlite3, tempfile, time

def short_time(ns):
    epoch = ns / 1_000_000_000 + 978307200
    return time.strftime("%-I:%M%p", time.localtime(epoch)).lower()

def build(db_path, cap):
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
    try:
        shutil.copyfile(db_path, tmp)
        con = sqlite3.connect(tmp)
        rows = con.execute(
            "SELECT m.ROWID, m.text, m.date, h.id "
            "FROM message m LEFT JOIN handle h ON m.handle_id = h.ROWID "
            "WHERE m.is_from_me = 0 AND m.is_read = 0 AND m.text IS NOT NULL "
            "ORDER BY m.date DESC LIMIT ?", (cap,)).fetchall()
        con.close()
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    items = []
    for idx, (row, text, date, handle) in enumerate(rows):
        sender = handle or "Unknown"
        items.append({
            "id": str(idx),
            "type": "text",
            "sender": sender,
            "preview": text[:140],
            "sub": short_time(date),
            "handle": sender,
            "row": row,
        })
    return {
        "source": "imessage",
        "title": "Unread texts",
        "left":  {"label": "Skip",  "kind": "skip"},
        "right": {"label": "Reply", "kind": "reply"},
        "reply": True,
        "items": items,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=75)
    ap.add_argument("--db", default=os.path.expanduser("~/Library/Messages/chat.db"))
    args = ap.parse_args()
    print(json.dumps(build(args.db, args.cap)))

if __name__ == "__main__":
    main()
