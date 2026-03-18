## Context

系統使用 FastAPI + Beanie (MongoDB) 架構，已有完整的 API layer。`src/templates/` 下有 10 個 Jinja2 HTML template，但只有 5 個有對應的 page route；各 router 各自建立獨立的 `Jinja2Templates` 實例，重複指向同一目錄。`fastapi-webpage`（作者自行開發）已列於 `pyproject.toml` 但從未使用，提供 `WebPage` 類別封裝 Jinja2，支援 decorator pattern、global context、reverse proxy scheme 處理。

## Goals / Non-Goals

**Goals:**

- 建立單一 `WebPage` singleton，消除各 router 重複的 `Jinja2Templates` 實例
- 補齊所有已有 template 但缺少 page route 的頁面（dashboard, submit task, templates list/form）
- 新增 login 頁面與 form-based login/logout
- 所有 form POST 採 POST-Redirect-GET (PRG) pattern
- Page-aware auth dependency：未登入 → redirect `/pages/login?next=<path>`
- `site_name` 透過 `WebPage.webpage_context` 全域注入所有 template
- Root `/` 依登入狀態 redirect

**Non-Goals:**

- 不重新設計現有 API endpoints（JSON response 維持不變）
- 不新增非已有 template 之外的頁面（如 class management、prize preview 等）
- 不引入前端框架（React/Vue 等），維持 server-side rendering
- 不修改 template 的視覺設計（HTML/CSS 不重寫）

## Decisions

### WebPage Singleton 放在 `shared/webpage.py`

`WebPage` 實例需被多個 router 共享且需在 lifespan 後更新 `webpage_context`（注入 `site_name`）。放在 `shared/` 模組讓各 router 以 `from shared.webpage import webpage` import，與現有 `shared/database.py`、`shared/redis.py` 模式一致。

備選方案：在 `main.py` 建立並注入 `app.state`，但需透過 `request.app.state` 存取，router 內使用較不方便。

### 新增 `pages/` Module 負責 login 與 dashboard

Login 和 dashboard 是橫跨多個 domain 的頁面（dashboard 需要 classes、checkin、tasks 等資料），沒有自然的 domain 歸屬。獨立的 `pages/` module 避免循環 import，集中管理與 domain 無關的頁面入口。

備選方案：放在 `core/users/` 或個別 domain router，但會造成 domain 邊界不清。

### Form-based Login 獨立於 API Login

現有 `POST /auth/login` 接收 JSON body，瀏覽器 form 需要 `application/x-www-form-urlencoded`。採用分離設計：
- `POST /auth/login`（JSON）：保持不變，供前端 JS / API client 使用
- `POST /pages/login`（Form）：新增，供瀏覽器 form 使用，走 PRG pattern

### PRG Pattern 使用 `@webpage.redirect()` + `url_for(...).include_query_params()`

`@webpage.redirect()` decorator 原生支援回傳 `str | tuple[str, int] | URL | URLPath`，並自動處理 reverse proxy scheme。錯誤訊息透過 `request.url_for("route_name").include_query_params(error=...)` 帶回 GET endpoint，型別安全且不需手動 URL encoding。

### Page-aware Auth Dependency 回傳 redirect 而非 401

API dependency (`get_current_user`) raise `HTTPException 401`，適合 JSON client。Page dependency (`get_page_user`) 在未登入時改為 raise `HTTPException 302` 帶 `Location` header（等效於 redirect），讓瀏覽器自動跳到 login 頁面，保留 `next` 參數供登入後回導。

### Dashboard 用 Permission Flag 區分內容區塊

`user.permissions` 為 IntFlag，template 用 `{% if current_user.permissions & MANAGE_CLASS %}` 顯示教師區塊，不需分開兩個 template。

## Risks / Trade-offs

- [WebPage singleton 是 module-level global] → 若測試需要隔離 `webpage_context`，需在測試 setup/teardown 重置。Mitigation：新增 `webpage_context_update({"site_name": None})` 在 test fixture。
- [Page-aware auth 用 302 exception 非標準做法] → FastAPI exception handler 可正確處理，但語意上略顯怪異。Mitigation：有 inline comment 解釋原因；未來可改為自訂 exception 類別。
- [`submit_task.html` / `template_form.html` 的 context 變數需對齊] → Template 現有變數名稱需與 route handler 回傳的 dict key 一致。Mitigation：tasks 中明確列出每個 template 的 context schema。

## Migration Plan

1. 新增 `shared/webpage.py`（無 breaking change）
2. 新增 `pages/` module（無 breaking change）
3. 逐一遷移各 router 的 page handler（現有 API route 不動）
4. 更新 `main.py`：移除舊 Jinja2Templates，加入 WebPage lifespan 初始化
5. 無資料庫 migration，無 rollback 複雜度

### SetupGuardMiddleware 強制進入 Setup 程序

系統第一次啟動時若尚未完成 setup，所有非 `/setup` 路徑的請求應強制 redirect 到 `/setup`，防止使用者在未設定狀態下存取任何功能。

實作方式：在 `main.py` 加入 `SetupGuardMiddleware`（繼承 `BaseHTTPMiddleware`），攔截所有請求，若 `app.state.system_config is None` 且路徑不以 `/setup` 開頭，則回傳 302 redirect 到 `/setup`。Middleware 放在 `SessionMiddleware` 之後掛載。

備選方案：在每個 router 加入個別 guard，但這樣容易遺漏新增的 route。統一的 middleware 確保全面覆蓋。

### SITE_ADMIN Permission Preset

Admin 帳號需要同時具備教師功能（管理課程、任務）、使用者管理、以及系統管理能力。定義 `SITE_ADMIN` preset = `TEACHER | MANAGE_USERS | READ_SYSTEM | WRITE_SYSTEM`（0xEFF），在 setup wizard 建立 admin 帳號時直接賦予此 preset。

`SITE_ADMIN` 定義在 `core/auth/permissions.py`，與其他 role preset（`STUDENT`、`TEACHER`、`USER_ADMIN`、`SYS_ADMIN`）並列。這些 preset 僅作為程式碼常數，不儲存於資料庫。

### Dashboard Permission Flags 透過 Handler Context 傳入

Jinja2 模板不支援 Python bitwise `&` 運算子，無法在 template 內直接計算 `user.permissions & MANAGE_CLASS`。因此在 dashboard route handler 中預先計算所有布林值，以 `can_manage_class`、`can_manage_tasks`、`can_manage_users`、`is_sys_admin` 等 key 傳入 template context。

Template 以 `{% if can_manage_class %}` 等條件分支控制管理入口的顯示，handler 負責計算，template 負責呈現，符合職責分離原則。

## Open Questions

（無）
