## 1. 共用 Page Context Dependency

- [x] 1.1 建立 `src/shared/page_context.py`，實作 `get_page_context()` async dependency（使用 FastAPI Depends 而非 Jinja2 Context Processor），回傳 shared page context dependency injects sidebar variables 所需的全部變數
- [x] 1.2 更新 `src/pages/router.py` 中所有教師/管理員 handler（teacher_class_hub、dashboard 等），改用 `get_page_context()` 並合併 context，確保 all teacher and admin page handlers use shared page context
- [x] 1.3 更新 `src/tasks/templates/router.py` 中的 class_members_page handler，注入共用 context（修復 class members page includes sidebar context bug）
- [x] [P] 1.4 更新 `src/tasks/submissions/router.py` 中的 submission_review_page handler，注入共用 context（修復 submission review page includes sidebar context）
- [x] [P] 1.5 更新 `src/tasks/checkin/router.py` 和 `src/gamification/points/router.py` 中的 handler，注入共用 context 確保 all teacher pages render consistent sidebar

## 2. 側邊欄資訊架構重設計

- [x] 2.1 重寫 `src/templates/shared/base.html` 教師側邊欄區塊：實作 teacher sidebar uses class dropdown selector with search，取代現有展開式列表（側邊欄班級選擇器取代展開式列表）
- [x] 2.2 在班級工具子項目中新增導覽連結：teacher sidebar includes submission review and attendance links（側邊欄新增「任務審查」與「出席紀錄」導覽項）
- [x] 2.3 修復 create class button works from any page — 移除文字中的全形「＋」，確保 create class button shows single icon
- [x] 2.4 重寫側邊欄管理區塊：sidebar merges admin sections into unified platform management（合併管理區塊為「平台管理」）
- [x] 2.5 修改 student sidebar shows class navigation 區塊，確保學生版側邊欄不受教師重設計影響

## 3. 教師頁面 Layout 重設計

- [x] 3.1 在 `base.html` 或共用 macro 中建立 breadcrumb 元件，支援 all teacher and admin pages display breadcrumb navigation（所有教師/管理員頁面加入 Breadcrumb）
- [x] [P] 3.2 重設計 `src/templates/teacher/class_hub.html`：新增統計卡片（班級總覽新增統計卡片）、更新 class hub page provides unified tool entry 加入任務審查與出席紀錄卡片
- [x] [P] 3.3 在 class hub 頁面實作 class hub page displays invite code — compact inline bar 含複製與重新產生按鈕（邀請碼移至班級總覽頁面）
- [x] [P] 3.4 更新 class hub handler 提供 class hub page displays class summary 所需的新統計資料（成員數、簽到率、待審查數、提交率）
- [x] [P] 3.5 保留 class hub page displays Discord Webhook integration 整合設定區塊
- [x] [P] 3.6 重設計 `src/templates/teacher/class_members.html`：雙欄 layout（teacher manages class members），移除邀請碼（members page does not show invite code）
- [x] [P] 3.7 重設計 `src/templates/teacher/submission_review.html`：卡片式 layout（teacher can view all student submissions for a class）+ 補繳標籤（resubmission shows resubmit badge）
- [x] [P] 3.8 在 submission_review 頁面實作 submission review page provides filter tabs（任務審查頁面改為卡片式 + Filter Tabs）

## 4. 管理員頁面重設計

- [x] [P] 4.1 重設計 `src/templates/admin/overview.html`（或 index.html）：統計卡片 + 管理入口卡片，實作 admin panel overview page displays system summary
- [x] [P] 4.2 更新管理員 handler 提供統計資料（總用戶數、活躍班級數、已封存班級數）
- [x] [P] 4.3 確保管理員側邊欄項目符合 admin navigation reflects caller's permissions（「平台管理」區塊依權限渲染）

## 5. 測試與驗證

- [x] 5.1 撰寫測試驗證 `get_page_context()` 對不同角色（學生、教師、管理員）回傳正確的 context 變數
- [x] 5.2 撰寫測試驗證所有教師頁面（class hub、members、templates、submissions、checkin、attendance、points、leaderboard）都包含 sidebar context 變數
- [x] 5.3 撰寫測試驗證班級總覽頁面的統計卡片資料正確
- [x] 5.4 手動驗證側邊欄班級選擇器搜尋功能、filter tabs 篩選功能
