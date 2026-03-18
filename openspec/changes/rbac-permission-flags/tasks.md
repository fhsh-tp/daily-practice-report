## 1. Permission 定義

- [x] 1.1 建立 `src/core/auth/permissions.py`，實作 Permission IntFlag 分 5 個 domain（Permission flags defined as IntFlag with five domains）：Self 0x001–0x008、Class 0x010–0x020、Task 0x040–0x080、User 0x100–0x200、System 0x400–0x800
- [x] 1.2 在同檔案中定義 Role Preset 存在 code，不入 DB（Role presets defined as module-level constants）：`STUDENT`、`TEACHER`、`USER_ADMIN`、`SYS_ADMIN` 四個 `Permission` 常數

## 2. Route 守衛

- [x] 2.1 建立 `src/core/auth/guards.py`，實作使用 require_permission FastAPI dependency 作為 route 守衛（Route guard enforces required permission flag）：`require_permission(flag: Permission)` dependency factory，未持有 flag 的請求回傳 HTTP 403

## 3. User Model 更新

- [x] 3.1 修改 `src/core/users/models.py`，實作 User model stores permissions as integer and supports tags：移除 `role: UserRole`，新增 `permissions: int = 0`、`tags: list[str] = []`
- [x] 3.2 更新 `src/core/users/` 下的 Pydantic schema（`UserCreate`、`UserResponse` 等），新增 `permissions` 與 `tags` 欄位，移除 `role`

## 4. 認證流程更新

- [x] 4.1 修改 `src/core/users/router.py`，更新 User registration by teacher：改用 `require_permission(MANAGE_USERS)` 守衛，接受 `permissions` 欄位替代 `role`（User admin creates student account）
- [x] 4.2 修改 `src/core/auth/local_provider.py`，`authenticate()` 回傳的 User 含 `permissions` int
- [x] 4.3 修改 `src/core/auth/deps.py`（`get_current_user`），確保解出的 User payload 含 `permissions`
- [x] 4.4 更新 `src/core/classes/router.py`、`src/tasks/templates/router.py` 等現有 router，以 `require_permission` 替換原有 `role == "teacher"` 判斷

## 5. Migration（Migration：User.role → User.permissions）

- [x] 5.1 建立 migration script，實作 Migration maps existing role field to permissions integer：`role = "student"` → `STUDENT` int、`role = "teacher"` → `TEACHER` int，移除 `role` 欄位（Student role migrated to permissions、Teacher role migrated to permissions）

## 6. 測試

- [ ] 6.1 撰寫 `tests/auth/test_permissions.py`：覆蓋 flag 組合（Permission flag check with bitwise AND）、各 preset 組成驗證（Student preset grants self and read permissions 等）
- [ ] 6.2 撰寫 `tests/auth/test_guards.py`：覆蓋 guard 放行（Authorized request passes guard）與 403 拒絕（Unauthorized request blocked by guard）
- [x] 6.3 撰寫 migration 整合測試，驗證 role 欄位正確轉換（User tags are updatable — 在 user router 測試中驗證）
