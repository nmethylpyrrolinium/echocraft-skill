#!/usr/bin/env python3
"""Static heuristic audit of a front-end source tree for emotionally expressive / personal-content apps.

Scans .html .css .scss .js .jsx .ts .tsx .vue .svelte files and reports:
  * motion without reduced-motion handling (CSS and JS-driven)
  * privacy: remote data flows, analytics, browser storage of personal content,
    third-party hosts, and "private/local" claims that the code contradicts
  * deletion paths that look local-only while a remote client exists
  * coercive, diagnostic, therapeutic or unearned-inference copy
  * basic accessibility smells (focus removal, zoom lock, missing alt/labels, autoplay)
  * diagnostic prompts for decorative excess (glass, gradients, glow, particles)
  * full-screen effect layers that may block the primary task

IMPORTANT: this is a regex-level scan. It cannot see runtime behaviour, server config,
minified bundles, or intent. It is NOT an accessibility audit, privacy review or security
review. Every finding is a question to answer by reading the code, not a verdict.
Stdlib only.
"""
import argparse
import json
import os
import re
import sys

SEV_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3}
EXTS = (".html", ".htm", ".css", ".scss", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".mjs")
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "coverage", "vendor"}

RULES = {
    "EC-A01": ("high", "Motion with no prefers-reduced-motion handling anywhere",
               "Users who disable motion at OS level still get animation, and vestibular triggers are real.",
               "Add an @media (prefers-reduced-motion: reduce) block that replaces motion with opacity/instant changes, and read matchMedia in JS loops."),
    "EC-A01J": ("medium", "JS-driven animation (rAF/canvas/WebGL) does not read the reduced-motion preference",
                "CSS media queries do not stop requestAnimationFrame, canvas or WebGL loops.",
                "Check matchMedia('(prefers-reduced-motion: reduce)') before starting loops; render a static frame and offer an in-app toggle."),
    "EC-A02": ("medium", "Focus outline removed",
               "Keyboard users lose their position unless a visible replacement exists.",
               "Replace with a visible :focus-visible style (outline or ring, 3:1 contrast) instead of removing it."),
    "EC-A04": ("medium", "Viewport blocks zoom",
               "Low-vision users cannot enlarge content.", "Remove user-scalable=no / maximum-scale=1."),
    "EC-A05": ("medium", "<img> without alt attribute",
               "Screen readers announce the file name or skip meaning.", "Add alt text, or alt=\"\" if purely decorative."),
    "EC-A06": ("medium", "Form control with no accessible-name candidate",
               "Placeholders disappear and are not reliable names.", "Add a <label for>, wrap in <label>, or add aria-label."),
    "EC-A07": ("medium", "Autoplaying media",
               "Unexpected sound or motion is intrusive and can be harmful in quiet or sensitive contexts.",
               "Start media only on a user gesture; default sound off."),
    "EC-A08": ("low", "Toast/snackbar messages but no aria-live/role=status anywhere",
               "Screen reader users may never hear transient confirmations or errors.", "Render toasts into a role=\"status\" (or alert for errors) container."),
    "EC-A09": ("low", "Very small font size", "Text under 11px is hard to read, especially on phones.", "Use a readable minimum and relative units."),
    "EC-P01": ("info", "Remote data flow detected", "Any personal content that reaches this code path leaves the device.",
               "List it in the data-flow inventory: what is sent, to whom, when, with what consent and deletion path."),
    "EC-P02": ("medium", "Analytics / telemetry SDK detected", "Behavioural data about emotional content is sensitive even when only counts are collected.",
               "Confirm it is required, disclosed and opt-in; otherwise remove it."),
    "EC-P03": ("info", "Browser storage in use", "localStorage/IndexedDB are not encrypted, are readable by any script on the origin, and can be cleared by the browser.",
               "Document it honestly in the data-flow inventory; do not describe it as secure."),
    "EC-P03S": ("medium", "Personal-looking content written to browser storage", "Journal/mood text in plain browser storage is exposed on shared devices and to any injected script.",
                "Disclose it, offer a clear-from-this-device control, and consider whether the data needs to be stored at all."),
    "EC-P04": ("info", "Third-party host requested", "Requests to third parties disclose IP address, user agent and often referrer.",
               "Confirm necessity; self-host assets for sensitive screens; disclose in the privacy notes."),
    "EC-P05": ("high", "Privacy claim contradicted by detected remote data flow",
               "The copy promises data stays local, but the code contains a path that transmits data.",
               "Either remove the remote path, make it explicit opt-in, or change the claim to what is true."),
    "EC-P05U": ("info", "Privacy claim present; not contradicted by this static scan",
                "A static scan cannot prove a negative: service workers, other bundles and third-party scripts may transmit data.",
                "Trace every data flow and keep the claim only if the trace supports it."),
    "EC-X01": ("medium", "External script without Subresource Integrity", "A compromised CDN could run arbitrary code with access to journal content.",
               "Pin the version and add integrity + crossorigin, or self-host. Question whether the dependency is needed."),
    "EC-D01": ("medium", "Deletion looks local-only but a remote client exists",
               "Users will read 'delete' as 'gone'; remote copies and backups may remain.",
               "Verify backend behaviour; label the control honestly ('Remove from this device') until a remote delete is proven."),
    "EC-D02": ("medium", "Remote storage client found but no deletion path found",
               "Users have no visible way to remove data they created.", "Add and test a deletion path, and state what it covers."),
    "EC-D03": ("info", "Deletion path found", "Confirm scope wording, confirmation or undo, and what survives (backups, caches, third parties).", "Test it and record the result."),
    "EC-C01": ("medium", "Guilt, pressure or streak-style microcopy", "Implying neglect or loss pressures engagement and can shame users in a vulnerable context.",
               "Use a neutral invitation: say what is available, not what the user failed to do."),
    "EC-C02": ("high", "Diagnostic or clinical claim in copy", "The product cannot diagnose; unverified clinical claims can mislead people in distress.",
               "Remove, or restate as a plain description of what the feature does."),
    "EC-C03": ("medium", "Therapy/healing/wellness-outcome wording", "Outcome claims need a verified basis the product may not have.",
               "Describe the activity (write, revisit, release) rather than promising a clinical outcome."),
    "EC-C04": ("medium", "System-asserted emotional inference in copy", "A guess about the user's state shown as fact is an unearned interpretation.",
               "Show what the user stated, label derived values as derived, make any inference optional, explainable and dismissible."),
    "EC-V01": ("info", "Diagnostic: heavy backdrop-filter / glass use", "Blur layers cost performance and lower text contrast; stacked glass hides hierarchy.",
               "Keep glass for one layer with a stated purpose; give text a solid or high-contrast surface."),
    "EC-V02": ("info", "Diagnostic: many gradients", "Gradients used everywhere stop signalling anything.", "Reserve gradients for one semantic job (e.g. state of the day); use flat surfaces elsewhere."),
    "EC-V03": ("info", "Diagnostic: particle systems", "Particles with no information role are decoration that competes with content and drains battery.",
               "Tie each effect to a user action or state, cap its cost, and provide a static alternative."),
    "EC-V04": ("info", "Diagnostic: many glow shadows", "Glow on many elements flattens hierarchy and reduces contrast.", "Limit glow to the single element that deserves attention."),
    "EC-V05": ("medium", "Full-viewport effect layer without pointer-events:none",
               "A fixed overlay/canvas can swallow taps and clicks and sit over content.", "Add pointer-events:none to purely visual layers and keep them behind content (z-index)."),
    "EC-V06": ("medium", "cursor:none", "Hiding the pointer removes the user's position cue.", "Keep the native cursor or provide an accessible equivalent."),
}

