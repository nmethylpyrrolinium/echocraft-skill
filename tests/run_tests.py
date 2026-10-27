#!/usr/bin/env python3
"""Run the deterministic script tests for EchoCraft.

Each file in tests/expected-findings/*.json describes one case: which script to run, on which
fixture, and which rule ids must (or must not) appear. These tests exercise the SCRIPTS only.
They do not test whether an AI agent follows the skill - see tests/MANUAL_EVALUATION.md for that.

Usage:  python3 tests/run_tests.py [-v] [case-name-substring]
Exit code 0 only if every case passes. Stdlib only.
"""
import glob
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILL = os.path.join(ROOT, "echocraft")
FIX = os.path.join(HERE, "fixtures")


def make_fake_secrets(tmp):
    """Build obviously fake secrets at run time so the repository itself never contains them."""
    parts = {
        "jwt": "eyJ" + "A" * 12 + "." + "B" * 12 + "." + "C" * 12,
        "aws": "AKIA" + "ABCDEFGHIJKLMNOP",
        "ghp": "ghp_" + "a1" * 18,
        "pem": "-----BEGIN " + "RSA PRIVATE KEY-----",
        "url": "https://" + "a" * 20 + ".supabase.co",
        "mail": "jane.doe@" + "gmail.com",
        "assign": 'api_key = "' + "x7" * 10 + '"',
        "deny": "ZZ-PRIVATE-ID-" + "4821",
    }
    with open(os.path.join(tmp, "config.js"), "w") as f:
        f.write("\n".join([parts["jwt"], parts["aws"], parts["ghp"], parts["url"], parts["assign"]]) + "\n")
    with open(os.path.join(tmp, "notes.md"), "w") as f:
        f.write(parts["pem"] + "\ncontact " + parts["mail"] + "\nproject " + parts["deny"] + "\n")
    with open(os.path.join(tmp, ".env"), "w") as f:
        f.write("SOMETHING=1\n")
    with open(os.path.join(tmp, "clean.txt"), "w") as f:
        f.write("nothing sensitive here, see example@example.com\n")
    return list(parts.values())


def dig(obj, path):
    for p in path.split("."):
        obj = obj[int(p)] if isinstance(obj, list) else obj[p]
    return obj


def run_case(path, verbose):
    spec = json.load(open(path))
    name = os.path.basename(path)[:-5]
    tmp = tempfile.mkdtemp(prefix="echocraft-test-")
    secrets = []
    if spec.get("setup") == "fake_secrets":
        secrets = make_fake_secrets(tmp)
    subst = lambda s: s.replace("{fixtures}", FIX).replace("{skill}", SKILL).replace("{root}", ROOT).replace("{tmp}", tmp)
    cmd = [sys.executable, os.path.join(SKILL, "scripts", spec["script"])] + [subst(a) for a in spec["args"]]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    errs = []
    if p.returncode != spec.get("expect_exit", 0):
        errs.append("exit %d, expected %d" % (p.returncode, spec.get("expect_exit", 0)))
    out = p.stdout
    try:
        data = json.loads(out)
    except ValueError:
        data = None
        errs.append("stdout was not JSON: %r" % out[:200])
    if data is not None:
        got = {f["rule"] for f in data.get("findings", [])}
        for r in spec.get("must_include", []):
            if r not in got:
                errs.append("missing expected rule %s (got %s)" % (r, sorted(got)))
        for r in spec.get("must_not_include", []):
            if r in got:
                errs.append("unexpected rule %s" % r)
        for a in spec.get("asserts", []):
            try:
                v = dig(data, a["path"])
            except (KeyError, IndexError, ValueError):
                errs.append("assert path %s not found" % a["path"])
                continue
            ok = {"gte": lambda: v >= a["value"], "lte": lambda: v <= a["value"], "eq": lambda: v == a["value"],
                  "len_gte": lambda: len(v) >= a["value"], "len_eq": lambda: len(v) == a["value"]}[a["op"]]()
            if not ok:
                errs.append("assert %s %s %s failed (got %r)" % (a["path"], a["op"], a["value"], v))
    for s in secrets:
        if s in out or s in p.stderr:
            errs.append("secret-looking string was echoed in output")
    if verbose:
        sys.stdout.write("    $ %s\n" % " ".join(cmd[1:]))
    return name, spec, errs


def main():
    argv = [a for a in sys.argv[1:] if a != "-v"]
    verbose = "-v" in sys.argv
    cases = sorted(glob.glob(os.path.join(HERE, "expected-findings", "*.json")))
    if argv:
        cases = [c for c in cases if argv[0] in c]
    fails = 0
    for c in cases:
        name, spec, errs = run_case(c, verbose)
        print("%s  %-34s scenario %-4s %s" % ("PASS" if not errs else "FAIL", name, spec.get("scenario", "-"), spec.get("description", "")))
        for e in errs:
            print("        - " + e)
        fails += bool(errs)
    print("\n%d case(s), %d passed, %d failed" % (len(cases), len(cases) - fails, fails))
    print("These are script tests only; agent-behaviour scenarios are in tests/MANUAL_EVALUATION.md and have NOT been run.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
