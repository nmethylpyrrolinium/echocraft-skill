---
name: echocraft
description: >-
  Engineering method for building and reviewing emotionally expressive interfaces: journaling, mood, reflection,
  ritual, companion and atmospheric or cinematic apps. Use when a task adds or reviews mood or reflection features,
  emotional microcopy, atmospheric visuals or motion, empty and returning-user states, personalization, or
  export, deletion or sync of personal content, and whenever an app is described as private or local-first.
  Defines an emotional contract, maps interface states, extends the existing design system instead of replacing it,
  traces data flows, checks accessibility and reduced motion, and reports only evidence that was actually
  gathered. Do not use for generic marketing pages, dashboards or forms with no emotional or personal-content
  dimension.
license: MIT
compatibility: Instructions work in any agent that loads Agent Skills. Bundled scripts need Python 3.8+ (standard library only); without a shell, follow the manual checklists in the references.
metadata:
  author: "Alam"
  version: "0.1.0"
---

# EchoCraft

Help the user build interfaces that feel emotionally considered without inventing feelings, hiding data flows, or excluding people. The method is the ECHO CYCLE (below). It produces artifacts a reviewer can check: a contract, a state table, a data-flow inventory, and an evidence report.

## 0. Activation gate (decide before anything else)

| Class | Signal | What to do |
|---|---|---|
| N - not applicable | Landing page, admin dashboard, generic form, no personal or emotional content | Do not apply this skill. Do the task normally and do not mention the skill. |
| L - light | Expressive visuals, motion or copy, but no personal data stored or sent | Steps 1, 3, 5, 6, 7 using the atmosphere and accessibility references. Skip the privacy inventory. |
| F - full | Journals, moods, reflections, personalization, sync, export, deletion, or any privacy claim | All steps. |

If the class is unclear, ask at most one question whose answer changes the scope.

## Non-negotiables

1. Inspect the project before proposing anything. Prefer its architecture, dependencies and design language. Never rewrite an established design system to be more dramatic.
2. Every emotional word shown to a user has provenance: **stated** (the user chose it), **derived** (computed from stated data by a rule you can explain) or **inferred** (a guess). Inferred states need explicit opt-in, a label, an explanation and a way to dismiss. Default to not inferring.
3. No diagnosis, therapy, treatment or wellbeing-outcome claims unless the owner supplies a verified basis. Do not add emotion detection or hidden profiling.
4. Never pressure engagement with guilt, streak loss, or a sad companion. Offer a neutral way to continue.
5. Emotional participation is optional whenever the core task can be done without it. Declining must leave a complete, unpunished experience.
6. Do not claim "private", "local-first", "encrypted", "deleted" or "secure" without tracing the data flow. State what the code shows and what needs backend or independent review.
7. Never print or store secrets, tokens, private identifiers or user entries. Redact in reports and examples.
8. Never claim a test, screenshot, browser run or audit that did not happen. Say what was not run.
9. Motion, sound and effects must be skippable, reducible, and must not block the primary task.
10. Do not add dependencies for effects that CSS or existing code can do.

## The ECHO CYCLE as steps

Each step names what to produce. Read the reference only when you reach that step.

1. **Establish intent.** Inspect stack, entry points, styles, storage, auth, backend calls, tests and deploy config first. Then write a five-line brief: objective, user's expressive tolerance, accessibility needs, constraints, acceptance criteria. Ask only what you cannot learn from the repo.
2. **Contextualize.** Fill `assets/emotional-contract-template.md` using `references/emotional-contract.md`: what the interface may infer, what it must never assume, what the user controls, what happens with too little data or a declined prompt.
3. **Harmonize.** Map states with `references/state-mapping.md` and `assets/state-transition-template.md`; run `scripts/state_table_check.py`. Then inventory existing tokens with `scripts/inspect_tokens.py` and define any additions using `references/atmosphere-system.md`. Tokens and rules come before components; every visual choice gets a stated reason.
4. **Observe privacy and agency.** For Full class: fill `assets/data-flow-template.md` using `references/privacy-and-agency.md`; run `scripts/audit_frontend.py` and `scripts/scan_secrets.py`. Classify each privacy claim as code-verified, config-dependent, or needs independent review.
5. **Construct the smallest coherent change.** Match existing conventions. Implement explicit states and fallbacks. Small reviewable increments. No framework swaps or rewrites.
6. **Yield to accessibility and control.** Follow `references/accessibility-review.md`: keyboard, visible focus, contrast, reduced motion, non-colour signals, labels, pause/skip/disable for expressive effects.
7. **Challenge the result.** Test the conditions in `references/evaluation-method.md`: ordinary, empty, incomplete, returning, error, offline, narrow screen, reduced motion. Look for incoherence, leakage and unearned assumptions.
8. **Log evidence.** Fill `assets/evidence-report-template.md`: commands actually run, results, limitations, unresolved risks.
9. **Evolve responsibly.** Recommend changes from observed failures and explicit user feedback. Do not change the emotional contract silently.

