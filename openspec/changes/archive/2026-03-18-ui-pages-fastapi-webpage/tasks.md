## 1. 建立 WebPage Singleton 與共用基礎設施

- [x] 1.1 建立 `src/shared/webpage.py`，實作 WebPage singleton（設計決策：WebPage Singleton 放在 `shared/webpage.py`），匯出 `webpage` 實例供所有 router import，實作 WebPage singleton provides shared template rendering
- [x] 1.2 修改 `src/main.py`：移除頂層 `Jinja2Templates` 實例，在 lifespan 結束前呼叫 `webpage.webpage_context_update({"site_name": config.site_name})`（設計決策：WebPage Singleton 放在 `shared/webpage.py`）
- [x] 1.3 修改 `src/main.py` root route `GET /`：依登入狀態 redirect 到 `dashboard_page` 或 `login_page`，實作 Root route redirects based on authentication state
- [x] 1.4 建立 `src/pages/__init__.py` 初始化 pages module（設計決策：新增 `pages/` Module 負責 login 與 dashboard）

## 2. Page-aware Auth Dependency

- [x] 2.1 建立 `src/pages/deps.py`，實作 `get_page_user` dependency：未登入時 redirect 到 `login_page?next=<path>` 而非 raise 401（設計決策：Page-aware Auth Dependency 回傳 redirect 而非 401；實作 Page-aware auth dependency redirects to login）

## 3. Login 與 Logout 頁面

- [x] 3.1 建立 `src/templates/login.html`，繼承 `base.html`，包含 username/password form 與 error 顯示，實作 Login page renders HTML login form
- [x] 3.2 修改 `src/templates/shared/base.html`：使用 `{{ webpage.site_name }}` 取代 hardcoded 標題，登出改為 `<form method="post">` button
- [x] 3.3 建立 `src/pages/router.py`，新增 `GET /pages/login`（name=`login_page`）讀取 `error` query param 並渲染 `login.html`
- [x] 3.4 在 `src/pages/router.py` 新增 `POST /pages/login`（form-based login）：成功 redirect 到 `dashboard_page`，失敗 redirect 到 `login_page` with `include_query_params(error=...)`，使用 `@webpage.redirect()`（設計決策：Form-based Login 獨立於 API Login；設計決策：PRG Pattern 使用 `@webpage.redirect()` + `url_for(...).include_query_params()`；實作 Browser-based form login endpoint；實作 User login with credentials）
- [x] 3.5 修改 `src/core/auth/router.py` `POST /auth/logout`：改為 redirect 到 `login_page`，使用 `@webpage.redirect()`，實作 Browser-based logout redirects to login

## 4. Dashboard 頁面

- [x] 4.1 在 `src/pages/router.py` 新增 `GET /pages/dashboard`（name=`dashboard_page`），使用 `get_page_user` dependency，依 permissions 載入學生或教師所需資料（classes、checkin status、today's task），實作 Dashboard is the unified authenticated entry point；使用 dashboard 用 Permission Flag 區分內容區塊決策
- [x] 4.2 更新 `src/templates/student/dashboard.html`：確認所有 context 變數對齊（`classes`、checkin 狀態、today_template 等），使用 `webpage.site_name`

## 5. Setup Wizard 遷移 WebPage + PRG

- [x] 5.1 修改 `src/core/system/router.py`：移除本地 `Jinja2Templates`，改用 `shared.webpage`，`GET /setup` 改用 `@webpage.page()`，讀取 `error` query param，實作 Setup wizard is shown on first deployment
- [x] 5.2 修改 `src/core/system/router.py` `POST /setup`：改用 `@webpage.redirect()`，失敗時 redirect 到 `setup_page` with `include_query_params(error=...)`，實作 Setup wizard form submits initial configuration

## 6. 學生任務提交頁面

- [x] 6.1 在 `src/tasks/submissions/router.py` 新增 `GET /pages/student/classes/{class_id}/submit`（name=`submit_task_page`），使用 `get_page_user` dependency，渲染 `student/submit_task.html`，實作 Student task submission HTML page
- [x] 6.2 在 `src/tasks/submissions/router.py` 新增 `POST /classes/{class_id}/submit`（form-based），採 PRG pattern，成功 redirect 到 `dashboard_page`，失敗 redirect 到 `submit_task_page` with `include_query_params(error=...)`，實作 Student submission via browser form uses PRG pattern

