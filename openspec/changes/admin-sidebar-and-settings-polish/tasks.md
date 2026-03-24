## 1. 側邊欄「平台管理」收斂為單一「管理後台」入口

- [x] 1.1 修改 `src/templates/shared/base.html`「平台管理」區塊：將三個獨立項目（使用者管理、班級管理、系統管理）替換為單一「管理後台」連結（admin navigation reflects caller's permissions — sidebar does not show individual admin items）

## 2. 個人設定頁面 avatar 區塊增加 Gravatar 連結與 tooltip

- [x] [P] 2.1 修改 `src/templates/settings.html` avatar 區塊：有 email 時新增「前往 Gravatar 更換頭像」外部連結按鈕與 tooltip 說明（user avatar uses Gravatar — settings page shows Gravatar link for user with email、settings page shows tooltip for Gravatar explanation）
- [x] [P] 2.2 修改 `src/templates/settings.html` avatar 區塊：無 email 時將黃色警告框改為灰色小字提示（settings page shows subtle hint when email is missing）

## 3. 個人設定頁面 layout 微調

- [x] 3.1 微調 `src/templates/settings.html` 整體 layout：提升卡片間距、視覺一致性（個人設定頁面 layout 微調）

## 4. 測試

- [x] 4.1 驗證側邊欄在管理員身分下只顯示單一「管理後台」連結（admin navigation reflects caller's permissions）
- [x] 4.2 驗證個人設定頁面 avatar 區塊在有 email 時顯示 Gravatar 連結（user avatar uses Gravatar）
