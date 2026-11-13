# TAAI 2026 派工表：給 AI 程式助理的共同規則

這份檔案給 Codex、Claude Code 等助理共用。開始任何修改前請先讀完。

## 專案

- TAAI 2026 研討會（2026/11/20–21，大板根森林溫泉酒店）的派工表，統籌是盧信廷。
- 網址：https://luboblu.github.io/taai2026-dispatch/
- GitHub Pages 直接從 `main` 分支發布，push 後約 1 分鐘生效，不需要建置。
- 所有人都能看；只有統籌用 GitHub token 在網頁上登入後，才能編輯和發布。

## 檔案

| 檔案 | 說明 | 可以改嗎 |
|---|---|---|
| `index.html` | 整個程式（HTML、CSS、JS 都在這裡，不用任何套件或外部字型） | 可以 |
| `data.json` | 大家看到的資料 | **不可以** |
| `.nojekyll` | 讓 GitHub Pages 直接提供檔案 | 保留 |
| `tools/mock_server.py` | 本機測試伺服器 | 可以 |
| `AGENTS.md`、`CLAUDE.md` | 本說明 | 可以 |

`data.json` 只能由統籌在網頁上按「發布」寫入（經 GitHub Contents API），它常常更新。任何助理都不要用 git 或程式直接修改它。

## 協作規則

1. **同一時間只讓一個助理改 `index.html`。** 整個程式在同一個檔案裡，兩邊同時改一定會衝突。
2. **開始前先 `git pull`。** 以 repo 裡最新的 `index.html` 為基礎修改。不要拿自己手上的舊副本整檔覆蓋，否則會蓋掉別人的修改。
3. **改完立刻 commit 並 push**（直接推 `main`，或開 PR 讓統籌合併）。commit 訊息用繁體中文，寫清楚改了什麼。
4. **只 commit 程式和說明。** 不要 commit `data.json` 的變動，也不要 commit `.test/`。
5. **不要把任何 token、密碼、電話或 email 寫進檔案。** 這個 repo 是公開的。

## 網頁文字

- 繁體中文，簡潔、專業，像一般正式網站，不用表情符號。
- 參考 GitHub Primer、IBM Carbon 這類設計系統：中性色、細線分隔、小圓角，顏色只用來表示狀態。
- 主色沿用 TAAI 官網：深藍 `#0d4a9e`、文字 `#0c1f2a`、米白 `#f6f4ee`。顏色都定義在 `:root` 的 CSS 變數，並有深色模式。
- 字級用 `rem`，跟著右上角「Aa」（小／中／大）縮放；列印時固定為原始大小。

## 資料格式與相容性（最重要）

資料的讀入和整理在 `normalize()`，要公開的欄位由 `publishable()` 決定。主要欄位：

- `sessions`：場次 `{id, room, day, start, end, title, sub, assign:{roleId: 姓名}, status, note}`
- `roles[區域]`：該區每場的職務欄位 `[{id, name}]`
- `leads[區域]`：區域負責人；`leadNeeds`：需求人數；`leadStatus`：通知狀態
- `jobs`：工作（可連到場次 `linkId`，或自訂時間）
- `todos`：籌備待辦
- `areas`、`areaOverrides`：自訂區域與改名
- `noteList`：公開備註；`roomNotes[區域]`：各區備註，每條都是 `{id, text, at}`
- `people[姓名]`：`{group, contact}`

多人姓名存成用「、」串起來的字串；`—` 代表「不需要」。

規則：

- **私人資料絕不能發布。** `privateNoteList`（我的筆記）和人員的 `contact`（聯絡方式）只存在瀏覽器裡。新增欄位時，要確認 `publishable()` 沒有把私人資料帶出去。
- **舊版頁面要讀得懂，也不能把資料弄壞。** 瀏覽器快取或還開著的分頁可能還在跑舊版，而舊版發布時會丟掉它不認得的欄位。例如：備註清單放在 `noteList`，`notes` 同時保留一份純文字給舊版看。
- **`normalize()` 對同一份資料每次結果都要相同。** 例如轉換時產生的 id 要固定，否則頁面會一直顯示「尚未發布」。
- **要修改既有資料時，不要直接改 `data.json`。** 寫成一次性的套用函式（參考 `applyAgendaFix`、`applyStaffPlan`）：
  - 只在統籌登入後執行一次，用 localStorage 記錄已執行。
  - 只補空白、不覆蓋已填的內容。
  - 跳出可以「復原」的提示。
  - 由統籌按「發布」後才公開。

## 程式結構（`index.html`）

- 網址路由：`#overview`、`#board`、`#jobs`、`#todo`、`#people`、`#notes`、`#agenda`、`#room-<區域>`。相關函式是 `parseHash()`、`go()`。
- 畫面：`render()` 依目前頁面呼叫 `renderOverview`、`renderBoard`、`renderJobs`、`renderTodo`、`renderPeople`、`renderNotes`、`renderAgenda`、`renderRoom`。`refresh()` 會重畫並保留捲動位置和游標。
- 修改資料後呼叫 `save()`（存到 localStorage），再 `refresh()`。
- 刪除用 `toast(訊息, undoFrom(修改前的 JSON))` 提供復原，不用 `window.confirm`。需要確認時用 `askConfirm()`。
- 發布與衝突處理：`publish()`、`loadHosted()`、`resolveLocal()`、`pollRemote()`、`openConflict()`。
- 人員與時段重疊：`allTasks()`、`conflictInfo()`、`overlaps()`。
- 測試輔助：`window.TAAI`（`getState`、`mode`、`publishable`、`buildXlsx`、`setNow` 等）。

## 測試

在 repo 根目錄執行：

```bash
python3 tools/mock_server.py
```

接著打開 http://127.0.0.1:8791/index.html ，按「統籌登入」輸入假 token `good-token`。這樣可以測發布，資料只會寫進 `.test/data.json`。

改完至少確認：

- 每個頁面都能打開，瀏覽器主控台沒有 JS 錯誤。
- 寬度 1320、990、770、375px，以及字級小／中／大，都沒有左右捲動。
- 列印：現場總表每天 1 頁，待辦 1 頁。
- 有動到資料格式時：
  - 用舊版 `index.html` 讀新資料，畫面不會出現亂碼。
  - 用新版讀舊資料，不會顯示「尚未發布」。

不要用真的 GitHub token 測試。

## 部署

1. push 到 `main`。
2. 用加了隨機參數的網址確認新版已上線，例如：

```bash
curl -s "https://luboblu.github.io/taai2026-dispatch/?cb=$RANDOM" | grep -c "某段新程式"
```
