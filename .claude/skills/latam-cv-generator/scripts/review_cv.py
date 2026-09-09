#!/usr/bin/env python3
"""
Review a generated CV using OpenAI GPT-4o as an expert LATAM recruiter.

This script sends the CV to GPT-4o with a recruiter persona to validate
that it appears human, realistic, and professionally appropriate.

Usage:
    python review_cv.py <cv_markdown_file>

Or import and use programmatically:
    from review_cv import review_cv_with_expert
    reviewed_cv = review_cv_with_expert(cv_markdown)
"""

import os
import sys
import argparse
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not found in .env file")
    sys.exit(1)


EXPERT_RECRUITER_SYSTEM_PROMPT = """You are an expert LATAM recruiter with 15+ years of experience reviewing CVs from candidates in Argentina, Colombia, Mexico, and Brazil. You work with US companies that hire LATAM talent remotely.

Your task is to review a CV and make minimal fixes if needed. The goal: this CV should make a hiring manager genuinely want to speak with this person. It should feel like a real human wrote it about themselves.

**CRITICAL: You must return the CV in EXACTLY the same markdown format as provided, with minimal changes.**

## What to Check:

1. **Realism & Authenticity**
   - Does the career progression look natural and believable?
   - Are the universities and companies real and appropriate for the country?
   - Does the candidate's experience timeline make sense?
   - Are there any red flags that scream "AI-generated"?

2. **Cultural Appropriateness**
   - Are degree names appropriate for the country?
   - Are company names correctly spelled?
   - Is the location format correct (City, Country)?
   - Are language proficiency levels realistic? (English must be Advanced/Excellent/Professional — never Bilingual, Native, or Native Speaker)

3. **Professional Quality & Compelling Factor**
   - Does the current role have at least 2–3 bullets with realistic metrics (team sizes, percentages, volume, scope)? Numbers should be believable — not superhero-level.
   - Are bullet points varied in structure? Not every bullet should start with a heroic past-tense verb. A mix of impact bullets and responsibility bullets reads more human.
   - Would a hiring manager actually want to speak with this person after reading this?

4. **Professional Summary**
   - Does it read like the person's own LinkedIn About section — specific to their background, not to a specific job posting?
   - Does it have a grounded, specific opener (not a template phrase)?
   - Does it avoid sounding like it was written to apply for a specific role?

5. **Banned AI Language to Flag and Remove**
   The following words/phrases must not appear anywhere in the CV. Replace with natural, specific alternatives:
   - "Spearheaded", "leveraged", "orchestrated", "synergized", "catalyzed", "ideated"
   - "Seamlessly", "holistic", "robust", "dynamic", "transformative", "innovative", "cutting-edge"
   - "Stakeholder alignment", "drove alignment", "cross-functional synergies"
   - "Results-driven", "detail-oriented", "passionate about", "proven track record"
   - Any phrase that sounds like a job description template rather than something a real person would say

## What to Fix (ONLY if necessary):

- **Banned AI language** — replace with natural, specific alternatives
- **Bullet structure uniformity** — if every bullet follows the exact same pattern, vary 1–2 of them
- **Professional summary that reads like a template** — rewrite to sound like the person's real LinkedIn About. **Warmth comes from concrete specifics, never from sentiment.** A real person writes "Most of my day is spent inside product feeds, making sure specs and pricing are right before anything goes live" — they do not write "I thrive on accuracy" or "I am passionate about my work". If your rewrite contains a feeling-word about the work rather than a fact about the work, it is wrong. When in doubt, leave the summary exactly as it is: an unchanged plain summary is a better outcome than a warmer one that breaks the banned-language rule.
- **Missing metrics in current role** — if the current role has zero metrics, add 1–2 believable ones
- **Minor typos or formatting issues**
- **Overly AI-sounding language** (make it more human)
- **Unrealistic responsibilities** (tone down if too perfect)

## What NOT to Change:

- **Do NOT change the candidate's name**
- **Do NOT change universities or companies** (unless they're clearly fake)
- **Do NOT change dates or timeline**
- **Do NOT add new sections or experiences**
- **Do NOT remove experiences**
- **Do NOT change the overall structure**
- **Do NOT make the candidate look more qualified than they are** — the CV intentionally has 1 minor gap

## Your Response Format:

Return a JSON object with:

```json
{
  "needs_changes": true/false,
  "issues_found": [
    "List of any issues or red flags you spotted"
  ],
  "changes_made": [
    "List of specific changes you made (if any)"
  ],
  "final_cv": "The CV in markdown format (either original or slightly edited)"
}
```

## MANDATORY Final Self-Check

Before returning, re-read your own `final_cv` — not the CV you were given — and confirm none of the banned words or phrases in section 5 appear anywhere in it. **The banned list applies to text YOU write, not only to text you received.** The summary is where this rule is broken most often: rewriting it for warmth is exactly the moment "passionate about" or "thrive on" slips in. If you find a banned phrase in your own rewrite, replace it with a concrete fact or restore the original wording, then check again.

A downstream automated validator scans `final_cv` for these phrases and will discard your entire edit to that section if it finds one — so a violation loses your good changes along with the bad.

**IMPORTANT:**
- If the CV is already good, return `needs_changes: false` and `final_cv` should be the EXACT original
- Only make changes if there are actual issues that would make a recruiter suspicious or reduce the hiring manager's interest
- Keep changes minimal - this should feel like light editing, not rewriting
- Maintain the exact markdown structure and formatting
"""