## 7. 教師 Task Template 管理頁面

- [x] 7.1 在 `src/tasks/templates/router.py` 新增 `GET /pages/teacher/classes/{class_id}/templates`（name=`templates_list_page`），使用 `require_permission(MANAGE_TASKS)` dependency，渲染 `teacher/templates_list.html`，實作 Teacher template list HTML page
- [x] 7.2 在 `src/tasks/templates/router.py` 新增 `GET /pages/teacher/classes/{class_id}/templates/new`（name=`template_form_page`），使用 `require_permission(MANAGE_TASKS)` dependency，讀取 `error` query param，渲染 `teacher/template_form.html`，實作 Teacher template form HTML page
- [x] 7.3 更新 `src/templates/teacher/templates_list.html` 與 `teacher/template_form.html`：確認 context 變數對齊

## 8. Checkin PRG

- [x] 8.1 修改 `src/tasks/checkin/router.py` `POST /classes/{class_id}/checkin`：改用 `@webpage.redirect()`，成功或已簽到 redirect 到 `dashboard_page`，視窗關閉 redirect 到 `dashboard_page` with `include_query_params(error=...)`，實作 Student performs daily check-in via browser form

## 9. 現有 Page Handler 遷移 WebPage

- [x] 9.1 修改 `src/community/feed/router.py`：移除本地 `Jinja2Templates`，改用 `shared.webpage`，`GET /pages/classes/{class_id}/feed` 改用 `@webpage.page()`，實作 Community feed HTML page
- [x] 9.2 修改 `src/gamification/leaderboard/router.py`：移除本地 `Jinja2Templates`，改用 `shared.webpage`，`GET /pages/classes/{class_id}/leaderboard` 改用 `@webpage.page()`，實作 Leaderboard HTML page
- [x] 9.3 修改 `src/gamification/badges/router.py`：移除本地 `Jinja2Templates`，改用 `shared.webpage`，`GET /pages/students/me/badges` 改用 `@webpage.page()`，實作 Student badges HTML page
- [x] 9.4 修改 `src/gamification/points/router.py`：移除本地 `Jinja2Templates`，改用 `shared.webpage`，`GET /pages/classes/{class_id}/points` 改用 `@webpage.page()`，實作 Teacher points management HTML page

## 10. Mount pages router 與整合

- [x] 10.1 在 `src/main.py` import 並 `app.include_router(pages_router)`，確保 login / dashboard routes 已掛載

## 11. 測試

- [x] 11.1 新增 `tests/test_pages.py`：測試 login page GET、form login PRG（成功/失敗）、logout redirect、dashboard GET（需登入），覆蓋 All form POSTs use POST-Redirect-GET pattern
- [x] 11.2 新增 dashboard page unit test：確認學生與教師各自取得正確 context
- [x] 11.3 新增 submit task page test：測試 PRG 成功/失敗 redirect，覆蓋 Student submission via browser form uses PRG pattern
- [x] 11.4 確認現有 `tests/test_setup_wizard.py` 測試 PRG redirect，必要時更新

## 12. Setup Guard 與 Admin 權限補強

- [x] 12.1 在 `src/main.py` 新增 `SetupGuardMiddleware`（設計決策：SetupGuardMiddleware 強制進入 setup 程序）：繼承 `BaseHTTPMiddleware`，當 `app.state.system_config is None` 且請求路徑不以 `/setup` 開頭時，回傳 302 redirect 到 `/setup`
- [x] 12.2 在 `src/core/auth/permissions.py` 新增 `SITE_ADMIN` permission preset（設計決策：SITE_ADMIN permission preset）= `TEACHER | MANAGE_USERS | READ_SYSTEM | WRITE_SYSTEM`（0xEFF），並更新 `src/core/system/router.py` setup wizard 建立 admin 帳號時賦予此 preset
- [x] 12.3 更新 `src/pages/router.py` dashboard handler 與 `src/templates/student/dashboard.html`：實作 Dashboard permission flags 透過 handler context 傳入（設計決策：Dashboard permission flags 透過 handler context 傳入），預先計算 `can_manage_class`、`can_manage_tasks`、`can_manage_users`、`is_sys_admin` 布林值，新增管理入口區塊
