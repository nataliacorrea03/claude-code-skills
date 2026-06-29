import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "trash_files.py"

def run(paths):
    p = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(paths),
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)

class TrashFilesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_moves_files_to_trash(self):
        f1 = self.tmp / "trash_me_1.txt"; f1.write_text("a")
        f2 = self.tmp / "trash_me_2.txt"; f2.write_text("b")
        res = run([str(f1), str(f2)])
        assert res["trashed"] == 2 and res["failed"] == []
        assert not f1.exists() and not f2.exists()
        # cleanup: remove from Trash so the test does not accumulate junk
        trash = Path.home() / ".Trash"
        for name in ("trash_me_1", "trash_me_2"):
            for cand in trash.glob(name + "*"):
                try: cand.unlink()
                except OSError: pass

    def test_reports_failure_for_missing_path(self):
        res = run([str(self.tmp / "does_not_exist.txt")])
        assert res["trashed"] == 0 and len(res["failed"]) == 1

    def test_escapes_special_characters_in_filenames(self):
        # Filenames with double-quotes and backslashes must trash end-to-end.
        f = self.tmp / 'weird"na\\me.txt'
        f.write_text("special chars")
        res = run([str(f)])
        assert res["trashed"] == 1 and res["failed"] == []
        assert not f.exists()
        trash = Path.home() / ".Trash"
        for cand in trash.glob("weird*"):
            try: cand.unlink()
            except OSError: pass

    def test_handles_non_ascii_filenames(self):
        # macOS screenshot names contain a narrow no-break space (U+202F) before AM/PM.
        # The path must NOT be interpolated into the AppleScript as a \uXXXX escape
        # (AppleScript cannot parse that); passing it as a run-arg keeps it intact.
        name = "Screenshot 2026-05-23 at 7.11.37 PM.png"
        f = self.tmp / name
        f.write_bytes(b"\x89PNG\r\n\x1a\n")
        res = run([str(f)])
        assert res["trashed"] == 1 and res["failed"] == [], res
        assert not f.exists()
        trash = Path.home() / ".Trash"
        for cand in trash.glob("Screenshot 2026-05-23*"):
            try: cand.unlink()
            except OSError: pass

if __name__ == "__main__":
    unittest.main()
