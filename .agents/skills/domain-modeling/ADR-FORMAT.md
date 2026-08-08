# ADR 格式

ADR 位於 `docs/adr/`，採連續編號：`0001-slug.md`、`0002-slug.md`。僅在第一份 ADR 需要時才建立目錄。

## Template

```md
# {決策的短標題}

{1–3 句：context 是什麼、決定了什麼、為什麼。}
```

到此為止。ADR 可以只是一段；價值在記錄「做了哪個 decision」與「原因」，不是填滿 section。

## Optional sections

僅在確有價值時才加入，多數 ADR 不需要：

- **Status** frontmatter（`proposed | accepted | deprecated | superseded by ADR-NNNN`）：decision 重審時有用。
- **Considered Options**：僅在被拒絕 alternatives 值得保留時使用。
- **Consequences**：僅在有不明顯 downstream effect 時使用。

## 編號

掃描 `docs/adr/` 既有最高編號後加一。

## 何時提供 ADR

必須同時滿足：難以逆轉、沒有 context 會令人意外、且基於真實 trade-off。容易逆轉就直接改；不令人意外就不會有人問；沒有 real alternative 就不必記錄顯而易見的選擇。

合格例子：architecture shape、context 間的 integration pattern、具有 lock-in 的 technology choice、boundary／scope decision、刻意偏離通常作法、code 無法看出的 constraint，以及不明顯的 rejected alternative。
