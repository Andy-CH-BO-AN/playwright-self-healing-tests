---
name: git-change-conventions
description: 在此 repository 建立或命名 branch、pull request、commit 時使用。遵守既定 type prefix，並撰寫詳盡 commit message。
---

# Git Change Conventions

task 包含建立 branch、更新 README、命名 pull request、撰寫 commit message，或提議 branch／PR／commit naming convention 時使用。

## PR title format

Pull request title 必須精確採用：`<TYPE>: <summary>`。

允許的 `<TYPE>`：

- `FEATURE:` new feature
- `FIX:` bug fix
- `REFACTOR:` 無行為變更的 code refactor
- `DOCS:` documentation only
- `TEST:` tests only
- `STYLE:` 僅 formatting，例如 linting 或 layout cleanup
- `PERF:` performance improvement
- `CHORE:` maintenance 或 miscellaneous housekeeping
- `CI:` continuous integration configuration 或 script

## Branch format

Git branch 不可含 `:` 或 space，故採用：`<type>/<summary-in-kebab-case>`。

例：`feat/add-weekly-fatigue-summary`、`fix/handle-empty-garmin-heart-rate-payload`。

## 必要規則

1. 除非有明確理由，branch 與 PR title 使用相同 logical type。
2. branch 使用 short lowercase prefix（如 `feat`）；PR title 使用完整允許的 TYPE（如 `FEATURE:`）。
3. prefix 後文字精確描述實際變更。
4. 使用者未明確改變 convention 前，不得自創 top-level prefix。
5. 跨多 category 時選擇最符合主要 user-facing outcome 的 prefix。
6. branch summary 轉為 lowercase kebab-case。
7. PR description 應包含 summary、why、what changed、重要 implementation／validation note。

## Commit message 規則

- Commit message 必須詳盡，不可過短。
- subject line 清楚說明 intent 與 affected area。
- 非 trivial 變更優先採 multiline commit message。
- body 摘要 what changed、why 需要此變更、重要 implementation 或 validation note。

## 範例

- Branch：`feat/add-weekly-fatigue-summary`
- PR title：`FEATURE: add weekly fatigue summary to coach report`
- Branch：`fix/handle-empty-garmin-heart-rate-payload`
- PR title：`FIX: handle empty Garmin heart rate payload`
- Branch：`docs/add-shared-git-naming-conventions`
- PR title：`DOCS: add shared Git naming conventions for branch, PR, and commits`

## GitHub CLI environment

所有 `gh` command 必須在 local host environment 執行，使用其 credential store 與 GitHub configuration。不可使用 sandboxed `gh` credential 或 fallback；local-host `gh` authentication 失敗時停止並回報 authentication blocker。

## 使用 GitHub CLI 建立 PR

使用 `gh` 建立 PR 時套用上述 convention：

```bash
gh pr create \
  --title "TYPE: summary" \
  --body "## Summary
<這個 PR 做什麼>

## Why
<為何需要此變更>

## Changes
- <file/area>: <description>

## Validation
- <執行的 test、manual check 或 screenshot>" \
  --base main
```

- 不得使用 `--draft`；每個 PR 都必須可立即 review。
- team 要求 reviewer 時加入 `--reviewer <handle>`。
- 有 project label 時加入 `--label <label>`。
- PR title TYPE 必須用允許名稱，不可直接將 branch prefix 大寫：`feat`→`FEATURE`、`fix`→`FIX`、`refactor`→`REFACTOR`、`docs`→`DOCS`、`test`→`TEST`、`style`→`STYLE`、`perf`→`PERF`、`chore`→`CHORE`、`ci`→`CI`。

## PR review follow-up

完成要求的 PR review change 後，commit 並 push fix，再使用 PR 的 **Add a comment** action 發布 `@codex review`，要求 Codex reviewer 再次審查。

## Output expectation

- 被要求建立名稱時，提供精確符合 convention 的 branch 與 PR title。
- 被要求 commit 時，依變更範圍撰寫詳盡 commit message，不用單行 shorthand。
