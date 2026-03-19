## 1. 權限旗標重構（MANAGE_CLASS 拆分為 MANAGE_OWN_CLASS 與 MANAGE_ALL_CLASSES）

- [x] 1.1 在 `src/core/auth/permissions.py` 中執行「將 MANAGE_CLASS 拆分為 MANAGE_OWN_CLASS 與 MANAGE_ALL_CLASSES」設計決策：將 `MANAGE_CLASS` 重新命名為 `MANAGE_OWN_CLASS`（保留 0x020 值），並新增 `MANAGE_ALL_CLASSES`（0x1000）旗標，確認 Permission flags defined as IntFlag with five domains 規格通過
- [x] 1.2 在 `permissions.py` 中新增 `STAFF`（同 TEACHER）與 `CLASS_MANAGER`（含 MANAGE_ALL_CLASSES）兩個 Role presets defined as module-level constants，並更新 `TEACHER` preset 改為使用 `MANAGE_OWN_CLASS`
- [x] 1.3 更新 `GET /admin/permissions/presets`（Permission presets API endpoint）回傳值包含 `STAFF` 與 `CLASS_MANAGER`
- [x] 1.4 撰寫資料庫遷移腳本：將持有舊 `MANAGE_CLASS` bit 的使用者改為持有 `MANAGE_OWN_CLASS`（確保 BREAKING 改動安全升級）

## 2. IdentityTag 身分識別系統

- [x] 2.1 在 `src/core/users/models.py` 中實作「IdentityTag 以獨立 Enum 欄位儲存於 User model」設計決策：定義 `IdentityTag` enum（IdentityTag enum defines three identity values）並在 `User` document 加入 `identity_tags: list[IdentityTag] = []` 欄位（User model stores identity_tags as a list）
- [x] 2.2 撰寫資料庫遷移腳本：依現有 permissions 推斷初始 identity_tags（持有 MANAGE_OWN_CLASS → teacher；SUBMIT_TASK without MANAGE_OWN_CLASS → student）
- [x] 2.3 實作 `GET /admin/permissions/identity-tags`（Identity tags endpoint returns available tag values），回傳所有有效 IdentityTag 值，要求 `MANAGE_USERS`
- [x] 2.4 更新 `PUT /admin/users/{id}` 支援 `identity_tags` 欄位更新（Identity tags are managed only by users with MANAGE_USERS）

## 3. User Model 擴充與自改限制

- [x] 3.1 在 `User` document 新增 `name: str = ""`、`email: str = ""` 欄位；新增嵌入式 `StudentProfile`（class_name, seat_number）submodel 並加入 `student_profile: StudentProfile | None = None`
- [x] 3.2 實作 `PUT /auth/profile`，落實「User 自改欄位限制」設計：只允許修改 `display_name`（Authenticated user can update own display name），忽略其他欄位，拒絕未登入請求
- [x] 3.3 更新 `PUT /admin/users/{id}`（User update API）支援 `name`、`email`、`student_profile` 欄位
- [x] 3.4 更新 `GET /admin/users`（User list API returns paginated user records）與 `GET /admin/users/{id}`（Single user read API）回傳新欄位（name、email、identity_tags、student_profile）

## 4. 使用者資料可見性（Pydantic Response Schema 分層）

- [x] 4.1 實作「可見性以 Pydantic response model 分層實作」設計決策：定義三個 response schema `UserPublicView`、`UserStaffView`、`UserAdminView`，確認 User profile visibility is controlled by viewer identity 規格通過
- [x] 4.2 在所有回傳使用者資料的非管理員 endpoint，依 `current_user.identity_tags` 選擇正確的 view schema（TEACHER/STAFF → UserStaffView；其他 → UserPublicView）
- [x] 4.3 確認 admin endpoints 一律套用 `UserAdminView`

## 5. can_manage_class 集中判斷邏輯

- [x] 5.1 在 `src/core/classes/service.py` 實作 `can_manage_class(user, class_obj)` 函式，落實「can_manage() 集中在 service 層判斷」設計決策：持有 MANAGE_ALL_CLASSES → True；持有 MANAGE_OWN_CLASS + teacher 成員 → True；否則 False
- [x] 5.2 更新 `src/core/classes/router.py` 所有 write endpoint（建立班級、修改成員、改可見性、重產邀請碼）改為呼叫 `can_manage_class()`，並確認 Teacher manages class members 與 Class invite code regeneration 規格通過
- [x] 5.3 更新 Teacher creates a class 邏輯：建立班級需持有 `MANAGE_OWN_CLASS` 或 `MANAGE_ALL_CLASSES`

## 6. 教師批次邀請學生

- [x] 6.1 實作「批次邀請學生的資料流」設計：`GET /classes/{class_id}/invite/search`（Teacher batch-invites students to a class，搜尋功能），支援 `q` 與 `type=name|class_name` 參數，只回傳尚未加入該 class 的 STUDENT identity 使用者
- [x] 6.2 實作 `POST /classes/{class_id}/invite/batch`，批次直接加入指定 user_ids，已是成員者靜默跳過，未授權者回傳 403
- [x] 6.3 在教師班級管理頁面新增批次邀請 UI（搜尋欄 + checkbox 清單 + 確認按鈕）

## 7. CSV Batch Import 更新與範本下載

- [x] 7.1 更新 `POST /admin/users/import`（CSV batch import API）解析邏輯，支援新欄位：`name`、`email`、`identity_tag`、`class_name`、`seat_number`；新增 Unknown identity tag 失敗原因
- [x] 7.2 實作 `GET /admin/users/import/template?type=student` 與 `?type=staff`（CSV batch import template download），回傳含範例列的 CSV 檔案

## 8. 管理員 UI 更新

- [x] 8.1 更新使用者建立/編輯頁面（`/pages/admin/users/new`、`/pages/admin/users/{id}/edit`）加入 identity_tags 多選欄位、name、email 文字欄位，以及 student_profile 條件性顯示區塊
- [x] 8.2 在管理員使用者列表頁面（`/pages/admin/users/`）新增 identity_tags 與 name 欄位顯示
- [x] 8.3 在 CSV 批量匯入頁面加入範本下載連結（學生版 / 教職員版）
