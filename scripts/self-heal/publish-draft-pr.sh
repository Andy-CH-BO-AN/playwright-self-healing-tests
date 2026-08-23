#!/usr/bin/env bash
set -euo pipefail

# Publish automated repair changes as a Draft PR for human review.
# Required env vars:
#   GH_TOKEN, GITHUB_REPOSITORY, DEFAULT_BRANCH, EVIDENCE_ROOT,
#   FINGERPRINTS, REPAIR_STATUS, SOURCE_RUN_ID, SOURCE_RUN_URL,
#   SOURCE_SHA, RUNNER_TEMP, GITHUB_STEP_SUMMARY

branch="fix/self-heal-${SOURCE_RUN_ID}"
existing_pr=$(gh pr list \
  --repo "$GITHUB_REPOSITORY" \
  --head "$branch" \
  --state all \
  --limit 1 \
  --json url \
  --jq '.[0].url // ""')

if [ -n "$existing_pr" ]; then
  {
    echo "## AI Self-Heal"
    echo "A pull request already exists for Scheduled E2E run ${SOURCE_RUN_ID}: ${existing_pr}"
  } >> "$GITHUB_STEP_SUMMARY"
  exit 0
fi

gh auth setup-git
if git ls-remote --exit-code --heads origin "refs/heads/${branch}" > /dev/null; then
  {
    echo "## AI Self-Heal"
    echo "Branch ${branch} already exists without a pull request; refusing to overwrite it."
  } >> "$GITHUB_STEP_SUMMARY"
  exit 1
fi

mapfile -d '' failure_files < <(
  find "$EVIDENCE_ROOT" -type f -name failure.json -print0
)
source_failures=()
for f in "${failure_files[@]}"; do
  nodeid=$(jq -r '.nodeid // ""' "$f")
  if [ -n "$nodeid" ]; then
    source_failures+=("- \`${nodeid}\`")
  fi
done

diff_stat=$(git diff --stat)
pr_body="${RUNNER_TEMP:-/tmp}/self-heal-pr.md"

{
  for fp in $FINGERPRINTS; do
    echo "<!-- self-heal-fingerprint: ${fp} -->"
  done
  echo "## Summary"
  echo "Automated locator repair for failure(s) detected by the Scheduled E2E Monitor."
  echo
  echo "## Repair status"
  if [ "$REPAIR_STATUS" = "REPAIRED" ]; then
    echo "Complete repair — all E2E tests passed."
  else
    echo "Partial repair — human follow-up required (some E2E failures remain after repair rounds)."
  fi
  echo
  echo "## Source failure(s)"
  echo "- Scheduled run: [${SOURCE_RUN_ID}](${SOURCE_RUN_URL})"
  echo "- Tested commit: \`${SOURCE_SHA}\`"
  if [ "${#source_failures[@]}" -gt 0 ]; then
    echo "- Failing testcase(s):"
    for sf in "${source_failures[@]}"; do
      echo "  ${sf}"
    done
  fi
  echo
  echo "## Changes"
  echo '```text'
  printf '%s\n' "$diff_stat"
  echo '```'
  echo
  echo "## Validation"
  echo "The self-heal validation sequence was run before this commit was created."
  echo
  echo "Human review is required. This Draft PR will not be approved or merged automatically."
} > "$pr_body"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git switch -c "$branch"
git add pages/
git commit \
  -m "FIX: repair locator drift from nightly run ${SOURCE_RUN_ID}" \
  -m "Repair locator failure(s) detected by Scheduled E2E run ${SOURCE_RUN_ID} at ${SOURCE_SHA}." \
  -m "Status: ${REPAIR_STATUS}. The self-heal validation sequence was run before this commit was created."

git push origin "HEAD:refs/heads/${branch}"
pr_url=$(gh pr create \
  --repo "$GITHUB_REPOSITORY" \
  --base "$DEFAULT_BRANCH" \
  --head "$branch" \
  --draft \
  --title "FIX: repair locator drift from nightly run ${SOURCE_RUN_ID}" \
  --body-file "$pr_body")

{
  echo "## AI Self-Heal"
  echo "Created Draft PR (${REPAIR_STATUS}): ${pr_url}"
} >> "$GITHUB_STEP_SUMMARY"
