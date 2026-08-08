---
name: handoff
description: 將目前對話濃縮為可供下一位 agent 接手的交接文件。
---

撰寫交接文件，摘要目前對話，讓新的 agent 能繼續工作。儲存至使用者 OS 的 temporary directory，不可寫入目前 workspace。

文件須包含「建議 skills」區段，列出下一位 agent 應使用的 skills。

不得重複已存在於其他 artifact 的內容（spec、plan、ADR、issue、commit、diff）；改以 path 或 URL 參照。

遮蔽敏感資訊，例如 API key、password 與 personally identifiable information。

若使用者傳入 argument，視為下一個 session 的重點並據此調整文件。
