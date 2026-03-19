## Context

`User` model 現在有 `role: Literal["student", "teacher"]`，所有現有 route 用 `current_user.role == "teacher"` 做授權。需要改成以 IntFlag 位元組合儲存的細粒度權限，同時保持向下相容的遷移路徑。

## Goals / Non-Goals

**Goals:**

- 定義 `Permission` IntFlag，12 個 flag，分 5 個 domain
- 定義 4 個命名 Role Preset 作為 code 常數（不入 DB）
- User 存 `permissions: int`，一個欄位儲存所有授權資訊
- `require_permission(flag)` FastAPI dependency，用於 route decorator
- `tags: list[str]` 加入 User model

**Non-Goals:**

- 不實作動態角色管理 UI（Role Preset 是 code 常數，不是 DB 資料）
- 不實作 row-level security（只到 API endpoint 層級）
- 不處理 OAuth / 外部 IdP 整合

## Decisions

### Permission IntFlag 分 5 個 domain

**決定**：
```
# Self domain
READ_OWN_PROFILE  = 0x001
WRITE_OWN_PROFILE = 0x002
SUBMIT_TASK       = 0x004
CHECKIN           = 0x008

# Class domain
READ_CLASS        = 0x010
MANAGE_CLASS      = 0x020

# Task domain
READ_TASKS        = 0x040
MANAGE_TASKS      = 0x080

# User domain
READ_USERS        = 0x100
MANAGE_USERS      = 0x200

# System domain
READ_SYSTEM       = 0x400
WRITE_SYSTEM      = 0x800
```

**理由**：hex 值讓每個 domain 的 bit 區段清晰可讀，便於除錯。未來可在各 domain 後段擴充新 flag 而不影響現有值。

**替代方案**：decimal 連續值（1、2、4、8...）— 功能相同，但 hex 更易辨識 domain。

### Role Preset 存在 code，不入 DB

**決定**：4 個 preset 是 Python 模組層級常數：
```
STUDENT    = 0x05F  # READ/WRITE_OWN + SUBMIT + CHECKIN + READ_CLASS + READ_TASKS
TEACHER    = 0x0FF  # STUDENT + MANAGE_CLASS + MANAGE_TASKS + READ_USERS
USER_ADMIN = 0x303  # Self basic + READ/MANAGE_USERS
SYS_ADMIN  = 0xC03  # Self basic + READ/WRITE_SYSTEM
```

**理由**：Preset 是語義便利，不是資料。存 DB 會造成 preset 版本管理問題（DB preset 跟 code preset 不同步）。使用者實際授權的是 `permissions: int`，preset 只是 UI 方便選用。

**替代方案**：DB 中存 role 名稱，查表得 permissions — 過度複雜，且 permissions 在 JWT 中傳遞時仍需要是 int。

### 使用 require_permission FastAPI dependency 作為 route 守衛

**決定**：
```python
def require_permission(flag: Permission):
    async def guard(current_user: User = Depends(get_current_user)):
        if not (current_user.permissions & flag):
            raise HTTPException(403)
        return current_user
    return guard
```

**理由**：與現有 `Depends(get_current_user)` 模式一致。可組合（一個 route 可同時 require 多個 flag）。

### Migration：User.role → User.permissions

**決定**：提供 migration script，將現有 `role = "student"` 映射到 `STUDENT` preset int，`role = "teacher"` 映射到 `TEACHER` preset int。

**理由**：破壞性變更需要 migration；使用現有 migration-scripts 機制。

## Risks / Trade-offs

- [Risk] `Permission IntFlag 分 5 個 domain` bit 值未來可能耗盡 domain 空間（每個 domain 目前只有 2-4 bits 空間）
  → Mitigation：Python `int` 是任意精度，hex 區段設計已預留擴充空間（每個 domain 最多可擴到 4 bits，未來可跨 domain 邊界）
- [Risk] JWT token 中的 permissions int 與 DB 不同步（token 過期前使用者權限已被修改）
  → Mitigation：短 token TTL（建議 15 分鐘），或在關鍵操作前重新驗證 DB（此 change scope 外）
