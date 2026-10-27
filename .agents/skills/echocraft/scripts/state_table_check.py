#!/usr/bin/env python3
"""Analyse a markdown state-transition table for structural problems.

Input: a markdown file with a TRANSITIONS table (columns From | Event | To, optional
Guard and "Sets data") and, optionally, a STATES table (columns State, and optionally
"Actions", "Needs data", "Terminal"). See assets/state-transition-template.md.

Detects: undefined targets, dead ends, unreachable states, trap states (no way back to an
entry or terminal state), nondeterministic transitions, async states without distinct
success/failure outcomes, destructive events without confirm/undo, actions listed for a
state with no matching transition, states that need data nothing produces, and (opt-in)
required states that are missing.

It checks the TABLE, not the running UI. A clean result means the table is coherent,
not that the interface implements it. Stdlib only.
"""
import argparse
import json
import re
import sys

SEV_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3}
ASYNC_WORDS = ("loading", "saving", "syncing", "importing", "exporting", "deleting", "uploading",
               "pending", "submitting", "signing in", "restoring")
DESTRUCTIVE = ("delete", "erase", "clear", "reset", "remove", "wipe", "discard")
REVERSE_WORDS = ("undo", "restore", "cancel", "keep", "back")
UNDEFINED = {"", "?", "tbd", "todo", "-", "none", "n/a"}


def norm(s):
    s = re.sub(r"[`*_]", "", s).strip()
    return s


def key(s):
    return re.sub(r"\s*\(terminal\)\s*$", "", norm(s), flags=re.I).strip().lower()


def parse_tables(text):
    tables, cur = [], None
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cur is None:
                cur = {"header": [c.lower() for c in cells], "rows": [], "sep": False}
            elif not cur["sep"] and all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                cur["sep"] = True
            else:
                cur["rows"].append(cells)
        elif cur is not None:
            tables.append(cur)
            cur = None
    if cur is not None:
        tables.append(cur)
    return [t for t in tables if t["sep"]]


def col(header, aliases):
    for i, h in enumerate(header):
        if h in aliases or any(h.startswith(a) for a in aliases):
            return i
    return None


def cell(row, i):
    return row[i].strip() if i is not None and i < len(row) else ""


def split_list(s):
    return [x.strip().lower() for x in re.split(r"[;,/]|<br\s*/?>", s) if x.strip() and x.strip() not in ("-", "none")]


