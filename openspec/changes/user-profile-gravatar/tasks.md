## 1. Gravatar 支援

- [ ] 1.1 在 Jinja2 環境中注冊 `gravatar_url` custom filter，套用設計決策「Gravatar URL 計算位置」（User avatar uses Gravatar）
- [ ] 1.2 Filter 邏輯：email 非空時計算 `md5(email.strip().lower())`，email 為空時回傳 identicon URL（Gravatar shown when email is set、Identicon shown when email is empty）
- [ ] 1.3 修改 `base.html` 側邊欄頭像：以 `<img>` 標籤使用 `gravatar_url(current_user.email)` 取代文字首字母 avatar

## 2. Email 必填

- [ ] 2.1 修改 `admin/user_form.html`：email 欄位加入 `required` 屬性與必填視覺標示，套用 /ui-ux-pro-max 風格（Admin user creation form requires email、Form shows email as required）
- [ ] 2.2 修改後端 user creation 端點：驗證 email 為必填，缺少時回 422（Email is required when creating a new user account、User creation fails without email）

## 3. 個人設定頁面（後端）

- [ ] 3.1 在 `router.py` 新增 `GET /pages/settings` 路由（User can access personal settings page）
- [ ] 3.2 新增 `POST /pages/settings/display-name` 端點，套用設計決策「個人設定頁表單設計」（User can update display name）
- [ ] 3.3 新增 `POST /pages/settings/password` 端點，驗證舊密碼後更新（User can change password、Wrong current password is rejected）

## 4. 個人設定頁面（前端）

- [ ] 4.1 建立 `src/templates/settings.html`，使用 /ui-ux-pro-max 風格，包含兩個獨立表單（顯示名稱、密碼）
- [ ] 4.2 若 email 為空，顯示「請更新 email 以啟用頭像功能」提示（套用設計決策「既有帳號 email 處理」）
- [ ] 4.3 在側邊欄加入「個人設定」連結（Settings page is accessible when logged in）

## 5. 測試

- [ ] 5.1 為 `gravatar_url` filter 撰寫單元測試（含 email 為空的 edge case）
- [ ] 5.2 為密碼修改端點撰寫測試（正確舊密碼、錯誤舊密碼）
- [ ] 5.3 為 email 必填驗證撰寫測試