RE = lambda p, f=re.I: re.compile(p, f)
CLAIM_RE = RE(r"never leaves? your (?:device|phone|browser)|stays? (?:only )?on your (?:device|phone|browser)|100% (?:private|local)|"
              r"completely (?:private|local|offline)|local[- ]only|no data (?:is )?(?:ever )?(?:sent|leaves|uploaded|collected)|"
              r"nothing (?:is )?(?:ever )?(?:uploaded|sent|leaves)|we never (?:store|see|collect)|fully offline|your data never|"
              r"end-to-end encrypt|only you can (?:see|read)")
REMOTE_RE = RE(r"https?://[^\s'\"`)]*supabase\.co|\bcreateClient\s*\(|supabase\.|firebase|\bsendBeacon\b|new\s+WebSocket|XMLHttpRequest|"
               r"\bfetch\s*\(\s*[`'\"]https?:|\baxios\.(?:post|put|get)\s*\(|\.from\(['\"]\w+['\"]\)\.(?:insert|upsert|select|update)")
SAME_ORIGIN_FETCH = RE(r"\bfetch\s*\(\s*[`'\"](?!https?:)")
ANALYTICS_RE = RE(r"googletagmanager|google-analytics|\bgtag\s*\(|\bmixpanel\b|segment\.(?:com|io)|posthog|plausible\.io|hotjar|amplitude|"
                  r"fullstory|clarity\.ms|\bsentry\b|datadog|logrocket|\bfbq\s*\(")
