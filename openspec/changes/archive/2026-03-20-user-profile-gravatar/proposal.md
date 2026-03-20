## Why

目前使用者沒有個人設定頁，無法自行修改顯示名稱、密碼等基本資訊；頭像以文字首字母代替，識別性低。加入 Gravatar 可免費提供個人化頭像，並將 email 升格為必填欄位以支援此功能。

## What Changes

- **使用者個人設定頁**：所有登入使用者可存取個人設定頁（`/pages/settings`），可修改顯示名稱與密碼。
- **Gravatar 頭像**：系統依據使用者 email 的 MD5 hash 產生 Gravatar URL，作為頭像顯示於側邊欄、儀表板等處（無 Gravatar 設定時顯示預設 identicon）。
- **Email 必填**：建立帳號（admin 新增使用者）時 email 成為必填欄位；現有帳號保留舊資料，但個人設定頁顯示提示。

## Capabilities

### New Capabilities

- `user-profile`：使用者個人設定頁面與自助修改資料的能力

### Modified Capabilities

- `user-auth`：User model 中 email 升格為必填（建立時）；新增 Gravatar URL 計算
- `user-management`：管理員新增使用者表單中 email 為必填欄位

## Impact

- Affected specs: `user-profile`（新）、`user-auth`、`user-management`
- Affected code:
  - `src/core/users/models.py`（email 必填調整）
  - `src/templates/admin/user_form.html`（email 必填標示）
  - `src/templates/shared/base.html`（側邊欄頭像改用 Gravatar）
  - `src/pages/router.py`（新增 settings 路由）
  - `src/templates/settings.html`（新 template）
