# Archive app - flawed table used as a test fixture

| From | Event | To | Guard | Sets data |
|---|---|---|---|---|
| start | open app | loading entries | | |
| loading entries | load ok | entries list | count > 0 | entries |
| loading entries | load ok | empty | count = 0 | |
| loading entries | load fails | error | | |
| entries list | tap delete | deleting entry | | |
| deleting entry | done | entries list | | |
| entries list | open export | export dialog | | |
| export dialog | choose format | export options | | |
| export options | back | export dialog | | |
| entries list | tap entry | reading | | |
| entries list | tap entry | entry editor | | |
| entries list | open stats | stats panel | | |
| entries list | undo last | ? | | |
| entries list | open settings | settings | | |
| settings | close | entries list | | |
| archive screen | open | entries list | | |
| empty | add first entry | entry editor | | |
| entry editor | save | entries list | | |
| reading | back | entries list | | |

| State | Actions available | Needs data |
|---|---|---|
| entries list | tap delete, open export, tap entry, pin entry, open stats, open settings | entries |
| stats panel | back | insights |
