## Why

系統目前只有 `student | teacher` 兩個固定角色，無法支援細粒度的存取控管。隨著系統功能擴充（班級管理、使用者管理、系統設定），需要一個可擴充的授權模型，讓角色可以自由組合，而不是固定階層。

## What Changes

- 將 `User.role: Literal["student", "teacher"]` 改為 `User.permissions: int`，儲存 IntFlag 位元組合
- 新增 `Permission` IntFlag 定義（12 個細粒度 flag，分 5 個 domain）
- 新增 4 個 Role Preset 常數（Student、Teacher、UserAdmin、SysAdmin）
- 新增 FastAPI dependency `require_permission(flag)` 用於 route 層級的授權守衛
- 在 `User` model 新增 `tags: list[str]` 自由格式標籤欄位
- 更新現有 route 的權限守衛，替換原有 `role` 檢查

## Capabilities

### New Capabilities

- `permission-system`: 基於 IntFlag 的細粒度權限定義、Role Preset 常數，與 FastAPI 授權 dependency

### Modified Capabilities

- `user-auth`: User model 從 `role` 欄位改為 `permissions: int` 與 `tags: list[str]`；認證相關 schema 更新

## Impact

- 修改檔案：`src/core/users/models.py`（新增 `permissions`、`tags`，移除 `role`）
- 新增檔案：`src/core/auth/permissions.py`（Permission IntFlag、Role Presets）
- 新增檔案：`src/core/auth/guards.py`（`require_permission` FastAPI dependency）
- 修改檔案：`src/core/users/router.py`、`src/core/classes/router.py` 等現有 router（更新 auth guard 呼叫）
- 修改檔案：`src/core/auth/local_provider.py`（`authenticate` 回傳 User 含 permissions）
- **BREAKING**：`User.role` 欄位移除，需要 migration
