# caveman

像聰明穴居人一樣說話：思考力不變，文字更少。

## 功能

將每次 model response 壓縮成穴居人式 prose。刪除 article、filler、客套語與 hedging；保留每個 technical detail、code block、error string 與 symbol。實測可減少 65% output token，並保持完整正確性。此 mode 會持續整個 session，直到切換或停止。

六種強度：

| Level | 改變 |
|---|---|
| `lite` | 刪除 filler／hedging，保留完整句子與專業感。 |
| `full` | 預設；刪除 article，可用片語與短同義詞。 |
| `ultra` | 極短片語；不可用自創 abbreviation 或 causal arrow。 |
| `wenyan-lite` | 輕度文言 register。 |
| `wenyan-full` | 最大文言化，可減少 80–90% character。 |
| `wenyan-ultra` | 極端文言壓縮。 |

Auto-clarity rule：遇到 security warning、irreversible-action confirmation、可能造成歧義的 multi-step sequence 或使用者重複提問時，改用一般 prose；清楚部分結束後恢復。

## 呼叫方式

```text
$caveman              # full（預設）
$caveman lite         # 較輕壓縮
$caveman ultra        # 極端壓縮
$caveman wenyan-full  # 文言模式
$caveman off          # 回到一般模式
```

## 輸出範例

問題：`Why does my React component re-render?`

一般 prose：

> Your component re-renders because you create a new object reference each render. Wrapping it in `useMemo` will fix the issue.

caveman（full）：

> New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`.

caveman（ultra）：

> Inline obj prop, new ref, re-render. `useMemo`.

## 參考

- [`SKILL.md`](./SKILL.md)：完整 LLM-facing instruction。
- [Repository README](../../../README.md)：repository overview。
