## Why

目前的 `MANAGE_CLASS` 權限旗標是全域性的，任何擁有此旗標的人都能管理所有班級，無法限制教師只管理自己的班級。此外，系統缺乏獨立的身分識別機制（教師、學生、職員），導致「你是誰」與「你能做什麼」混合在一起，無法根據身分動態控制資料可見性。

## What Changes

- **BREAKING** 將 `MANAGE_CLASS` 拆分為 `MANAGE_OWN_CLASS`（教師管自己的班級）與 `MANAGE_ALL_CLASSES`（classmanager 管所有班級）
- 新增 `identity_tags` 欄位於 User model，支援 `teacher`、`student`、`staff` 三種身分識別 tag，與 permissions 完全分離
- 擴充 User model：新增 `name`（真實姓名）、`email`；學生額外有嵌入式 `student_profile`（班級、座號）
- 新增資料可見性規則：依 viewer 的 identity_tags 決定可看到哪些欄位
- 教師可直接批次邀請學生加入班級（搜尋班級/姓名，勾選後批次加入）
- 更新角色預設（Role Presets）以反映新旗標與身分識別
- 新增 Batch Upload CSV 範本（學生版、教職員版）

## Capabilities

### New Capabilities

- `identity-tags`: 身分識別 tag 系統（teacher/student/staff），與 permissions 權限旗標獨立分離，用於控制資料可見性與 UI 顯示

### Modified Capabilities

- `permission-system`: 新增 `MANAGE_OWN_CLASS` 與 `MANAGE_ALL_CLASSES` 旗標，移除舊的 `MANAGE_CLASS`；更新角色 Presets
- `class-management`: 加入 ownership-scoped 管理邏輯（can_manage 判斷）；新增教師批次邀請學生功能
- `user-management`: 擴充 User model 欄位（name、email、identity_tags、student_profile）；新增可見性控制規則；新增 Batch Upload CSV 範本下載

## Impact

- 受影響的 specs：`permission-system`、`class-management`、`user-management`、新增 `identity-tags`
- 受影響的程式碼：
  - `src/core/auth/permissions.py`（旗標定義與 Presets）
  - `src/core/users/models.py`（User model 擴充）
  - `src/core/users/router.py`（可見性控制、CSV 範本端點）
  - `src/core/users/service.py`（欄位更新權限控制）
  - `src/core/classes/models.py`（無需更動）
  - `src/core/classes/service.py`（ownership 判斷邏輯、批次邀請）
  - `src/core/classes/router.py`（批次邀請端點、搜尋端點）
  - `src/pages/`（教師班級管理頁面更新、批次邀請 UI）
  - `src/templates/`（相關 Jinja2 template 更新）
