import json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ADAPTER = Path(__file__).resolve().parent.parent / "adapters" / "files.py"

def run(folder, *args):
    out = subprocess.check_output([sys.executable, str(ADAPTER), str(folder), *args])
    return json.loads(out)

class FilesAdapterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_lists_visible_files_excludes_hidden_and_dirs(self):
        (self.tmp / "a.png").write_bytes(b"x")
        (self.tmp / "b.pdf").write_bytes(b"y")
        (self.tmp / ".hidden").write_bytes(b"z")
        (self.tmp / "subdir").mkdir()
        m = run(self.tmp)
        assert m["source"] == "files"
        labels = {i["label"] for i in m["items"]}
        assert labels == {"a.png", "b.pdf"}
        img = next(i for i in m["items"] if i["label"] == "a.png")
        assert img["type"] == "image" and img["thumb"] is True
        pdf = next(i for i in m["items"] if i["label"] == "b.pdf")
        assert pdf["type"] == "file" and pdf["thumb"] is False
        assert all(os.path.isabs(i["path"]) for i in m["items"])

    def test_cap_and_oldest_sort(self):
        for n in range(5):
            f = self.tmp / f"f{n}.txt"
            f.write_bytes(b"x")
            os.utime(f, (1000 + n, 1000 + n))  # f0 oldest
        m = run(self.tmp, "--cap", "2", "--sort", "oldest")
        assert [i["label"] for i in m["items"]] == ["f0.txt", "f1.txt"]

    def test_largest_sort(self):
        (self.tmp / "small.txt").write_bytes(b"x")
        (self.tmp / "big.txt").write_bytes(b"x" * 5000)
        m = run(self.tmp, "--sort", "largest")
        assert m["items"][0]["label"] == "big.txt"

    def test_text_files_carry_a_content_preview(self):
        (self.tmp / "note.txt").write_text("buy milk and eggs")
        (self.tmp / "pic.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        (self.tmp / "data.bin").write_bytes(b"\x00\x01\x02")
        m = run(self.tmp)
        note = next(i for i in m["items"] if i["label"] == "note.txt")
        assert note["preview"] == "buy milk and eggs"
        pic = next(i for i in m["items"] if i["label"] == "pic.png")
        assert "preview" not in pic  # images use their thumbnail, no text preview
        binf = next(i for i in m["items"] if i["label"] == "data.bin")
        assert "preview" not in binf  # unknown extension gets no preview

if __name__ == "__main__":
    unittest.main()
