# Accessibility review

A practical review for expressive, motion-heavy interfaces. It complements, and does not replace, an audit against WCAG 2.2 by a qualified reviewer. Success-criterion numbers below are cited from the author's knowledge of WCAG 2.2 and should be checked against the W3C text before being quoted in a compliance statement.

## Contents
1. What the scripts can and cannot catch
2. Keyboard and focus
3. Contrast and non-colour signals
4. Motion, flashing and auto-moving content
5. Sound
6. Labels, names and announcements
7. Touch and small screens
8. Expressive effects checklist
9. Manual test with no tools
10. Reporting

## 1. What the scripts can and cannot catch

`scripts/audit_frontend.py` can flag: no reduced-motion handling anywhere, JS loops ignoring the preference, removed focus outlines, zoom-blocking viewport, images without alt, controls without a name candidate, autoplay, tiny fonts, full-screen layers without `pointer-events:none`, hidden cursor. It cannot judge: whether a focus style is visible enough, tab order, reading order, whether alt text is meaningful, colour contrast of rendered text, screen-reader output, or anything set at runtime. Treat a clean scan as silence, not as a pass.

## 2. Keyboard and focus

- Every control reachable and operable by keyboard (WCAG 2.1.1); no trap (2.1.2). Escape closes modals and returns focus to the trigger.
- Focus indicator visible on every focusable element (2.4.7) and not hidden under sticky bars (2.4.11). Prefer `:focus-visible` with a 3:1 contrast outline; never `outline:none` without a replacement.
- Order follows reading order. When a view changes, move focus deliberately (usually to the new heading) and say so in the state's acceptance criteria.
- Custom controls (orbs, sliders, ritual surfaces) need a keyboard path that achieves the same outcome, not a mouse-only gesture.

## 3. Contrast and non-colour signals

- Text 4.5:1 (large text 3:1) (1.4.3); UI boundaries, icons, focus rings 3:1 (1.4.11). Check with `scripts/inspect_tokens.py --pairs`, then check on the rendered page, over images and gradients.
- Never colour alone (1.4.1): mood and state also get text, shape or icon.
- Dark atmospheric themes: muted text, placeholder text and disabled states are the usual failures.
- Support 200% text zoom and 320 CSS px width without loss of content (1.4.4, 1.4.10).

## 4. Motion, flashing and auto-moving content

- Respect `prefers-reduced-motion` in CSS and in JS loops; add an in-app control that overrides the OS default in either direction.
- Auto-starting movement lasting over five seconds needs pause/stop/hide (2.2.2).
- No more than three flashes in one second (2.3.1).
- Non-essential interaction-triggered animation should be disableable (2.3.3, AAA).
- Replace, do not merely remove: keep the information (state, confirmation) in text or a static change.

## 5. Sound

- No autoplay of audio over three seconds without a control (1.4.2); default silent.
- Provide a visual or text equivalent for any sound that carries meaning (1.2.1 for prerecorded audio-only content; same principle for feedback sounds).
- Mute control reachable by keyboard and visible without searching.

## 6. Labels, names and announcements

- Every form control has an accessible name from a label, `aria-label` or `aria-labelledby` (3.3.2, 4.1.2); placeholders are not labels.
- Toasts and saves are announced: a `role="status"` live region for confirmations, `role="alert"` for errors (4.1.3).
- Canvas and WebGL scenes: decorative ones are `aria-hidden="true"`; informative ones have a text alternative adjacent.
- Headings describe structure; one `h1` per view.
- Language set on the document.

## 7. Touch and small screens

- Targets at least 24x24 CSS px (2.5.8, AA) and ideally 44x44 for primary controls on touch.
- Keep spacing so adjacent targets are not mis-tapped, especially destructive ones next to safe ones.
- Do not require precise or timed gestures (hold, drag) without an alternative.
- Respect safe areas on devices with notches; keep inputs visible with the keyboard open.

## 8. Expressive effects checklist

- [ ] The effect has a purpose that is written down.
- [ ] A static or instant alternative exists and is used under reduced motion.
- [ ] The effect can be paused, skipped or disabled without leaving the screen.
- [ ] It does not cover, block clicks on, or lower the contrast of the primary task.
- [ ] It stops when the tab is hidden and does not run on writing screens by default.
- [ ] It adds no unannounced sound.
- [ ] It does not flash.

## 9. Manual test with no tools

1. Unplug the mouse (or do not touch the screen): tab through every view; confirm focus is always visible and every action is possible.
2. Turn on the OS reduced-motion setting; reload; confirm no movement and nothing missing.
3. Zoom to 200% and narrow to 320px: no horizontal scroll, no overlap.
4. Turn off colour (greyscale filter): mood and state are still distinguishable.
5. Turn on a screen reader and do the main task once; listen for unlabeled controls and silent saves.
6. Mute the device: nothing important is lost.

If you cannot run these, hand them to the user as a checklist and label them Not verified.

## 10. Reporting

For each item state: method (tool run, manual, not run), result, evidence. Do not write "accessible" or "WCAG compliant"; write what was checked and what was not.
