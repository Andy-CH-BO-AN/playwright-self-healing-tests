# HTML Report 格式

Architecture review 為單一 self-contained HTML，寫入 OS temporary directory。Tailwind 與 Mermaid 皆由 CDN 載入。Mermaid 適合 graph-shaped diagram；手工 div 與 inline SVG 適合 mass diagram、cross-section 等 editorial visual。兩者混用，避免所有 diagram 都長得一樣。

## Scaffold

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="utf-8" />
    <title>Architecture review — {{repo name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* Tailwind 無法清楚處理的少量自訂樣式：dashed seam、手繪感 arrow head 等。 */
      .seam { stroke-dasharray: 4 4; }
      .leak { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## Header

顯示 repo name、date 與簡短 legend：實線 box = module、虛線 = seam、red arrow = leakage、粗 dark box = deep module。不要 introduction paragraph，直接進入 candidate。

## Candidate card

Diagram 承擔主要說明，prose 簡短、直白，並自然使用 `/codebase-design` glossary。

每個 candidate 為一個 `<article>`：

- **Title**：短標題，說明 deepening，例如「收斂 Order intake pipeline」。
- **Badge row**：recommendation strength（`強烈建議` = emerald、`值得探索` = amber、`推測性` = slate）與 dependency category tag（`in-process`、`local-substitutable`、`ports & adapters`、`mock`）。
- **Files**：以 `font-mono text-sm` 顯示的 file list。
- **Before / After diagram**：核心內容，兩欄並排；使用下列 pattern。
- **Problem**：一句，描述問題。
- **Solution**：一句，描述變更。
- **Wins**：bullet，每項最多六個詞，例如「Test 只跨一個 interface」、「Pricing 不再跨 seam 泄漏」、「刪除 4 個 shallow wrapper」。
- **ADR callout**：適用時以 amber-tinted box 顯示一行。

不可寫冗長說明 paragraph。若 diagram 需靠 paragraph 才能理解，重畫 diagram。

## Diagram pattern

選擇最符合 candidate 的 pattern，可混用，不要讓每張圖看起來相同。

### Mermaid graph

dependency／call flow 適合 `flowchart` 或 `graph`，用於說明「X 呼叫 Y 呼叫 Z，結構混亂」。放在 Tailwind card 中，避免突兀；用 classDef 讓 leakage edge 為 red、deep module 為 dark。sequence diagram 適合呈現「before 6 round-trip；after 1」。

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.leak.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

### 手工 boxes-and-arrows

Mermaid layout 不適合時，以有 border 與 label 的 `<div>` 表示 module，以 inline SVG `<line>` 或 `<path>` 絕對定位 arrow。after diagram 要呈現厚邊框 deep module、內部 faded module 時特別適用。

### Cross-section

以水平 band（`h-12 border-l-4`）呈現 layered shallowness。before 顯示六層各自幾乎不做事；after 以一條 thick band 標示收斂後責任。

### Mass diagram

每個 module 用兩個 rectangle：interface surface area 與 implementation。before：interface 幾乎同高，表現 shallow；after：interface 短、implementation 高，表現 deep。

### Call-graph collapse

before 用 nested box 呈現 function call tree；after 收斂為一個 box，原本 internal call 在其中淡化顯示。

## Style guidance

- 偏 editorial，不要 corporate dashboard；保留大量 whitespace；heading 可使用 serif（`font-serif`）。
- 色彩節制：一個 accent（emerald 或 indigo），red 僅代表 leakage，amber 僅代表 warning。
- diagram 約 320px 高，讓 before／after 可舒適並排。
- module label 用 `text-xs uppercase tracking-wider`，呈現 schematic 而非 application UI。
- 僅允許 Tailwind CDN 與 Mermaid ESM import；report 其餘內容必須 static，不加 app code 或 interactivity（Mermaid 本身除外）。

## Top recommendation

一張較大的 card：candidate name、為何優先的一句話、連至其 card 的 anchor link。僅此而已。

## 語氣與詞彙

使用繁體中文、簡潔表達；architecture noun 與 verb 必須來自 `/codebase-design` skill。簡潔不代表可偏離 glossary。

必須精確使用：module、interface、implementation、depth、deep、shallow、seam、adapter、leverage、locality。

不可替換：component、service、unit（指 module 時）、API、signature（指 interface 時）、boundary（指 seam 時）、layer／wrapper（實指 module 時）。

合適說法：

- 「Order intake module 是 shallow，interface 幾乎等同 implementation。」
- 「Pricing 跨 seam 泄漏。」
- 「深化：一個 interface，一個測試位置。」
- 「兩個 adapter 證明 seam：production 用 HTTP，test 用 in-memory。」

Wins bullet 應命名 glossary gain，例如「locality：bug 集中於一個 module」、「leverage：一個 interface，N 個 call site」、「interface 縮小；implementation 吸收 wrapper」。不可寫「更容易維護」或「更乾淨的 code」等沒有 glossary 價值的詞。

不要 hedging、throat-clearing 或「值得注意的是」。句子可成為 bullet 就改為 bullet；bullet 可刪就刪；沒有 `/codebase-design` glossary 的詞時，優先使用其中既有詞，而不是新造詞。
