#!/usr/bin/env python3
"""Validate an Agent Skill directory.

Checks the SKILL.md frontmatter against the constraints documented at
https://agentskills.io/specification (name, description, license, compatibility,
metadata, allowed-tools) and adds package-hygiene checks: referenced paths exist,
every script/reference/asset is reachable from SKILL.md, size guidance.

Stdlib only. Exit code 1 when any finding at or above --fail-on is present.
This is a structural check; it does not judge whether the skill is *good*.
"""
import argparse
import json
import os
import re
import sys

ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEV_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3}


def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def parse_frontmatter(text):
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        raise ValueError("SKILL.md must start with '---' at byte 0")
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError("frontmatter is not closed with '---'")
    fm, body = lines[1:end], "\n".join(lines[end + 1:])
    data, i = {}, 0
    while i < len(fm):
        line = fm[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in " \t":
            raise ValueError("unexpected indentation at frontmatter line %d" % (i + 2))
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            raise ValueError("cannot parse frontmatter line %d: %r" % (i + 2, line))
        key, val = m.groups()
        i += 1
        if val in (">", ">-", "|", "|-"):
            block = []
            while i < len(fm) and (fm[i].startswith((" ", "\t")) or not fm[i].strip()):
                block.append(fm[i].strip())
                i += 1
            data[key] = (" " if val.startswith(">") else "\n").join(b for b in block if b)
        elif val == "":
            sub = {}
            while i < len(fm) and (fm[i].startswith((" ", "\t")) or not fm[i].strip()):
                s = fm[i].strip()
                if s:
                    mm = re.match(r"^([A-Za-z0-9_.-]+):\s*(.*)$", s)
                    if not mm:
                        raise ValueError("cannot parse metadata line: %r" % s)
                    raw = mm.group(2).strip()
                    sub[mm.group(1)] = (unquote(raw), raw[:1] in "\"'")
                i += 1
            data[key] = sub
        else:
            data[key] = unquote(val)
    return data, body


def run(a):
    root = os.path.abspath(a.skill_dir)
    findings = []

    def add(rule, sev, msg, file=None):
        findings.append({"rule": rule, "severity": sev, "file": file, "message": msg})

    skill_md = os.path.join(root, "SKILL.md")
    if not os.path.isfile(skill_md):
        add("SK-MISSING", "high", "SKILL.md not found", "SKILL.md")
        return findings, root

    text = open(skill_md, encoding="utf-8").read()
    try:
        fm, body = parse_frontmatter(text)
    except ValueError as e:
        add("SK-FRONTMATTER", "high", str(e), "SKILL.md")
        return findings, root

    for k in fm:
        if k not in ALLOWED_KEYS:
            add("SK-UNKNOWN-KEY", "high",
                "unexpected frontmatter key %r (allowed: %s)" % (k, ", ".join(sorted(ALLOWED_KEYS))), "SKILL.md")

    name = fm.get("name")
    if not name:
        add("SK-NAME-MISSING", "high", "name is required", "SKILL.md")
    else:
        if len(name) > 64:
            add("SK-NAME-LENGTH", "high", "name is %d chars (max 64)" % len(name), "SKILL.md")
        if not NAME_RE.match(name):
            add("SK-NAME-FORMAT", "high",
                "name must be lowercase letters/digits/hyphens with no leading, trailing or consecutive hyphens: %r" % name,
                "SKILL.md")
        if name != os.path.basename(root):
            add("SK-NAME-DIR", "high",
                "name %r must equal the parent directory name %r" % (name, os.path.basename(root)), "SKILL.md")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        add("SK-DESC-MISSING", "high", "description is required and must be non-empty", "SKILL.md")
    else:
        if len(desc) > 1024:
            add("SK-DESC-LENGTH", "high", "description is %d chars (max 1024)" % len(desc), "SKILL.md")
        if not re.search(r"(?i)\bwhen\b|\bwhenever\b", desc):
            add("SK-DESC-WHEN", "low", "description should say WHEN to use the skill, not only what it does", "SKILL.md")

    comp = fm.get("compatibility")
    if comp is not None and (not isinstance(comp, str) or not (1 <= len(comp) <= 500)):
        add("SK-COMPAT", "high", "compatibility must be a string of 1-500 chars", "SKILL.md")

    meta = fm.get("metadata")
    if meta is not None:
        if not isinstance(meta, dict):
            add("SK-META-TYPE", "high", "metadata must be a mapping of string keys to string values", "SKILL.md")
        else:
            for k, (v, quoted) in meta.items():
                if not quoted and re.fullmatch(r"[0-9.]+", v):
                    add("SK-META-QUOTE", "low",
                        "metadata value for %r should be quoted so YAML keeps it a string" % k, "SKILL.md")

    at = fm.get("allowed-tools")
    if at is not None and not isinstance(at, str):
        add("SK-ALLOWED-TOOLS", "high", "allowed-tools must be a space-separated string (experimental field)", "SKILL.md")

    if not body.strip():
        add("SK-BODY-EMPTY", "high", "SKILL.md body is empty", "SKILL.md")
    nlines = len(text.splitlines())
    if nlines > 500:
        add("SK-BODY-LINES", "medium", "SKILL.md is %d lines (guidance: < 500)" % nlines, "SKILL.md")
    approx_tokens = len(body) // 4
    if approx_tokens > 5000:
        add("SK-BODY-TOKENS", "medium",
            "SKILL.md body is ~%d tokens by a chars/4 estimate (guidance: < 5000)" % approx_tokens, "SKILL.md")

    # Referenced paths must exist; everything bundled must be reachable from SKILL.md.
    path_re = re.compile(r"(?<![\w/.-])((?:references|assets|scripts)/[\w][\w./-]*[\w])")
    link_re = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
    md_files = [skill_md]
    for sub in ("references", "assets"):
        d = os.path.join(root, sub)
        if os.path.isdir(d):
            md_files += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".md")]
    skill_refs = set()
    for f in md_files:
        t = open(f, encoding="utf-8").read()
        rel = os.path.relpath(f, root)
        cands = set(path_re.findall(t))
        for l in link_re.findall(t):
            if re.match(r"^(https?:|mailto:)", l):
                continue
            cands.add(os.path.normpath(os.path.join(os.path.dirname(rel), l)))
        for c in sorted(cands):
            if any(ch in c for ch in "*<>{}$"):
                continue
            if not os.path.exists(os.path.join(root, c)):
                add("SK-LINK-BROKEN", "high", "referenced path does not exist: %s" % c, rel)
            elif f == skill_md:
                skill_refs.add(os.path.normpath(c))
        if len(t.splitlines()) > 300 and not re.search(r"(?im)^#+\s*(contents|table of contents)\b", t):
            add("SK-REF-TOC", "low", "file over 300 lines should start with a contents section", rel)

    for sub in ("references", "assets", "scripts"):
        d = os.path.join(root, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.startswith(("_", ".")) or os.path.isdir(os.path.join(d, f)):
                continue
            rel = os.path.normpath(os.path.join(sub, f))
            if rel not in skill_refs:
                add("SK-ORPHAN", "medium",
                    "%s is not referenced from SKILL.md (an agent will not know when to use it)" % rel, rel)
    return findings, root


def main():
    ap = argparse.ArgumentParser(description="Validate an Agent Skill directory (structure + hygiene).")
    ap.add_argument("skill_dir")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on", default="high", choices=["high", "medium", "low", "never"])
    a = ap.parse_args()
    findings, root = run(a)
    findings.sort(key=lambda f: -SEV_ORDER[f["severity"]])
    worst = max([SEV_ORDER[f["severity"]] for f in findings] or [-1])
    if a.json:
        print(json.dumps({"tool": "validate_skill", "target": root, "findings": findings}, indent=2))
    else:
        print("validate_skill: %s" % root)
        for f in findings:
            print("  [%s] %s %s - %s" % (f["severity"].upper(), f["rule"], f["file"] or "", f["message"]))
        print("  %d finding(s)" % len(findings) if findings else "  OK - no findings")
    thr = {"high": 3, "medium": 2, "low": 1, "never": 99}[a.fail_on]
    return 1 if worst >= thr else 0


if __name__ == "__main__":
    sys.exit(main())
