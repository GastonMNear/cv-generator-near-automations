#!/usr/bin/env python3
"""
Clay API Authentication for Email Replies Workflow
Authenticates and stores session cookie for subsequent API calls
"""

import urllib.request
import json
import ssl
import os
import sys

# Clay credentials
CLAY_USERNAME = "kevin.dubon@hirewithnear.com"
CLAY_PASSWORD = "P$3NsPEHJu6se2p"

def authenticate():
    """Authenticate with Clay API and return session cookie"""

    # Create SSL context
    ctx = ssl.create_default_context()
    BASE = "https://api.clay.com/v3"

    # Login request
    login_data = json.dumps({
        "email": CLAY_USERNAME,
        "password": CLAY_PASSWORD,
        "source": "web"
    }).encode()

    req = urllib.request.Request(
        f"{BASE}/auth/login",
        data=login_data,
        headers={
            "Content-Type": "application/json",
            "Origin": "https://app.clay.com",
            "Referer": "https://app.clay.com/"
        },
        method="POST"
    )

    try:
        # Execute login
        resp = urllib.request.urlopen(req, context=ctx)
        cookie_header = resp.headers.get("Set-Cookie", "")
        session = cookie_header.split(";")[0]  # Extract "claysession=..."

        if not session.startswith("claysession="):
            print(json.dumps({"success": False, "error": "Invalid session cookie format"}))
            return None

        print(json.dumps({"success": True, "session": session}))
        return session

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ""
        print(json.dumps({
            "success": False,
            "error": f"HTTP {e.code}: {e.reason}",
            "details": error_body
        }))
        return None
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        return None

if __name__ == "__main__":
    authenticate()
