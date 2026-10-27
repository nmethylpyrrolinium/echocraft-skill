# Journal - coherent table (should produce no structural findings)

| From | Event | To | Guard | Sets data |
|---|---|---|---|---|
| first visit | open app | loading | | |
| returning visit | open app | loading | | |
| loading | load ok | list | count > 0 | entries |
| loading | load ok | empty | count = 0 | |
| loading | load fails | error | | |
| error | retry | loading | | |
| error | work offline | offline | | |
| error | close app | closed (terminal) | | |
| offline | reconnect | loading | | |
| offline | close app | closed (terminal) | | |
| empty | start writing | writing | | |
| empty | close app | closed (terminal) | | |
| list | new entry | writing | | |
| list | delete entry | confirm delete | | |
| list | close app | closed (terminal) | | |
| confirm delete | confirm | undo window | | |
| confirm delete | cancel | list | | |
| undo window | undo | list | | |
| undo window | window expires | list | | |
| writing | save | saving | | |
| writing | leave without saving | list | | |
| saving | save ok | list | | |
| saving | save fails | writing | | |

| State | Actions available | Needs data |
|---|---|---|
| list | new entry, delete entry, close app | entries |
| writing | save, leave without saving | |
| empty | start writing, close app | |
