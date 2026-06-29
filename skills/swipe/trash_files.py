import json, os, subprocess, sys

# Pass the path as an AppleScript run-argument, NOT interpolated into the script
# text. This avoids ALL string-escaping problems: filenames can contain quotes,
# backslashes, or non-ASCII like the narrow no-break space (U+202F) macOS puts in
# screenshot names. Interpolating the path into the script (even via json.dumps,
# which emits \uXXXX that AppleScript cannot parse) breaks on those characters.
TRASH_SCRIPT = (
    'on run argv\n'
    '  tell application "Finder" to delete (POSIX file (item 1 of argv) as alias)\n'
    'end run'
)

def trash_one(path):
    # Finder "delete" moves to Trash and preserves Put Back. Fails if path is gone.
    if not os.path.exists(path):
        return False, "path does not exist"
    p = subprocess.run(["osascript", "-e", TRASH_SCRIPT, path], capture_output=True, text=True)
    if p.returncode != 0:
        return False, p.stderr.strip() or "osascript failed"
    return True, None

def main():
    paths = json.load(sys.stdin)
    trashed, failed = 0, []
    for path in paths:
        ok, err = trash_one(path)
        if ok:
            trashed += 1
        else:
            failed.append({"path": path, "error": err})
    print(json.dumps({"trashed": trashed, "failed": failed}))

if __name__ == "__main__":
    main()
