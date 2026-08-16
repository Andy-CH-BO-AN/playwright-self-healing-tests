# 專案協作規範

## 先思考，再動手

- 明確說出假設、未知與取捨；有多種合理解讀時，先列出差異，不可暗中選擇。
- 有更簡單的方案時應提出；需求或限制不清楚且可能影響結果時，先說明卡點並提問。

## 簡單與最小變更

- 只實作本次需求，不加入推測性的功能、可配置性、抽象或不可能情境的防禦處理。
- 變更必須可直接追溯至需求。保留既有風格；不順便重構、格式化或移除既有無關死碼。
- 只移除由本次變更造成的未使用項目。

## 目標導向執行

- 先將需求轉成可驗證的成功條件；多步任務先列出簡短步驟與各步驗證方式。
- 修 bug 先建立可重現案例；重構前後皆驗證相關測試。
- 完成前執行適當的 formatter、lint、受影響測試與必要回歸，並自行檢視 diff。

## UI 自動化

新增或修改 UI automation 時，必須遵守 [UI Automation Engineering Rules](docs/ai/ui-automation-engineering-rules.md)。核心目標是忠實模擬使用者行為，並在產品變更時產生可靠、易診斷的 failure signal。

## 專責 Agents

- `reviewer`：唯讀審查 correctness、風險與測試缺口。
- `test-architect`：唯讀設計以風險為本、成本最低的測試策略；不實作 automation。
- `senior-sdet`：設計與實作可靠、可維護的 test automation。

定義檔位於 `ai/agents/`，並由 `.codex/agents/` 與 `.agents/agents/` 連結共用。需要上述專長時，使用相對應的 custom agent。所有對使用者的敘述、文件與說明預設採繁體中文；程式碼、CLI、專有名詞與既有必要字串除外。

## Repository Skills

本專案共用 skills 位於 `.agents/skills/`，由 Codex 自動掃描。clone 或 pull 後重新啟動 Codex，即可在任何電腦使用相同 skill；不可將此專案專用 skill 安裝至使用者層級目錄。