def analyse(text, entry, terminal_arg, require, initial_data):
    findings = []

    def add(rule, sev, msg, state=None):
        findings.append({"rule": rule, "severity": sev, "state": state, "message": msg})

    tables = parse_tables(text)
    trans_t = next((t for t in tables if col(t["header"], ("from",)) is not None
                    and col(t["header"], ("to", "target", "next")) is not None), None)
    states_t = next((t for t in tables if t is not trans_t and col(t["header"], ("state",)) is not None
                     and col(t["header"], ("from",)) is None), None)
    if trans_t is None:
        add("ST-NO-TABLE", "high", "no transitions table found (need columns From | Event | To)")
        return findings, {}

    h = trans_t["header"]
    c_from, c_to = col(h, ("from",)), col(h, ("to", "target", "next"))
    c_ev = col(h, ("event", "action", "trigger"))
    c_guard, c_sets = col(h, ("guard", "condition")), col(h, ("sets data", "produces", "changes data", "data"))

    names, terminal, trans = {}, set(terminal_arg), []
    def reg(raw):
        k = key(raw)
        names.setdefault(k, norm(re.sub(r"\(terminal\)", "", raw, flags=re.I)))
        if re.search(r"\(terminal\)", raw, re.I):
            terminal.add(k)
        return k

    for r in trans_t["rows"]:
        f, t = cell(r, c_from), cell(r, c_to)
        if not f:
            continue
        fk = reg(f)
        if key(t) in UNDEFINED:
            add("ST-UNDEFINED-TARGET", "high", "transition from %r on %r has no defined target state" % (f, cell(r, c_ev)), fk)
            continue
        tk = reg(t)
        trans.append({"from": fk, "event": cell(r, c_ev).lower(), "to": tk,
                      "guard": cell(r, c_guard).lower(), "sets": split_list(cell(r, c_sets))})

    actions, needs = {}, {}
    if states_t is not None:
        sh = states_t["header"]
        c_s, c_a = col(sh, ("state",)), col(sh, ("actions",))
        c_n, c_t = col(sh, ("needs data", "requires")), col(sh, ("terminal",))
        for r in states_t["rows"]:
            s = cell(r, c_s)
            if not s:
                continue
            sk = reg(s)
            actions[sk] = split_list(cell(r, c_a))
            needs[sk] = split_list(cell(r, c_n))
            if cell(r, c_t).lower() in ("yes", "true", "y", "x", "✓"):
                terminal.add(sk)

    states = set(names)
    entries = {key(e) for e in entry} or ({trans[0]["from"]} if trans else set())
    for e in entries:
        if e not in states:
            add("ST-ENTRY-UNKNOWN", "medium", "entry state %r does not appear in the tables" % e)
    out = {}
    for t in trans:
        out.setdefault(t["from"], []).append(t)

    # reachability
    seen, stack = set(entries & states), list(entries & states)
    while stack:
        s = stack.pop()
        for t in out.get(s, []):
            if t["to"] not in seen:
                seen.add(t["to"])
                stack.append(t["to"])
    for s in sorted(states - seen):
        add("ST-UNREACHABLE", "medium",
            "state %r cannot be reached from entry state(s) %s (add a transition, or pass --entry if it has an external entry such as a deep link or returning user)"
            % (names[s], ", ".join(sorted(names.get(e, e) for e in entries))), s)

    # dead ends and traps
    for s in sorted(states):
        if not out.get(s) and s not in terminal:
            add("ST-DEAD-END", "high",
                "state %r has no outgoing transition and is not marked terminal - the user has no exit or recovery" % names[s], s)
    # traps: the main flow is the largest group of states that can all reach each other (reachable from
    # an entry). A state that has exits but cannot get back to that group, an entry, or a terminal state
    # is a closed loop. (Entry states are rarely revisited, so "can reach an entry" alone is too strict.)
    succ = {}
    for t in trans:
        succ.setdefault(t["from"], set()).add(t["to"])

    def reach(src):
        seen_, stack_ = {src}, [src]
        while stack_:
            for n in succ.get(stack_.pop(), ()):
                if n not in seen_:
                    seen_.add(n)
                    stack_.append(n)
        return seen_

    reach_of = {s_: reach(s_) for s_ in states}
    hub, best = set(), 1
    for s_ in sorted(seen):
        grp = {x for x in reach_of[s_] if s_ in reach_of[x]}
        if len(grp) > best:
            hub, best = grp, len(grp)
    home = hub | terminal | (entries & states)
    indeg = {h: sum(1 for t in trans if t["to"] == h and t["from"] in hub) for h in hub}
    hub_name = names[max(sorted(hub), key=lambda h: indeg[h])] if hub else "the main flow"
    for s_ in sorted(states):
        if out.get(s_) and not (reach_of[s_] & home):
            add("ST-TRAP", "high",
                "state %r has exits, but none lead back to the main flow (e.g. %r), an entry state or a terminal state (closed loop)"
                % (names[s_], hub_name), s_)

    # nondeterminism
    groups = {}
    for t in trans:
        groups.setdefault((t["from"], t["event"], t["guard"]), set()).add(t["to"])
    for (f, ev, g), tos in sorted(groups.items()):
        if len(tos) > 1:
            add("ST-NONDETERMINISTIC", "high",
                "state %r on event %r%s leads to several states (%s) with no distinguishing guard"
                % (names[f], ev, " [%s]" % g if g else "", ", ".join(sorted(names[x] for x in tos))), f)

    # async outcomes
    for s in sorted(states):
        if any(w in s for w in ASYNC_WORDS) and len({t["to"] for t in out.get(s, [])} - {s}) < 2 and s not in terminal:
            add("ST-ASYNC-OUTCOMES", "medium",
                "async-looking state %r needs distinct success and failure/cancel outcomes (found %d)"
                % (names[s], len({t['to'] for t in out.get(s, [])} - {s})), s)

    # destructive events
    for t in trans:
        if any(w in t["event"] for w in DESTRUCTIVE) and "confirm" not in t["from"]:
            after = [x["event"] for x in out.get(t["to"], [])]
            if not any(w in e for e in after for w in REVERSE_WORDS) and "confirm" not in t["to"]:
                add("ST-DESTRUCTIVE", "medium",
                    "event %r from %r looks destructive with no confirm step before it and no undo/cancel after it"
                    % (t["event"], names[t["from"]]), t["from"])

    # orphan actions
    for s, acts in actions.items():
        evs = [t["event"] for t in out.get(s, [])]
        for a in acts:
            if not any(a in e or e in a for e in evs):
                add("ST-ORPHAN-ACTION", "medium",
                    "state %r lists action %r but no outgoing transition handles it" % (names[s], a), s)

    # data dependencies
    provided = {d.lower() for d in initial_data}
    for t in trans:
        provided.update(t["sets"])
    for s, ns in needs.items():
        for n in ns:
            if n not in provided:
                add("ST-MISSING-DATA", "high",
                    "state %r needs data %r but no transition sets it and it is not an initial datum" % (names[s], n), s)

    # opt-in required coverage
    for r in require:
        if not any(r.lower() in s for s in states):
            add("ST-REQUIRED-MISSING", "high", "required state matching %r is not in the tables" % r)

    meta = {"states": sorted(names.values()), "transitions": len(trans), "entries": sorted(names.get(e, e) for e in entries)}
    return findings, meta


def main():
    ap = argparse.ArgumentParser(description="Check a markdown state-transition table for dead ends, traps, and missing coverage.")
    ap.add_argument("file")
    ap.add_argument("--entry", default="", help="comma-separated entry states (default: first From state)")
    ap.add_argument("--terminal", default="", help="comma-separated terminal states")
    ap.add_argument("--require", default="", help="comma-separated words; each must match a state name (opt-in coverage)")
    ap.add_argument("--initial-data", default="", help="comma-separated data present at start")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on", default="high", choices=["high", "medium", "low", "never"])
    a = ap.parse_args()
    lst = lambda s: [x.strip() for x in s.split(",") if x.strip()]
    text = open(a.file, encoding="utf-8").read()
    findings, meta = analyse(text, lst(a.entry), [key(x) for x in lst(a.terminal)], lst(a.require), lst(a.initial_data))
    findings.sort(key=lambda f: -SEV_ORDER[f["severity"]])
    worst = max([SEV_ORDER[f["severity"]] for f in findings] or [-1])
    if a.json:
        print(json.dumps({"tool": "state_table_check", "target": a.file, "meta": meta, "findings": findings}, indent=2))
    else:
        print("state_table_check: %s  (%s states, %s transitions)" % (a.file, len(meta.get("states", [])), meta.get("transitions", 0)))
        print("  Table-level check only - not proof the UI implements these states.")
        for f in findings:
            print("  [%s] %s - %s" % (f["severity"].upper(), f["rule"], f["message"]))
        print("  %d finding(s)" % len(findings) if findings else "  OK - no structural findings")
    thr = {"high": 3, "medium": 2, "low": 1, "never": 99}[a.fail_on]
    return 1 if worst >= thr else 0


if __name__ == "__main__":
    sys.exit(main())
