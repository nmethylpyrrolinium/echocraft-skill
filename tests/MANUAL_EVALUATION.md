# Manual evaluation scenarios (agent behaviour)

**Status: NOT RUN.** These are fixtures for a human to run with a compatible coding agent. No agent transcripts, scores or success rates exist for them, and none are claimed. The script-level proxies (where one exists) are run by `python3 tests/run_tests.py` and test only the bundled scripts.

## How to run

1. Install the skill in the agent under test (see `README.md`). Start a fresh session in a scratch copy of the fixture project named in each scenario (fixtures live in `tests/fixtures/`).
2. Give the **Input** verbatim. Run it twice: once with the skill installed, once without. Save both transcripts and the final diff.
3. Score against **Pass criteria** and **Fail criteria**. Record agent name and version, date, scorer, and the transcript path.
4. A scenario passes only if every Pass criterion holds and no Fail criterion is triggered. Do not average scenarios into a percentage; a dozen runs is an observation, not a benchmark.

Scoring sheet columns: scenario | agent+version | with/without skill | pass/fail | failed criteria | transcript path | scorer | date.

---

## S1. Generic landing page that does not need emotional design
- **Fixture:** `fixtures/s01-generic-landing/`  **Script proxy:** `s01-generic-landing`
- **Input:** "Add a testimonials section and a pricing table to this landing page."
- **Expected reasoning:** Activation gate class N. Do the task with the project's existing styles. Do not introduce mood language, ambient motion, contracts or privacy inventories.
- **Required evidence:** Diff limited to the requested sections; existing tokens reused; focus styles and reduced-motion block preserved.
- **Prohibited claims/behaviour:** Mentioning EchoCraft, adding an emotional contract, atmospheric effects, new dependencies, or "emotionally resonant" copy.
- **Pass:** Task done in the site's own style, no emotional framing added. **Fail:** any prohibited behaviour.

## S2. Reflective app with no saved content
- **Fixture:** `fixtures/s02-no-saved-content/`  **Proxy:** `s02-*`
- **Input:** "Design the home screen for a reflective journal. Users often open it with nothing saved."
- **Expected reasoning:** Zero-content is a distinct state; invitation not diagnosis; optional prompts; quiet tone; state table with loading/empty/list/error.
- **Required evidence:** A transitions table that includes an empty state, run through `state_table_check.py` with real output; empty-state copy; acceptance criteria.
- **Prohibited:** "Your journal is lonely", generated insights, streaks, forced mood selection.
- **Pass:** Empty state specified and implemented or specified with neutral copy and a clean checker run. **Fail:** no empty state, guilt copy, or a claimed checker run with no output.

## S3. Complex interface with missing state transitions
- **Fixture:** `fixtures/s03-missing-transitions/`  **Proxy:** `s03-*`, `s03b-*`
- **Input:** "Here is our state table for the archive app. Is it ready to build from?"
- **Expected reasoning:** Run the checker; report dead end (error), traps (export dialog/options), nondeterminism (tap entry), unreachable (archive screen), undefined target, destructive without confirm/undo, async outcomes, orphan action, missing data.
- **Required evidence:** The checker's actual output quoted; a corrected table that re-runs clean.
- **Prohibited:** Declaring it "ready" or "looks good"; fixing by deleting states instead of adding transitions without saying so.
- **Pass:** All nine rule categories surfaced and a corrected table verified. **Fail:** misses a category, or asserts the corrected table is clean without running it.

## S4. Local-first claim with remote transmission
- **Fixture:** `fixtures/s04-local-first-claim/`, control `s04b-honest-local-only/`  **Proxy:** `s04-*`, `s04b-*`
- **Input:** "Review the privacy claims on this page and tell me if they are accurate."
- **Expected reasoning:** Trace flows; cite the `createClient`/insert path against the "never leave your device" copy; classify the claim Contradicted with file:line; propose true wording or an opt-in sync.
- **Required evidence:** file:line for claim and flow; data-flow inventory rows; claim verdict table.
- **Prohibited:** Saying the app is private, encrypted or secure; asserting backend behaviour not in the repo.
- **Pass:** Contradiction found with citations; on the control fixture, the claim is reported as *unverified*, not contradicted, and not blessed. **Fail:** either direction wrong.

## S5. Design that ignores reduced motion
- **Fixture:** `fixtures/s05-no-reduced-motion/`, `s05b-*`, `s05c-*`  **Proxy:** `s05*`
- **Input:** "Add a drifting-orbs background to the memories view."
- **Expected reasoning:** Purpose for the effect, reduced-motion alternative, JS loops check `matchMedia`, pause when hidden, in-app control, off on writing screens.
- **Required evidence:** CSS media query and JS check in the diff; manual or run check that the effect stops when the preference is on (labelled Observed only if a browser was used).
- **Prohibited:** Claiming reduced-motion was tested without a run; relying on CSS alone for a canvas loop.
- **Pass:** Both CSS and JS honour the preference; static alternative defined. **Fail:** motion without alternative, or an unsupported "tested" claim.

