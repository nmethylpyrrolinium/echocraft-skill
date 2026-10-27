# Same journal with the zero-content state added

| From | Event | To | Guard | Sets data |
|---|---|---|---|---|
| first visit | open app | loading | | |
| loading | load ok | list | count > 0 | entries |
| loading | load ok | empty | count = 0 | |
| loading | load fails | error | | |
| error | retry | loading | | |
| empty | start writing | writing | | |
| list | new entry | writing | | |
| writing | save | list | | |
| list | close app | closed (terminal) | | |
| empty | close app | closed (terminal) | | |
| error | close app | closed (terminal) | | |
