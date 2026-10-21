#!/bin/bash
# Hirebase job search: US remote, full-time, 1-500 employees, Near's qualified sub-industries, last 7 days.
# Bills 1 unit per job returned. Size first for free: same body to /v2/jobs/estimate with "limit": 0.
# Usage: HIREBASE_API_KEY=... ./search_request.sh [page]
PAGE="${1:-1}"
BODY=$(python3 -c "import json,sys; b=json.load(open('$(dirname "$0")/search_request.json')); b['page']=int(sys.argv[1]); print(json.dumps(b))" "$PAGE")
curl -s -X POST 'https://api.hirebase.org/v2/jobs/search' \
  -H 'Content-Type: application/json' \
  -H "x-api-key: $HIREBASE_API_KEY" \
  -d "$BODY"
