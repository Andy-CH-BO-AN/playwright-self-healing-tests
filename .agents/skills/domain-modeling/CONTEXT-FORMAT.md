# CONTEXT.md 格式

## 結構

```md
# {Context 名稱}

{此 context 是什麼、為何存在的一至兩句說明。}

## Language

**Order**：
{對此 term 的一至兩句說明}
_Avoid_: Purchase, transaction

**Invoice**：
交付後向 customer 發出的付款請求。
_Avoid_: Bill, payment request

**Customer**：
下 order 的人或 organization。
_Avoid_: Client, buyer, account
```

## 規則

- **明確取捨。**同一概念有多個詞時，選一個最佳詞，其餘放在 `_Avoid_`。
- **定義簡短。**最多一到兩句；定義它「是什麼」，不是「做什麼」。
- **只收錄專案 context 特有的 term。**timeout、error type、utility pattern 等一般 programming concept 即使常用也不屬於此處。新增前問：這是 context 專屬概念還是一般程式概念？只有前者可收錄。
- 自然形成 cluster 時，以 subheading 分組；若全部屬同一 cohesive area，flat list 即可。

## 單一與多 context repo

**單一 context（多數 repo）：**root 一份 `CONTEXT.md`。

**多 context：**root 的 `CONTEXT-MAP.md` 列出 context、位置與關係，例如：

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — 接收並追蹤 customer order
- [Billing](./src/billing/CONTEXT.md) — 建立 invoice 並處理 payment
- [Fulfillment](./src/fulfillment/CONTEXT.md) — 管理 warehouse picking 與 shipping

## Relationships

- **Ordering → Fulfillment**: Ordering 發出 `OrderPlaced` event；Fulfillment 消費它以開始 picking
- **Fulfillment → Billing**: Fulfillment 發出 `ShipmentDispatched` event；Billing 消費它以建立 invoice
- **Ordering ↔ Billing**: 共用 `CustomerId` 與 `Money` type
```

skill 判斷結構：有 `CONTEXT-MAP.md` 時先讀它定位 context；只有 root `CONTEXT.md` 時為單一 context；兩者皆無時，第一個 term 確定才延遲建立 root `CONTEXT.md`。多 context 時推論目前主題所屬 context；不清楚就提問。
