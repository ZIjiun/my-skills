# my-skills

個人用的 Claude skill。一個資料夾一個 skill。

| Skill | 用途 |
|---|---|
| [coworker-reply-coach](./coworker-reply-coach/SKILL.md) | 回覆同事訊息的教練：判斷狀況、承接情緒、給草稿並說明原因 |
| [video-to-notes](./video-to-notes/SKILL.md) | 把 YouTube、Bilibili、本地影片整理成附截圖與時間戳的繁中筆記，寫進 Notion；要的話另外輸出 PDF 講義 |

每個 skill 資料夾裡：

- `SKILL.md`：skill 本體
- `CHANGELOG.md`：更新紀錄
- `upstream-sources.json`：改寫自哪些別人的 skill，以及最後檢視過的版本（有參考來源才有）
- 其他檔案：範本、參考資料、腳本等（視 skill 而定）

各 skill 的授權以資料夾內的 LICENSE 為準（例如 video-to-notes 因改寫自 GPL-3.0 的作品，同樣是 GPL-3.0）。

安裝到 Claude 的 zip 會另外多一個 `skill-source.json`，記錄它對應這個 repo 的哪個版本。
