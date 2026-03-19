## Context

目前系統使用 Python `IntFlag` 儲存使用者權限，以 bitwise 操作進行授權檢查。現有的 `MANAGE_CLASS` 旗標為全域性的——任何持有此旗標的人均可管理**所有**班級，沒有 ownership 範圍限制。此外，系統沒有正式的身分識別欄位；「你是誰」與「你能做什麼」完全混合在 `permissions` 整數中，導致無法依身分動態控制資料可見性。

主要相關檔案：`src/core/auth/permissions.py`、`src/core/users/models.py`、`src/core/classes/service.py`、`src/core/classes/router.py`、`src/core/users/router.py`。

## Goals / Non-Goals

**Goals:**

- 將 `MANAGE_CLASS` 拆分為 ownership-scoped（`MANAGE_OWN_CLASS`）與全域（`MANAGE_ALL_CLASSES`）兩個旗標
- 新增獨立的 `identity_tags` 欄位（teacher/student/staff），與 permissions 完全分離
- 擴充 User model 支援 `name`、`email`、`student_profile`（班級、座號）
- 實作依 viewer identity 決定的資料可見性規則
- 新增教師批次邀請學生功能（搜尋 + 勾選）
- 提供 Batch Upload CSV 範本下載

**Non-Goals:**

- 不實作 per-resource permission bits（如 UNIX 完整的 rwxrwxrwx 數字模型）
- 不開放 API（目前純 web UI 管理）
- 不實作 OAuth 或外部身分驗證整合

## Decisions

### 將 MANAGE_CLASS 拆分為 MANAGE_OWN_CLASS 與 MANAGE_ALL_CLASSES

**決策**：移除舊的 `MANAGE_CLASS`，新增兩個旗標：

- `MANAGE_OWN_CLASS`（0x020）：教師用，只能管理自己是 teacher 成員的班級
- `MANAGE_ALL_CLASSES`（0x1000）：classmanager 用，可管理所有班級（相當於 sudo）

**替代方案**：在現有 `MANAGE_CLASS` 基礎上加 ownership check，不新增旗標。此方案雖然改動較少，但旗標語義不清——同一個旗標在不同 context 下代表不同範圍，未來容易混淆。

**理由**：兩個語義清晰的旗標，比一個需要 context-aware 判斷的旗標更安全且易維護。

### can_manage() 集中在 service 層判斷

**決策**：在 `src/core/classes/service.py` 中新增 `can_manage_class(user, class_obj)` 函式，集中所有 ownership + permission 判斷邏輯：

```
can_manage_class(user, class_obj):
  if MANAGE_ALL_CLASSES in user.permissions → True
  if MANAGE_OWN_CLASS in user.permissions:
    membership = get_membership(class_obj.id, user.id)
    return membership and membership.role == "teacher"
  return False
```

Router 層只呼叫 `can_manage_class()`，不重複判斷邏輯。

**理由**：避免 ownership 判斷分散在各 endpoint，降低遺漏某個 endpoint 的風險。

### IdentityTag 以獨立 Enum 欄位儲存於 User model

**決策**：新增 `identity_tags: list[IdentityTag] = []` 欄位，`IdentityTag` 為 `str` Enum：`TEACHER`、`STUDENT`、`STAFF`。此欄位與 `permissions` 完全獨立。

**替代方案 A**：繼續用 `tags: list[str]` 加上約定（如 `"role:teacher"`）。缺點是沒有型別驗證，容易拼錯。

**替代方案 B**：新增 `role: str | None` 單一欄位。缺點是無法表達兼任情況（如兼任行政的教師同時有 teacher + staff）。

**理由**：list Enum 既有型別安全，又支援多重身分。

### 可見性以 Pydantic response model 分層實作

**決策**：定義三個 response schema：

- `UserPublicView`：只含 `id`、`display_name`（學生互看時使用）
- `UserStaffView`：加上 `name`、`email`、`identity_tags`（教師/職員查看學生時使用）
- `UserAdminView`：完整欄位（MANAGE_USERS 用）

API endpoints 依 `current_user.identity_tags` 選擇回傳的 schema。

**理由**：可見性邏輯集中在 serialization 層，不散落在各 endpoint，且 Pydantic model 本身即為文件。

### User 自改欄位限制

**決策**：使用者只能透過 `PUT /auth/profile` 修改 `display_name`。`name`、`email`、`identity_tags`、`student_profile`、`permissions` 均只能由持有 `MANAGE_USERS` 的管理者修改。

**理由**：學生的真實姓名、學號等資料來自學校行政系統，不應由學生自行更改。

### 批次邀請學生的資料流

**決策**：新增兩個 endpoint：

1. `GET /classes/{class_id}/invite/search?q=<keyword>&type=<name|class_name>` — 搜尋尚未加入此 class 的學生
2. `POST /classes/{class_id}/invite/batch` — 批次加入（直接加入，不需學生確認）

**理由**：教師在同一個 web UI 操作，直接加入比「發送邀請等待確認」更符合課室管理場景，減少摩擦。

## Risks / Trade-offs

- [Risk] `MANAGE_CLASS` BREAKING 改動會使所有現有角色 Preset 中持有此旗標的使用者失去班級管理權 → Mitigation：需提供資料庫遷移腳本，將 `MANAGE_CLASS` bit 的持有者轉換為 `MANAGE_OWN_CLASS`
- [Risk] `identity_tags` 初始值為空，現有使用者沒有 identity tag → Mitigation：遷移腳本依現有 permissions 推斷初始 identity（如持有 `MANAGE_OWN_CLASS` 的設為 teacher）
- [Risk] Pydantic response model 層的可見性判斷若未覆蓋所有 user list endpoint，可能洩漏 `name` 欄位 → Mitigation：tasks 中明確要求每個回傳 user 資料的 endpoint 都必須套用正確的 view schema

## Open Questions

- 批次邀請的上限（一次最多幾人）？目前不設限，但未來高流量場景可能需要。
- `student_profile.class_name`（行政班別）是否需要驗證格式？目前視為自由字串。
