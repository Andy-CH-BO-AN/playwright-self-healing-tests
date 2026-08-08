---
name: improve-codebase-architecture
description: 掃描 codebase 的 deepening 機會，以視覺化 HTML report 呈現，並針對使用者選擇的項目進行 grilling。
---

# 改善 Codebase Architecture

找出 architectural friction，提出 **deepening opportunities**：將 shallow module 轉為 deep module 的 refactor。目標是提升 testability 與 AI-navigability。

此 command 必須以 project 的 domain model 為依據，並採用共通 design vocabulary：

- 執行 `$codebase-design` skill，使用其 architecture vocabulary（**module**、**interface**、**depth**、**seam**、**adapter**、**leverage**、**locality**）及原則（deletion test、"the interface is the test surface"、"one adapter = hypothetical seam, two = real"）。每個 suggestion 必須精確使用這些詞；不可改用「component」、「service」、「API」或「boundary」。
- `CONTEXT.md` 的 domain language 為良好 seam 命名；`docs/adr/` 的 ADR 記錄不可重新爭論的決策。

## 流程

### 1. 探索

**掃描前先定範圍：YAGNI。**Deepening module 的價值在於讓未來修改更容易，因此優先檢視近期常變動處。

- 使用者指定 module、subsystem 或 pain point 時直接採用，略過後續推論。
- 否則查看一段足夠的 `git log --oneline`，找出重複出現的 hotspot files／area，優先由這些 path 開始；若變更分散且沒有 hotspot，才擴大範圍。

先讀專案 glossary（`CONTEXT.md`）與即將處理 area 的 ADR。接著派 sub-agent 探索 codebase，不可僵化套用 heuristic；記錄理解時遇到的 friction：

- 是否理解一個概念需要反覆切換許多小 module？
- 哪些 module 是 **shallow**，其 interface 幾乎和 implementation 一樣複雜？
- 是否為了 testability 抽出 pure function，真正 bug 卻藏在呼叫關係，使 **locality** 消失？
- 哪些緊密耦合 module 跨越 seam 泄漏？
- 哪些 area 沒測試，或難以透過現有 interface 測試？

對可疑 shallow module 套用 **deletion test**：刪除它會集中 complexity，還是只會移動 complexity？「會集中」才是值得處理的 signal。

### 2. 用 HTML report 呈現候選項目

將 self-contained HTML 寫入 OS temporary directory，不可寫入 repo。由 `$TMPDIR` 取得 temp dir，否則採用 Linux `/tmp`、Windows `%TEMP%`；檔名為 `<tmpdir>/architecture-review-<timestamp>.html`，每次執行皆建立新檔。以 Linux `xdg-open <path>`、macOS `open <path>`、Windows `start <path>` 開啟，並回報 absolute path。

Report 必須完全離線可用：所有 CSS 直接寫入 `<style>`，所有 diagram 使用 inline SVG 或 HTML/CSS。不可載入 CDN、外部 script、外部 stylesheet、字型或 image。每個 candidate 都要有 before／after visualisation。

每個 candidate card 包含：

- **Files**：涉及檔案／module
- **Problem**：現有 architecture 為何造成 friction
- **Solution**：plain English 說明改變
- **Benefits**：以 locality、leverage 與測試改善解釋
- **Before / After diagram**：並排自繪，呈現 shallowness 與 deepening
- **Recommendation strength**：`Strong`、`Worth exploring` 或 `Speculative` badge

結尾加入 **Top recommendation**：最先處理哪個 candidate 與原因。

domain 以 `CONTEXT.md`，architecture 以 `$codebase-design` vocabulary 表達。若 `CONTEXT.md` 定義「Order」，寫「Order intake module」，不可寫「FooBarHandler」或「Order service」。

**ADR conflict**：只有 friction 真實到值得重開 ADR 時才呈現矛盾，且在 card 明確標記，例如：_「與 ADR-0007 矛盾，但值得重開，因為…」_。不可列出所有理論上被 ADR 排除的 refactor。

完整 scaffold、diagram pattern 與 style guidance 見 [HTML-REPORT.md](HTML-REPORT.md)。不可先提出 interface；檔案建立後詢問使用者：「你想先探索哪一個？」

### 3. Grilling loop

使用者選擇 candidate 後，執行 `$grilling` skill，依序釐清 constraint、dependency、deepened module 的 shape、seam 後的內容與存續測試。

決策逐漸清楚時立刻產生 side effect，執行 `$domain-modeling` skill 以維護 domain model：

- deepened module 使用 `CONTEXT.md` 尚無的 concept 命名時，加入 term；僅在需要時建立檔案。
- 對話中釐清模糊 term 時，立即更新 `CONTEXT.md`。
- 使用者以可承重的理由否決 candidate 時，可問：「要不要將此記為 ADR，避免未來 architecture review 再次提出？」只有理由能避免未來探索者重提同一項時才提供；「目前不值得」等短暫或顯而易見原因不提供。
- 想探索 deepened module 的 alternative interface 時，執行 `$codebase-design` skill，採用其 design-it-twice parallel sub-agent pattern。