STORAGE_RE = RE(r"\blocalStorage\b|\bsessionStorage\b|\bindexedDB\b|document\.cookie")
PERSONAL_KEY_RE = RE(r"setItem\s*\(\s*[`'\"][^`'\"]*(entr|journal|mood|diary|note|reflect|memor|feeling|emotion)")
LOCAL_DELETE_RE = RE(r"localStorage\.(?:removeItem|clear)\s*\(|sessionStorage\.(?:removeItem|clear)\s*\(")
REMOTE_DELETE_RE = RE(r"method\s*:\s*['\"]DELETE['\"]|\.delete\s*\(\s*\)\s*\.eq\(|\.from\([^)]*\)\s*\.delete\s*\(|deleteDoc\s*\(|\.remove\s*\(\s*\[")
ANY_DELETE_RE = RE(r"removeItem\s*\(|localStorage\.clear|method\s*:\s*['\"]DELETE['\"]|\.delete\s*\(|deleteDoc|\bdelete(?:Entry|Memory|Note|Account|Data|All)\b")
COERCIVE_RE = RE(r"you(?:'ve| have)? (?:haven'?t|have not|missed|forgot|abandoned|neglected)\b|we miss(?:ed)? you|don'?t (?:give up|break your streak|lose your streak)|"
                 r"streak (?:lost|broken|at risk)|you(?:'re| are) falling behind|last chance|your (?:pet|companion|cat|character|friend) (?:is|will be|gets?) (?:sad|lonely|hurt|waiting|worried)|"
                 r"come back (?:now|today)\b|you owe|are you sure you want to (?:leave|go)\b")
DIAG_RE = RE(r"\bdiagnos(?:e|es|is|ed|tic)\b|\bclinically\b|\btreats? (?:your )?(?:anxiety|depression|trauma)|\bcures?\b|"
             r"you(?:'re| are) (?:depressed|anxious|bipolar|traumati[sz]ed|suffering from)|clinically proven")
THERAPY_RE = RE(r"\btherap(?:y|eutic|ist)\b|\bheal(?:s|ing)?\b|reduces? (?:your )?(?:anxiety|stress|depression)|improves? (?:your )?mental health")
INFER_RE = RE(r"\bwe (?:detected|noticed|can tell|sense|think you)\b|\b(?:ai|our (?:ai|algorithm|model)) (?:detected|sensed|knows|thinks)\b|"
              r"\byour mood is\b|\byou(?:'re| are) (?:clearly|probably|obviously)\b|\byou seem (?:to be )?\w+|\bit looks like you(?:'re| are)\b")
