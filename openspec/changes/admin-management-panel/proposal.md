## Why

Setup 後的管理者帳號目前缺乏對應的管理介面，無法進行使用者 CRUD、權限指派或系統設定，導致管理功能形同虛設。需要建立統一的 Admin Panel 讓具備管理權限的使用者能夠實際操作系統。

## What Changes

- 新增統一 Admin Panel 路由群組（`/pages/admin/*`），依登入者權限顯示對應功能
- 新增使用者管理後端 API（列表、讀取、更新、刪除、批次刪除、批次改權限、CSV 匯入）
- 新增 Permission Schema API，動態回傳 domain 結構與 preset 清單，使 UI 不需硬編碼
- 新增系統設定讀取 / 更新 API（`GET /admin/system`、`PUT /admin/system`）
- 使用者權限指派 UI 採 domain × level 矩陣（每個 domain 可選「無 / 只讀 / 讀寫」），preset 作為快速填入捷徑
- `PERMISSION_SCHEMA` 結構定義於 `permissions.py`，開發者新增 flag 後自動帶入 UI

## Capabilities

### New Capabilities

- `admin-panel`: 統一的 Admin Panel 頁面層（路由、模板、導覽），包含使用者管理與系統設定入口
- `user-management`: 使用者帳號的 CRUD API、批次操作（批次刪除、批次改權限）、CSV 批次匯入

### Modified Capabilities

- `permission-system`: 新增 `PERMISSION_SCHEMA` 結構（domain → read/write flag 映射）及 `GET /admin/permissions/schema` 與 `GET /admin/permissions/presets` API
- `system-config`: 新增 `GET /admin/system` 與 `PUT /admin/system` API，允許管理者更新 site name 等系統設定
- `web-pages`: 新增 `/pages/admin/*` 頁面路由群組，含 guard（需 `MANAGE_USERS` 或 `WRITE_SYSTEM`）

## Impact

- Affected specs: `admin-panel`（新）、`user-management`（新）、`permission-system`（修改）、`system-config`（修改）、`web-pages`（修改）
- Affected code:
  - `src/core/auth/permissions.py` — 新增 `PERMISSION_SCHEMA`
  - `src/core/users/router.py` — 新增完整 CRUD + bulk + import endpoints
  - `src/core/system/router.py` — 新增 system read/update endpoints
  - `src/pages/router.py` — 新增 admin 頁面路由
  - `src/templates/admin/` — 新增 admin 模板目錄（layout、users list、user form、system form）
  - `src/core/system/models.py` — 可能新增可更新欄位
