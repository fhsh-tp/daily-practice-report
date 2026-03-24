## Why

教師管理介面存在多項 UX 問題：(1) 部分教師頁面（如成員管理）因 route handler 未傳遞側邊欄 context 變數，導致側邊欄退化為學生版本；(2) 側邊欄缺少「任務審查」與「出席紀錄」入口，教師無法快速存取核心功能；(3)「新增班級」按鈕圖示重複顯示；(4) 班級數量達 8+ 時缺乏快速切換機制；(5) 管理區塊分散為「管理工具」與「管理員」兩段，增加認知負擔。這些問題直接影響教師日常操作效率，需要從架構到 UI 層全面重設計。

## What Changes

- 建立 `get_page_context()` 共用 FastAPI Dependency，自動為所有頁面注入側邊欄所需的權限變數（`can_manage_class`、`can_manage_tasks`、`can_manage_users`、`is_sys_admin`）與班級列表（`classes`），從根本消除因 handler 遺漏變數而導致側邊欄顯示錯誤的問題
- 重新設計教師側邊欄資訊架構：引入班級下拉選擇器（含搜尋功能，支援 8+ 班級）、新增「任務審查」與「出席紀錄」導覽項目、修復「＋ 新增班級」圖示重複問題
- 合併「管理工具」與「管理員」側邊欄區塊為統一的「平台管理」區塊，依權限動態顯示項目
- 重新設計班級總覽（Class Hub）頁面：新增統計卡片區（成員數、今日簽到、待審查任務、本週提交率）、將邀請碼移至此頁面以 compact inline bar 呈現
- 重新設計成員管理頁面 layout：移除邀請碼（已移至班級總覽）、改為雙欄 layout（批次邀請 | 成員列表）
- 重新設計任務審查頁面 layout：改為卡片式呈現、新增 filter tabs（待審閱/已確認/已退回/全部）
- 所有教師/管理員頁面統一加入 Breadcrumb 導覽
- 重新設計管理員概覽頁面：合併使用者管理、班級管理、系統管理為統一入口，搭配統計卡片

## Capabilities

### New Capabilities

- `page-context-dependency`: 共用 FastAPI Dependency，自動注入側邊欄所需的權限與班級列表 context 變數至所有頁面 template

### Modified Capabilities

- `web-pages`: 側邊欄資訊架構重設計 — 班級下拉選擇器、新增導覽項目（任務審查、出席紀錄）、合併管理區塊為「平台管理」、修復圖示重複
- `class-hub-page`: 班級總覽頁面重設計 — 統計卡片、邀請碼 compact bar、Breadcrumb 導覽
- `submission-review`: 任務審查頁面 layout 重設計 — 卡片式呈現、filter tabs、Breadcrumb 導覽
- `class-management`: 成員管理頁面 layout 重設計 — 雙欄 layout、移除邀請碼
- `admin-panel`: 管理員概覽頁面重設計 — 統一入口卡片、統計卡片

## Impact

- 受影響的 Spec：`web-pages`、`class-hub-page`、`submission-review`、`class-management`、`admin-panel`
- 新增檔案：`src/shared/page_context.py`
- 受影響的程式碼：
  - `src/templates/shared/base.html`（側邊欄 template 重寫）
  - `src/templates/teacher/class_hub.html`（班級總覽重設計）
  - `src/templates/teacher/class_members.html`（成員管理重設計）
  - `src/templates/teacher/submission_review.html`（任務審查重設計）
  - `src/templates/admin/overview.html`（管理員概覽重設計）
  - `src/pages/router.py`（所有教師/管理員 route handler 改用共用 dependency）
  - `src/tasks/templates/router.py`（class_members_page handler 修正）
  - `src/tasks/submissions/router.py`（submission_review_page handler 修正）
  - `src/gamification/points/router.py`（points handler 修正）
  - `src/tasks/checkin/router.py`（checkin handler 修正）
- Future Work：方案 C — 將側邊欄遷移為 Jinja2 context processor 完全解耦（不在此 change 範圍內）
