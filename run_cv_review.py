#!/usr/bin/env python3
"""
Run expert CV review and create Google Doc
"""
import sys
import os
from pathlib import Path

# Add script directory to path
script_dir = Path("c:/Users/lenovo/Documents/Kevin - Near automations/.claude/skills/latam-cv-generator/scripts")
sys.path.insert(0, str(script_dir))

from review_cv import review_cv_with_expert
from create_google_doc import create_cv_google_doc

# Read generated CV
cv_path = "c:/Users/lenovo/Documents/Kevin - Near automations/.temp/generated_cv.md"
with open(cv_path, 'r', encoding='utf-8') as f:
    cv_markdown = f.read()

print("[REVIEW] Sending CV to expert recruiter for review...")
print("="*60)

# Send to expert recruiter
review_result = review_cv_with_expert(cv_markdown)

# Check results
if review_result['needs_changes']:
    print(f"\n[REVIEW] Changes were made")
    print(f"[ISSUES] Issues found: {', '.join(review_result['issues_found'])}")
    print(f"[CHANGES] Changes applied: {', '.join(review_result['changes_made'])}")
else:
    print("\n[REVIEW] CV looks good - no changes needed")

print("\n" + "="*60)

# Use the reviewed CV (either original or edited)
final_cv_markdown = review_result['final_cv']

# Save reviewed CV
reviewed_cv_path = "c:/Users/lenovo/Documents/Kevin - Near automations/.temp/reviewed_cv.md"
with open(reviewed_cv_path, 'w', encoding='utf-8') as f:
    f.write(final_cv_markdown)

print(f"[SAVE] Reviewed CV saved to: {reviewed_cv_path}")

# Extract candidate name from CV (first line after # )
candidate_name = final_cv_markdown.split('\n')[0].replace('# ', '').strip()

# Create Google Doc
print(f"\n[DOC] Creating Google Doc for: {candidate_name}")
print("="*60)

doc_url = create_cv_google_doc(
    cv_markdown=final_cv_markdown,
    title=f"{candidate_name} - CV"
)

print(f"\n[SUCCESS] CV created successfully!")
print(f"[DOC] Google Doc: {doc_url}")

# Output JSON result
import json
result = {
    "candidate_name": candidate_name,
    "google_doc_url": doc_url,
    "review": {
        "needs_changes": review_result['needs_changes'],
        "issues_found": review_result['issues_found'],
        "changes_made": review_result['changes_made']
    }
}

result_path = "c:/Users/lenovo/Documents/Kevin - Near automations/.temp/cv_result.json"
with open(result_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)

print(f"\n[SAVE] Result saved to: {result_path}")

# Clean up temporary files
print(f"\n[CLEANUP] Removing temporary markdown files...")
try:
    if os.path.exists(cv_path):
        os.remove(cv_path)
        print(f"[OK] Deleted: {cv_path}")
    if os.path.exists(reviewed_cv_path):
        os.remove(reviewed_cv_path)
        print(f"[OK] Deleted: {reviewed_cv_path}")
except Exception as e:
    print(f"[WARN] Cleanup warning: {e}")

print(f"\n{'='*60}")
print(f"WORKFLOW COMPLETE")
print(f"{'='*60}")
