# State map - <feature or product>

Entry states (including external entries such as returning user or deep link):
Terminal states:
Why each non-obvious state exists (one line each):

## Transitions
Keep these exact column names; `scripts/state_table_check.py` reads them. Mark terminal states by writing `(terminal)` after the name. Use a Guard when one event has several outcomes.

| From | Event | To | Guard | Sets data |
|---|---|---|---|---|
| first visit | open app | loading | | |

## States (optional but recommended)
| State | Actions available | Needs data |
|---|---|---|
| | | |

## Per-state specification
Repeat for each state you keep.

### <state name>
1. Entry conditions:
2. What the user sees (tone mode, motion):
3. Actions available:
4. Data retained or changed:
5. Exit / reversal:
6. Accessibility and reduced motion:
7. Error and recovery:
8. Acceptance criteria (Given / when / then):

## Check
Command run:  `python3 scripts/state_table_check.py <this file> --entry "..." --require "..."`
Result (paste real output):