## Decision rules

| Situation | Rule |
|---|---|
| Existing design system | Inventory it first; add tokens only for a gap you can name; reuse its naming. |
| Brief asks for "more emotional" | Ask what the user should feel able to *do*, then change behaviour and copy before adding effects. |
| Too little data for an insight | Show less: counts, a neutral invitation, or nothing. Never fabricate a trend. |
| User declines personalization | Complete experience, no repeated nagging; re-offer only from settings the user opens. |
| Entry content might show distress | Do not add detection or automated replies. A static, user-initiated help-resources entry is a product decision for the owner and needs expert review; flag it, do not improvise it. |
| Remote sync exists beside a local-first claim | Treat the claim as unverified; fix the claim or the flow. |
| Delete behaviour of the backend is unknown | Label the control by what is proven ("Remove from this device"), report "unknown", ask for backend evidence. |
| Effect hides or slows the main task | Cut or demote the effect; the task wins. |
| New library proposed for a small effect | Show the CSS or existing-code alternative; add only with a stated need, pinned version and integrity check. |
| Test or browser tools unavailable | Use the capability ladder below and report the gap. |
| Milestone or celebration | Celebrate what the user did, once, dismissibly; never attach loss or obligation. |

## Capability ladder (use the strongest available, report which)

1. Real browser or device run with screenshots, keyboard and reduced-motion toggled.
2. Project's own tests, linter and build.
3. Bundled scripts on the source tree (static heuristics only).
4. Manual reading of the code, with file and line references.
5. A checklist handed to the user for steps you cannot run.

## Scripts (standard library Python; run with `python3`)

- `scripts/validate_skill.py <dir>` - structure and metadata check for this skill package.
- `scripts/state_table_check.py <file.md> [--entry a,b] [--require x,y]` - dead ends, traps, unreachable and nondeterministic states in a transition table.
- `scripts/inspect_tokens.py <dir> [--pairs="--fg:--bg"]` - existing CSS custom properties, hard-coded colour share, contrast of named pairs.
- `scripts/audit_frontend.py <dir>` - static heuristics: reduced motion, remote flows, analytics, storage, claims vs flows, deletion, copy, accessibility smells, effect diagnostics.
- `scripts/scan_secrets.py <dir> [--deny STRING]` - credential and private-identifier patterns; output is redacted.

All scripts accept `--json`. Their findings are questions to verify in code, not verdicts. A clean run is not proof of compliance.

## Reporting

Use these labels exactly: **Executed** (command ran, output seen), **Observed** (looked at in a real browser or device), **Static** (read from code or script heuristics), **Not verified** (not done or not possible). Never upgrade a label. End every report with what remains unverified.

## Reference map

| File | Read when |
|---|---|
| `references/emotional-contract.md` | Writing or auditing the contract, copy tone, personalization |
| `references/state-mapping.md` | Mapping journeys, empty/error/offline/deletion states |
| `references/atmosphere-system.md` | Turning a brief into tokens, motion, sound, microcopy; anti-template diagnostics |
| `references/privacy-and-agency.md` | Any storage, sync, export, deletion, analytics or privacy claim |
| `references/accessibility-review.md` | Reviewing keyboard, contrast, motion, screen-reader behaviour |
| `references/evaluation-method.md` | Testing, evidence levels, what to report |
| `assets/emotional-contract-template.md` | Step 2 output |
| `assets/state-transition-template.md` | Step 3 output (feeds the checker) |
| `assets/data-flow-template.md` | Step 4 output |
| `assets/evidence-report-template.md` | Step 8 output |
