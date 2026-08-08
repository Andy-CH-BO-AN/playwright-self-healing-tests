---
name: grilling
description: 以密集提問檢驗使用者的計畫、決策或想法。使用者想壓力測試思考或使用任何「grill」觸發語時使用。
---

持續訪談使用者直到取得共同理解。將其整理為**設計樹**：每個決策都分支為依賴它的後續決策。

以**回合**處理設計樹。**frontier** 是所有前置條件已確認、可立即提問而不用猜測答案的決策。每回合詢問完整 frontier：為每題編號並給出建議答案；再等待使用者回答後才進入下一回合。

每題採用以下格式：

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

每回合的回答會重塑設計樹：已確定的決策向外推進 frontier，並解除相依問題。重新計算 frontier 後提出下一回合。若答案取決於本回合仍未解決的另一題，該題屬於後續回合，不可同回合提出。

查找**事實**是你的工作，不是使用者的責任。frontier 問題需要環境事實（filesystem、tool 等）時，派 sub-agent 查找；不可詢問你可自行查到的內容。不可因此阻塞：執行中的探索仍是未解決的前置條件，只有其下游問題等待 sub-agent 回報，其餘 frontier 立即提問。**決策**屬於使用者，提出每項決策後等待回答。

frontier 為空時 session 才完成：設計樹每個分支皆已檢視，不留下暗中假設。使用者確認已取得共同理解前，不得執行該方案。
