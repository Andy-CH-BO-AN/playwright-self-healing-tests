# UI Automation Engineering Rules

本文件定義本 repository 的 UI automation engineering rules。所有新增或修改 UI automation 的 engineer／agent 都必須遵守。

目標不是讓 testcase 永遠變綠，而是：**可靠模擬真實使用者行為，並在產品行為改變時提供可信、容易診斷的 failure signal。**

## Locator Strategy

Locator 優先使用使用者可感知的語意或穩定 test contract：

1. role
2. label
3. accessible name
4. visible text
5. stable explicit test identifier

避免 brittle XPath、deep CSS hierarchy、generated class name、DOM position-based selector 與 dynamic implementation-specific selector。除非有明確理由，不要使用與 DOM implementation 高度耦合的 locator。

Locator 不應大量散落在 testcase。重複或有 domain meaning 的 locator 應集中在適當的 page／component abstraction；但不要為了集中 locator 建立沒有實際用途的巨大 Page Object。

## Page & Component Objects

Page Object／Component Object 用來集中 locator、隱藏重複的 UI interaction detail、提供有 domain meaning 的操作，並讓 testcase 保留 business intent。

- 不要建立巨大的 `BasePage`。
- 不要將每個 framework API 再包裝一層，例如沒有額外語意的 `custom_click()`、`custom_fill()`、`custom_get_text()`、`custom_wait()`。
- 原生 framework API 已清楚時直接使用；只有 interaction 被多處使用，或 abstraction 確實降低 duplication／maintenance cost 時才建立 abstraction。
- 主要 business outcome assertion 留在 testcase，不要全部藏進 Page Object。

## Interaction & Synchronization

優先使用真實使用者可執行的 framework 原生 interaction：`click`、`fill`、`keyboard`、`select`、`hover`、`drag`、dialog handling 與 navigation。

不要用 JavaScript 強制修改 DOM 來讓 testcase 通過；避免 JavaScript force click、任意移除 overlay、直接 enable disabled element、修改 DOM state 與無理由的 force interaction。element 被遮住、disabled、不可見或不可操作時，先判斷是否為真實 product state。

禁止使用固定 sleep 作為一般 synchronization strategy，例如 `time.sleep(...)`。等待應基於 observable state：framework auto-waiting、locator expectation、UI state 或 relevant navigation state。等待的是「狀態」，不是「時間」。

不要以任意增加 timeout 或 retry count 掩蓋 synchronization 問題。

## State Isolation & Parallel Safety

Testcase 原則上必須可獨立執行。不可依賴 testcase execution order、shared Page、shared mutable BrowserContext、前一個 testcase 的 state，或 shared cart／session state。

注意可能污染 testcase 的 cookies、localStorage、sessionStorage、authentication state、shopping cart 與 feature state。共用 authentication／storage state 只有在不破壞 test independence 時才使用。

即使目前沒有 parallel execution，architecture 也不應阻礙未來 parallel。真正加入 parallel 時，重新檢查 test data、account、backend state、external resource 的 collision 與 rate limits；不同 BrowserContext 不代表 backend state 已完全隔離。

## UI Assertions & Test Flow

Testcase 優先驗證使用者可觀察的 business outcome，不要只驗證 click 沒 exception、URL changed、element exists 或 page loaded。依情境驗證正確頁面與資料、cart／transaction state、validation result、state transition 與完整 user outcome。

避免 assertion 過度依賴 DOM hierarchy、CSS class、frontend internal state 與 implementation detail。E2E testcase 必須維持 business readability，讓 reviewer 能清楚看出：`prerequisite → user action → observable outcome`。

不要把 testcase 寫成一長串 locator script。完整 user flow 可自然驗證多個重要 integration point 時可以保留；若 flow 過長而明顯傷害 failure localization、state coupling 或 maintenance cost，合理拆分。

## Failure Diagnostics

UI failure 至少保留足以進行 root cause analysis 的 evidence，優先為 traceback、screenshot 與 browser trace；需要時加入 console logs、network errors、current URL、relevant page state 或 video。

高成本 artifact 優先只在 failure 時保留，不要為 passing tests 無條件產生大量 screenshot、trace 或 video。evidence 應協助區分 product regression、locator regression、synchronization issue、test bug、environment issue 與 flaky behavior。

Retry-pass 仍是需要注意的 signal，不可直接視為正常穩定 PASS。不要以 retry、timeout 或 force interaction 掩蓋 flaky root cause。

## Core Anti-Patterns

避免 fixed sleep、brittle XPath、deep CSS selector、unjustified force click、JavaScript bypass UI behavior、testcase execution-order dependency、shared mutable browser state、giant `BasePage`、wrapper around every framework API、duplicated locator、retry masking flaky behavior、excessive timeout，以及只檢查 navigation 的 assertion。

每個 abstraction、wait、retry、fixture 與 helper 都必須有明確工程理由。
