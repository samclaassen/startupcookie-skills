# Construction pass

Run this by hand on every sentence after the lint is clean. These rules came from months of reviewer corrections on client posts, blogs and captions. Each one names the pattern, the test, and a before/after pair. The examples use a fictional company, Fieldnote (a scheduling tool for clinics).

## A. Actors and verbs

**A1. A person does the verb.** Software, "the platform", "the system", a report, a test, a letter or a page never does the action.
- Before: "Fieldnote sends reminders so no-shows drop."
- After: "Front-desk staff turn on text reminders in Fieldnote, and patients confirm or cancel from the text."

**A2. No get-passives or agentless sentences.**
- Before: "Someone gets woken up at 3am."
- After: "The on-call engineer wakes up at 3am."

**A3. A capability is what a person *can* do, not a present-tense fact about them.**
- Before: "An owner runs payroll in two clicks."
- After: "An owner can run payroll from the billing tab."

**A4. No loose verbs for technical steps.** "Roll", "let through", "kick off", "calling the thing" get replaced with the literal step.
- Before: "We roll the fix and let traffic through."
- After: "We deploy the patch to production and re-enable the login endpoint."

## B. Meaning

**B1. Literal test.** Ask what the sentence literally says. If the answer needs a second sentence, rewrite the first.

**B2. Drawable test.** If a reader couldn't sketch what the sentence describes, it's too abstract. Replace vague nouns ("the thing", "whatever wins", "what gets in the way of their work") with the named object.

**B3. No figures of speech standing in for a plain fact.** "A seat at the table" → "a vote on the budget".

**B4. Don't overstate.** "Didn't have many followers" is not "had almost no followers". Keep the claim at the strength the evidence supports. For counts, say the count, not "likely" or "most probably".

**B5. A sentence about what a page *doesn't* say is not information.** Cut it and send the question to the client.

**B6. Every pronoun has a named antecedent.** "They", "it", "this", "that's what" with nothing before them → the noun.

**B7. Never refer to a subset of a set the reader hasn't seen.** "Two of its four parts" when the four parts were never listed → list them or drop the count.

**B8. No draft-coined shorthand.** If you invented a label while drafting ("the cadence gap"), it doesn't go in published text. Say the thing.

## C. Openers

**C1. The opener stands alone.** Write it for someone who has never heard of the subject. Every term it leans on gets defined in plain words first, or doesn't appear.

**C2. Concise, specific, arguable.** About one clause, roughly 12 words, a claim the author would defend. Flat fact statements give the reader nothing to agree or argue with.
- Before: "Security reports are published by many companies every year."
- After: "Most startups test their app's security once, then ship for a year as if it still counts."

**C3. No opener that needs the body.** "I message my engineers in the morning and get answers at 2am" reads as if the reader already knows the story. Give them the point first.

**C4. Don't open with a quote, and don't spend the first sentence introducing what follows.**

**C5. No long subordinate-clause openers.** "When we first started working with teams who were scaling..." → start at the main clause.

## D. Structure

**D1. No antithesis pair or aphorism run.** "It's not X, it's Y", "rarely X. They Y.", "No speeches. No discussion." State the thesis once, attached to a fact, in a sentence of normal length.

**D2. No distributive summary clause.** "...each with what it lacked" gestures at a pattern without naming anything. Name the thing or end the sentence.

**D3. No scope lists after a colon with nobody doing anything.** "Three areas: billing, scheduling, notes." → who does what in each.

**D4. Headings.** An H2 is the question a reader would type, or the plain answer. If a heading needs its paragraph to be understood, it fails. No "X: Y" headings. A heading never counts or inventories the deliverable ("7 findings, 3 fixes").

**D5. Closers.** The close is about the reader's situation, never the company's history. No persona-addressed questions ("So if you carry the pager, what would have woken you?"). If you ask a question, ask the opening question again, plainly, to the reader.

**D6. TLDRs are literal and add something.** "TLDR: the sandbox had internet access" only works if the post explained why that's a problem. Riddles and compressed images fail.

## E. Honesty

**E1. Nothing invented.** No made-up scenes, feelings, opinions or details put in a real person's mouth. No invented client details. A sourced scene is fine. A scene invented to sound relatable is not.

**E2. No manufactured relatability.** No runs of rhetorical questions, no "we've all been there".

**E3. Don't undercut the subject.** Re-read every sentence as a prospective customer: does it make the author or company *less* desirable to work with? ("...and they set up every single one themselves.") Cut it.

**E4. No point-free fact drops.** Apply the "and?" test. If a reader would say "and?", the post needs the consequence: what we did, what it means, where to find it.

## F. Platform fit

**F1. Match the real length of the author's posts.** Don't shorten to escape the lint. Short posts with no substance read as lazy.

**F2. Captions are not ads.** The customer's people are the actors, the product is named once, and no sentence lists product capabilities.

**F3. Share captions withhold the answer.** When sharing a longer piece, name the topic and the question, not the conclusion. The reader should want to click.

**F4. Recent events.** Use "last week" or "last weekend". Exact dates only go in when the date is the news. Don't put retrieval dates or timestamps in published body text.
