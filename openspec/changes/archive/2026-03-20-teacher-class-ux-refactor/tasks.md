## 1. 班級 Hub 頁面（後端）

- [x] 1.1 在 `router.py` 新增 `GET /pages/teacher/class/<class_id>` 路由（class hub page provides unified tool entry、class hub page displays class summary）
- [x] 1.2 套用設計決策「班級 Hub 頁面路由設計」，路由需驗證使用者有 `can_manage_class` 或為班級擁有者，否則 403（Unauthorized access is rejected）
- [x] 1.3 路由帶入班級名稱、成員數、簽到開關狀態等摘要資料

## 2. 班級 Hub 頁面（前端）

- [x] 2.1 建立 `src/templates/teacher/class_hub.html`，使用 /ui-ux-pro-max 風格，顯示班級摘要（Hub page shows class summary）
- [x] 2.2 在 hub 頁面加入工具卡片：成員管理、任務模板、簽到設定、排行榜、積分管理（Hub page renders tool cards）

## 3. 側邊欄重構

- [x] 3.1 修改 `base.html`：套用設計決策「側邊欄班級展開模式」，教師工具區改為班級名稱列表（Sidebar teacher section shows class list）
- [x] 3.2 加入「＋新增班級」常駐按鈕（Add new class button always visible）
- [x] 3.3 依據當前 URL 的 class_id 展開對應班級的工具連結（Active class expands tool links）
- [x] 3.4 使用 /ui-ux-pro-max 確保側邊欄視覺一致性

## 4. 班級列表 Tab 切換與搜尋

- [x] 4.1 套用設計決策「Tab 切換實作方式」，在管理員 `classes_list.html` 加入「運作中 / 已封存」tab（Class list supports tab switching between active and archived、Class list view separates active and archived classes、Active and archived classes in separate tabs）
- [x] 4.2 預設顯示運作中 tab，tab 標籤顯示班級數量（Default tab shows active classes、Tab counts reflect actual class counts）
- [x] 4.3 套用設計決策「搜尋實作方式」，在兩個 tab 加入搜尋輸入框（Class list supports search by name and teacher）
- [x] 4.4 實作前端 JavaScript 過濾邏輯，比對 data-name 與 data-teacher 屬性（Search filters by class name、Search filters by teacher name）
- [x] 4.5 在 router 為 class list 資料加入 teacher display_name 欄位（供搜尋用）
- [x] 4.6 使用 /ui-ux-pro-max 確保 tab 與搜尋元件視覺一致性

## 5. 測試

- [x] 5.1 為 class hub 路由撰寫權限測試（有權限可存取、無權限回 403）
- [x] 5.2 為側邊欄展開邏輯撰寫 URL 比對測試
