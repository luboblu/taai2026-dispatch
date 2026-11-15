---
name: deploy-check
description: 部署前後的檢查：確認沒有誤 commit data.json 或 .test/、已 pull 最新版，push 後用隨機參數網址確認 GitHub Pages 已上線。使用者說「部署」「推上線」「確認上線了嗎」時使用。
disable-model-invocation: true
---

依 AGENTS.md「協作規則」與「部署」。push 會公開內容，每次都要先讓統籌確認再執行。

**push 之前**

1. `git status -sb`、`git diff --stat origin/main...HEAD`：確認這次要推的 commit 只有程式與說明。
2. 確認變動清單裡**沒有** `data.json` 與 `.test/`。有的話停下來，告訴統籌。
3. `git pull --rebase` 取得最新的 `index.html`，有衝突就停下來回報，不要整檔覆蓋。
4. 確認 commit 訊息是繁體中文，寫清楚改了什麼。
5. 確認已跑過 `/preflight`，並完成 CLAUDE.md 要求的 Codex 唯讀審查（或統籌說這次不用）。

**push 之後**

1. 等約 1 分鐘（GitHub Pages 不需要建置）。
2. 挑一段這次新增的程式或文字當關鍵字，用隨機參數避開快取：

```bash
curl -s "https://luboblu.github.io/taai2026-dispatch/?cb=$RANDOM" | grep -c "<關鍵字>"
```

3. 結果大於 0 才算已上線；0 就再等一下重試，仍然是 0 要回報。
4. 回報時寫明：推了哪些 commit、關鍵字、檢查結果。
