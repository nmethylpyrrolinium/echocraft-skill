# Atmosphere system

How to turn a brief into design tokens and interaction rules, and how to diagnose decoration that does no work. Atmosphere is a means of supporting the user's task; it is not the task.

## Contents
1. Order of work
2. Inspect before adding
3. Visual thesis
4. Token layers and naming
5. Typography and measure
6. Colour and contrast
7. Layout, density, depth
8. Motion
9. Sound and haptics
10. Microcopy voice
11. Anti-template diagnostic
12. What not to claim

## 1. Order of work

1. Inspect the existing design language (section 2).
2. Write a one-sentence visual thesis with reasons (section 3).
3. Define or extend tokens (section 4) and interaction rules (sections 8-9).
4. Write the microcopy voice sheet (section 10).
5. Only then build components, using the tokens.
6. Run the diagnostic (section 11) on the result and fix what you cannot justify.

## 2. Inspect before adding

Run `python3 scripts/inspect_tokens.py <src> --pairs="--text:--bg"` (use the project's own token names). Read the output as a map of the existing language: how many tokens, which groups, how much colour is hard-coded.

Rules:
- If a token exists for the job, use it. If a near-match exists, extend its family with the same naming.
- Add a token only for a gap you can name in one sentence ("no token for a quiet-state surface").
- Do not replace a palette, type pairing or spacing scale because a new one would look more dramatic.
- If the language lives in hard-coded values or a framework, say so, and propose tokenization as a separate, optional step.
- Record each addition in the evidence report: name, value, reason.

## 3. Visual thesis

One sentence: what the surface is and why, e.g. "A dim, warm room where the page is the only light, because the user is writing something private at night." Then list 3-5 consequences for type, colour, motion and sound. A reference direction (film, print, architecture) is fine as inspiration but never as justification by itself. You cannot guarantee originality; you can show every choice has a reason and a cost.

## 4. Token layers and naming

- **Primitive**: raw values, named by what they are (`ink-900`, `gold-500`). Not used directly by components.
- **Semantic**: named by job (`text-primary`, `text-muted`, `surface-base`, `surface-raised`, `accent-attention`, `border-quiet`, `focus-ring`).
- **State/emotional**: named by the *stated* input they respond to, never by an inferred one (`mood-calm-tint`). Mapping from stated mood to tint is a design decision, not a diagnosis.
- **Motion**: `motion-duration-instant|quick|considered|slow`, `motion-ease-settle`.
- **Component**: only when a component needs an override.

Use the project's existing prefix and casing. If none exists, pick one and document it. Components reference semantic tokens only, so a reduced-motion, high-contrast or quiet theme can swap values without editing components.

## 5. Typography and measure

- A small hierarchy (display, heading, body, caption, label) with stated sizes and line heights.
- Body measure about 45-75 characters per line; narrower for reflective reading.
- Body text no smaller than comfortable on a phone; avoid text under 12px for anything meant to be read.
- Reserve decorative or display faces for large headings; body in a legible face.
- Respect user text-size and zoom; use relative units.

## 6. Colour and contrast

- Semantic pairs are tested, not eyeballed: `inspect_tokens.py --pairs` computes WCAG contrast for named pairs (hex/rgb only; no alpha).
- Targets: 4.5:1 for body text, 3:1 for large text and for UI boundaries and focus indicators.
- Muted text is the usual failure on dark themes. Test it first.
- Colour never carries meaning alone: pair mood colours with a label, icon or text.
- Provide the same information in a high-contrast or quiet variant if the atmosphere relies on low-contrast layers.

## 7. Layout, density, depth

- Choose a spacing scale and a rhythm; keep density consistent within a view type.
- Write views must be calm: few elements, large target, no competing animation.
- Depth (shadows, blur, layering) shows hierarchy. If everything is raised, nothing is.
- Responsive: design the narrow screen first when users write on phones; check 320px width without horizontal scroll.
- Safe areas and on-screen keyboard: input must stay visible when the keyboard opens.

## 8. Motion

For every animation write: **purpose** (inform, orient, confirm, comfort), **trigger** (user action or state), **duration**, **interruption** (what happens if the user acts mid-way), **reduced-motion alternative**.

| Kind | Typical duration | Notes |
|---|---|---|
| Feedback (press, toggle) | 80-200 ms | Immediate; never delay the action. |
| Transition (view, panel) | 200-450 ms | Interruptible; must not hide the destination content. |
| Ceremony (completion, review) | 0.6-2 s | User-initiated or one-shot; skippable. |
| Ambient (background drift) | looping | Decoration only; pausable; off in reduced motion; must not run on writing screens by default. |

- Anything that moves automatically for more than a few seconds needs a way to pause or stop it.
- Avoid flashing. Do not exceed three flashes in any one second.
- Reduced motion replaces movement with a crossfade or an instant change and keeps the information. Looping scenes show one static frame. Also provide an in-app control that works even when the OS setting is off.
- CSS media queries do not stop `requestAnimationFrame`, canvas or WebGL loops; check `matchMedia('(prefers-reduced-motion: reduce)')` in JS and listen for changes.
- Budget: keep animation off the main task path; pause loops when the tab is hidden.

## 9. Sound and haptics

- Off by default. Start only after a user gesture. Visible mute control that persists.
- Sound never carries information alone; provide a visual or text equivalent.
- Haptics are an enhancement: feature-detect (`navigator.vibrate` is not available in every browser; verify for your targets), never required, easy to disable.
- Sensitive contexts (late-night writing, public transit) make unexpected sound a harm; default quiet.

## 10. Microcopy voice

Write a half-page voice sheet: person (first/second), tense, sentence length, words to avoid, how errors read.
- Error pattern: what happened, what it means for their content, what they can do. No blame.
- Buttons name the action ("Save entry", "Remove from this device"), not the emotion.
- Same concept, same word, everywhere.
- No exclamation-driven cheer in quiet states.

## 11. Anti-template diagnostic

Prompts, not prohibitions. For each hit, answer the question; if you cannot, simplify. `scripts/audit_frontend.py` flags a few by count (EC-V01 to EC-V06); the rest need your eye.

| Pattern | Question | Why it is weak when unjustified | More intentional alternative |
|---|---|---|---|
| Generic gradient backgrounds | What does the gradient *mean*? | Signals "wellness template", adds banding and cost | One flat surface plus one semantic accent tied to stated mood |
| Floating particles, stars, orbs | What information or action do they carry? | Compete with text, drain battery, trigger motion sensitivity | A single element that responds to the user's action, or a still texture |
| Glass / heavy blur everywhere | Which layer is truly in front? | Lowers text contrast, slow on low-end devices | One translucent layer with a solid fallback |
| Glow on many elements | What is the one thing to look at? | Flattens hierarchy | Glow only on the primary focus or current state |
| Card for everything | Is each item a distinct object? | Boxes inside boxes hide structure | Lists, rules and spacing; cards for objects the user handles |
| Arbitrary entrance animations | What does each one orient? | Delay content, no meaning | Animate only changes of state or position the user needs to track |
| Decorative complexity over content | Can the task be done at a glance? | Hides the primary action | Reduce until the task is obvious, then add back |
| Mixed visual metaphors | Is it a night sky, a paper desk or a lab? | Dilutes the thesis | Pick one metaphor and prune what does not belong |
| Fake depth (parallax) on text screens | Does it help reading? | Motion sickness risk, reduces legibility | None on reading and writing views |

## 12. What not to claim

Do not claim a design is original, award-level or "objectively" better. Report what was changed, why, and what was checked.
