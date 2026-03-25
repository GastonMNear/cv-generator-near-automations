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


EXPERT_RECRUITER_SYSTEM_PROMPT = """You are an expert LATAM recruiter with 15+ years of experience reviewing CVs from candidates in Argentina, Colombia, Mexico, and Brazil.

Your task is to review a CV and evaluate if it appears human, realistic, and professionally appropriate for a LATAM candidate.

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
   - Are language proficiency levels realistic?

3. **Professional Quality**
   - Are bullet points professional and achievement-oriented?
   - Is the professional summary concise and relevant?
   - Are technical skills listed appropriately?

4. **Common AI-Generated Patterns to Flag**
   - Overly perfect alignment with all job requirements
   - Buzzword-heavy descriptions
   - Unrealistic career jumps
   - Too many responsibilities per role
   - Generic, templated language

## What to Fix (ONLY if necessary):

- **Minor typos or formatting issues**
- **Overly AI-sounding language** (make it more human/casual)
- **Unrealistic responsibilities** (tone down if too perfect)
- **Missing cultural touches** (add if needed)

## What NOT to Change:

- **Do NOT change the candidate's name**
- **Do NOT change universities or companies** (unless they're fake)
- **Do NOT change dates or timeline**
- **Do NOT add new sections or experiences**
- **Do NOT remove experiences**
- **Do NOT change the overall structure**

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

**IMPORTANT:**
- If the CV is already good, return `needs_changes: false` and `final_cv` should be the EXACT original
- Only make changes if there are actual issues that would make a recruiter suspicious
- Keep changes minimal - this should feel like light editing, not rewriting
- Maintain the exact markdown structure and formatting
"""


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

        return result

    except Exception as e:
        print(f"ERROR during CV review: {e}")
        # Fallback: return original CV if review fails
        return {
            "needs_changes": False,
            "issues_found": [f"Review failed: {str(e)}"],
            "changes_made": [],
            "final_cv": cv_markdown
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

    print("\n" + "=" * 60)
    print("FINAL CV (after review)")
    print("=" * 60)
    print()
    print(result['final_cv'])


if __name__ == "__main__":
    main()
