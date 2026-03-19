## Context

目前 Setup Wizard 建立的管理者帳號持有 `SITE_ADMIN`（`0xEFF`）完整權限，但登入後只會看到學生 Dashboard，沒有任何管理介面。後端僅有 `POST /admin/users`（建立單一使用者），缺少列表、更新、刪除、批次操作與 CSV 匯入功能。系統設定在 spec 層面已有 `GET/PUT /admin/system` 的需求，但尚未實作。

權限系統已使用 Python `IntFlag` 設計完善，有五個 domain（Self、Class、Task、User、System），各 domain 有 read/write 分離。目前前端沒有任何反映此結構的 UI。

## Goals / Non-Goals

**Goals:**

- 建立統一 Admin Panel（`/pages/admin/*`），具備使用者管理與系統設定兩個功能區
- 補全使用者管理 CRUD API（列表、讀取、更新、刪除）
- 新增批次操作 API（批次刪除、批次改權限）
- 新增 CSV 批次匯入 API
- 新增 Permission Schema API（動態回傳 domain 結構），使 UI 無需硬編碼 flag
- 補實 `GET /admin/system` 與 `PUT /admin/system`
- 使用者權限指派 UI 採 domain × level 矩陣（無 / 只讀 / 讀寫）

**Non-Goals:**

- 客製化新增權限 flag（使用者只能選既有 preset 或 domain level 組合）
- 多租戶 / 組織層級的權限管理
- 使用者個人資料的詳細編輯（如頭像、聯絡資訊）
- 完整的 audit log 系統

## Decisions

### Permission Schema 以結構定義驅動 UI

在 `permissions.py` 新增 `PERMISSION_SCHEMA: list[dict]`，每個 dict 描述一個 domain 的 read/write flags：

```python
PERMISSION_SCHEMA = [
    {"domain": "Self",   "read": READ_OWN_PROFILE | SUBMIT_TASK | CHECKIN, "write": WRITE_OWN_PROFILE},
    {"domain": "Class",  "read": READ_CLASS,   "write": MANAGE_CLASS},
    {"domain": "Task",   "read": READ_TASKS,   "write": MANAGE_TASKS},
    {"domain": "User",   "read": READ_USERS,   "write": MANAGE_USERS},
    {"domain": "System", "read": READ_SYSTEM,  "write": WRITE_SYSTEM},
]
```

`GET /admin/permissions/schema` 序列化此結構回傳，前端依此動態渲染矩陣。開發者新增 flag 後只需更新 `PERMISSION_SCHEMA`，UI 自動帶入，無需改 template。

此方案優於「命名慣例自動解析」（後者對非英文 domain name 或特殊 flag 名稱脆弱）。

### Preset 作為「快速填入」捷徑

`GET /admin/permissions/presets` 回傳所有 preset 名稱及對應 int 值。UI 提供 preset 下拉選單，選擇後 **自動計算** 每個 domain 的 read/write level 並填入矩陣——使用者仍可在 preset 基礎上微調個別 domain。這比純粹「只選 preset」更靈活，同時保留快速操作入口。

### Admin 頁面使用 Cookie 認證，API 使用 Bearer Token

`/pages/admin/*` 沿用現有 cookie-based 頁面認證（`get_page_user` dep），與其他頁面一致。
`/admin/*` JSON API 維持 Bearer Token（現有 `require_permission` guard）。
前端 Jinja2 form 透過 PRG（POST-Redirect-GET）模式提交，批次操作與 CSV 匯入透過 fetch/HTMX 呼叫 JSON API。

### CSV 匯入格式與驗證

格式：`username,password,display_name,preset,tags`（tags 以分號 `;` 分隔）。
後端逐行解析，對每行執行與單筆建立相同的驗證（重複 username 等）。
回傳結構：`{success: N, failed: [{row, reason}]}`，前端顯示逐行結果。
不使用外部 CSV library，以 Python 標準 `csv` module 解析。

### 批次操作以 body 傳遞 ID 清單

`DELETE /admin/users/bulk` 與 `PATCH /admin/users/bulk` 接受 JSON body `{"ids": [...], "permissions": ...}`。
使用 DELETE with body（非 query string）以支援大量 ID。前端列表頁使用 checkbox 多選。

### Admin 頁面路由置於 `src/pages/router.py`

沿用現有 `pages` 模組架構，在同一 router 中新增 `/pages/admin/*` 路由群組，以 `get_page_user` dep 取得使用者後再做 permission check。
Admin Jinja2 模板放置於 `src/templates/admin/`。

## Risks / Trade-offs

- **DELETE with body** — 部分 HTTP proxy 不支援 DELETE body。緩解：若環境有限制，可改用 `POST /admin/users/bulk-delete`。
- **PERMISSION_SCHEMA 需手動維護** — 開發者新增 flag 後必須同步更新 `PERMISSION_SCHEMA`，否則 UI 不顯示新 flag。緩解：在 spec 中明確要求此維護義務。
- **CSV 匯入無 dry-run** — 目前設計為直接寫入，失敗行跳過。緩解：回傳詳細逐行錯誤報告，讓操作者確認。

## Migration Plan

無資料遷移需求。新 API 與新頁面路由屬新增，不修改現有 endpoint 行為。
`PERMISSION_SCHEMA` 新增至 `permissions.py` 為向後相容。
