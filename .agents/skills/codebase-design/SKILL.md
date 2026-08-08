---
name: codebase-design
description: 設計 deep module 的共通 vocabulary。使用於設計或改善 module interface、尋找 deepening opportunity、決定 seam、提升 testability／AI-navigability，或其他 skill 需要 deep-module vocabulary 時。
---

# Codebase Design

設計 **deep module**：用小 interface 隱藏大量 behavior，放在乾淨 seam，並能透過該 interface 測試。所有設計／重構都應使用以下語言與原則。目標是為 caller 提供 leverage、為 maintainer 提供 locality、並提升所有人的 testability。

## Glossary

必須精確使用這些詞，不可替換為「component」、「service」、「API」或「boundary」。一致 vocabulary 是核心。

- **Module**：任何具有 interface 與 implementation 的事物；刻意不限制尺度，可為 function、class、package 或跨 tier slice。_Avoid_: unit, component, service。
- **Interface**：caller 正確使用 module 所需知道的一切：type signature、invariant、ordering constraint、error mode、required configuration、performance characteristic。_Avoid_: API、signature（過窄，僅指 type-level surface）。
- **Implementation**：module 內部的 code body。不同於 **Adapter**：事物可以是小 adapter 配大 implementation（Postgres repo），或大 adapter 配小 implementation（in-memory fake）。seam 是主題時用 adapter，否則用 implementation。
- **Depth**：interface 所帶來的 leverage；caller／test 每學習一單位 interface 能運用多少 behavior。大量 behavior 藏在小 interface 後為 **deep**；interface 幾乎與 implementation 一樣複雜為 **shallow**。
- **Seam**（Michael Feathers）：可在不修改該處的情況下改變 behavior 的位置，也就是 module interface 所在位置。seam 放置位置是獨立設計決策，不等於其背後內容。_Avoid_: boundary（與 DDD bounded context 意義重疊）。
- **Adapter**：在 seam 滿足 interface 的 concrete thing。描述 role（填補哪個 slot），不是內部 substance。
- **Leverage**：depth 帶給 caller 的收益；每單位要學習的 interface 提供更多 capability。一份 implementation 回饋 N 個 call site 與 M 個 test。
- **Locality**：depth 帶給 maintainer 的收益；change、bug、knowledge、verification 集中一處，而不分散至 callers。修一次，全部修正。

## Deep 與 shallow

**Deep module** 是小 interface 加大量 implementation；**shallow module** 則是大 interface 加少量 implementation，應避免。設計 interface 時問：能否減少 method？能否簡化 parameter？能否在內部隱藏更多 complexity？

## 原則

- **Depth 是 interface 的屬性，不是 implementation。**deep module 可在內部由小、可 mock、可替換 parts 組成；它們不屬於 interface。module 可有供自身 test 使用的 internal seam，以及 interface 上的 external seam。
- **Deletion test。**想像刪除 module。complexity 消失代表它是 pass-through；若 complexity 在 N 個 caller 重現，代表它有價值。
- **Interface 是 test surface。**caller 與 test 跨越相同 seam。若要測到 interface 之後，module 的 shape 多半不對。
- **一個 adapter 是 hypothetical seam，兩個 adapter 才是 real seam。**沒有真正變異時不可引入 seam。

## 為 testability 設計

1. 接受 dependency，不在內部建立 dependency。
2. 回傳 result，不只產生 side effect。
3. 小 surface area：method 越少，test 越少；parameter 越少，setup 越簡單。

## 關係

Module 只有一個提供給 caller 與 test 的 Interface；Depth 由 Module 相對於 Interface 衡量；Seam 是 Interface 所在；Adapter 位於 Seam 並滿足 Interface；Depth 產生 caller 的 Leverage 與 maintainer 的 Locality。

## 不採用的 framing

- 不將 depth 視為 implementation line 與 interface line 比率（Ousterhout）：會鼓勵灌水 implementation；採 depth-as-leverage。
- 不將 Interface 侷限於 TypeScript `interface` keyword 或 class public method：它也包括 caller 必須知道的所有事實。
- 不說「Boundary」：它與 DDD bounded context 意義重疊；使用 **seam** 或 **interface**。

## 延伸閱讀

- 依 dependency 深化 shallow module cluster：見 [DEEPENING.md](DEEPENING.md)。
- 探索 alternative interface：見 [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md)。
