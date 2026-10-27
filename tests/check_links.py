#!/usr/bin/env python3
"""Check that relative markdown links and backticked repo paths in the package's .md files exist.

Resolves a path relative to the file, the repository root, and the skill folder (echocraft/).
Skips URLs, placeholders (<...>, *, {...}), shell commands and home-directory paths.
Usage: python3 tests/check_links.py   (exit 1 if any reference is broken)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
TICK = re.compile(r"`((?:echocraft|tests|docs|examples|references|assets|scripts)/[\w./{}*<>-]*[\w/])`")
bad, checked = [], 0
for d, dirs, files in os.walk(ROOT):
    dirs[:] = [x for x in dirs if x not in (".git", "__pycache__")]
    for f in files:
        if not f.endswith(".md") or "fixtures" in d:
            continue
        p = os.path.join(d, f)
        text = open(p, encoding="utf-8").read()
        refs = set(LINK.findall(text)) | set(TICK.findall(text))
        for r in sorted(refs):
            if re.match(r"^(https?:|mailto:|~)", r) or any(c in r for c in "*<>{}$"):
                continue
            checked += 1
            cands = [os.path.join(os.path.dirname(p), r), os.path.join(ROOT, r), os.path.join(ROOT, "echocraft", r)]
            if not any(os.path.exists(c) for c in cands):
                bad.append("%s -> %s" % (os.path.relpath(p, ROOT), r))
print("checked %d references in markdown files" % checked)
for b in bad:
    print("BROKEN: " + b)
print("OK - no broken references" if not bad else "%d broken reference(s)" % len(bad))
sys.exit(1 if bad else 0)
