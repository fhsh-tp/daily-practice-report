## Why

目前教師端側邊欄、班級成員管理頁面版面、以及學生端班級資訊顯示存在三個明確的 UI 錯誤，影響資訊一致性與使用體驗，需要立即修正。

## What Changes

- **側邊欄「建立第一個班級」誤顯**：當使用者擁有 `can_manage_all_classes` 權限（系統管理員）但無班級成員資格時，側邊欄教師工具區仍顯示「建立第一個班級」快捷鍵，與管理員可透過管理工具看到班級的事實矛盾。修正：若 `can_manage_all_classes` 為 true，隱藏此 fallback 項目。
- **班級成員管理頁 header 跑版**：`class_members.html` 的 header 使用 `flex justify-between flex-wrap`，三個子元素（標題、任務模板按鈕、簽到設定按鈕）在 wrap 時排版錯亂。修正：調整 flex 佈局，按鈕群組化。
- **學生端班級卡片未顯示教師**：學生儀表板的班級卡片只顯示班級名稱，當多個班級同名時無法辨識。修正：在班級資料中帶入 owner display_name 並顯示於卡片。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `web-pages`：班級成員管理頁 header 版面修正；學生儀表板班級卡片新增教師顯示欄位

## Impact

- Affected specs: `web-pages`
- Affected code:
  - `src/templates/shared/base.html`（側邊欄條件修正）
  - `src/templates/teacher/class_members.html`（header 跑版修正）
  - `src/templates/student/dashboard.html`（班級卡片新增教師欄位）
  - `src/pages/router.py`（`dashboard_page` 帶入 owner display_name）
