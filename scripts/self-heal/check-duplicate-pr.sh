#!/usr/bin/env bash
set -euo pipefail

# Check for existing open repair PRs that match the failure fingerprints.
# Required env vars: GH_TOKEN, GITHUB_REPOSITORY, EVIDENCE_ROOT, GITHUB_OUTPUT, GITHUB_STEP_SUMMARY

open_pr_bodies=$(gh pr list \
  --repo "$GITHUB_REPOSITORY" \
  --state open \
  --limit 100 \
  --json url,body,headRefName,isCrossRepository \
  | jq -c '
    [ .[] | select(
        (.isCrossRepository == false) and
        ((.headRefName // "") | startswith("fix/self-heal-"))
      ) | {url: .url, body: (.body // "")} ]
  ')

mapfile -d '' evidence_files < <(
  find "$EVIDENCE_ROOT" -type f -name failure.json -print0
)

fingerprints=()
for file in "${evidence_files[@]}"; do
  fingerprint_input=$(jq -c \
    '[.nodeid // "", .error_type // "", .error_message // ""]' \
    "$file")
  fp=$(printf '%s' "$fingerprint_input" | sha256sum | cut -d' ' -f1)
  fingerprints+=("$fp")

  marker="<!-- self-heal-fingerprint: ${fp} -->"
  matching_pr=$(echo "$open_pr_bodies" | jq -r --arg marker "$marker" '
    .[] | select(.body | contains($marker)) | .url
  ' | head -n 1)

  if [ -n "$matching_pr" ]; then
    echo "should_repair=false" >> "$GITHUB_OUTPUT"
    {
      echo "## AI Self-Heal"
      echo "Existing repair PR already handles failure (${fp}): ${matching_pr}"
    } >> "$GITHUB_STEP_SUMMARY"
    exit 0
  fi
done

echo "should_repair=true" >> "$GITHUB_OUTPUT"
echo "fingerprints=${fingerprints[*]}" >> "$GITHUB_OUTPUT"
