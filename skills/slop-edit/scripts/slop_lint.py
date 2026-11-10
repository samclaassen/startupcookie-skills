#!/usr/bin/env python3
"""slop_lint.py - mechanical lint for AI-sounding prose.

Usage:
    python3 slop_lint.py draft.md [--extra-bans bans.txt] [--json] [--allow-emoji]
                                  [--allow-questions] [--blog]

Exit code 1 when any ERROR is found, 0 otherwise.

--extra-bans: a text file, one rule per line:
    error | regex | message
    warn  | regex | message
Lines starting with # are ignored. Regexes are case-insensitive.

The lint catches surface patterns only. A clean result does NOT mean the draft
reads as human: run the construction pass in references/construction-rules.md.
"""
import argparse
import json
import re
import sys

# (level, pattern, message)
RULES = [
    # Punctuation
    ("error", r"—", "Em dash. Use a comma, a full stop, or rewrite the sentence."),
    ("error", r"–(?!\d)", "En dash used as punctuation. Use a comma or full stop."),
    ("error", r"\s--\s", "Double hyphen used as a dash."),

    # Antithesis / mirror constructions
    ("error", r"\b(it'?s|this is|that'?s|is|was|are|were)\s+not\s+(just\s+|only\s+|about\s+)?[^.?!\n]{1,60}?[,;.]\s*(it'?s|this is|that'?s|but|they'?re|we'?re)\b",
     "'Not X, it's Y' mirror construction."),
    ("error", r"\b(isn'?t|wasn'?t|aren'?t|weren'?t)\s+[^.?!\n]{1,60}?[,;.]\s*(it'?s|it was|they'?re|but)\b",
     "'Isn't X, it's Y' mirror construction."),
    ("error", r"\bnot because\b[^.?!\n]{1,80}\bbut because\b", "'Not because X but because Y' construction."),
    ("warn", r"\b(rarely|never|seldom)\s+\w+[^.?!\n]{0,40}\.\s+(They|It|We)\s+\w+", "Antithesis pair ('rarely X. They Y.')."),
    ("error", r"\bwas never (about )?[^.?!\n]{1,40},\s*it was\b", "'Was never X, it was Y' construction."),

    # Filler / faux-thoughtful lead-ins
    ("error", r"\b(keep|kept) (going|coming) back to\b", "Faux-thoughtful lead-in ('keep coming back to')."),
    ("error", r"\bthe part I keep\b", "Faux-thoughtful lead-in."),
    ("error", r"\b(has|have) stayed with me\b|\bstuck with me\b|\bwhat stays with me\b", "Faux-reflective filler."),
    ("error", r"\bhere'?s (the thing|what I think|my take|what'?s actually)\b", "Filler set-up line."),
    ("error", r"\bfrom there, here'?s\b", "Filler list intro."),
    ("error", r"\b(in this (article|post|guide)|we'?ll (cover|explore|walk through)|read on|let'?s dive in|dive into|without further ado)\b",
     "Signposting. Start with the content."),
    ("error", r"\bline-by-line\b", "Stock flourish."),

    # Vague 'shows up / comes out' family
    ("error", r"\bshow(s|ed|ing)? up\b", "'Shows up' (vague). Say what happens, to whom."),
    ("error", r"\bcom(es|ing)? out of\b|\bcame out of\b", "'Comes out of' (vague). Name the source."),
    ("error", r"\b(came|come|comes) (up|back)\b(?=[^.?!\n]{0,40}\b(theme|finding|answer|result|feedback|interview|survey)s?\b)",
     "'Came up / came back' for findings. Name who said or found what."),
    ("error", r"\b(gets?|got|getting) quieter\b|\broom (goes|went) quiet\b|\bfalls? silent\b", "Manufactured-drama cliché."),
    ("warn", r"\b(got|stood|get|stand)s? in the way\b", "'Got in the way' (vague). Name the obstacle."),

    # Words that almost always signal generic AI prose
    ("error", r"\b(matters?|mattered)\b", "'Matters' (empty emphasis)."),
    ("error", r"\b(delve|delves|delving|tapestry|testament to|landscape of|ever-evolving|game[- ]changer|unlock(s|ing)? the|elevate|seamless(ly)?|robust|leverag(e|es|ing)|synerg\w*|cutting[- ]edge|best[- ]in[- ]class|world[- ]class|revolutioni[sz]\w*|supercharg\w*|empower\w*|holistic|paradigm)\b",
     "Marketing or AI-stock word."),
    ("warn", r"\b(incredibly|truly|deeply|really|very|simply|actually|basically|literally)\b", "Intensifier adverb. Cut or replace with a fact."),
    ("warn", r"\b(crucial|vital|essential|powerful|innovative|transformative|exciting|amazing|unparalleled)\b", "Evaluative adjective. Replace with the fact that earns it."),
    ("warn", r"\b(in the room|at the table|on the calendar|in the budget)\b", "Figure of speech standing in for a plain fact."),
    ("warn", r"\b\w+-shaped\b", "'-shaped' coinage."),

    # Negation-led and agentless constructions
    ("warn", r"(^|[.!?]\s+)Nobody\b", "Sentence opens with 'Nobody'. Name who did or didn't."),
    ("warn", r"\b(paged|checked|escalated|owns?|noticed) nobody\b|\bnobody (paged|checked|escalated|owns?|noticed)\b", "'Nobody X' construction."),
    ("warn", r"\b(gets?|got|getting) (woken|hit|flagged|caught|missed|ignored|lost|broken|fixed|shipped|done)\b", "Get-passive. Name the actor."),
    ("warn", r"\b(each|every) one (was|is) (missing|lacking)\b|\beach with what it lacked\b|\bplus \w+ for each\b",
     "Distributive summary clause. Name the thing or end the sentence."),

    # Closers and questions
    ("warn", r"(what do you think|thoughts\?|agree\?|let me know in the comments|drop a comment)", "Engagement-bait closer."),
    ("warn", r"\bif you (carry|run|own|lead|manage)\b[^.?!\n]*\?", "Persona-addressed question. Ask the reader plainly or cut it."),
    ("warn", r"\bTL;?DR;?\s*[:\-]?\s*the\b", "TLDR that may be a riddle. Make it literal."),

    # Staccato / triads
    ("warn", r"(^|\n|[.!?]\s)(\w+\.\s){2,}\w+\.", "Staccato fragment run ('Power. Space. Water.')."),
    ("warn", r"\bNo \w+\. No \w+\.", "'No X. No Y.' triad."),

    # Openers
    ("warn", r"^(That'?s what|This is what|Here'?s why|It'?s (time|no secret))", "Opener with no antecedent or stock opener."),

    # Headings
    ("warn", r"^#{1,6}\s+[^\n]*:\s", "Heading with a colon ('X: Y'). Use the plain question or answer."),
]

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]")
HASHTAG_RE = re.compile(r"(?<!\w)#[A-Za-z]\w+")
BLOG_RULES = [
    ("warn", r"\b(19|20)\d{2}\)", "Author-year citation in body. Hyperlink the source instead."),
    ("error", r"\b(retrieved|accessed|read) (on )?(\w+ \d{1,2},? )?(19|20)\d{2}\b", "Retrieval date in published text."),
]


