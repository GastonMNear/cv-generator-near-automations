#!/usr/bin/env bash
# One booked-call auto-pause run: HubSpot bookings -> Smartlead crawl -> pause -> Slack.
#
# DRY RUN by default. Pass --live to actually pause.
#   ./run.sh                 # dry run, look back 12h
#   ./run.sh --live          # live
#   ./run.sh --hours 24      # wider window (use after a missed run)
#   ./run.sh --since-last-weekday-run 13:03   # back to 13:03 on the previous
#                                             # WEEKDAY (Monday spans the weekend)
#
# Env (from repo .env or the routine's secrets):
#   SMARTLEAD_API_KEY  HUBSPOT_ACCESS_TOKEN  SLACK_BOT_TOKEN  PAUSE_SLACK_CHANNEL_ID
# No `set -u`: .env values can contain unescaped $-sequences (e.g. a password with
# $3), which would abort sourcing under nounset.
set -o pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"

# Load .env when present (local runs). In a cloud routine the secrets are already
# exported, and this is skipped.
if [ -f "$REPO/.env" ]; then
  set -a; . "$REPO/.env" 2>/dev/null; set +a
fi

LIVE=""
HOURS="12"
SINCE_WEEKDAY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --live)  LIVE="--live"; shift ;;
    --hours) HOURS="$2"; shift 2 ;;
    # Anchor the window to a time on the previous WEEKDAY instead of a fixed
    # lookback, so the Monday run spans the weekend. See SKILL.md "Coverage".
    --since-last-weekday-run) SINCE_WEEKDAY="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 64 ;;
  esac
done

if [ -n "$SINCE_WEEKDAY" ]; then
  WINDOW_ARGS="--since-last-weekday-run $SINCE_WEEKDAY"
else
  WINDOW_ARGS="--hours $HOURS"
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
WORK="${TMPDIR:-/tmp}/booked-pause-$STAMP"
mkdir -p "$WORK"
BOOKINGS="$WORK/bookings.json"
RESULT="$WORK/result.json"

echo "== booked-call-pause $STAMP ${LIVE:-(dry run)} =="

# 1. HubSpot: what booked in the window?
python3 "$HERE/fetch_bookings.py" $WINDOW_ARGS --out "$BOOKINGS" || exit 1

COUNT="$(python3 -c "import json;print(len(json.load(open('$BOOKINGS'))))")"
if [ "$COUNT" = "0" ]; then
  echo "no bookings in the window — skipping the Smartlead crawl"
  exit 0
fi
echo "$COUNT booking(s) to process"

# 2+3. One crawl for the whole batch, then pause per matched lead.
python3 "$HERE/pause_booked.py" --bookings "$BOOKINGS" --json-out "$RESULT" $LIVE
RC=$?
if [ $RC -ne 0 ]; then
  echo "pause step failed (rc=$RC) — not posting to Slack" >&2
  exit $RC
fi

# 4. Report (silent when nothing matched and nothing failed).
python3 "$HERE/post_to_slack.py" "$RESULT" || true

echo "artifacts: $WORK"
