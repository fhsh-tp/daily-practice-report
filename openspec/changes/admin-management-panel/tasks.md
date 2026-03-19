## 1. Permission Schema 基礎建設

- [ ] 1.1 在 `src/core/auth/permissions.py` 新增 `PERMISSION_SCHEMA` 常數（定義 Self、Class、Task、User、System 五個 domain 的 read/write flag 映射），對應 design 決策「Permission Schema 以結構定義驅動 UI」，滿足「PERMISSION_SCHEMA defines domain-to-flag mapping」需求
- [ ] 1.2 在 `src/core/users/router.py` 新增 `GET /admin/permissions/schema` 端點（需要 `MANAGE_USERS`），序列化 `PERMISSION_SCHEMA` 回傳，滿足「Permission schema API endpoint」需求
- [ ] 1.3 在 `src/core/users/router.py` 新增 `GET /admin/permissions/presets` 端點（需要 `MANAGE_USERS`），回傳所有 preset 名稱與 int 值，滿足「Permission presets API endpoint」需求

## 2. 使用者管理 API

- [ ] 2.1 在 `src/core/users/router.py` 新增 `GET /admin/users` 端點（分頁、需要 `MANAGE_USERS`），滿足「User list API returns paginated user records」需求
- [ ] 2.2 在 `src/core/users/router.py` 新增 `GET /admin/users/{id}` 端點（需要 `MANAGE_USERS`），滿足「Single user read API」需求
- [ ] 2.3 在 `src/core/users/router.py` 新增 `PUT /admin/users/{id}` 端點（可更新 `display_name`、`permissions`、`tags`、`new_password`，需要 `MANAGE_USERS`），滿足「User update API」需求
- [ ] 2.4 在 `src/core/users/router.py` 新增 `DELETE /admin/users/{id}` 端點（禁止刪除自己，需要 `MANAGE_USERS`），滿足「Single user delete API」需求
- [ ] 2.5 在 `src/core/users/router.py` 新增 `DELETE /admin/users/bulk` 端點（對應 design 決策「批次操作以 body 傳遞 ID 清單」，接受 JSON body `{"ids": [...]}` 需要 `MANAGE_USERS`，排除自身 ID），滿足「Bulk delete API」需求
- [ ] 2.6 在 `src/core/users/router.py` 新增 `PATCH /admin/users/bulk` 端點（接受 JSON body `{"ids": [...], "permissions": int}`，需要 `MANAGE_USERS`），滿足「Bulk permissions update API」需求
- [ ] 2.7 在 `src/core/users/router.py` 新增 `POST /admin/users/import` 端點（multipart CSV 上傳，用 Python `csv` module 解析，回傳 success/failed 報告），對應 design 決策「CSV 匯入格式與驗證」，滿足「CSV batch import API」需求

## 3. 系統設定 API

- [ ] 3.1 在 `src/core/system/router.py` 新增 `GET /admin/system` 端點（需要 `READ_SYSTEM`），回傳 `site_name` 與 `admin_email`，滿足「System config read API」需求
- [ ] 3.2 在 `src/core/system/router.py` 新增 `PUT /admin/system` 端點（需要 `WRITE_SYSTEM`），更新 MongoDB `SystemConfig`、`app.state.system_config` 及 `webpage_context_update`，滿足「System config update API」需求

## 4. Admin 頁面路由與模板

- [ ] 4.1 建立 `src/templates/admin/layout.html`（含 admin navigation bar，依使用者權限顯示 User Management / System Settings 連結），對應 design 決策「Admin 頁面路由置於 src/pages/router.py」，滿足「Admin templates use a shared admin layout」需求
- [ ] 4.2 在 `src/pages/router.py` 新增 admin 頁面路由群組（`/pages/admin/*`），對應 design 決策「Admin 頁面使用 Cookie 認證，API 使用 Bearer Token」與「Admin 頁面路由置於 `src/pages/router.py`」，加入 admin 基礎 guard（需要 `MANAGE_USERS` OR `WRITE_SYSTEM`），滿足「Admin page group requires admin-level permission」和「Admin Panel is accessible only to authorized users」需求
- [ ] 4.3 建立 `src/templates/admin/index.html` 並新增 `GET /pages/admin/` 路由（顯示使用者總數與 site name），滿足「Admin Panel overview page displays system summary」和「Admin navigation reflects caller's permissions」需求
- [ ] 4.4 建立 `src/templates/admin/users_list.html` 並新增 `GET /pages/admin/users/` 路由（使用者表格、checkbox 多選、批次操作控制項），滿足「Admin user list page」需求
- [ ] 4.5 建立 `src/templates/admin/user_form.html`（含 permission matrix + preset 下拉快速填入，對應 design 決策「Preset 作為「快速填入」捷徑」）並新增 `GET /pages/admin/users/new` 路由，滿足「User create and edit pages」需求
- [ ] 4.6 新增 `GET /pages/admin/users/{id}/edit` 路由（使用同一 `user_form.html`，pre-fill 現有使用者資料），滿足「User create and edit pages」（pre-fill 情境）需求
- [ ] 4.7 建立 `src/templates/admin/system_settings.html` 並新增 `GET /pages/admin/system/` 路由（PRG 模式表單、顯示 success/error 訊息），滿足「System settings admin page」需求

## 5. 測試

- [ ] 5.1 為 `GET /admin/permissions/schema` 與 `GET /admin/permissions/presets` 撰寫單元測試，驗證 `PERMISSION_SCHEMA` 結構完整性（五個 domain）
- [ ] 5.2 為使用者 CRUD API（`GET /admin/users`、`GET /admin/users/{id}`、`PUT /admin/users/{id}`、`DELETE /admin/users/{id}`）撰寫整合測試
- [ ] 5.3 為批次操作 API（`DELETE /admin/users/bulk`、`PATCH /admin/users/bulk`）撰寫整合測試，含自身 ID 排除情境
- [ ] 5.4 為 `POST /admin/users/import` 撰寫整合測試，涵蓋有效 CSV、重複 username、無效 preset 三種情境
- [ ] 5.5 為 `GET /admin/system` 與 `PUT /admin/system` 撰寫整合測試，驗證 in-memory 狀態同步更新
- [ ] 5.6 為 `/pages/admin/*` 路由群組撰寫頁面測試，驗證 403（無權限）、302（未登入）及正常渲染情境
