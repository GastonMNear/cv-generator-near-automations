#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete CV Workflow: Review + Google Doc Creation
"""

import sys
from pathlib import Path
import os
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add scripts directory to path
script_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(script_dir))

from review_cv import review_cv_with_expert
from create_google_doc import create_cv_google_doc

def main():
    # Read the generated CV
    cv_path = Path(__file__).parent / ".temp" / "generated_cv.md"

    if not cv_path.exists():
        print(f"Error: CV file not found at {cv_path}")
        sys.exit(1)

    with open(cv_path, 'r', encoding='utf-8') as f:
        cv_markdown = f.read()

    print("=" * 60)
    print("STEP 1: EXPERT RECRUITER REVIEW")
    print("=" * 60)
    print()

    # Send to expert for review
    print("Sending CV to expert recruiter for review...")
    review_result = review_cv_with_expert(cv_markdown)

    # Display review results
    if review_result['needs_changes']:
        print(f"\n✓ Expert Review Complete: Changes were made")
        print(f"   Issues found: {', '.join(review_result['issues_found'])}")
        print(f"   Changes made: {', '.join(review_result['changes_made'])}")
    else:
        print("\n✓ Expert Review Complete: CV looks good - no changes needed")

    # Get final CV
    final_cv = review_result['final_cv']

    # Save reviewed CV to temp file
    reviewed_cv_path = Path(__file__).parent / ".temp" / "reviewed_cv.md"
    with open(reviewed_cv_path, 'w', encoding='utf-8') as f:
        f.write(final_cv)

    print()
    print("=" * 60)
    print("STEP 2: CREATE GOOGLE DOC")
    print("=" * 60)
    print()

    # Extract candidate name from CV (first line after # )
    first_line = final_cv.split('\n')[0].replace('# ', '').strip()
    candidate_name = first_line

    print(f"Creating Google Doc for: {candidate_name}")

    # Create Google Doc
    doc_url = create_cv_google_doc(
        cv_markdown=final_cv,
        title=f"{candidate_name} - CV"
    )

    print(f"\n✓ Google Doc created successfully!")
    print()
    print("=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)
    print()
    print(f"Google Doc URL: {doc_url}")
    print()

    # Clean up temporary files
    print("Cleaning up temporary files...")
    for temp_file in [cv_path, reviewed_cv_path]:
        if temp_file.exists():
            os.remove(temp_file)
            print(f"  ✓ Deleted {temp_file.name}")

    print()
    print("All done!")

    # Return results
    return {
        'candidate_name': candidate_name,
        'google_doc_url': doc_url,
        'review_result': review_result
    }

if __name__ == "__main__":
    result = main()
