請先讀完並遵守共同規則：@AGENTS.md

（AGENTS.md 是給 Codex 和 Claude Code 共用的說明，有改規則請改在那份。以下只寫 Claude Code 的做法。）

## 在 Claude Code 裡和 Codex 一起改

統籌直接在 Claude Code 提出修改時，由 Claude 主導，並用這台電腦上的 Codex CLI（`codex`，已登入統籌的 ChatGPT 帳號）協助。

1. **一般修改由 Claude 自己改、自己測。**
2. **上線前一律請 Codex 做唯讀審查。** 用唯讀沙盒（`-s read-only`），Codex 不能改任何檔案：

   ```bash
   codex exec -s read-only -o .test/codex-review.txt "你是程式審查者，只能讀、不能改任何檔案。請用 git diff（或 git show <sha>）看對 index.html 的修改，並依 AGENTS.md 的規則審查。用繁體中文回覆：只列出真正會造成資料錯誤、遺失、畫面壞掉或違反 AGENTS.md 的問題，每點附上函式名稱或行號與理由；沒有問題就直接說沒有。不要列風格建議。" < /dev/null > .test/codex-run.log 2>&1
   ```

   - 審查結果在 `.test/codex-review.txt`。
   - `codex review --uncommitted` 或 `--commit <sha>` 也可以用，但這兩個參數不能再加自訂指示，回覆會是英文。
3. **逐條確認 Codex 的意見。** Codex 的意見要自己讀程式或實際測試確認，真的有問題才修。回報給統籌時，要說明哪些採用、哪些不採用，以及原因。
4. **大量、重複性的修改可以交給 Codex 實作**，例如同一種改動要套到很多地方：

   ```bash
   codex exec -s workspace-write "…"
   ```

   - 交給 Codex 時，Claude 不要同時改 `index.html`。
   - Codex 做完後，由 Claude 看 diff、測試，沒問題才 commit。
5. **統籌說「這次不用 Codex」時就跳過。**
6. **每次都要讓統籌看得到 Codex 有沒有參與。**
   - 開始用 Codex 前先說一句，工作清單也要有「請 Codex 審查」或「交給 Codex 實作」這一步。
   - 最後的回覆固定有一段「Codex 審查」，寫明：
     - 有沒有跑、跑了多久
     - 用的模型與推理強度（看 `.test/codex-run.log` 開頭的 `model:`、`reasoning effort:`）
     - 指出哪些問題
     - 哪些採用、哪些不採用，以及原因
   - 沒有用 Codex 時，也要寫明沒用和原因。
   - 不要加 `--ephemeral`，Codex 的紀錄才會留下來，統籌可以用 `codex resume` 查看。
7. **Codex 用的是統籌的 ChatGPT 額度。**
   - 審查一次要幾分鐘，請在背景執行，輸出放在 `.test/`（不會進 git）。
   - 模型和推理強度照統籌的 `~/.codex/config.toml`，不要自己改。
