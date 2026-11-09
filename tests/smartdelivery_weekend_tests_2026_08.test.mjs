import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const root = path.resolve(import.meta.dirname, "..");
const source = fs.readFileSync(
  path.join(root, "scripts", "smartdelivery_weekend_tests_2026_08.mjs"),
  "utf8",
);

test("runner uses only the authorized helper campaign and sequence mapping", () => {
  assert.match(source, /const CAMPAIGN_ID = 3806282;/);
  assert.match(source, /const SEQUENCE_MAPPING_ID = 10217009;/);
  assert.doesNotMatch(source, /const CAMPAIGN_ID = 3620482;/);
  assert.doesNotMatch(source, /const SEQUENCE_MAPPING_ID = 954403[23];/);
});

test("preflight verifies paused campaign, one started lead, and sequence one", () => {
  assert.match(source, /\/campaigns\/\$\{CAMPAIGN_ID\}`/);
  assert.match(source, /\/campaigns\/\$\{CAMPAIGN_ID\}\/leads\?offset=0&limit=10/);
  assert.match(source, /campaign[^\n]*PAUSED|PAUSED[^\n]*campaign/);
  assert.match(source, /lead[^\n]*STARTED|STARTED[^\n]*lead/);
  assert.match(source, /seq_number\) === 1/);
});

test("runner has sequential bulk creation and final reconciliation commands", () => {
  assert.match(source, /async function createRemainingTests|function createRemainingTests/);
  assert.match(source, /async function finalReconciliation|function finalReconciliation/);
  assert.match(source, /command === "bulk"/);
  assert.match(source, /command === "reconcile"/);
  assert.match(source, /final-reconciliation\.md/);
});

test("canary rechecks helper campaign and lead state after creation", () => {
  assert.match(source, /verifyHelperState\(\)/);
  assert.match(source, /helper_state_after_canary/);
});

test("revised run ends at Sunday August 16 EOD in New York", () => {
  assert.match(source, /const END = "2026-08-17T03:59:59\.999Z";/);
  assert.match(source, /local_end: "2026-08-16 23:59:59\.999 EDT"/);
  assert.doesNotMatch(source, /2026-09-01T03:59:59\.999Z/);
});

test("replacement canary ignores only the stopped historical canary and reconciles by new ID", () => {
  assert.match(source, /historicalStoppedCanary/);
  assert.match(source, /beforeMatchIds/);
  assert.match(source, /newExactMatches/);
  assert.match(source, /hasVerifiedCreationRecord\(test, testId\)/);
});

test("bulk execution accepts the user-authorized immediate-send window", () => {
  assert.match(source, /execution_window_accepted/);
  assert.match(source, /user-authorized immediate sends/);
});

test("resume and final reconciliation use verified IDs instead of the ten-row report page", () => {
  assert.match(source, /function verifiedCurrentRunIds/);
  assert.match(source, /const priorVerifiedIds = verifiedCurrentRunIds\(test\)/);
  assert.match(source, /const currentRunIds = verifiedCurrentRunIds\(test\)/);
});
