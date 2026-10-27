# State mapping

A way to turn a product brief into a set of interface states that can be tested, and to find the holes before users do. Templates: `assets/state-transition-template.md`. Checker: `scripts/state_table_check.py`.

## Contents
1. Select states from requirements
2. State catalog
3. Per-state specification
4. Method
5. Detecting problems
6. Acceptance criteria format
7. Worked mini example

## 1. Select states from requirements

Do not implement every state. Include a state only when a requirement or data condition creates it:
- Auth exists -> signed out, expired session.
- Remote data exists -> loading, recoverable failure, unrecoverable failure, offline.
- Content is user-created -> empty, one item, many items, deletion.
- Import or export is a feature -> import, export, partial failure.
- Visits repeat -> first visit, returning visit.
- Optional expression or personalization exists -> offered, accepted, declined, disabled later.

Write the reason next to each state ("because entries sync to a server"). If you cannot, drop it.

## 2. State catalog

first visit; no content; one saved item; many saved items; loading; success; recoverable failure; unrecoverable failure; offline; expired session; deletion (confirm, undo window, done, failed); import; export; returning user; personalization offered / declined / on; reduced-motion on; quiet mode on.

Cardinality matters: 0, 1 and many often need three different layouts and three different tones.

## 3. Per-state specification

For every state you keep, write all eight:

1. **Entry conditions** - what must be true, and from which states/events.
2. **What the user sees** - content, tone mode (quiet/neutral/celebratory/reflective), motion.
3. **Actions available** - every control, including the escape.
4. **Data retained or changed** - what is saved, discarded, sent anywhere.
5. **Exit and reversal** - how to leave, and what undo exists (real, not implied).
6. **Accessibility and reduced motion** - focus placement, announcements, the reduced-motion variant.
7. **Error and recovery** - what can fail here and the user's way out.
8. **Acceptance criteria** - testable statements (section 6).

## 4. Method

1. List the user's journeys in plain sentences ("opens the app, writes, saves, later deletes").
2. Derive states from data conditions and async operations, not from screens.
3. Fill the transitions table: From | Event | To | Guard | Sets data. One row per event, with guards where one event has several outcomes ("count = 0" vs "count > 0").
4. Add the States table (State | Actions available | Needs data) for states with controls or data dependencies.
5. Run `python3 scripts/state_table_check.py table.md --entry "first visit,returning visit" --require loading,empty,error` (adjust `--require` to the states your requirements justify; the flag is opt-in).
6. Fix findings, then write acceptance criteria per state.
7. Implement the table literally: one state variable, explicit transitions, no implicit flags that can disagree.

Entry states that start from outside the app (deep link, returning user, push, session restored) must be passed to `--entry`, otherwise they are reported unreachable.

## 5. Detecting problems

Checker rules and what they mean:

| Rule | Meaning | Typical fix |
|---|---|---|
| ST-DEAD-END | State with no exit that is not terminal | Add retry, back, close |
| ST-TRAP | Closed loop that cannot return to the main flow | Add an exit from the loop |
| ST-UNREACHABLE | No path from any entry | Add the transition or declare an external entry |
| ST-NONDETERMINISTIC | Same state and event lead to different states, no guard | Add a guard or split the event |
| ST-UNDEFINED-TARGET | Target is blank, `?` or TBD | Decide it |
| ST-ASYNC-OUTCOMES | Loading/saving/etc. lacks distinct success and failure/cancel paths | Add the missing outcome |
| ST-DESTRUCTIVE | Delete/erase/reset without confirm before or undo/cancel after | Add confirm or undo that really works |
| ST-ORPHAN-ACTION | A listed action has no transition | Add the transition or remove the control |
| ST-MISSING-DATA | A state needs data nothing produces | Add the producing transition or an initial value |
| ST-REQUIRED-MISSING | An opt-in required state is absent | Add it, or justify removing it from `--require` |

Contradictory controls (a button that both saves and discards, "Back" that destroys data) are not detectable from the table alone. Read each state's action list asking: can two of these mean opposite things on the same tap target? Does any control depend on data this state does not have?

The checker reads the table, not the UI. After the table is clean, verify the running interface against it (`references/evaluation-method.md`).

## 6. Acceptance criteria format

Given a precondition, when an event, then observable results including data and announcement.

- Given no saved entries, when the app loads, then the empty state shows an invitation and no summary, and focus lands on the heading.
- Given a save fails, when the user taps Retry, then the draft text is still present and no duplicate is created.
- Given the user chose "Not now" on personalization, when they return later, then no personalization prompt appears unless they open Settings.
- Given reduced motion is on, when an entry is saved, then confirmation appears without movement and is announced to assistive tech.

## 7. Worked mini example

| From | Event | To | Guard | Sets data |
|---|---|---|---|---|
| first visit | open app | loading | | |
| loading | load ok | empty | count = 0 | |
| loading | load ok | list | count > 0 | entries |
| loading | load fails | error | | |
| error | retry | loading | | |
| empty | start writing | writing | | |

A full coherent table is in `tests/fixtures/s03b-complete-states/state-table.md` in the package repository (not part of the installable skill).
