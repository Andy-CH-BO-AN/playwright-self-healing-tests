# Deepening

在考慮 dependency 的前提下，安全地深化 shallow module cluster。假設已使用 [SKILL.md](SKILL.md) 的 **module**、**interface**、**seam**、**adapter** vocabulary。

## Dependency category

評估 deepening candidate 時先分類 dependency；分類決定 deepened module 如何跨 seam 測試。

1. **In-process**：pure computation、in-memory state、無 I/O。永遠可深化：合併 module，直接透過新 interface 測試，不需 adapter。
2. **Local-substitutable**：有 local test stand-in 的 dependency（例如 Postgres 的 PGLite、in-memory filesystem）。有 stand-in 才能深化；test suite 以 stand-in 測 deepened module。seam 為 internal，不在 module external interface 建 port。
3. **Remote but owned（Ports & Adapters）**：跨 network boundary 的自有 service（microservice、internal API）。在 seam 定義 **port**（interface）；deep module 擁有 logic，transport 為 injected **adapter**。test 使用 in-memory adapter，production 使用 HTTP／gRPC／queue adapter。建議：在 seam 定義 port，以 production HTTP adapter 和 test in-memory adapter，使 logic 即使跨網路仍集中於一個 deep module。
4. **True external（Mock）**：不受控制的 third-party service（Stripe、Twilio 等）。deepened module 接受 external dependency 的 injected port；test 提供 mock adapter。

## Seam discipline

- **一個 adapter 是 hypothetical seam，兩個 adapter 才是 real seam。**至少需要兩個合理 adapter（通常 production＋test）才引入 port；single-adapter seam 只是 indirection。
- **Internal 與 external seam。**deep module 可有僅供自身 test 的 internal seam，以及 interface 的 external seam；不可因 test 使用 internal seam 就把它 expose 到 interface。

## Testing strategy：replace，不要 layer

- deepened module interface 的 test 建立後，舊 shallow module unit test 會成為 waste，刪除它們。
- 在 deepened module interface 寫新 test；**interface 是 test surface**。
- test 透過 interface assert observable outcome，不檢查 internal state。
- test 應能存活於 internal refactor；它描述 behavior，而非 implementation。implementation 改變就需修改的 test，代表測過了 interface。
