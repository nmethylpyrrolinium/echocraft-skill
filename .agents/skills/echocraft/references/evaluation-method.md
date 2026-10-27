# Evaluation method

How to test an emotionally expressive change, how to log evidence honestly, and how to evaluate the skill itself.

## Contents
1. Evidence levels
2. Condition matrix
3. Capability ladder
4. Logging rules
5. Report structure
6. Evaluating the skill (not the app)
7. Failure modes to watch for in agent behaviour

## 1. Evidence levels

| Label | Meaning | Allowed wording |
|---|---|---|
| Executed | A command ran and you read its output | "Ran `npm test`: 41 passed, 0 failed" (quote the real numbers) |
| Observed | You looked at the running app in a real browser or device | "In Chromium at 390px, focus ring visible on all five controls" |
| Static | Read from code or from a script's heuristics | "`app.js:42` writes entries to localStorage" |
| Not verified | Not done, or not possible here | "Screen-reader behaviour not tested" |

Never promote a level. A script that found nothing is Static, not "verified clean".

## 2. Condition matrix

Test each relevant condition; mark N/A with a reason, never skip silently.

| Condition | What to check |
|---|---|
| Ordinary | Main task completes; copy matches the contract |
| Empty | Invitation, no summary, no fake insight |
| One item / many items | Layout, tone, performance with realistic counts |
| Incomplete | Optional fields skipped; draft preserved |
| Returning user | Neutral welcome; no remarks about absence |
| Error (recoverable / not) | Message states what happened and next step; data not lost |
| Offline | Behaviour is stated; no silent data loss |
| Session expired | Draft preserved; sign-in returns to same place |
| Narrow screen | 320px, keyboard open, safe areas |
| Reduced motion | No movement, information intact, in-app control works |
| Keyboard only | Every action reachable; focus visible |
| Declined personalization | Complete, no re-prompts |
| Deletion / export | Scope wording true; result verified where reachable |

## 3. Capability ladder

Use the strongest available and say which: (1) real browser run with screenshots; (2) the project's tests, linter, build; (3) bundled scripts; (4) manual code reading with file:line; (5) a checklist for the user. If a browser tool is unavailable, do not describe visual results; describe code and tell the user what to look at.

## 4. Logging rules

- Record the exact command and the exit status.
- Quote counts and messages from real output; do not round or summarise into success.
- Redact secrets, tokens, private identifiers and user content.
- Note environment (OS, runtime versions, browser) when it affects results.
- If a step fails, record the failure, then the fix, then the re-run.
- Do not fabricate screenshots, scores, timings or success rates.

## 5. Report structure

Use `assets/evidence-report-template.md`: objective and acceptance criteria; changes made; states covered; data-flow summary; checks with evidence level; findings and fixes; limitations; unresolved risks; what the user should verify.

## 6. Evaluating the skill (not the app)

Scripts are tested by `tests/run_tests.py`. Agent behaviour is evaluated with the scenarios in `tests/MANUAL_EVALUATION.md`:
1. Run each scenario's input twice in the same agent: once with the skill installed, once without. Save both transcripts.
2. Score each against that scenario's pass/fail criteria. Record who scored and when.
3. Treat results as observations from a small sample; do not report percentages from a handful of runs.
4. Re-run after any change to SKILL.md or references; compare, do not assume improvement.

## 7. Failure modes to watch for in agent behaviour

- Applies emotional styling to an unrelated project (activation gate ignored).
- Writes prose instead of changing code or producing the artifacts.
- Asserts a privacy property from the frontend alone.
- Claims a test or screenshot that never ran.
- Replaces an existing design system.
- Adds a library for an effect CSS can do.
- Invents an emotional insight from too little data.
- Refuses ordinary useful work because a safety rule was over-read.
