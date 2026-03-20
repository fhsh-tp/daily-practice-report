## Why

系統審查發現儀表板頁面存在多個 runtime bug 及 spec 不符問題：`submit_task.html` 在無模板時崩潰、`badges.html` 對 datetime 做不合法切片、多個頁面使用 API auth 而非頁面 auth（未登入回 JSON 401 而非導向登入頁）、儀表板 router 缺少大量 template 所需的 context 變數（badge 數、連續天數、提交數、徽章列表、活動記錄）。這些問題導致核心功能不可用，需要立即修復。

## What Changes

- **修復** `submit_task.html`：在 `template is None` 時顯示提示訊息，不渲染空模板欄位
- **修復** `badges.html`：將 `award.awarded_at[:10]` 改為 `award.awarded_at.strftime('%Y-%m-%d')`
- **修復** badges、leaderboard、feed 三個頁面 route：從 `get_current_user` 改用 `get_page_user`（未登入 → 302 to login）
- **補足** `dashboard_page` router context：加入 `stats.badge_count`、`stats.streak_days`、`stats.submission_count`、`badges`（badge strip 資料）、`recent_activities`（活動 Feed）、`class_status.member_count`（教師 Widget）
- **修復** checkin PRG：「已簽到」時 redirect 不帶 error 參數（spec 要求 HTTP 302 無 error）

## Capabilities

### New Capabilities

（無新能力，皆為現有功能修復）

### Modified Capabilities

- `web-pages`：補充 dashboard 頁面 context 規格（badge_count、streak_days、submission_count、badges、recent_activities）；規定頁面 auth 依賴必須使用 `get_page_user`；明確 checkin PRG 對「已簽到」vs「時間已關閉」的不同 redirect 行為
- `checkin`：更新 browser form check-in 的 PRG 規格，區分「已簽到」（無 error 參數）與「視窗關閉」（帶 error 參數）兩種 redirect

## Impact

- Affected specs: `web-pages`、`checkin`
- Affected code:
  - `src/templates/student/submit_task.html`
  - `src/templates/student/badges.html`
  - `src/gamification/badges/router.py`（`badges_page`）
  - `src/gamification/leaderboard/router.py`（`leaderboard_page`）
  - `src/community/feed/router.py`（`feed_page`）
  - `src/pages/router.py`（`dashboard_page`）
  - `src/tasks/checkin/router.py`（`checkin_browser`）
