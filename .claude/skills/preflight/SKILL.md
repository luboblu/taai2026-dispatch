---
name: preflight
description: 修改 index.html 後、上線前的檢查：啟動本機 mock 伺服器，逐頁、逐寬度確認沒有 JS 錯誤與左右捲動，並檢查列印版面。使用者說「跑 preflight」「上線前檢查」「測試一下」時使用。
---

依 AGENTS.md「測試」一節，在 repo 根目錄執行。不要用真的 GitHub token。

1. **語法檢查**：對 index.html 內嵌的 `<script>` 跑 `node --check`（`.claude/hooks/check-index.py` 的邏輯，也可以直接對剛改的檔案觸發）。
2. **啟動 mock 伺服器**：`python3 tools/mock_server.py`，用 `run_in_background` 執行。它會把 index.html 與 data.json 複製到 `.test/`，repo 內的檔案不會被改到。
3. **用內建瀏覽器開** `http://127.0.0.1:8791/index.html`，按「統籌登入」輸入假 token `good-token`。
4. **逐頁檢查**：`#overview`、`#board`、`#jobs`、`#todo`、`#people`、`#notes`、`#agenda`，以及至少一個 `#room-<區域>`。每頁用 `read_console_messages`（onlyErrors）確認沒有 JS 錯誤。
5. **逐寬度檢查**：用 `resize_window` 測 1320、990、770、375px，各搭配字級小／中／大（右上角「Aa」）。用 `javascript_tool` 確認 `document.documentElement.scrollWidth <= window.innerWidth`，也就是沒有左右捲動。測完用 preset `desktop` 還原視窗。
6. **列印版面**：現場總表每天 1 頁，待辦 1 頁（可參考 `.test/` 內既有的列印輸出，或用 `print-d1.html` 這類頁面）。
7. **動到資料格式時**：用舊版 index.html（`git show HEAD:index.html`）讀新資料，畫面不可亂碼；用新版讀舊資料，不可顯示「尚未發布」。並確認 `TAAI.publishable()` 的輸出沒有 `privateNoteList` 與人員的 `contact`。
8. **收尾**：用 `/__quit` 關閉伺服器，回報每一項的結果。沒測的項目要明講，不要只說「通過」。

完成後提醒：上線前依 CLAUDE.md 還要請 Codex 做唯讀審查。
