## Why

現有 Jinja2 template 使用 Pico CSS，UI 幾乎無設計，inline style 散落各處，三個角色（學生、教師、管理員）共用同一個 dashboard template 且無角色導向的導覽結構，無 dark mode 支援，任務提交頁面的 Markdown 欄位僅使用基本 textarea。本次改版建立統一的設計系統（Academic Pro），以 Tailwind CSS CDN 取代 Pico CSS，並以 TUI Editor 提供所見即所得的 Markdown 編輯體驗。

## What Changes

- 移除所有 template 中的 Pico CSS CDN 引用，替換為 Tailwind CSS CDN (Play CDN)
- 建立 `shared/base.html` 設計系統：Poppins 標題字型 + Open Sans 內文字型、brand purple 色彩系統（violet-600 主色）、Light/Dark mode 雙主題（`dark:` class 切換）
- 新增 RWD 導覽結構：Desktop 可收合 Sidebar + Topbar、Tablet Top navbar、Mobile Bottom tab bar
- 重新設計 Dashboard：Widget Grid（積分/徽章/連續天數）+ 班級卡片 + 今日動態 + 徽章條
- 任務提交頁面改用混合欄位：短文字 + **TUI Editor Markdown 欄位**（預設 Markdown 原始碼模式 + 右側即時預覽）+ 數字 + 核取方塊
- 徽章頁面：Gamified 卡片格局，含未解鎖狀態
- 排行榜：Medal podium + 自己高亮表格
- 登入頁面：置中卡片設計，含行內錯誤訊息
- 系統初始設定頁面：統一設計語言（不再使用獨立 CSS）

## Capabilities

### New Capabilities

- `ui-design-system`: Tailwind CSS 設計系統 — 色彩 token、字型、dark mode 切換機制、shared base template 結構

### Modified Capabilities

- `web-pages`: 導覽結構從單純 top navbar 改為 RWD 三層（sidebar/topbar/bottom-tab），base template 完全重寫
- `task-submissions`: 提交表單新增 TUI Editor 支援，Markdown 欄位從 EasyMDE 遷移至 TUI Editor，預設 markdown 原始碼模式

## Impact

- 影響的 spec：`web-pages`、`task-submissions`
- 影響的 template 檔案：
  - `src/templates/shared/base.html`
  - `src/templates/login.html`
  - `src/templates/setup.html`
  - `src/templates/student/dashboard.html`
  - `src/templates/student/submit_task.html`
  - `src/templates/student/badges.html`
  - `src/templates/teacher/templates_list.html`
  - `src/templates/teacher/template_form.html`
  - `src/templates/teacher/points_manage.html`
  - `src/templates/community/feed.html`
  - `src/templates/community/leaderboard.html`
- 外部依賴新增：
  - Tailwind CSS Play CDN（`https://cdn.tailwindcss.com`）
  - Toast UI Editor CDN（`https://uicdn.toast.com/editor/latest/`）
  - Google Fonts（Poppins + Open Sans）
- 移除依賴：Pico CSS CDN、EasyMDE CDN