MOTION_RE = RE(r"@keyframes|\banimation(?:-name)?\s*:|\btransition\s*:|requestAnimationFrame|\.animate\s*\(|\bgsap\b|\bTHREE\.|three(?:\.min)?\.js")
JS_MOTION_RE = RE(r"requestAnimationFrame|\bTHREE\.|three(?:\.min)?\.js|\bgsap\b")
RM_CSS_RE = RE(r"prefers-reduced-motion")
RM_JS_RE = RE(r"matchMedia\s*\([^)]*prefers-reduced-motion")
OVERLAY_SEL_RE = RE(r"canvas|overlay|particle|\bfx\b|vignette|noise|grain|aurora|stars|backdrop|cosmic|nebula|bg-?layer")


def read_files(root):
    out = []
    if os.path.isfile(root):
        return [(root, open(root, encoding="utf-8", errors="ignore").read())]
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS and not x.startswith("."))
        for f in sorted(files):
            if f.lower().endswith(EXTS):
                p = os.path.join(d, f)
                out.append((p, open(p, encoding="utf-8", errors="ignore").read()))
    return out


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def in_comment(text, pos):
    """True when pos sits on a line that is only a code comment (//, /*, *, #)."""
    start = text.rfind("\n", 0, pos) + 1
    return text[start:pos].lstrip().startswith(("//", "/*", "*", "#"))


