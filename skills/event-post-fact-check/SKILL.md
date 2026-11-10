---
name: event-post-fact-check
description: Draft and fact-check social posts about a conference, summit, talk or trade show so every name, affiliation, session, sponsorship, photo and hashtag is verified before publishing. Use for post-event LinkedIn posts by a speaker or attendee, company-page event recaps, and speaker shout-outs. Separates what the official program proves from what someone remembers.
license: MIT
metadata:
  author: StartupCookie
  homepage: https://startupcookie.com
---

# Event Post Fact-Check

> Made by [StartupCookie](https://startupcookie.com), a San Francisco marketing team for B2B startups.

Event posts go wrong in predictable ways: a sponsor that wasn't, a speaker's old affiliation, a photo paired with the wrong talk, a summary of a talk the author didn't attend, an "official" hashtag nobody uses. This skill drafts the post **and** produces a claims table showing where every fact came from.

## Inputs
- Who is posting (person or company page) and their role at the event (speaker, attendee, exhibitor).
- What they remember (voice note, chat message, transcript). Treat this as **recollection**, not fact.
- Photos, with the order they were sent.
- Event name and approximate date.

## Step 1. Get the official record
Find the event's own program: agenda PDF, schedule page, session pages, speaker bios. Find the full speaker list yourself; don't ask the user for it, and don't report "search was down" as a reason to skip.

From the program, record: event name, city, venue, dates, the poster's own session (title, slot, room), and every other session or person the post will mention.

## Step 2. Build the claims table
Every factual element in the draft gets a row before you write prose:

| Claim | Status | Source |
|---|---|---|
| Speaker X is at University Y | **Program** | agenda p.4 |
| X's talk was about Z | **Program description** (pre-event) | session page |
| X approached the poster after his talk | **Recollection** | poster's message |
| Company was a sponsor | **Unverified → removed** | flyer logo only |

Status values:
- **Program**: stated in official event materials.
- **Program description**: what the talk was *meant* to cover, written before the event. Not proof of what was said in the room.
- **Recollection**: what the poster remembers. Usable in first person, never stated as general fact.
- **Verified elsewhere**: confirmed on the person's or company's own site.
- **Unverified**: not usable until confirmed. Remove it or ask.

## Step 3. Verification rules
1. **Affiliations:** confirm against the program and the person's current profile. Use the legal or display name they use themselves (site footer, LinkedIn).
2. **Talk summaries:** hedge to the published description. "Her approach helps clients" becomes "Her talk set out an approach meant to help clients" if the description only says she argues for it. Cut synthesis the description doesn't support.
3. **Pairing talks:** link two talks only where both descriptions support the connection, and don't claim either speaker referenced the other.
4. **Agenda ≠ room.** Note in the delivery: "Talk summaries come from the published descriptions, not notes from the room." Ask the poster to confirm they attended each talk mentioned, and which moments actually happened.
5. **Sponsorship, awards and partnerships:** don't state them without direct evidence (sponsor page, organizer post you can open). A search-result preview or a logo on a flyer isn't enough. Remove the claim and keep what you can support ("we had a booth").
6. **Photos:** pair each photo with a talk only from the poster's explicit clarification or visible evidence (signage, a title slide). Use the order the photos were sent as a hint, not proof. A distant shot with no signage stays unpaired. If a post has no usable photo, keep it text-only and say what photo would work (title slide, photo with the speaker, program screenshot).
7. **Tagging:** verify the exact profile before tagging. Tag the person first, then the institution.
8. **Hashtags:** look for an official hashtag on the event's own channels. If there isn't one, use one the organizer actually uses, or a topic tag you've checked is in real use. Never call a hashtag "official" or "established" without evidence; if unresolved, say so and leave the choice to the poster.
9. **Citations:** if the post cites research, check every DOI (for example against Crossref) and flag anything written from memory. Re-check any statistic against the newest edition of its report.
10. **Off-limits:** respect anything the poster has asked to hold back (topics, unannounced customers, numbers).

## Step 4. Write the post
- Write a **complete, standalone draft** the team can correct. Don't fill it with `[placeholder]` gaps.
- Recent events: "last week" or "last weekend". Exact dates only when the date is the news.
- People are the actors in every sentence. The company page post describes what the company does for its customers; it doesn't pivot to the founder's bio.
- Once the announcement post is out, follow-up posts drop the conference framing and stand on the idea.
- Run the slop-edit skill (if installed) before delivery.

## Step 5. Deliver
```
DRAFT — <account> — <event>
<post text>

Claims table: (as above)
Photos: <file> → <post/talk> (basis: <clarification / signage>) · <file> unpaired (why)
Hashtag: <tag> (basis) | unresolved: <options>
Removed: <claim> — <why>
Please confirm: <list of recollection-based lines and open items, by person>
```
