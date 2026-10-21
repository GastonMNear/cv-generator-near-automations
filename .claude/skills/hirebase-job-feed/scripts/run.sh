#!/usr/bin/env bash
# One Hirebase -> Clay feed run. DRY RUN by default (free estimate only).
#   ./run.sh                    # dry run, yesterday (UTC)
#   ./run.sh --live             # fetch + post every job to Clay
#   ./run.sh --live --sample 3  # cheap end-to-end test
#   ./run.sh --date 2026-10-19  # a specific day (after a missed run)
#
# Env (from repo .env or the routine's secrets): HIREBASE_API_KEY  CLAY_HIREBASE_WEBHOOK_URL
# No `set -u`: .env values can contain unescaped $-sequences, which abort sourcing under nounset.
set -o pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"

# Load .env when present (local runs). In a cloud routine the secrets are already exported.
if [ -f "$REPO/.env" ]; then
  set -a; . "$REPO/.env" 2>/dev/null; set +a
fi

python3 -u "$HERE/feed.py" "$@"
