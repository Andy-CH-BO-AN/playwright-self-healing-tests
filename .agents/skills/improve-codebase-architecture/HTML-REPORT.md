# 離線 HTML Report 格式

Architecture review 是寫入 OS temporary directory 的單一 self-contained HTML。它必須在沒有 network、CDN、外部 script、external stylesheet、external font 或 image 的情況下可完整開啟與閱讀。所有 CSS 寫入 `<style>`；所有 diagram 使用 inline SVG 或 HTML/CSS；不可使用 Mermaid。

## Scaffold

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Architecture review — {{repo name}}</title>
    <style>
      :root { color: #172033; background: #f8fafc; font-family: system-ui, sans-serif; }
      body { margin: 0; }
      main { max-width: 1080px; margin: 0 auto; padding: 48px 24px; }
      .stack { display: grid; gap: 28px; }
      .card { padding: 24px; border: 1px solid #dbe3ef; border-radius: 12px; background: #fff; }
      .meta { color: #526074; font: 13px ui-monospace, monospace; }
      .badge { display: inline-block; padding: 3px 9px; border-radius: 999px; font-size: 12px; font-weight: 700; }
      .strong { color: #065f46; background: #d1fae5; }
      .explore { color: #92400e; background: #fef3c7; }
      .speculative { color: #475569; background: #e2e8f0; }
      .comparison { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
      .diagram { min-height: 300px; padding: 16px; border: 1px solid #dbe3ef; border-radius: 8px; background: #f8fafc; }
      .diagram svg { display: block; width: 100%; height: 280px; }
      .warning { padding: 12px; border-radius: 8px; color: #92400e; background: #fffbeb; }
      @media (max-width: 720px) { .comparison { grid-template-columns: 1fr; } }
    </style>
  </head>
  <body>
    <main class="stack">
      <header>...</header>
      <section id="candidates" class="stack">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## Header

顯示 repo name、date 與簡短 legend：實線 box = module、虛線 = seam、red arrow = leakage、粗 dark box = deep module。不要 introduction paragraph，直接進入 candidate。

## Candidate card

Diagram 承擔主要說明，prose 簡短、直白，並自然使用 `/codebase-design` glossary。每個 candidate 為一個 `<article class="card">`，包含：

- **Title**：短標題，說明 deepening，例如「收斂 Order intake pipeline」。
- **Badge row**：recommendation strength（`強烈建議` = emerald、`值得探索` = amber、`推測性` = slate）與 dependency category tag（`in-process`、`local-substitutable`、`ports & adapters`、`mock`）。
- **Files**：以 `.meta` 顯示的 file list。
- **Before / After diagram**：核心內容，以 `.comparison` 兩欄並排。
- **Problem**、**Solution**：各一句。
- **Wins**：bullet，每項最多六個詞。
- **ADR callout**：適用時以 `.warning` 顯示一行。

不可寫冗長說明 paragraph。若 diagram 需靠 paragraph 才能理解，重畫 diagram。

## Diagram pattern

只使用不需 JavaScript 的 inline SVG 或 HTML/CSS，選擇最符合 candidate 的 pattern，可混用。

### Dependency／call flow

以 inline SVG 的 `<rect>` 表示 module、`<line>` 或 `<path>` 表示 dependency。所有 marker、arrowhead、label 與 style 都定義在同一個 `<svg>` 裡。seam 使用 `stroke-dasharray="5 5"`，leakage 使用 `stroke="#dc2626"`。例如：

```html
<svg viewBox="0 0 520 280" role="img" aria-label="Order intake dependency flow">
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#475569" />
    </marker>
  </defs>
  <rect x="24" y="108" width="120" height="56" rx="8" fill="#fff" stroke="#475569" />
  <text x="84" y="140" text-anchor="middle">OrderHandler</text>
  <rect x="200" y="108" width="120" height="56" rx="8" fill="#fff" stroke="#475569" />
  <text x="260" y="140" text-anchor="middle">OrderRepo</text>
  <rect x="376" y="108" width="120" height="56" rx="8" fill="#fff" stroke="#dc2626" />
  <text x="436" y="140" text-anchor="middle">PricingClient</text>
  <line x1="144" y1="136" x2="200" y2="136" stroke="#475569" marker-end="url(#arrow)" />
  <line x1="320" y1="136" x2="376" y2="136" stroke="#dc2626" marker-end="url(#arrow)" />
</svg>
```

### Cross-section

以一組 inline SVG `<rect>` 堆疊 band 表示 layered shallowness。before 顯示多個 thin band；after 使用一條標示收斂責任的 thick band。

### Mass diagram

以兩個 SVG rectangle 表示每個 module 的 interface surface area 與 implementation。before 讓 interface 與 implementation 幾乎同高；after 讓 interface 短、implementation 高。

### Call-graph collapse

before 以 nested SVG box 呈現 function call tree；after 以一個粗邊框 box 包含 faded internal call。不要使用 JavaScript animation。

## Style guidance

- 偏 editorial，不要 corporate dashboard；保留大量 whitespace；採用 system font，不下載 font。
- 色彩節制：一個 accent（emerald 或 indigo），red 僅代表 leakage，amber 僅代表 warning。
- diagram 約 320px 高，讓 before／after 可舒適並排。
- module label 需清晰、可在 SVG 直接閱讀。
- HTML 必須無 network request；不得加入 `<script src>`、`<link href>`、`@import` 或 remote image URL。

## Top recommendation

一張較大的 card：candidate name、為何優先的一句話、連至其 card 的 anchor link。僅此而已。

## 語氣與詞彙

使用繁體中文、簡潔表達；architecture noun 與 verb 必須來自 `/codebase-design` skill。必須精確使用：module、interface、implementation、depth、deep、shallow、seam、adapter、leverage、locality。

不可替換：component、service、unit（指 module 時）、API、signature（指 interface 時）、boundary（指 seam 時）、layer／wrapper（實指 module 時）。

合適說法：

- 「Order intake module 是 shallow，interface 幾乎等同 implementation。」
- 「Pricing 跨 seam 泄漏。」
- 「深化：一個 interface，一個測試位置。」
- 「兩個 adapter 證明 seam：production 用 HTTP，test 用 in-memory。」

Wins bullet 應命名 glossary gain，例如「locality：bug 集中於一個 module」、「leverage：一個 interface，N 個 call site」、「interface 縮小；implementation 吸收 wrapper」。不可寫「更容易維護」或「更乾淨的 code」等沒有 glossary 價值的詞。

不要 hedging、throat-clearing 或「值得注意的是」。句子可成為 bullet 就改為 bullet；bullet 可刪就刪；沒有 `/codebase-design` glossary 的詞時，優先使用其中既有詞，而不是新造詞。
