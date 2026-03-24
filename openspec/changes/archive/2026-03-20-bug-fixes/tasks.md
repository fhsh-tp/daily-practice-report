## 1. 側邊欄條件修正

- [x] 1.1 修改 `base.html`：套用設計決策「側邊欄「建立第一個班級」條件修正」，在 fallback 項目加入 `{% if not can_manage_all_classes %}` 條件（sidebar hides create-class shortcut for all-class managers）
- [x] 1.2 驗證系統管理員登入後側邊欄不顯示「建立第一個班級」（Scenario: System admin sees no create-class shortcut）
- [x] 1.3 驗證無班級的普通教師仍顯示「建立第一個班級」（Scenario: Teacher with no classes still sees create-class shortcut）

## 2. 班級成員管理頁 Header 跑版修正

- [x] 2.1 修改 `class_members.html`：套用設計決策「班級成員管理頁 header 版面」，將按鈕包入群組讓 header 成為兩個 flex 子元素（class members page header renders without layout overflow）
- [x] 2.2 驗證班級成員管理頁在標準視窗寬度下按鈕不跑版（Scenario: Header buttons are grouped）

## 3. 學生儀表板顯示教師名稱

- [x] 3.1 修改 `router.py` `dashboard_page`：套用設計決策「學生儀表板帶入教師名稱」，查詢 `User.get(cls.owner_id)` 並將 `owner_display_name` 加入 dict，查詢失敗時 fallback 為空字串（student dashboard class card displays teacher name）
- [x] 3.2 修改 `student/dashboard.html`：在班級卡片中顯示 `owner_display_name`（Scenario: Class card shows teacher display name）
- [x] 3.3 驗證 owner 帳號不存在時，班級卡片不報錯並顯示空字串（Scenario: Teacher name fallback when owner not found）

## 4. 測試

- [x] 4.1 為側邊欄條件邏輯撰寫單元測試（`can_manage_all_classes` vs `can_manage_class`）
- [x] 4.2 為 `dashboard_page` 帶入 `owner_display_name` 撰寫單元測試（含 owner 不存在的 edge case）