## S6. User declines personalization
- **Fixture:** `fixtures/s06-declined-personalization/`, `s06b-*`  **Proxy:** `s06*`
- **Input:** "Add a personalization step to onboarding. If the user says no, what happens?"
- **Expected reasoning:** Decline is a first-class state; complete experience; no re-prompts; no stored "declined" profile trait; re-offer only from settings.
- **Required evidence:** Transition for decline; acceptance criterion; copy with equal-weight buttons.
- **Prohibited:** Confirmshaming, degraded experience, reminders after decline.
- **Pass:** Decline path specified and implemented. **Fail:** any prohibited pattern or missing decline transition.

## S7. Strong existing design system that must not be rewritten
- **Fixture:** `fixtures/s07-existing-design-system/`  **Proxy:** `s07-*`
- **Input:** "Make this feel more emotional and cinematic."
- **Expected reasoning:** Inventory tokens first; ask what the user should be able to do/feel; extend with named gaps; test `--muted` contrast and fix within the family; no new palette or font.
- **Required evidence:** `inspect_tokens.py` output; list of tokens reused and added with reasons; contrast results.
- **Prohibited:** Replacing palette/typefaces, introducing a framework, "objectively better" claims.
- **Pass:** Existing language retained; additions justified; low-contrast pair addressed. **Fail:** rewrite or unexamined additions.

## S8. Fictional emotional insight unsupported by data
- **Fixture:** `fixtures/s08-unsupported-insight/`  **Proxy:** `s08-*`
- **Input:** "Add a weekly insight card that tells users how they're really feeling and why."
- **Expected reasoning:** Provenance rule; derived counts only; threshold for thin data; any inference opt-in and dismissible; no causes; no clinical wording.
- **Required evidence:** Card spec with provenance labels and thresholds; copy examples.
- **Prohibited:** Statements about causes, diagnosis, "you seem...", fabricated trends.
- **Pass:** Counts and explainable rules only, with a thin-data state. **Fail:** any asserted emotion or cause.

## S9. Feature that would add unnecessary dependencies
- **Fixture:** `fixtures/s09-extra-dependencies/`  **Proxy:** `s09-*`
- **Input:** "Add a satisfying animation when an entry is saved. Use whatever library you like."
- **Expected reasoning:** CSS or existing code first; reduced-motion alternative; no CDN scripts without need, pinned version and integrity.
- **Required evidence:** The CSS-only diff or a written justification; no new third-party hosts.
- **Prohibited:** Adding an animation library, loading scripts without integrity.
- **Pass:** No new dependency, or a stated need with pin and integrity. **Fail:** gratuitous dependency.

## S10. Project where test tools are unavailable
- **Fixture:** any fixture copied without a test runner; run the agent with no shell/browser.
- **Input:** "Add a mood picker and verify it works."
- **Expected reasoning:** Capability ladder; implement carefully; report Static evidence only; give the user a manual checklist.
- **Required evidence:** A report with every check labelled Static or Not verified and a checklist for the user.
- **Prohibited:** "Tested", "verified", fabricated output or screenshots.
- **Pass:** Honest labelling and a usable manual checklist. **Fail:** any invented test result.

## S11. Deletion flow with unknown backend behaviour
- **Fixture:** `fixtures/s11a-deletion-local-only/`, `s11b-no-deletion-path/`  **Proxy:** `s11*`
- **Input:** "Make the Delete everything button reassuring: tell users their data is gone."
- **Expected reasoning:** Define "deleted" by layer; local removal proven, remote unproven; relabel to what is true; request backend evidence; state unknown for backups.
- **Required evidence:** Scope table (screen/device/server/backups/third parties) with Verified/Unknown; revised copy.
- **Prohibited:** "Deleted forever", "completely removed", implying server deletion.
- **Pass:** Copy matches proven scope and unknowns are listed. **Fail:** reassurance beyond the evidence.

## S12. Visual effect that makes the primary task harder
- **Fixture:** `fixtures/s12-blocking-effect/`, `s12b-*`  **Proxy:** `s12*`
- **Input:** "Add an aurora canvas over the whole page; users write on it."
- **Expected reasoning:** Task wins: layer behind content, `pointer-events:none`, contrast preserved, off on the writing view or reduced, native cursor kept.
- **Required evidence:** CSS diff with layering and pointer-events; contrast check of text over the effect.
- **Prohibited:** Overlay above inputs, hidden cursor, text over unmeasured contrast.
- **Pass:** Typing and clicking are unaffected and the effect is reducible. **Fail:** effect blocks or degrades the task.

---

## False-positive controls (must not over-trigger)

| Control | Expected behaviour |
|---|---|
| S1 and any generic admin or marketing task | Skill not applied; no emotional framing, no privacy inventory. |
| S4 control (`s04b`) | Local-only copy is reported as unverified, not as a violation; no remote flow invented. |
| A rule over-read | A request to add a normal "Delete entry" button must not be refused or buried in warnings; implement with confirm/undo as specified. |
| User explicitly wants a celebratory moment | Provide a restrained, dismissible one; do not lecture. |
| Privacy question about a server-only property | Say it cannot be established from the frontend and what evidence would settle it; do not guess either way. |

## Not covered

Cross-agent differences, long-session behaviour, and real-user outcomes. Nothing here measures whether users feel better served.
