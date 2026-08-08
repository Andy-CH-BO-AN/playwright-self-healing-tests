---
name: domain-modeling
description: 建立與精煉專案的 domain model。使用於釐清 domain terminology、ubiquitous language、記錄 architectural decision，或其他 skill 需維護 domain model 時。
---

# Domain Modeling

設計時主動建立並精煉 project domain model。這是主動的 discipline：挑戰詞彙、建立 edge-case scenario，並在詞義確定時立即寫下 glossary 與 decision。（僅讀取 `CONTEXT.md` 取得 vocabulary 不是此 skill；本 skill 用於改變 model，不只是使用它。）

## File structure

多數 repo 僅有單一 context：

```
/
├── CONTEXT.md
├── docs/adr/
└── src/
```

root 有 `CONTEXT-MAP.md` 時表示有多個 context；map 指向各自的 `CONTEXT.md` 與 `docs/adr/`，而 root `docs/adr/` 記錄 system-wide decision。

僅在有內容可寫時才建立檔案：第一個 term 確定時才建立 `CONTEXT.md`；第一份 ADR 需要時才建立對應 scope 的 `docs/adr/`。

## Session 中的行為

### 對照 glossary 挑戰用語

使用者用語與 `CONTEXT.md` 衝突時立刻指出，例如：「glossary 將 `cancellation` 定義為 X，但你現在似乎指 Y；哪一個才正確？」

### 釐清模糊語言

遇到含糊或一詞多義的詞，提出精確 canonical term，例如：「你說的 `account` 是 Customer 還是 User？兩者不同。」

### 討論具體 scenario

討論 domain relationship 時，建立能測試 edge case 的具體 scenario，迫使使用者清楚概念邊界。

### 與 code 交叉驗證

使用者陳述系統行為時，檢查 code 是否一致。發現矛盾時提出，例如：「code 會取消整筆 Order，但你說允許 partial cancellation；哪個正確？」

### 即時更新 CONTEXT.md

term 一確定立刻更新 `CONTEXT.md`，不可最後才批次整理；採用 [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md) 格式。`CONTEXT.md` 只能是 glossary，不含 implementation detail；不可把它當 spec、scratch pad 或 implementation decision 的儲存處。

### 謹慎提供 ADR

只有同時符合以下三項才可提供建立 ADR：

1. **難以逆轉**：日後改變主意的成本明顯。
2. **缺乏 context 會令人意外**：未來讀者會問「為什麼這樣做？」
3. **是真實取捨的結果**：存在合理 alternative，並基於特定理由選擇。

任一不符合就略過 ADR。採用 [ADR-FORMAT.md](./ADR-FORMAT.md) 格式。

先決定 ADR scope：有 `CONTEXT-MAP.md` 時，context-specific decision 寫入該 bounded context 的 `docs/adr/`；只有跨 context 或 system-wide decision 才寫入 root `docs/adr/`。單一 context repo 則使用 root `docs/adr/`。
