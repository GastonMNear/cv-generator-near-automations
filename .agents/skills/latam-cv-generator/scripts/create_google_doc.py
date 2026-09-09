#!/usr/bin/env python3
"""
Create a Google Doc from CV markdown content.

Usage:
    python create_google_doc.py <cv_markdown_file> [--title "CV Title"]

Or import and use programmatically:
    from create_google_doc import create_cv_google_doc
    doc_url = create_cv_google_doc(cv_content, title="John Doe - CV")
"""

import os
import sys
import argparse
import re
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    print("ERROR: Missing Google credentials in .env file")
    print("Required: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN")
    sys.exit(1)


def get_access_token() -> str:
    """Get a fresh access token using the refresh token."""
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
    )

    if token_resp.status_code != 200:
        raise Exception(f"Failed to get access token: {token_resp.text}")

    return token_resp.json()["access_token"]


def parse_markdown_cv(markdown: str) -> Dict[str, Any]:
    """Parse markdown CV into structured sections."""
    sections = {}
    current_section = None
    current_content = []

    lines = markdown.strip().split('\n')

    for line in lines:
        # H1 (name)
        if line.startswith('# '):
            sections['name'] = line[2:].strip()
        # H2 (major sections)
        elif line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[3:].strip()
            current_content = []
        else:
            if current_section:
                current_content.append(line)
            elif 'header' not in sections:
                # Lines before first H2 are header info
                if 'header' not in sections:
                    sections['header'] = []
                sections['header'].append(line)

    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content)

    return sections


def markdown_to_google_docs_requests(markdown: str) -> List[Dict[str, Any]]:
    """Convert markdown CV to Google Docs API batch update requests."""
    requests_list = []

    # Parse the CV
    sections = parse_markdown_cv(markdown)

    # Track current insertion index
    index = 1

    # Helper function to add text with style
    def add_text(text: str, bold: bool = False, font_size: int = 11, is_heading: bool = False):
        nonlocal index

        # Skip empty text
        if not text:
            return

        # Insert text
        requests_list.append({
            "insertText": {
                "location": {"index": index},
                "text": text
            }
        })

        # Always apply explicit styling to prevent bold/size inheritance from prior text
        is_bold = bold or is_heading
        requests_list.append({
            "updateTextStyle": {
                "range": {
                    "startIndex": index,
                    "endIndex": index + len(text)
                },
                "textStyle": {
                    "bold": is_bold,
                    "fontSize": {"magnitude": font_size, "unit": "PT"}
                },
                "fields": "bold,fontSize"
            }
        })

        index += len(text)

    # Add name (H1)
    if 'name' in sections:
        add_text(sections['name'] + '\n', bold=True, font_size=18, is_heading=True)
        add_text('\n')

    # Add header info (contact details)
    if 'header' in sections:
        for line in sections['header']:
            if line.strip():
                # Check if it's a bold field (e.g., **Email:**)
                if line.startswith('**') and ':**' in line:
                    parts = line.split(':**', 1)
                    field_name = parts[0].replace('**', '') + ':'
                    field_value = parts[1].strip() if len(parts) > 1 else ''

                    add_text(field_name + ' ', bold=True)
                    add_text(field_value + '\n')
                else:
                    add_text(line + '\n')
        add_text('\n')

    # Process each section
    for section_name in ['Professional Summary', 'Work Experience', 'Education', 'Skills', 'Certifications']:
        if section_name in sections:
            # Section heading (H2)
            add_text(section_name + '\n', bold=True, font_size=14, is_heading=True)
            add_text('\n')

            # Section content
            content = sections[section_name].strip()

            # Process line by line
            for line in content.split('\n'):
                if not line.strip():
                    add_text('\n')
                    continue

                # H3 (job titles, degree names)
                if line.startswith('### '):
                    add_text(line[4:] + '\n', bold=True, font_size=12)
                # Bold lines (company, university)
                elif line.startswith('**') and line.endswith('**'):
                    text = line.replace('**', '')
                    add_text(text + '\n', bold=True)
                # Bullet points
                elif line.startswith('- '):
                    add_text('• ' + line[2:] + '\n')
                # Regular text
                else:
                    # Handle inline bold (e.g., **Technical Skills:**)
                    if '**' in line:
                        parts = re.split(r'(\*\*.*?\*\*)', line)
                        for part in parts:
                            if part.startswith('**') and part.endswith('**'):
                                add_text(part[2:-2], bold=True)
                            else:
                                add_text(part)
                        add_text('\n')
                    else:
                        add_text(line + '\n')

            add_text('\n')

    return requests_list


def create_cv_google_doc(cv_markdown: str, title: str = "CV") -> str:
    """
    Create a Google Doc from CV markdown content.

    Args:
        cv_markdown: CV content in markdown format
        title: Title for the Google Doc

    Returns:
        URL of the created Google Doc
    """
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Step 1: Create blank document
    create_resp = requests.post(
        "https://docs.googleapis.com/v1/documents",
        headers=headers,
        json={"title": title}
    )

    if create_resp.status_code != 200:
        raise Exception(f"Failed to create document: {create_resp.text}")

    doc_id = create_resp.json()["documentId"]
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    print(f"Created document: {title}")
    print(f"Document ID: {doc_id}")

    # Step 2: Convert markdown to Google Docs requests
    print("Converting markdown to Google Docs format...")
    requests_list = markdown_to_google_docs_requests(cv_markdown)

    # Step 3: Batch update document with content
    print(f"Inserting content ({len(requests_list)} operations)...")
    update_resp = requests.post(
        f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate",
        headers=headers,
        json={"requests": requests_list}
    )

    if update_resp.status_code != 200:
        raise Exception(f"Failed to update document: {update_resp.text}")

    print("Content inserted successfully!")

    # Step 4: Move to folder if DRIVE_FOLDER_ID is set
    if DRIVE_FOLDER_ID:
        print(f"Moving document to folder {DRIVE_FOLDER_ID}...")
        move_resp = requests.patch(
            f"https://www.googleapis.com/drive/v3/files/{doc_id}",
            headers=headers,
            params={"addParents": DRIVE_FOLDER_ID},
        )

        if move_resp.status_code == 200:
            print("Document moved to folder successfully!")
        else:
            print(f"Warning: Failed to move to folder: {move_resp.text}")

    return doc_url


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Create a Google Doc from CV markdown file"
    )
    parser.add_argument(
        "cv_file",
        help="Path to markdown CV file"
    )
    parser.add_argument(
        "--title",
        default="CV",
        help="Title for the Google Doc (default: 'CV')"
    )

    args = parser.parse_args()

    # Read CV file
    if not os.path.exists(args.cv_file):
        print(f"ERROR: File not found: {args.cv_file}")
        sys.exit(1)

    with open(args.cv_file, 'r', encoding='utf-8') as f:
        cv_markdown = f.read()

    # Create Google Doc
    try:
        doc_url = create_cv_google_doc(cv_markdown, args.title)
        print(f"\nSUCCESS!")
        print(f"Google Doc URL: {doc_url}")
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
