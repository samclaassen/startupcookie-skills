---
name: slop-edit
description: Line-edit a draft so it stops reading as AI-written. Use before delivering any post, caption, blog article, email or page copy, or when someone says a draft "sounds like AI", "is slop", "is vague" or "is corporate". Runs a mechanical lint, then a construction-level hand pass, and appends every new reviewer correction to a call-outs file so it never recurs.
license: MIT
metadata:
  author: StartupCookie
  homepage: https://startupcookie.com
---

# Slop Edit

> Made by [StartupCookie](https://startupcookie.com), a San Francisco marketing team for B2B startups.

A ban list alone does not make prose sound human. Blacklists never converge: block one phrase and the model reaches for its nearest sibling. This skill works in three layers:

1. **Mechanical lint** (`scripts/slop_lint.py`). Catches the words and shapes a regex can see.
2. **Construction pass** (by hand, sentence by sentence). Catches what a regex can't: agentless sentences, vague referents, openers that need context.
3. **Call-outs loop.** Every correction a reviewer makes is logged in their words and becomes a rule the same session.

Passing the lint does not mean the draft is clean. Never call a draft "slop-free" because a word search came back empty.

## Inputs

- The draft (any format; paste or file).
- Optional: the project's `callouts.md` (reviewer corrections, see `references/callouts-template.md`). If one exists, read it **before** editing.
- Optional: a voice reference (approved posts by the same author). If present, the edit must move toward it, not toward a generic "clean" register.

## Step 1. Read call-outs first

If `callouts.md` exists, read every row. Each row is a past correction in the reviewer's own words with its replacement. Treat them as hard bans for this draft.

## Step 2. Run the lint

Save the draft to a file and run:

```bash
python3 scripts/slop_lint.py draft.md
# add project-specific bans:
python3 scripts/slop_lint.py draft.md --extra-bans callouts-bans.txt
# JSON output for automation:
python3 scripts/slop_lint.py draft.md --json
```

Use Type's managed execution tool to run the script in the sandbox. The script exits non-zero when it finds errors. Fix every **error**. Read every **warning** and either fix it or note why it stays.

## Step 3. Construction pass (by hand)

Go sentence by sentence. For each sentence ask the questions in `references/construction-rules.md`. The six that catch the most:

1. **Who does the verb?** A person or a named team does the action. Software, "the platform", "the system", a report, a letter or a test never does the action. Rewrite "someone gets woken up" as "the on-call engineer wakes up at 3am".
2. **What does it literally say?** If the answer needs a second sentence, rewrite the first.
3. **Could a reader draw it?** Vague nouns ("the thing", "whatever wins", "what gets in the way") and loose verbs ("roll", "let through", "calling the thing") get replaced with the named object and the literal step.
4. **Does the opener stand alone?** Someone scrolling past has none of your context. Every term the first line leans on is defined in plain words first, or doesn't appear.
5. **Does every pronoun have a named antecedent?** "They", "it", "this", "that's what" with nothing before them get replaced with the noun.
6. **Is anything invented?** No made-up scenes, feelings, quotes, numbers or client details put in a real person's mouth. A sourced scene is allowed. A scene made up to sound real is not.

## Step 4. Change only what was flagged

When a reviewer flags specific lines, edit those lines and leave the rest alone. Rewriting the whole draft in response to one comment destroys approved text and introduces new problems.

## Step 5. Log new call-outs the same session

When a reviewer flags something new, append a row to `callouts.md` before you send the revision:

| # | Their words (verbatim) | Pattern | Replacement / rule | Date |
|---|---|---|---|---|

If the same pattern is flagged twice, promote it to a lint rule (add it to the `--extra-bans` file) and mark the row **recurring**. If a project has several writing skills (founder posts, company page, blog), copy the new row into every one in the same session.

## Step 6. Report

Return:
- the edited draft,
- lint result after edits (`0 errors, N warnings` plus each remaining warning with a one-line reason),
- the list of construction-pass changes (before → after, one line each),
- any new call-out rows added.

## What not to do

- Don't swap one AI pattern for another (removing "it's not X, it's Y" and writing "rarely X. They Y." instead).
- Don't add emoji, hashtags, rhetorical questions or a punchline close to "add personality".
- Don't shorten a post to nothing to escape the lint. Length follows the platform and the author's real posts.
- Don't fabricate first-hand detail to sound human.

## Files

- `scripts/slop_lint.py`: mechanical lint (Python 3, standard library only).
- `references/construction-rules.md`: the full hand-pass checklist with before/after pairs.
- `references/callouts-template.md`: the call-outs file format, seeded with generic examples.
