## Why

側邊欄「平台管理」區塊目前會列出使用者管理、班級管理、系統管理三個獨立連結，但管理後台頁面本身已有 Tab 導覽（總覽/使用者管理/班級管理/系統設定），造成重複導覽。同時，側邊欄高亮邏輯只有「系統管理」會亮起（因為它直接連到 admin overview），其他兩項點進去後不會在側邊欄顯示 active 狀態，UX 不一致。改為收斂成單一「管理後台」入口，由管理後台頁面的 Tab 處理子頁面切換即可。

此外，個人設定頁面（settings）的 UI 需要美化：avatar 區塊應提供 Gravatar 連結讓使用者自行更換頭像，現有的「請聯絡管理員更新 Email」警告應改為 tooltip 提示「頭像由 Gravatar 提供，綁定 Email」。

## What Changes

- 將側邊欄「平台管理」區塊從三個獨立連結（使用者管理、班級管理、系統管理）收斂為單一「管理後台」連結，指向 `/pages/admin/`
- 個人設定頁面 UI 美化：avatar 區塊新增 Gravatar 外部連結按鈕、將 email 缺失警告改為 tooltip 提示
- 個人設定頁面整體 layout 微調，提升視覺一致性

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `admin-panel`: 側邊欄從三個獨立項目收斂為單一「管理後台」入口
- `user-profile`: 個人設定頁面 avatar 區塊新增 Gravatar 連結、tooltip 取代 email 警告

## Impact

- 受影響的 Spec：`admin-panel`、`user-profile`
- 受影響的程式碼：
  - `src/templates/shared/base.html`（側邊欄「平台管理」區塊簡化）
  - `src/templates/settings.html`（avatar 區塊、Gravatar 連結、tooltip）
