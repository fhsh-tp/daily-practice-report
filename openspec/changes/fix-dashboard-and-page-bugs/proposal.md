## Why

系統審查發現儀表板頁面存在多個 runtime bug 及 spec 不符問題：`submit_task.html` 在無模板時崩潰、`badges.html` 對 datetime 做不合法切片、多個頁面使用 API auth 而非頁面 auth（未登入回 JSON 401 而非導向登入頁）、儀表板 router 缺少大量 template 所需的 context 變數（badge 數、連續天數、提交數、徽章列表、活動記錄）。這些問題導致核心功能不可用，需要立即修復。

## What Changes

- **修復** `submit_task.html`：在 `template is None` 時顯示提示訊息，不渲染空模板欄位
- **修復** `badges.html`：將 `award.awarded_at[:10]` 改為 `award.awarded_at.strftime('%Y-%m-%d')`
- **修復** badges、leaderboard、feed 三個頁面 route：從 `get_current_user` 改用 `get_page_user`（未登入 → 302 to login）
- **補足** `dashboard_page` router context：加入 `stats.badge_count`、`stats.streak_days`、`stats.submission_count`、`badges`（badge strip 資料）、`recent_activities`（活動 Feed）、`class_status.member_count`（教師 Widget）
- **修復** checkin PRG：「已簽到」時 redirect 不帶 error 參數（spec 要求 HTTP 302 無 error）
- **重構** 所有 Jinja2 template 中的硬編碼路徑：將 `href="/pages/..."` 等靜態路徑全部改為 `url_for(...)` 呼叫；帶 query string 的連結使用 `.include_query_params()` 方法
- **修復** 測試 fixture：因 `url_for()` 在 Jinja2 渲染時需路由已完整注冊，補足所有測試 app factory 中缺少的 router 及 Beanie 模型

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
  - `src/templates/student/dashboard.html`
  - `src/templates/shared/base.html`
  - `src/templates/admin/layout.html`
  - `src/templates/admin/index.html`
  - `src/templates/admin/users_list.html`
  - `src/templates/admin/user_form.html`
  - `src/templates/admin/system_settings.html`
  - `src/templates/admin/classes_list.html`
  - `src/templates/login.html`
  - `src/templates/community/feed.html`
  - `src/templates/teacher/class_members.html`
  - `src/templates/teacher/template_assign.html`
  - `src/templates/teacher/template_form.html`
  - `src/templates/teacher/templates_list.html`
  - `src/templates/teacher/points_manage.html`
  - `src/gamification/badges/router.py`（`badges_page`）
  - `src/gamification/leaderboard/router.py`（`leaderboard_page`）
  - `src/community/feed/router.py`（`feed_page`）
  - `src/pages/router.py`（`dashboard_page`）
  - `src/tasks/checkin/router.py`（`checkin_browser`）
  - `tests/test_pages.py`
  - `tests/test_dashboard_and_page_bugs.py`
  - `tests/test_ui_polish.py`
  - `tests/test_checkin_config_page.py`
  - `tests/test_task_scheduling.py`
  - `tests/test_setup_wizard.py`
  - `tests/test_admin_pages.py`
