## Context

目前教師/管理員介面使用 FastAPI + Jinja2 SSR 架構，所有頁面繼承 `shared/base.html`。側邊欄透過 template context 變數（`can_manage_class`、`can_manage_tasks` 等）決定呈現內容。每個 route handler 需手動傳遞這些變數，但部分 handler（如 `class_members_page`）遺漏了全部側邊欄變數，導致側邊欄退化為學生版。

教師通常管理 4-8 個班級（需支援 8+），日常操作混合班級內深入操作與跨班級總覽。管理員可能與教師為同一人，也可能是獨立角色。

## Goals / Non-Goals

**Goals:**

- 建立共用 `get_page_context()` dependency，一次性解決所有 handler 遺漏側邊欄 context 的問題
- 重設計側邊欄資訊架構：班級下拉選擇器（含搜尋）、新增「任務審查」與「出席紀錄」導覽項、合併管理區塊
- 修復「＋ 新增班級」SVG 圖示 + 全形「＋」文字重複問題
- 重設計教師頁面 layout：統計卡片、Breadcrumb、邀請碼移至班級總覽、任務審查 filter tabs
- 重設計管理員概覽頁面 layout

**Non-Goals:**

- 方案 C（Jinja2 context processor 完全解耦側邊欄）— 列為 future work
- 學生端頁面重設計
- 後端 API 變更或資料模型修改
- Mobile responsive 重設計（維持現有行為）

## Decisions

### 使用 FastAPI Depends 而非 Jinja2 Context Processor

建立 `src/shared/page_context.py` 提供 `get_page_context()` async function，由各 route handler 透過 `Depends()` 注入。

**替代方案：** Jinja2 全域 context processor（自動注入所有 template）。放棄原因：需修改 `Starlette` 的 `Jinja2Templates` 類別，侵入性高且難以 mock 測試。`Depends()` 是 FastAPI 原生慣用模式。

**實作細節：**
- `get_page_context(request: Request, current_user: User = Depends(get_page_user))` → `dict`
- 回傳包含：`can_manage_class`、`can_manage_all_classes`、`can_manage_tasks`、`can_manage_users`、`is_sys_admin`、`classes`（教師管理的非封存班級列表）
- 各 handler 使用 `{**page_ctx, ...page_specific}` 合併回傳

### 側邊欄班級選擇器取代展開式列表

目前側邊欄以展開式列表呈現所有班級，8+ 班級時佔滿整個側邊欄。改為下拉式班級選擇器：

**替代方案：** 可收合手風琴（accordion）列表。放棄原因：8+ 班級時仍需大量滾動，且缺乏搜尋能力。

**實作細節：**
- 預設顯示當前選中班級名稱 + 下拉箭頭
- 點擊展開 dropdown，頂部有搜尋欄位
- 選擇班級後導航至該班級的 class hub 頁面
- 選中班級後下方自動展開工具項目（成員管理、任務模板、任務審查、簽到設定、出席紀錄、排行榜、積分管理）
- 純 client-side JS，不需 API 呼叫

### 側邊欄新增「任務審查」與「出席紀錄」導覽項

在班級工具子項目中新增兩個入口，現有路由已存在：
- 任務審查：`/pages/teacher/class/{class_id}/submissions`
- 出席紀錄：`/pages/teacher/classes/{class_id}/attendance`

### 合併管理區塊為「平台管理」

將現有「管理工具」（使用者管理、班級管理）與「管理員」（系統管理）合併為單一「平台管理」區塊，依權限顯示：
- `MANAGE_USERS` → 使用者管理
- `MANAGE_ALL_CLASSES` → 班級管理
- `WRITE_SYSTEM` → 系統管理

### 邀請碼移至班級總覽頁面

邀請碼從成員管理頁面移至班級總覽（Class Hub），以 compact inline bar 呈現（含複製與重新產生按鈕）。教師打開班級即可立即分享邀請碼，UX 更直覺。

### 所有教師/管理員頁面加入 Breadcrumb

統一在頁面標題上方顯示 Breadcrumb 導覽（儀表板 > 班級名稱 > 當前頁面），提供清晰的位置脈絡。

### 班級總覽新增統計卡片

在快速操作 grid 上方新增四張統計卡片：成員數、今日簽到率、待審查任務數、本週提交率。資料在 server-side 計算，不需額外 API。

### 任務審查頁面改為卡片式 + Filter Tabs

取代現有按學生分組的 accordion 展開式，改為扁平的卡片列表。頂部 filter tabs（待審閱/已確認/已退回/全部）以 client-side JS 篩選。補繳提交以特殊標籤標示。

## Risks / Trade-offs

- **[所有 handler 需更新]** → 逐一為每個 teacher/admin handler 加入 `page_ctx = Depends(get_page_context)` 並合併回傳。風險：遺漏某個 handler。緩解：建立測試驗證所有教師頁面都包含必要的 sidebar context 變數。
- **[班級選擇器 JS 複雜度]** → 下拉選擇器需要額外 client-side JS（搜尋過濾、展開/收合、keyboard navigation）。緩解：保持實作簡單，不引入前端框架。
- **[邀請碼移動造成使用者困惑]** → 原本在成員管理的邀請碼移至班級總覽，老用戶可能短暫找不到。緩解：同步更新新增班級的 onboarding 流程指引。
- **[統計卡片效能]** → 班級總覽需要額外 DB 查詢（簽到率、待審查數、提交率）。緩解：查詢範圍限定於單一班級，資料量有限，效能影響可忽略。
