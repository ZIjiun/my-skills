# my-skills

個人用的 Claude skill。一個資料夾一個 skill。

| Skill | 用途 |
|---|---|
| [coworker-reply-coach](./coworker-reply-coach/SKILL.md) | 回覆同事訊息的教練：判斷狀況、承接情緒、給草稿並說明原因 |

每個 skill 資料夾裡：

- `SKILL.md`：skill 本體
- `CHANGELOG.md`：更新紀錄
- `upstream-sources.json`：改寫自哪些別人的 skill，以及最後檢視過的版本（有參考來源才有）

安裝到 Claude 的 zip 會另外多一個 `skill-source.json`，記錄它對應這個 repo 的哪個版本。
