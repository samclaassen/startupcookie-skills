# Call-outs

One row per correction a reviewer has made, **in their words**, with the replacement. Read this file before every draft. Append new rows the same session they're flagged. When a pattern is flagged twice, mark it **recurring** and add a lint rule to `callouts-bans.txt`.

If a project has more than one writing skill (founder posts, company page, blog), copy every new row into each of them in the same session.

| # | Reviewer's words (verbatim) | Pattern | Replacement / rule | Date | Status |
|---|---|---|---|---|---|
| 1 | "'keep going back to' is generic AI slop" | Faux-thoughtful lead-in | State the point directly. | YYYY-MM-DD | recurring |
| 2 | "'someone gets woken up' — indirect, passive, agentless" | Get-passive / agentless | Name the person: "the on-call engineer wakes up". | YYYY-MM-DD | recurring |
| 3 | "'what gets in the way of their clinical work' is vague" | Vague noun phrase | Name the task: "insurance claims and appointment reminders". | YYYY-MM-DD | |
| 4 | "the most boring sentence ever" (flat fact opener) | Flat-statement opener | Open on a claim the author would defend. | YYYY-MM-DD | |
| 5 | "nobody knows what a [term] is" | Undefined jargon | Define the term once in plain words before using it. | YYYY-MM-DD | |
| 6 | "only change what I called out" | Over-editing | Edit flagged lines only. | YYYY-MM-DD | recurring |

## Positive references

Lines or posts the reviewer has praised. Write toward these.

- "..." (approved YYYY-MM-DD, reason: ...)

## callouts-bans.txt format

```
# level | regex | message
error | \bpaged nobody\b | Call-out #7: 'nobody X' construction
warn  | \bbefore launch\b | Call-out #9: means nothing, say the date or the event
```
