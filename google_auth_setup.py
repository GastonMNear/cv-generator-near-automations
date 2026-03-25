"""One-time OAuth setup: opens browser, you log in, and it saves the refresh token to .env."""

import os
import re
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8090"
SCOPES = "https://www.googleapis.com/auth/documents https://www.googleapis.com/auth/drive"

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERROR: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET missing from .env")
    exit(1)

auth_code = None


class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = parse_qs(urlparse(self.path).query)
        if "code" in query:
            auth_code = query["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Success! You can close this tab.</h1>")
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            error = query.get("error", ["unknown"])[0]
            self.wfile.write(f"<h1>Error: {error}</h1>".encode())

    def log_message(self, format, *args):
        pass  # suppress request logs


# Step 1: Open browser for consent
auth_url = (
    f"https://accounts.google.com/o/oauth2/v2/auth"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&response_type=code"
    f"&scope={SCOPES}"
    f"&access_type=offline"
    f"&prompt=consent"
)

print("Opening browser for Google sign-in...")
webbrowser.open(auth_url)
print("Waiting for authorization (sign in and click Allow)...\n")

# Step 2: Wait for the redirect
server = HTTPServer(("localhost", 8090), OAuthHandler)
server.handle_request()

if not auth_code:
    print("ERROR: No authorization code received.")
    exit(1)

print("Authorization code received. Exchanging for tokens...")

# Step 3: Exchange code for tokens
token_resp = requests.post(
    "https://oauth2.googleapis.com/token",
    data={
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    },
)

if token_resp.status_code != 200:
    print(f"ERROR: Token exchange failed: {token_resp.text}")
    exit(1)

tokens = token_resp.json()
refresh_token = tokens.get("refresh_token")

if not refresh_token:
    print(f"ERROR: No refresh token in response: {tokens}")
    exit(1)

# Step 4: Save refresh token to .env
env_path = os.path.join(os.path.dirname(__file__), ".env")
with open(env_path, "r") as f:
    env_content = f.read()

env_content = re.sub(
    r"GOOGLE_REFRESH_TOKEN=.*",
    f"GOOGLE_REFRESH_TOKEN={refresh_token}",
    env_content,
)

with open(env_path, "w") as f:
    f.write(env_content)

print(f"\nSUCCESS! Refresh token saved to .env")
print("You can now delete this script — it's only needed once.")
