import json, shutil, sqlite3, subprocess, sys, tempfile, unittest
from pathlib import Path

ADAPTER = Path(__file__).resolve().parent.parent / "adapters" / "imessage.py"

def make_db(path):
    con = sqlite3.connect(path)
    con.executescript("""
      CREATE TABLE handle (ROWID INTEGER PRIMARY KEY, id TEXT);
      CREATE TABLE message (ROWID INTEGER PRIMARY KEY, text TEXT, is_from_me INT,
                            is_read INT, date INT, handle_id INT);
      INSERT INTO handle VALUES (1, '+19175551234');
      INSERT INTO handle VALUES (2, 'pal@icloud.com');
      -- unread received (should appear), newest first by date
      INSERT INTO message VALUES (10, 'hey are you around tmrw', 0, 0, 700000000000000000, 1);
      INSERT INTO message VALUES (11, 'lunch?', 0, 0, 710000000000000000, 2);
      -- already read received (excluded)
      INSERT INTO message VALUES (12, 'old read msg', 0, 1, 600000000000000000, 1);
      -- sent by me (excluded)
      INSERT INTO message VALUES (13, 'my own msg', 1, 0, 720000000000000000, 1);
      -- null text / reaction (excluded)
      INSERT INTO message VALUES (14, NULL, 0, 0, 730000000000000000, 2);
    """)
    con.commit(); con.close()

def run(db, *args):
    out = subprocess.check_output([sys.executable, str(ADAPTER), "--db", str(db), *args])
    return json.loads(out)

class IMessageAdapterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.db = self.tmp / "chat.db"
        make_db(self.db)

    def test_only_unread_received_with_text(self):
        m = run(self.db)
        assert m["source"] == "imessage" and m["reply"] is True
        assert m["right"]["kind"] == "reply" and m["left"]["kind"] == "skip"
        previews = [i["preview"] for i in m["items"]]
        assert previews == ["lunch?", "hey are you around tmrw"]  # newest first
        first = m["items"][0]
        assert first["type"] == "text" and first["sender"] == "pal@icloud.com"
        assert first["handle"] == "pal@icloud.com" and first["row"] == 11

    def test_cap(self):
        m = run(self.db, "--cap", "1")
        assert len(m["items"]) == 1 and m["items"][0]["preview"] == "lunch?"

if __name__ == "__main__":
    unittest.main()
