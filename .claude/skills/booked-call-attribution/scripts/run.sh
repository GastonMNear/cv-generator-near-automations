#!/usr/bin/env bash
# Chain the whole weekly run. This is what a Claude routine should call.
#
#   ./run.sh                 previous full Mon-Sun week, writes the sheet and posts
#   ./run.sh 2026-08-24      the week containing that date (backfill)
#   ./run.sh --dry-run       compute everything, print the message, write nothing
#
# NOTE: no `set -u`. The repo .env contains a value with an unescaped `$3`, and
# sourcing it under `set -u` aborts the script.
set -eo pipefail
cd "$(dirname "$0")"

WEEK=""; DRY=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY="--dry-run" ;;
    -*) echo "unknown flag: $arg" >&2; exit 2 ;;
    *) WEEK="$arg" ;;
  esac
done

# Load repo .env when running locally. Cloud routines inject secrets directly and
# have no .env, so its absence is normal, not an error.
# scripts/ sits at <repo>/.claude/skills/booked-call-attribution/scripts, so the repo
# root is four levels up. Prefer git for it, and fall back to the relative walk when
# the checkout is not a git work tree.
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || (cd ../../../.. && pwd))"
ENV_FILE="$REPO_ROOT/.env"
if [ -f "$ENV_FILE" ]; then set -a; . "$ENV_FILE"; set +a; fi

WORK="${TMPDIR:-/tmp}/booked-call-attribution"
mkdir -p "$WORK"

echo "=== 1/4  HubSpot: bookings for the week ==="
python3 fetch_booked_calls.py $WEEK --out "$WORK/bookings.json"

# A zero-booking week runs the whole chain rather than short-circuiting: every step
# handles an empty set (the sheet write is a no-op, Slack reports the empty week), and
# a special-case path here previously fed post_to_slack.py a bookings payload it
# could not read. A quiet week should still produce its report.

echo "=== 2/4  Smartlead: resolve + measure first replies ==="
python3 attribute.py --bookings "$WORK/bookings.json" \
                     --booked-leads "$WORK/booked_leads.json" \
                     --out "$WORK/attribution.json"

echo "=== 3/4  Google Sheets ==="
python3 write_to_sheet.py --attribution "$WORK/attribution.json" $DRY

echo "=== 4/4  Slack ==="
python3 post_to_slack.py --attribution "$WORK/attribution.json" $DRY

echo "Done. Artifacts in $WORK"
