# Design It Twice

使用者要為 chosen deepening candidate 探索 alternative interface 時，採用此 parallel sub-agent pattern。源自 Ousterhout 的「Design It Twice」：第一個想法通常不是最佳解。使用 [SKILL.md](SKILL.md) 的 **module**、**interface**、**seam**、**adapter**、**leverage** vocabulary。

## 流程

### 1. 說明 problem space

spawn sub-agent 前先面向使用者說明：新 interface 必須滿足的 constraint、所依賴的 dependency 與其 [DEEPENING.md](DEEPENING.md) category，以及僅用來具體化 constraint 的 rough code sketch（不是 proposal）。展示後立即進入步驟 2，讓使用者在 agent 並行工作時閱讀思考。

### 2. Spawn sub-agent

並行 spawn 3 個以上 sub-agent；每個必須提出**根本不同**的 deepened module interface。每個 agent 接收獨立 technical brief：file path、coupling detail、dependency category、seam 後內容，以及 `SKILL.md`／`CONTEXT.md` vocabulary。給予不同 constraint：

- Agent 1：最小 interface，目標僅 1–3 entry point，最大化每個 entry point 的 leverage。
- Agent 2：最大 flexibility，支援多種 use case 與 extension。
- Agent 3：為最常見 caller 最佳化，讓 default case 極為簡單。
- Agent 4（適用時）：以 ports & adapters 設計 cross-seam dependency。

每個 agent 輸出：

1. Interface（type、method、parameter、invariant、ordering、error mode）
2. caller usage example
3. implementation 在 seam 後隱藏什麼
4. dependency strategy 與 adapter
5. trade-off：何處 leverage 高、何處薄弱

### 3. 呈現與比較

依序呈現 design 以便使用者吸收，再以 prose 比較 **depth**（interface leverage）、**locality**（change 集中處）與 **seam placement**。最後給出明確建議：哪個最強及原因；若不同 design 的元素可結合，提出 hybrid。使用者需要強而有力的判斷，不是選單。
