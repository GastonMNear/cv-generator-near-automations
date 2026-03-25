"""Quick test: authenticate with Google OAuth and create a test doc in your Drive folder."""

import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

if not client_id or not client_secret or not refresh_token or not folder_id:
    print("FAIL: Missing one or more env vars:")
    print(f"  GOOGLE_CLIENT_ID: {'set' if client_id else 'MISSING'}")
    print(f"  GOOGLE_CLIENT_SECRET: {'set' if client_secret else 'MISSING'}")
    print(f"  GOOGLE_REFRESH_TOKEN: {'set' if refresh_token else 'MISSING'}")
    print(f"  GOOGLE_DRIVE_FOLDER_ID: {'set' if folder_id else 'MISSING'}")
    exit(1)

print("1. Building OAuth credentials...")
creds = Credentials(
    token=None,
    refresh_token=refresh_token,
    client_id=client_id,
    client_secret=client_secret,
    token_uri="https://oauth2.googleapis.com/token",
)
print("   OK")

print("2. Creating test Google Doc...")
docs_service = build("docs", "v1", credentials=creds)
doc = docs_service.documents().create(body={"title": "Test CV - Delete Me"}).execute()
doc_id = doc["documentId"]
print(f"   OK - doc created with ID: {doc_id}")

print("3. Adding test content...")
docs_service.documents().batchUpdate(
    documentId=doc_id,
    body={
        "requests": [
            {"insertText": {"location": {"index": 1}, "text": "This is a test document created by the CV automation pipeline.\n\nIf you can see this in your Google Drive folder, authentication is working correctly!"}}
        ]
    },
).execute()
print("   OK - content added")

print("4. Moving doc to your Drive folder...")
drive_service = build("drive", "v3", credentials=creds)
drive_service.files().update(
    fileId=doc_id,
    addParents=folder_id,
    removeParents="root",
    fields="id, parents",
).execute()
print(f"   OK - moved to folder {folder_id}")

print()
print(f"SUCCESS! Check your Google Drive folder for 'Test CV - Delete Me'")
print(f"Doc URL: https://docs.google.com/document/d/{doc_id}/edit")