def load_extra(path):
    rules = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|", 2)]
            if len(parts) != 3 or parts[0] not in ("error", "warn"):
                print(f"skipping malformed extra-ban line: {line}", file=sys.stderr)
                continue
            rules.append(tuple(parts))
    return rules


def line_col(text, idx):
    line = text.count("\n", 0, idx) + 1
    col = idx - (text.rfind("\n", 0, idx) + 1) + 1
    return line, col


def lint(text, rules, allow_emoji=False, allow_questions=False):
    findings = []
    for level, pattern, msg in rules:
        flags = re.IGNORECASE | re.MULTILINE
        for m in re.finditer(pattern, text, flags):
            ln, col = line_col(text, m.start())
            findings.append({"level": level, "line": ln, "col": col,
                             "match": m.group(0).strip()[:80], "message": msg})
    if not allow_emoji:
        for m in EMOJI_RE.finditer(text):
            ln, col = line_col(text, m.start())
            findings.append({"level": "warn", "line": ln, "col": col, "match": m.group(0),
                             "message": "Emoji. Remove unless the account's real posts use them."})
    tags = HASHTAG_RE.findall(text)
    if len(tags) > 3:
        findings.append({"level": "warn", "line": 0, "col": 0, "match": " ".join(tags[:6]),
                         "message": f"{len(tags)} hashtags. Use 0-3 relevant tags."})
    if not allow_questions:
        for para_i, para in enumerate(re.split(r"\n\s*\n", text)):
            if para.count("?") >= 3:
                findings.append({"level": "warn", "line": 0, "col": 0, "match": para[:60],
                                 "message": "Three or more questions in one paragraph (manufactured relatability)."})
    # Sentence-length uniformity (burstiness)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text)) if len(s.split()) > 2]
    if len(sentences) >= 6:
        lengths = [len(s.split()) for s in sentences]
        mean = sum(lengths) / len(lengths)
        var = sum((x - mean) ** 2 for x in lengths) / len(lengths)
        cv = (var ** 0.5) / mean if mean else 0
        if cv < 0.35:
            findings.append({"level": "warn", "line": 0, "col": 0, "match": f"cv={cv:.2f}",
                             "message": "Sentence lengths are very uniform. Human prose varies more; mix short and long."})
    findings.sort(key=lambda f: (f["line"], f["col"]))
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--extra-bans")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--allow-emoji", action="store_true")
    ap.add_argument("--allow-questions", action="store_true")
    ap.add_argument("--blog", action="store_true", help="add long-form/blog rules")
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as fh:
        text = fh.read()
    rules = list(RULES)
    if args.blog:
        rules += BLOG_RULES
    if args.extra_bans:
        rules += load_extra(args.extra_bans)

    findings = lint(text, rules, args.allow_emoji, args.allow_questions)
    errors = sum(1 for f in findings if f["level"] == "error")
    warns = len(findings) - errors

    if args.json:
        print(json.dumps({"errors": errors, "warnings": warns, "findings": findings}, indent=2))
    else:
        for f in findings:
            loc = f"{f['line']}:{f['col']}" if f["line"] else "doc"
            print(f"{f['level'].upper():5} {loc:>7}  {f['message']}  [{f['match']}]")
        print(f"\n{errors} error(s), {warns} warning(s)")
        if errors == 0:
            print("Lint clean. Now run the construction pass: a clean lint is not a clean draft.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
