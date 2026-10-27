# Reflective journal - states (missing the zero-content state)

| From | Event | To | Guard | Sets data |
|---|---|---|---|---|
| first visit | open app | loading | | |
| loading | load ok | list | | entries |
| loading | load fails | error | | |
| error | retry | loading | | |
| list | new entry | writing | | |
| writing | save | list | | |
| list | close app | closed (terminal) | | |
| error | close app | closed (terminal) | | |
