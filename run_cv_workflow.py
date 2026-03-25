#!/usr/bin/env python3
"""Run expert review and Google Doc creation for the generated CV."""

import sys
import os
from pathlib import Path

# Add script directory to path
script_dir = Path("c:/Users/lenovo/Documents/Kevin - Near automations/.claude/skills/latam-cv-generator/scripts")
sys.path.insert(0, str(script_dir))

# Set working directory for dotenv
os.chdir("c:/Users/lenovo/Documents/Kevin - Near automations")

# Read the generated CV
cv_path = ".temp/generated_cv.md"
with open(cv_path, 'r', encoding='utf-8') as f:
    cv_markdown = f.read()

print("CV loaded. Starting expert review...\n")

# Step 1: Expert review
from review_cv import review_cv_with_expert

review_result = review_cv_with_expert(cv_markdown)

print(f"\nNeeds Changes: {'YES' if review_result['needs_changes'] else 'NO'}")
if review_result['issues_found']:
    print("Issues Found:")
    for issue in review_result['issues_found']:
        print(f"  - {issue}")
if review_result['changes_made']:
    print("Changes Made:")
    for change in review_result['changes_made']:
        print(f"  - {change}")
else:
    print("No changes made - CV looks good!")

final_cv = review_result['final_cv']

# Save reviewed CV
reviewed_path = ".temp/reviewed_cv.md"
with open(reviewed_path, 'w', encoding='utf-8') as f:
    f.write(final_cv)
print(f"\nReviewed CV saved to {reviewed_path}")

# Step 2: Create Google Doc
print("\nCreating Google Doc...")
from create_google_doc import create_cv_google_doc

# Extract candidate name from CV (first line after # )
candidate_name = final_cv.split('\n')[0].replace('# ', '').strip()
print(f"Candidate: {candidate_name}")

doc_url = create_cv_google_doc(
    cv_markdown=final_cv,
    title=f"{candidate_name} - CV"
)

print(f"\nCV created successfully!")
print(f"Google Doc: {doc_url}")

# Clean up temp files
for temp_file in [cv_path, reviewed_path]:
    if os.path.exists(temp_file):
        os.remove(temp_file)
        print(f"Deleted temp file: {temp_file}")