# Phrases that must never appear in a CV. Kept in sync with the banned list in
# EXPERT_RECRUITER_SYSTEM_PROMPT section 5 and with references/prompt-template.md.
# Matched case-insensitively as substrings, so "Leverag" catches leverage/leveraged/leveraging.
BANNED_PHRASES = [
    "spearhead", "leverag", "orchestrat", "synerg", "catalyz", "ideated",
    "seamless", "holistic", "robust", "dynamic", "transformative",
    "innovative", "cutting-edge",
    "stakeholder alignment", "drove alignment",
    "results-driven", "detail-oriented", "passionate about", "proven track record",
    # Sentiment-about-the-work constructions the reviewer reaches for when asked to
    # warm up a summary. Observed in the wild 2026-09-08.
    "thrive on", "thrives on", "i love", "excited to", "enthusiasm for",
    "dedicated to delivering", "committed to excellence",
    # Never-allowed English proficiency framings.
    "bilingual", "native speaker", "native english",
]


def _split_sections(cv_markdown: str) -> "list[tuple[str, str]]":
    """Split a CV into (heading, body) sections on markdown headings.

    Returns a list of (heading_line, section_text) where section_text includes
    the heading. Text before the first heading is returned under heading "".
    """
    lines = cv_markdown.split("\n")
    sections = []
    current_heading = ""
    current: "list[str]" = []
    for line in lines:
        if line.startswith("#"):
            if current or current_heading:
                sections.append((current_heading, "\n".join(current)))
            current_heading = line.strip()
            current = [line]
        else:
            current.append(line)
    if current or current_heading:
        sections.append((current_heading, "\n".join(current)))
    return sections


def find_banned_phrases(text: str) -> "list[str]":
    """Return the banned phrases present in text, matched case-insensitively."""
    lowered = text.lower()
    return [phrase for phrase in BANNED_PHRASES if phrase in lowered]


def enforce_cv_constraints(original: str, reviewed: str) -> Dict[str, any]:
    """Discard reviewer edits that violate hard constraints, keeping the good ones.

    The GPT-4o reviewer reliably breaks two rules it has been given:

    1. Banned language. Asked to make a summary sound more human, it writes the
       sentiment vocabulary the prompt forbids ("thrive on", "passionate about").
       It has the banned list; it deprioritises it while actively editing.
    2. Date drift. It does not know the current date, so a current-year metric
       looks like a typo and gets "corrected" backward to the role's start year.

    Rather than trust the model or a human checklist, this reverts offending
    sections to the original text and keeps every clean section's edits.

    Returns dict with keys: cv, reverted_sections, violations.
    """
    import re

    orig_sections = _split_sections(original)
    rev_sections = _split_sections(reviewed)

    violations: "list[str]" = []

    # Date drift is checked whole-document: the set of years must be unchanged.
    orig_years = re.findall(r"\b(?:19|20)\d{2}\b", original)
    rev_years = re.findall(r"\b(?:19|20)\d{2}\b", reviewed)
    dates_drifted = orig_years != rev_years

    # If the heading structure changed the reviewer violated "do not change
    # structure"; section-wise repair is unsafe, so fall back to the original.
    orig_headings = [h for h, _ in orig_sections]
    rev_headings = [h for h, _ in rev_sections]
    if orig_headings != rev_headings:
        violations.append(
            "reviewer altered the CV's heading structure; discarded the entire review"
        )
        return {"cv": original, "reverted_sections": ["<all>"], "violations": violations}

    orig_by_index = {i: text for i, (_, text) in enumerate(orig_sections)}
    rebuilt: "list[str]" = []
    reverted: "list[str]" = []

    for i, (heading, rev_text) in enumerate(rev_sections):
        orig_text = orig_by_index[i]
        label = heading or "<preamble>"

        banned = find_banned_phrases(rev_text)
        banned_in_original = find_banned_phrases(orig_text)
        # Only fault the reviewer for phrases it introduced.
        introduced = [b for b in banned if b not in banned_in_original]

        section_years_changed = (
            re.findall(r"\b(?:19|20)\d{2}\b", orig_text)
            != re.findall(r"\b(?:19|20)\d{2}\b", rev_text)
        )

        if introduced:
            violations.append(
                f"{label}: reviewer introduced banned language {introduced!r}"
            )
            rebuilt.append(orig_text)
            reverted.append(label)
        elif section_years_changed:
            violations.append(
                f"{label}: reviewer changed year values (date drift)"
            )
            rebuilt.append(orig_text)
            reverted.append(label)
        else:
            rebuilt.append(rev_text)

        if banned_in_original:
            violations.append(
                f"{label}: banned language {banned_in_original!r} present in the "
                f"GENERATED CV and not fixed by the reviewer - fix the generation prompt"
            )

    final_cv = "\n".join(rebuilt)

    if dates_drifted and not reverted:
        violations.append(
            "document-level year mismatch with no section isolated; review manually"
        )

    return {"cv": final_cv, "reverted_sections": reverted, "violations": violations}


