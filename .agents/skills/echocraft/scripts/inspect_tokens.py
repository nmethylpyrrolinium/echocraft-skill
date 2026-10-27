#!/usr/bin/env python3
"""Inventory the design tokens a project ALREADY has, and check named colour pairs for contrast.

Run this before adding any token (see references/atmosphere-system.md). It reads CSS custom
properties from .css/.scss/.html files, groups them by prefix and kind, estimates how much
colour is hard-coded outside tokens, and optionally computes WCAG 2.x contrast ratios for
pairs you name, e.g.  --pairs "--text:--bg,--muted:--bg".

Limits: it resolves var() one level deep, reads hex and rgb()/rgba() colours only, uses the
first declaration it finds per name (theme overrides are listed but not evaluated), and
ignores alpha. A passing ratio is not a full accessibility check. Stdlib only.
"""
import argparse
import json
import os
import re
import sys

EXTS = (".css", ".scss", ".html", ".htm", ".vue", ".svelte")
SKIP = {"node_modules", ".git", "dist", "build"}
DECL = re.compile(r"(--[\w-]+)\s*:\s*([^;{}]+);")
HEX = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
RGB = re.compile(r"rgba?\(\s*(\d{1,3})\s*[, ]\s*(\d{1,3})\s*[, ]\s*(\d{1,3})")


def kind(v):
    v = v.strip()
    if HEX.search(v) or RGB.search(v) or re.search(r"\b(?:hsla?|oklch|oklab)\(", v):
        return "color"
    if re.search(r"\d(?:ms|s)\b", v) and not re.search(r"[a-z]{4,}", re.sub(r"\d+(?:ms|s)", "", v)):
        return "time"
    if re.fullmatch(r"-?[\d.]+(?:px|rem|em|vh|vw|%|ch)(?:\s+-?[\d.]+(?:px|rem|em|vh|vw|%|ch))*", v):
        return "size"
    if "," in v or re.search(r"serif|sans|mono|font", v, re.I) or '"' in v or "'" in v:
        return "font"
    if "gradient" in v:
        return "gradient"
    if "shadow" in v or re.search(r"\d+px\s+\d+px", v):
        return "shadow"
    return "other"


def to_rgb(v):
    m = HEX.search(v)
    if m:
        h = m.group(0)[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = RGB.search(v)
    if m:
        return tuple(min(255, int(x)) for x in m.groups())
    return None


def lum(rgb):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main():
    ap = argparse.ArgumentParser(description="Inventory existing CSS custom properties and check contrast pairs.")
    ap.add_argument("path")
    ap.add_argument("--pairs", default="", help='comma list "fg:bg", e.g. "--text:--bg,--muted:--bg"')
    ap.add_argument("--min", type=float, default=4.5, help="minimum ratio for text pairs (default 4.5)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on", default="high", choices=["high", "medium", "low", "never"])
    a = ap.parse_args()

    files = []
    if os.path.isfile(a.path):
        files = [a.path]
    else:
        for d, dirs, fs in os.walk(a.path):
            dirs[:] = sorted(x for x in dirs if x not in SKIP and not x.startswith("."))
            files += [os.path.join(d, f) for f in sorted(fs) if f.lower().endswith(EXTS)]

    tokens, hard_colors, token_colors = {}, 0, 0
    themes = set()
    for p in files:
        t = open(p, encoding="utf-8", errors="ignore").read()
        if re.search(r"prefers-color-scheme|data-theme", t):
            themes.add(os.path.basename(p))
        for i, line in enumerate(t.splitlines(), 1):
            decls = list(DECL.finditer(line))
            for m in decls:
                tokens.setdefault(m.group(1), []).append({"value": m.group(2).strip(), "file": os.path.basename(p), "line": i})
                token_colors += len(HEX.findall(m.group(2)))
            if decls:
                # hex colours on the same line but outside any token declaration
                rest = DECL.sub("", line)
                hard_colors += len(HEX.findall(rest))
            else:
                hard_colors += len(HEX.findall(line))

    groups = {}
    for name, occ in tokens.items():
        prefix = name.lstrip("-").split("-")[0]
        groups.setdefault(prefix, []).append(name)
    inv = {n: {"kind": kind(o[0]["value"]), "value": o[0]["value"], "declared": len(o), "where": "%s:%d" % (o[0]["file"], o[0]["line"])}
           for n, o in sorted(tokens.items())}

    def resolve(name, depth=0):
        if name not in tokens or depth > 3:
            return None
        v = tokens[name][0]["value"]
        m = re.fullmatch(r"var\(\s*(--[\w-]+)[^)]*\)", v)
        return resolve(m.group(1), depth + 1) if m else to_rgb(v)

    findings, pairs = [], []
    for pr in [x.strip() for x in a.pairs.split(",") if x.strip()]:
        fg, _, bg = pr.partition(":")
        c1, c2 = resolve(fg.strip()), resolve(bg.strip())
        if c1 is None or c2 is None:
            findings.append({"rule": "TK-PAIR-UNRESOLVED", "severity": "medium",
                             "message": "could not resolve %s or %s to a hex/rgb colour (alpha, hsl and computed values are not supported)" % (fg, bg)})
            continue
        r = ratio(c1, c2)
        pairs.append({"fg": fg, "bg": bg, "ratio": round(r, 2), "min": a.min, "pass": r >= a.min})
        if r < a.min:
            findings.append({"rule": "TK-CONTRAST", "severity": "high",
                             "message": "%s on %s is %.2f:1, below %.1f:1" % (fg, bg, r, a.min)})
    if not tokens:
        findings.append({"rule": "TK-NONE", "severity": "info",
                         "message": "no CSS custom properties found: the design language may live in hard-coded values or a framework; inspect before adding tokens"})
    total = hard_colors + token_colors
    summary = {"files": len(files), "tokens": len(tokens), "groups": {k: len(v) for k, v in sorted(groups.items())},
               "hardcoded_hex_outside_tokens": hard_colors, "hex_inside_token_declarations": token_colors,
               "token_coverage_of_hex": round(token_colors / total, 2) if total else None,
               "theme_switching_files": sorted(themes)}
    if a.json:
        print(json.dumps({"tool": "inspect_tokens", "target": a.path, "summary": summary, "tokens": inv, "pairs": pairs, "findings": findings}, indent=2))
    else:
        print("inspect_tokens: %s" % a.path)
        print("  %d tokens in %d files; groups: %s" % (len(tokens), len(files), ", ".join("%s(%d)" % kv for kv in sorted(summary["groups"].items())) or "none"))
        print("  hex colours inside token declarations: %d, hard-coded elsewhere: %d" % (token_colors, hard_colors))
        for n, d in inv.items():
            print("    %-24s %-8s %s" % (n, d["kind"], d["value"][:48]))
        for p in pairs:
            print("  contrast %s on %s = %.2f:1 %s" % (p["fg"], p["bg"], p["ratio"], "PASS" if p["pass"] else "FAIL"))
        for f in findings:
            print("  [%s] %s - %s" % (f["severity"].upper(), f["rule"], f["message"]))
    rank = {"info": 0, "low": 1, "medium": 2, "high": 3}
    worst = max([rank[f["severity"]] for f in findings] or [-1])
    return 1 if worst >= {"high": 3, "medium": 2, "low": 1, "never": 99}[a.fail_on] else 0


if __name__ == "__main__":
    sys.exit(main())
