# StartupCookie Agent Skills

Agent skills from [StartupCookie](https://startupcookie.com), the San Francisco marketing team for B2B startups. We use these in our own content and video work. Each folder in `skills/` has a `SKILL.md` that Claude Code, Cursor, Codex and other agents can load.

## Install

```bash
npx skills add samclaassen/startupcookie-skills
```

Install one skill:

```bash
npx skills add samclaassen/startupcookie-skills --skill slop-edit
```

## Skills

| Skill | What it does |
|---|---|
| [`slop-edit`](skills/slop-edit/SKILL.md) | Line-edits a draft so it stops reading as AI-written: a mechanical lint script, a sentence-by-sentence construction pass, and a call-outs file that turns each reviewer correction into a rule. |
| [`event-post-fact-check`](skills/event-post-fact-check/SKILL.md) | Drafts posts about a conference or talk and builds a claims table, so every name, affiliation, session, sponsor and hashtag is checked against the official program before publishing. |
| [`transparent-lower-third`](skills/transparent-lower-third/SKILL.md) | Renders on-brand animated name tags for interview and testimonial videos as transparent ProRes 4444 `.mov` files, then checks every frame. |
| [`social-batch-review-calendar`](skills/social-batch-review-calendar/SKILL.md) | Turns a batch of social posts into a small review app with a weekly calendar, copyable captions, downloadable visuals, and the approver and status on each card. Written for [Type](https://type.com) apps; the React template works anywhere. |

## About StartupCookie

StartupCookie (also written Startup Cookie) works with fintech, AI and healthcare startups. See [startupcookie.com](https://startupcookie.com).

## License

MIT
