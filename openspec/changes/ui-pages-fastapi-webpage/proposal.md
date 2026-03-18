## Why

系統目前大多數功能只有 API endpoint，缺乏瀏覽器可直接訪問的 HTML 頁面，且各 router 各自重複建立 `Jinja2Templates` 實例。透過遷移至已在 `pyproject.toml` 中的 `fastapi-webpage` 套件，並補齊缺少的頁面路由，讓使用者可以透過瀏覽器完整操作系統。

## What Changes

- 新增 `shared/webpage.py`，建立全域 `WebPage` singleton，取代各 router 分散的 `Jinja2Templates` 實例
- 所有現有 page handler 改用 `@webpage.page()` decorator 或 `@webpage.redirect()` decorator
- 新增 `pages/` module，包含 login 頁面、統一 dashboard、page-aware auth dependency
- 補齊四個已有 template 但缺少 route 的頁面：dashboard、submit task、templates list、template form
- 所有 form POST 採用 POST-Redirect-GET (PRG) pattern，錯誤訊息透過 `url_for(...).include_query_params(error=...)` 傳回 GET endpoint
- 未登入訪問需要認證的頁面時，redirect 到 `/pages/login?next=<original_path>`
- Root `/` 根據登入狀態 redirect 到 dashboard 或 login
- `lifespan` 啟動後將 `site_name` 注入 `WebPage.webpage_context`，供所有 template 使用
- 新增 `SetupGuardMiddleware` 至 `main.py`：系統尚未設定時，強制將所有請求 redirect 到 `/setup`
- 新增 `SITE_ADMIN` permission preset，並在 setup wizard 建立 admin 時賦予完整管理權限
- Dashboard 管理入口：依 permission flags 顯示班級管理、任務模板、使用者管理、系統設定入口，即使管理員尚未加入任何班級亦可見

## Capabilities

### New Capabilities

- `web-pages`: 瀏覽器可訪問的 HTML 頁面層，包含 login、dashboard、task submission、teacher template management，以及統一的 page-aware auth redirect 機制

### Modified Capabilities

- `user-auth`: 新增 form-based login/logout page endpoint，login POST 採 PRG pattern
- `setup-wizard`: `/setup` POST 改用 PRG pattern，錯誤訊息透過 query param 傳回；admin 帳號建立時賦予 `SITE_ADMIN` permissions
- `task-submissions`: 補齊 submit task page route，POST 採 PRG pattern
- `task-templates`: 補齊 teacher templates list 與 template form page routes
- `checkin`: checkin POST 採 PRG pattern，redirect 回 dashboard
- `community-feed`: feed page POST 採 PRG pattern
- `leaderboard`: leaderboard page handler 遷移至 `WebPage`
- `badge-system`: badges page handler 遷移至 `WebPage`
- `points-system`: points manage page handler 遷移至 `WebPage`

## Impact

- Affected specs: `web-pages`（新增）、`user-auth`、`setup-wizard`、`task-submissions`、`task-templates`、`checkin`、`community-feed`、`leaderboard`、`badge-system`、`points-system`
- Affected code:
  - `src/main.py` — 移除 Jinja2Templates，加入 WebPage context 初始化，root route 改為 redirect，新增 `SetupGuardMiddleware`
  - `src/shared/webpage.py` — **NEW**
  - `src/pages/__init__.py` — **NEW**
  - `src/pages/router.py` — **NEW** (login, dashboard, root redirect)
  - `src/pages/deps.py` — **NEW** (page-aware auth dependency)
  - `src/templates/login.html` — **NEW**
  - `src/templates/student/dashboard.html` — 補齊 context 變數
  - `src/templates/student/submit_task.html` — 補齊 context 變數
  - `src/templates/teacher/templates_list.html` — 補齊 context 變數
  - `src/templates/teacher/template_form.html` — 補齊 context 變數
  - `src/templates/shared/base.html` — 改用 `{{ webpage.site_name }}`，登出改為 POST form
  - `src/core/system/router.py` — PRG pattern，遷移 WebPage
  - `src/core/auth/router.py` — 新增 form login/logout page endpoints
  - `src/tasks/submissions/router.py` — 新增 submit page route，PRG pattern
  - `src/tasks/templates/router.py` — 新增 templates list/form page routes
  - `src/tasks/checkin/router.py` — PRG pattern
  - `src/community/feed/router.py` — PRG pattern，遷移 WebPage
  - `src/gamification/leaderboard/router.py` — 遷移 WebPage
  - `src/gamification/badges/router.py` — 遷移 WebPage
  - `src/gamification/points/router.py` — 遷移 WebPage
- Affected dependencies: `fastapi-webpage` (已在 pyproject.toml，未使用 → 啟用)