def review_cv_with_expert(cv_markdown: str) -> Dict[str, any]:
    """
    Review a CV using OpenAI GPT-4o as an expert LATAM recruiter.

    Args:
        cv_markdown: The CV in markdown format

    Returns:
        Dictionary containing:
        - needs_changes: bool
        - issues_found: list of strings
        - changes_made: list of strings
        - final_cv: string (markdown)
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    print("Sending CV to expert recruiter for review...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": EXPERT_RECRUITER_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Please review this CV:\n\n{cv_markdown}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3  # Lower temperature for more consistent reviews
        )

        review_result = response.choices[0].message.content

        # Parse the JSON response
        import json
        result = json.loads(review_result)

        # Validate response structure
        required_keys = ["needs_changes", "issues_found", "changes_made", "final_cv"]
        if not all(key in result for key in required_keys):
            raise ValueError(f"Invalid response format from API. Missing keys: {[k for k in required_keys if k not in result]}")

        # Enforce the hard constraints the reviewer is known to break. This runs
        # unconditionally so no caller can forget it.
        enforcement = enforce_cv_constraints(cv_markdown, result["final_cv"])
        result["final_cv"] = enforcement["cv"]
        result["violations"] = enforcement["violations"]
        result["reverted_sections"] = enforcement["reverted_sections"]

        if enforcement["violations"]:
            print("\nCONSTRAINT ENFORCEMENT:")
            for v in enforcement["violations"]:
                print(f"  ! {v}")
        if enforcement["reverted_sections"]:
            print(
                f"  -> reverted to original: "
                f"{', '.join(enforcement['reverted_sections'])}"
            )
            result["changes_made"] = list(result.get("changes_made", [])) + [
                f"AUTO-REVERTED by validator: "
                f"{', '.join(enforcement['reverted_sections'])}"
            ]
            # If every edit was thrown out, the CV is byte-identical to the input.
            if result["final_cv"] == cv_markdown:
                result["needs_changes"] = False

        return result

    except Exception as e:
        print(f"ERROR during CV review: {e}")
        # Fallback: return original CV if review fails
        return {
            "needs_changes": False,
            "issues_found": [f"Review failed: {str(e)}"],
            "changes_made": [],
            "final_cv": cv_markdown,
            "violations": [f"Review failed, original CV returned unchanged: {str(e)}"],
            "reverted_sections": []
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Review a CV using expert recruiter AI"
    )
    parser.add_argument(
        "cv_file",
        help="Path to markdown CV file"
    )

    args = parser.parse_args()

    # Read CV file
    if not os.path.exists(args.cv_file):
        print(f"ERROR: File not found: {args.cv_file}")
        sys.exit(1)

    with open(args.cv_file, 'r', encoding='utf-8') as f:
        cv_markdown = f.read()

    # Review CV
    print(f"\nReviewing CV from {args.cv_file}...\n")

    result = review_cv_with_expert(cv_markdown)

    # Print results
    print("=" * 60)
    print("EXPERT RECRUITER REVIEW RESULTS")
    print("=" * 60)

    print(f"\nNeeds Changes: {'YES' if result['needs_changes'] else 'NO'}")

    if result['issues_found']:
        print("\nIssues Found:")
        for issue in result['issues_found']:
            print(f"  - {issue}")

    if result['changes_made']:
        print("\nChanges Made:")
        for change in result['changes_made']:
            print(f"  - {change}")
    else:
        print("\nNo changes made - CV looks good!")

    if result.get('violations'):
        print("\nConstraint Violations (auto-handled):")
        for v in result['violations']:
            print(f"  ! {v}")

    print("\n" + "=" * 60)
    print("FINAL CV (after review)")
    print("=" * 60)
    print()
    print(result['final_cv'])


if __name__ == "__main__":
    main()
