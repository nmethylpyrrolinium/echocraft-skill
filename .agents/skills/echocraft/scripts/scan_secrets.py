#!/usr/bin/env python3
"""Scan a directory for credentials and private identifiers before sharing or packaging it.

Looks for private keys, cloud/API tokens, JWT-shaped strings, quoted credential assignments,
private backend project URLs, .env files, and non-placeholder email addresses. Add literal
strings that must never appear (project ids, real names, private URLs) with --deny or
--deny-file; deny-list entries are matched case-insensitively and never echoed back.

Matches are REDACTED in all output. A line containing "echocraft:allow-secret" is skipped.
Pattern matching cannot prove a tree is clean; it catches the common, accidental cases.
Stdlib only. Exit code 1 if anything at or above --fail-on is found.
"""
import argparse
import json
import os
import re
import sys

SEV_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
PATTERNS = [
    ("SEC-PRIVATE-KEY", "high", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP |ENCRYPTED )?PRIVATE KEY-----")),
    ("SEC-AWS-KEY", "high", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("SEC-JWT", "high", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("SEC-SUPABASE-KEY", "high", re.compile(r"\bsb_(?:publishable|secret)_[A-Za-z0-9_-]{16,}")),
    ("SEC-GITHUB-TOKEN", "high", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})")),
    ("SEC-SLACK-TOKEN", "high", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("SEC-API-KEY", "high", re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{24,}")),
    ("SEC-GOOGLE-KEY", "high", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("SEC-ASSIGNMENT", "high", re.compile(r"(?i)\b(?:api[_-]?key|secret|token|passwd|password|service[_-]?role[_-]?key)\b\s*[:=]\s*[\"'][^\"'\s]{12,}[\"']")),
    ("SEC-PROJECT-URL", "medium", re.compile(r"https://[a-z0-9]{20}\.supabase\.co")),
    ("SEC-EMAIL", "low", re.compile(r"\b[A-Za-z0-9._%+-]+@(?!example\.(?:com|org|net)\b|users\.noreply\.github\.com\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
]


def redact(s):
    s = s.strip()
    return (s[:4] + "..." + "[%d chars]" % len(s)) if len(s) > 8 else "[redacted]"


def scan(root, deny):
    F, files = [], 0
    base = root if os.path.isdir(root) else os.path.dirname(root)
    paths = []
    if os.path.isfile(root):
        paths = [root]
    else:
        for d, ds, fs in os.walk(root):
            ds[:] = sorted(x for x in ds if x not in SKIP_DIRS)
            paths += [os.path.join(d, f) for f in sorted(fs)]
    for p in paths:
        rel = os.path.relpath(p, base)
        if re.match(r"^\.env(\..*)?$", os.path.basename(p)) and not p.endswith((".example", ".sample")):
            F.append({"rule": "SEC-ENV-FILE", "severity": "high", "file": rel, "line": None, "match": "[file]",
                      "message": ".env-style file present; do not ship or commit it"})
        try:
            raw = open(p, "rb").read()
        except OSError:
            continue
        if b"\0" in raw[:4096]:
            continue
        files += 1
        for i, line in enumerate(raw.decode("utf-8", errors="ignore").splitlines(), 1):
            if "echocraft:allow-secret" in line:
                continue
            for rid, sev, rx in PATTERNS:
                for m in rx.finditer(line):
                    F.append({"rule": rid, "severity": sev, "file": rel, "line": i, "match": redact(m.group(0)),
                              "message": "possible %s" % rid.replace("SEC-", "").replace("-", " ").lower()})
            low = line.lower()
            for d in deny:
                if d and d.lower() in low:
                    F.append({"rule": "SEC-DENYLIST", "severity": "high", "file": rel, "line": i, "match": "[deny-list entry]",
                              "message": "a deny-listed private string appears here"})
    return F, files


def main():
    ap = argparse.ArgumentParser(description="Scan for credentials and private identifiers (output is redacted).")
    ap.add_argument("path")
    ap.add_argument("--deny", action="append", default=[], help="literal private string that must not appear (repeatable)")
    ap.add_argument("--deny-file", help="file with one deny-listed string per line (keep it outside the scanned tree)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on", default="high", choices=["high", "medium", "low", "never"])
    a = ap.parse_args()
    deny = list(a.deny)
    if a.deny_file:
        deny += [l.strip() for l in open(a.deny_file, encoding="utf-8") if l.strip()]
    F, n = scan(a.path, deny)
    F.sort(key=lambda f: (-SEV_ORDER[f["severity"]], f["file"], f["line"] or 0))
    worst = max([SEV_ORDER[f["severity"]] for f in F] or [-1])
    if a.json:
        print(json.dumps({"tool": "scan_secrets", "target": a.path, "files_scanned": n, "findings": F}, indent=2))
    else:
        print("scan_secrets: %s  (%d text files scanned; matches redacted)" % (a.path, n))
        for f in F:
            print("  [%s] %s %s:%s - %s [%s]" % (f["severity"].upper(), f["rule"], f["file"], f["line"] or "-", f["message"], f["match"]))
        print("  %d finding(s)" % len(F) if F else "  OK - no pattern matches (not proof the tree is clean)")
    return 1 if worst >= {"high": 3, "medium": 2, "low": 1, "never": 99}[a.fail_on] else 0


if __name__ == "__main__":
    sys.exit(main())
