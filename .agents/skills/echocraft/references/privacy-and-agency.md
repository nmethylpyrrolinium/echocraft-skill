# Privacy and agency

For apps that hold reflections, moods, behavioural history or other personal content. This is an engineering aid for tracing what the code does. It is not legal advice and does not replace a security or privacy review where one is warranted. Templates: `assets/data-flow-template.md`. Static scan: `scripts/audit_frontend.py`, `scripts/scan_secrets.py`.

## Contents
1. Principles
2. Data classes and risk
3. Build the data-flow inventory
4. Evidence classes for claims
5. Browser storage limits
6. Remote backends
7. Deletion and export
8. Third parties and analytics
9. Wording rules
10. Privacy-claim verification report
11. Rules that always apply

## 1. Principles

Minimise what is collected. Keep it where the user can see it. Make leaving, exporting and deleting real. Say only what you have verified, and say where verification stops.

## 2. Data classes and risk

| Class | Examples | Risk | Handling |
|---|---|---|---|
| R0 | UI preferences (theme, reduced motion) | Low | Local storage is fine |
| R1 | Usage and behaviour (timestamps, feature use) | Medium | Collect only with a stated need; no remote by default |
| R2 | User-authored content (entries, notes, images) | High | Disclosed storage location; export and delete paths |
| R3 | Emotional or health-adjacent data (stated moods, tags, summaries) and anything derived from R2 | High | As R2, plus no profiling and no use for engagement pressure |
| R4 | Credentials, tokens, identifiers, keys | Critical | Never in logs, reports, client bundles (except public-by-design keys), or examples |

Derived data inherits the class of its source. A mood summary of R2 text is R3.

## 3. Build the data-flow inventory

For each datum, one row: **what**, **class**, **where created**, **where stored** (memory, localStorage, sessionStorage, IndexedDB, cookie, service-worker cache, remote database, file storage, third-party), **persistence** (session, until cleared, indefinite), **transmitted?** (to whom, when, over what), **consent and notice** (what the user was told, opt-in or default), **user access** (view, export), **deletion** (what is removed, where, what survives), **logs/analytics/backups**, **evidence** (file:line), **status** (verified, config-dependent, unknown).

Method: search the source for every storage and network API, every third-party host, every SDK, service worker, and build step that bakes data in. Start from `audit_frontend.py` output (EC-P01 to EC-P04) and then read, because regexes miss minified code, dynamic URLs and server behaviour.

## 4. Evidence classes for claims

| Class | Meaning | Example | May the report assert it? |
|---|---|---|---|
| E1 Code-verified | Visible in the repo; cite file:line | "Entries are written to localStorage under key X" | Yes |
| E2 Config-dependent | Depends on backend or hosting settings not in the repo | "Row-level security restricts rows to the owner" | Only as "requires verifying in the backend", unless the user supplies the policy |
| E3 Review-dependent | Needs expertise or an external check | "Encrypted", "compliant", "secure against XSS" | No; state that review is required |
| E4 Unobservable | Cannot be known from the frontend | "Backups are deleted after 30 days" | No; list as unknown |

Every privacy sentence in the product or the README gets an E-class. A sentence you cannot class is removed or rewritten.

## 5. Browser storage limits

- Not encrypted by the browser at the app level; readable by any script running on the origin, including injected and third-party scripts.
- Readable by anyone with access to the unlocked device and browser profile.
- Can be cleared by the user, by the browser under storage pressure, or by privacy features; some browsers limit lifetime of script-written storage (browser-specific; verify for your targets). Do not promise durability. If durability matters, say how data is backed up or exported.
- Capacity is limited (commonly a few megabytes for localStorage; varies).
- Service-worker and HTTP caches may hold copies of content; include them in the inventory.
- "Local-first" describes where the primary copy lives, not that nothing is transmitted. Trace first, then label.

## 6. Remote backends

If a remote database or auth exists:
- **Authentication boundary**: which calls need a signed-in user; what an anonymous caller can reach.
- **Authorization**: per-row access rules for read, insert, update and delete, each verified separately. In row-level-security setups (for example Postgres-based backends), confirm RLS is enabled on every exposed table and write a test with a second account that must fail to read or modify the first account's rows.
- **Keys**: public client keys are designed to be public and are only safe if authorization rules are correct; service-role or admin keys must never ship to a client or appear in reports.
- **Sync**: is it optional and opt-in, or default? What is sent when it is on? What happens to remote copies when the user disables sync or deletes?
- **Logging and analytics**: what the backend and any SDK log; retention.
- Anything in the repo cannot prove these; mark E2 and ask the owner for the policy text or a test result.

## 7. Deletion and export

Define "deleted" precisely: from the screen, from this device, from the server, from backups, from third parties. Then:
- Test each layer you can reach and record the result; list the layers you cannot reach as unknown.
- If remote deletion is unproven, do not label the control "Delete"; label what is true ("Remove from this device") and say so in the UI.
- Confirm or offer undo for irreversible actions. Undo must really restore.
- Export: say what it includes, in an open format, without secrets or other users' data.
- Account deletion is its own flow with its own states (`references/state-mapping.md`).

## 8. Third parties and analytics

- Every third-party request (fonts, CDN scripts, images, embeds, players, share links) reveals IP address and user agent, usually referrer. List them.
- Prefer self-hosting assets on sensitive screens. Pin versions and use integrity attributes for external scripts.
- Do not add analytics, session replay or telemetry unless the requirements call for it, the user is told, and the data excludes content and mood. Never send entry text or mood values to analytics.
- Links out to music, video or social services are user-initiated navigation; say so rather than embedding trackers.

## 9. Wording rules

| Do not write | Write (if true) |
|---|---|
| "Your data never leaves your device" | "Entries are saved in this browser. Sync is off unless you turn it on." |
| "Encrypted" | Only after E1 evidence of what is encrypted, with what, where keys live. Otherwise omit. |
| "Deleted forever" | What was removed and from where |
| "Private" | Who can read it, by what mechanism |
| "We never see your entries" | Only with E1 + E2 evidence; else state what is stored remotely |

## 10. Privacy-claim verification report

Use this table in the evidence report.

| Claim (quote) | Where it appears | E-class | Evidence (file:line / test) | Verdict | Required next step |
|---|---|---|---|---|---|
| "..." | file:line | E1/E2/E3/E4 | ... | Supported / Contradicted / Unverified | ... |

Verdict **Contradicted** requires a cited code path. **Unverified** is the correct verdict for anything the repo cannot show.

## 11. Rules that always apply

- Never expose secrets in reports or generated examples.
- Never assume browser storage is encrypted or durable.
- Never claim local-first means completely private without tracing all flows.
- Never enable remote transmission or analytics without a requirement and user notice.
- Never invent consent, deletion, encryption or authorization guarantees.
- Never use inferred emotion to pressure engagement or purchases.
- Never make emotional participation compulsory.
- Never add emotion detection, surveillance or hidden profiling as a convenience.
