## Context

側邊欄「平台管理」區塊目前列出三個獨立項目（使用者管理、班級管理、系統管理），每個都直接連到對應的管理頁面。但管理後台本身已有橫向 Tab 導覽（總覽/使用者管理/班級管理/系統設定）可切換子頁面，導致重複導覽。且側邊欄的 active state 僅 `admin_overview_page` 路由（系統管理）會亮，進入使用者管理或班級管理頁面時側邊欄無法正確高亮。

個人設定頁面 (`settings.html`) 的 avatar 區塊目前顯示 Gravatar 圖片與 email，若 email 為空則出現黃色警告「請聯絡管理員更新 Email」。UX 改善方向：提供 Gravatar 外部連結讓有 email 的使用者可自行更換頭像，email 為空時改為較不醒目的 tooltip 提示。

## Goals / Non-Goals

**Goals:**

- 將側邊欄「平台管理」三個項目收斂為單一「管理後台」入口，消除與管理頁面 Tab 導覽的重複
- 個人設定頁面 avatar 區塊新增 Gravatar 外部連結、tooltip 取代 email 缺失警告
- 提升個人設定頁面視覺品質

**Non-Goals:**

- 管理後台 Tab 導覽本身的修改（已有完整功能）
- 新增後端 API 或資料模型變更
- Mobile responsive 調整

## Decisions

### 側邊欄「平台管理」收斂為單一「管理後台」入口

將現有三個獨立項目（使用者管理、班級管理、系統管理）替換為單一「管理後台」連結，指向 `/pages/admin/`。保留 `can_manage_users or can_manage_all_classes or is_sys_admin` 的權限閘門，只要有任一管理權限即顯示此入口。

**替代方案：** 保留三個項目但修復 active state 高亮邏輯。放棄原因：管理後台頁面 Tab 已提供完整子導覽，側邊欄重複列出徒增認知負擔。

### 個人設定頁面 avatar 區塊增加 Gravatar 連結與 tooltip

- 有 email 的使用者：avatar 旁顯示一個小按鈕或文字連結「前往 Gravatar 更換頭像」（外部連結），tooltip 提示「頭像由 Gravatar 提供，綁定您的 Email」
- 無 email 的使用者：移除黃色警告框，改為 avatar 下方的灰色小字 tooltip：「請聯絡管理員設定 Email 以自訂頭像」
- Gravatar 連結 URL：`https://gravatar.com/`

### 個人設定頁面 layout 微調

- 讓三個卡片（avatar、顯示名稱、密碼）更緊湊
- avatar 卡片加入 hover 提示

## Risks / Trade-offs

- **[側邊欄項目減少]** → 管理員少了「直達」特定管理頁面的捷徑，需多一次點擊（先到管理後台，再切 Tab）。緩解：管理後台概覽頁面已有管理功能入口卡片。
- **[Gravatar 外部連結]** → 連結到外部網站，使用者可能困惑。緩解：以 tooltip 明確說明頭像來自 Gravatar 服務。