def audit(root):
    files = read_files(root)
    base = root if os.path.isdir(root) else os.path.dirname(root)
    F = []

    def emit(rid, path, line, detail=""):
        sev, title, why, fix = RULES[rid]
        F.append({"rule": rid, "severity": sev, "file": os.path.relpath(path, base) if path else None, "line": line,
                  "title": title, "detail": detail, "why": why, "suggestion": fix})

    alltext = "\n".join(t for _, t in files)
    has_focus_visible = bool(re.search(r":focus-visible|:focus-within", alltext))
    remote_found = None
    local_delete = remote_delete = any_delete = False

    # --- project-level: motion
    motion_hit = next(((p, line_of(t, m.start())) for p, t in files for m in [MOTION_RE.search(t)] if m), None)
    if motion_hit:
        if not RM_CSS_RE.search(alltext) and not RM_JS_RE.search(alltext):
            emit("EC-A01", motion_hit[0], motion_hit[1])
        else:
            js_hit = next(((p, line_of(t, m.start())) for p, t in files for m in [JS_MOTION_RE.search(t)] if m), None)
            if js_hit and not RM_JS_RE.search(alltext):
                emit("EC-A01J", js_hit[0], js_hit[1])

    toast = RE(r"toast|snackbar").search(alltext)
    if toast and not RE(r"aria-live|role\s*=\s*[\"'](?:status|alert)").search(alltext):
        p, t = next((p, t) for p, t in files if RE(r"toast|snackbar").search(t))
        emit("EC-A08", p, line_of(t, RE(r"toast|snackbar").search(t).start()))

    seen_hosts, ext_scripts = set(), 0
    for path, t in files:
        for m in re.finditer(r"outline\s*:\s*(?:none|0)\b(?!\s*\w)", t, re.I):
            detail = "a :focus-visible rule exists elsewhere - confirm it covers this element" if has_focus_visible else "no :focus-visible replacement found in the project"
            emit("EC-A02", path, line_of(t, m.start()), detail)
        for m in re.finditer(r"user-scalable\s*=\s*(?:no|0)|maximum-scale\s*=\s*1(?:\.0)?\b", t, re.I):
            emit("EC-A04", path, line_of(t, m.start()))
        for m in re.finditer(r"<img\b[^>]*>", t, re.I | re.S):
            if not re.search(r"\balt\s*=", m.group(0), re.I):
                emit("EC-A05", path, line_of(t, m.start()))
        for m in re.finditer(r"<(?:input|textarea|select)\b[^>]*>", t, re.I | re.S):
            tag = m.group(0)
            if re.search(r"type\s*=\s*[\"']?(?:hidden|submit|button|reset|checkbox|radio)", tag, re.I) and "aria-label" not in tag:
                if not re.search(r"type\s*=\s*[\"']?(?:checkbox|radio)", tag, re.I):
                    continue
            if re.search(r"aria-label|aria-labelledby|\btitle\s*=", tag, re.I):
                continue
            idm = re.search(r"\bid\s*=\s*[\"']([^\"']+)", tag, re.I)
            if idm and re.search(r"for\s*=\s*[\"']%s[\"']" % re.escape(idm.group(1)), t, re.I):
                continue
            before = t[:m.start()]
            if before.lower().rfind("<label") > before.lower().rfind("</label>"):
                continue
            emit("EC-A06", path, line_of(t, m.start()), "no label, aria-label or wrapping <label> found")
        for m in re.finditer(r"<(?:audio|video)\b[^>]*\bautoplay\b|\.autoplay\s*=\s*true", t, re.I | re.S):
            emit("EC-A07", path, line_of(t, m.start()))
        for m in re.finditer(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", t, re.I):
            if float(m.group(1)) < 11:
                emit("EC-A09", path, line_of(t, m.start()), "%spx" % m.group(1))

        # privacy flows
        for m in REMOTE_RE.finditer(t):
            if remote_found is None:
                remote_found = (path, line_of(t, m.start()), m.group(0)[:40].rstrip("( "))
            emit("EC-P01", path, line_of(t, m.start()), "matched %r" % m.group(0)[:40].rstrip("( "))
            break
        if SAME_ORIGIN_FETCH.search(t):
            m = SAME_ORIGIN_FETCH.search(t)
            emit("EC-P01", path, line_of(t, m.start()), "same-origin fetch: confirm what the server does with it")
        for m in ANALYTICS_RE.finditer(t):
            emit("EC-P02", path, line_of(t, m.start()), "matched %r" % m.group(0))
            break
        m = STORAGE_RE.search(t)
        if m:
            emit("EC-P03", path, line_of(t, m.start()), m.group(0))
        for m in PERSONAL_KEY_RE.finditer(t):
            emit("EC-P03S", path, line_of(t, m.start()), "key matches personal-content pattern")
            break
        for m in re.finditer(r"(?:src|href|action)\s*=\s*[\"'](https?://([^/\"'\s]+))[^\"']*[\"']|url\(\s*[\"']?(https?://([^/\"')\s]+))", t, re.I):
            host = (m.group(2) or m.group(4) or "").lower()
            if host and host not in seen_hosts and host not in ("www.w3.org",):
                seen_hosts.add(host)
                emit("EC-P04", path, line_of(t, m.start()), host)
        for m in re.finditer(r"<script\b[^>]*\bsrc\s*=\s*[\"']https?://[^>]*>", t, re.I):
            ext_scripts += 1
            if not re.search(r"\bintegrity\s*=", m.group(0), re.I):
                emit("EC-X01", path, line_of(t, m.start()), re.search(r"src\s*=\s*[\"']([^\"']+)", m.group(0), re.I).group(1))
        if LOCAL_DELETE_RE.search(t):
            local_delete = True
        if REMOTE_DELETE_RE.search(t):
            remote_delete = True
        md = ANY_DELETE_RE.search(t)
        if md:
            any_delete = True
            emit("EC-D03", path, line_of(t, md.start()), md.group(0).rstrip("( "))

        # copy
        for rid, rx in (("EC-C01", COERCIVE_RE), ("EC-C02", DIAG_RE), ("EC-C03", THERAPY_RE), ("EC-C04", INFER_RE)):
            for m in rx.finditer(t):
                if in_comment(t, m.start()):
                    continue
                emit(rid, path, line_of(t, m.start()), "matched %r" % m.group(0)[:50])

        # effect layers
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", t):
            sel, body = m.group(1).strip().splitlines()[-1] if m.group(1).strip() else "", m.group(2)
            if OVERLAY_SEL_RE.search(sel) and re.search(r"position\s*:\s*(?:fixed|absolute)", body, re.I) \
                    and re.search(r"inset\s*:\s*0|100vw|100%|width\s*:\s*100", body, re.I) \
                    and not re.search(r"pointer-events\s*:\s*none", body, re.I):
                emit("EC-V05", path, line_of(t, m.start()), "selector %r" % sel[:50])
        for m in re.finditer(r"cursor\s*:\s*none", t, re.I):
            emit("EC-V06", path, line_of(t, m.start()))

    # claims vs flows
    for path, t in files:
        for m in CLAIM_RE.finditer(t):
            if in_comment(t, m.start()):
                continue
            if remote_found:
                emit("EC-P05", path, line_of(t, m.start()),
                     "claim %r vs remote flow at %s:%d (%s)" % (m.group(0), os.path.relpath(remote_found[0], base), remote_found[1], remote_found[2]))
            else:
                emit("EC-P05U", path, line_of(t, m.start()), "claim %r" % m.group(0))

    # deletion coherence
    if remote_found and local_delete and not remote_delete:
        emit("EC-D01", remote_found[0], remote_found[1], "local removal found, no remote delete call found")
    if remote_found and not any_delete:
        emit("EC-D02", remote_found[0], remote_found[1])

    # decorative-excess diagnostics (counts across project)
    counts = lambda rx: sum(len(rx.findall(t)) for _, t in files)
    n = counts(RE(r"backdrop-filter"))
    if n >= 4:
        emit("EC-V01", files[0][0] if files else None, None, "%d uses" % n)
    n = counts(RE(r"(?:linear|radial|conic)-gradient"))
    if n >= 15:
        emit("EC-V02", files[0][0] if files else None, None, "%d gradients" % n)
    n = counts(RE(r"particle"))
    if n >= 5:
        emit("EC-V03", files[0][0] if files else None, None, "%d mentions of 'particle'" % n)
    n = counts(RE(r"(?:box|text)-shadow\s*:[^;]*0\s+0\s+\d+px"))
    if n >= 8:
        emit("EC-V04", files[0][0] if files else None, None, "%d glow shadows" % n)

    # de-duplicate identical (rule,file,line,detail)
    uniq, seen = [], set()
    for f in F:
        k = (f["rule"], f["file"], f["line"], f["detail"])
        if k not in seen:
            seen.add(k)
            uniq.append(f)
    return uniq, len(files)


def main():
    ap = argparse.ArgumentParser(description="Static heuristic audit for emotionally expressive / personal-content front ends.")
    ap.add_argument("path", help="file or directory to scan")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on", default="high", choices=["high", "medium", "low", "never"])
    ap.add_argument("--ignore", default="", help="comma-separated rule ids to ignore")
    ap.add_argument("--min-severity", default="info", choices=list(SEV_ORDER))
    a = ap.parse_args()
    ign = {x.strip() for x in a.ignore.split(",") if x.strip()}
    F, nfiles = audit(a.path)
    F = [f for f in F if f["rule"] not in ign and SEV_ORDER[f["severity"]] >= SEV_ORDER[a.min_severity]]
    F.sort(key=lambda f: (-SEV_ORDER[f["severity"]], f["rule"], f["file"] or "", f["line"] or 0))
    worst = max([SEV_ORDER[f["severity"]] for f in F] or [-1])
    if a.json:
        print(json.dumps({"tool": "audit_frontend", "target": a.path, "files_scanned": nfiles, "findings": F}, indent=2))
    else:
        print("audit_frontend: %s  (%d files scanned)" % (a.path, nfiles))
        print("  Static heuristic scan - not an accessibility, privacy or security review. Each finding is a question to verify in code.")
        for f in F:
            loc = "%s:%s" % (f["file"], f["line"]) if f["line"] else (f["file"] or "")
            print("  [%s] %s %s - %s%s" % (f["severity"].upper(), f["rule"], loc, f["title"], " (%s)" % f["detail"] if f["detail"] else ""))
        print("  %d finding(s)" % len(F) if F else "  OK - no findings from this scan (absence of findings is not evidence of compliance)")
    thr = {"high": 3, "medium": 2, "low": 1, "never": 99}[a.fail_on]
    return 1 if worst >= thr else 0


if __name__ == "__main__":
    sys.exit(main())
