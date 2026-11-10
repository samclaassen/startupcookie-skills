---
name: social-batch-review-calendar
description: Turn a settled batch of social posts into an interactive Type app where the team and client can review, copy and publish. It has a weekly calendar showing each post's first paragraph and full image, a list view, copyable captions, downloadable full-resolution visuals, and the approver and status on every card. Use when a batch of 3+ posts across one or more accounts is ready for review or scheduling, instead of a PDF, a doc, image previews or a chat recap.
license: MIT
metadata:
  author: StartupCookie
  homepage: https://startupcookie.com
---

# Social Batch Review Calendar

> Made by [StartupCookie](https://startupcookie.com), a San Francisco marketing team for B2B startups.

Reviewers need to **read** each caption, **see** its visual, **copy** the text and **download** the image, and know **who approves** it. PDFs, Word docs, chat recaps and image-only previews fail at least one of those. This skill builds a small static Type app that does all four, from a template that has been used with real clients.

## The three rules
1. **The caption is real, selectable, copyable text.** Never an image of text, never only inside a table cell.
2. **The visual sits directly under its caption**, uncropped, with a Download button that saves the full-resolution file.
3. **Every card names the account, the approver and the state.**

## When to use
- The batch's text is settled enough for review (not mid-brainstorm).
- Three or more posts, or more than one account.
- If the user only needs one post, deliver the caption and visual inline in chat.

## Inputs
For each post: number, week, day (time only if agreed), account, handle, story/topic, approver, state, caption (paragraphs separated by blank lines), visuals (primary + labelled alternatives), notes (open decisions and day-of checks). Plus a title and an **approval-boundary** line ("Nothing here is approved for publishing until its card says Approved").

## Build steps
1. **Collect the images** into one folder, named so their stems are valid identifiers (`post1.png`, `post1_alt.png`). Keep the publishable resolution (for example 1080×1350 portrait, 1200×1200 square, 1600×900 landscape).
2. **Create a Type app** in the space (React + Vite starter). Don't rewrite the starter's `src/styles.css` variables or `src/main.tsx`.
3. **Encode the visuals.** Type apps store source text only, so images ship as data URLs. Run with Type's managed execution tool:
   ```bash
   python3 scripts/encode_visuals.py ./images ./<app>/src
   ```
   This writes `visuals-a.ts`, `visuals-b.ts`, … (each under the source-file size cap, default 480 KB) and `visuals.ts`, which re-exports them. Each export is `{ src, file, w, h }`. Full resolution is kept by default so Download gives the publishable file. If one image is too big for a single file, the script tells you to re-run with `--max-edge 1600`.
4. **Copy `assets/App.tsx` to `src/App.tsx`.** Edit only the "Batch content" block: `TITLE`, `BOUNDARY`, `ACCOUNTS`, `ACCOUNT_TONE`, `WEEKS`, `POSTS`. Each post's `visuals[].key` is the export name from step 3.
5. **Append `assets/calendar-styles.css`** to `src/styles.css`.
6. **Build and check.** Type-check passes; then open the preview and verify:
   - every week shows Mon–Fri columns with posts on their days,
   - each tile shows the account chip, state, **full uncropped image** and the **complete first paragraph**, plus "+ N more paragraphs · open",
   - opening a post shows every paragraph, Copy caption, character count, all visuals with Download buttons, and notes,
   - account filters and the Calendar/List switch work,
   - Copy puts the exact caption on the clipboard,
   - on a narrow window the week scrolls sideways instead of squashing cards.
7. **Publish the app and post the link**, with one line per post (account · day · story). Keep a durable copy of all captions outside the app (a doc in the space or the thread itself). The app must never be the only copy.

## Updating
When a caption changes, edit `POSTS` and republish. When an image changes, replace the file in the images folder and re-run `encode_visuals.py`; it removes stale `visuals-*.ts` files. Update the caption doc at the same time.

## What not to do
- No captions in a table: tables truncate and can't be copied cleanly.
- No dashboard metrics, charts or progress bars. This is a review surface.
- Don't crop images on the calendar tiles; reviewers need to see the whole visual.
- Don't invent posting times. If times aren't agreed, show days only.
- Don't deliver the batch as a doc and expect the reviewer to find the visuals. Every post must have its caption and visual together.

## Files
- `assets/App.tsx`: the working component (calendar, list, detail, copy, download, filters) with two placeholder posts.
- `assets/calendar-styles.css`: append to the app's stylesheet. Uses the starter's semantic variables, so light and dark mode both work.
- `scripts/encode_visuals.py`: encodes and splits images into `visuals-*.ts`. Needs Pillow.
