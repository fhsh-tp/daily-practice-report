## Context

系統目前使用 FastAPI + Jinja2 server-side rendering，11 個 template 均繼承 `shared/base.html`（`setup.html` 除外，使用獨立 inline CSS）。Pico CSS 提供基礎 semantic styling，幾乎無視覺設計。Inline style 散落各處（`style="float:right"`、`style="display:flex;gap:.5rem"`）。EasyMDE 用於 Markdown 欄位，無 dark mode 支援，導覽列只有 logo + 登出按鈕，缺乏角色導向的導覽結構。

目標使用者：小班到中型班級（50–200 人），繁體中文介面。三個角色：學生、教師、管理員（SITE_ADMIN）。

## Goals / Non-Goals

**Goals:**

- 以 Tailwind CSS CDN（Play CDN）取代 Pico CSS，統一 utility class 用法
- 建立 Academic Pro 設計系統：品牌色（Violet-600 / `#7c3aed`）、Poppins 標題字型、Open Sans 內文字型
- 支援 Light / Dark mode 雙主題（`dark:` class，由 `<html>` 元素的 `class` 控制）
- 建立 RWD 三層導覽：Mobile → Bottom tab bar、Tablet → Top navbar、Desktop → Collapsible sidebar + Top navbar
- 重新設計 Dashboard：Widget Grid（積分/徽章/連續天數/任務數）+ 班級卡片（Card Grid）+ 今日動態（Activity Feed）+ 徽章條（Gamified）
- 任務提交頁面改用**混合欄位**佈局（文字、Markdown TUI Editor、數字、核取方塊），以 Toast UI Editor 取代 EasyMDE
- Toast UI Editor 預設模式為 **Markdown 原始碼**（`initialEditType: 'markdown'`），搭配垂直分割即時預覽（`previewStyle: 'vertical'`）
- `setup.html` 統一繼承 `base.html`，使用設計系統

**Non-Goals:**

- 不修改任何 Python router、service、model 或 API endpoint
- 不新增新頁面（不在現有 11 個 template 範圍外）
- 不引入前端框架（React/Vue）
- 不實作 JS bundle 流程（維持 CDN 載入）
- 不修改 WebPage singleton 或 `shared/webpage.py` 邏輯
- 不變更 PRG pattern 或 auth dependency 行為

## Decisions

### 使用 Tailwind CSS Play CDN 而非 PostCSS 構建

Tailwind Play CDN（`cdn.tailwindcss.com`）在瀏覽器端即時生成樣式，不需要 Node.js 或構建流程，與現有 FastAPI 純 SSR 架構完全相容。代價是生產環境 CSS 體積稍大（~1 秒以內加載，對教育應用可接受）。備選方案：引入 PostCSS pipeline，但會大幅增加開發複雜度，不符合 YAGNI。

### Dark mode 採用 `class` 策略而非 `media` 策略

`tailwind.config` 設定 `darkMode: 'class'`，由 `<html>` 的 `dark` class 控制。這允許使用者手動切換主題並持久化到 `localStorage`，不依賴作業系統偏好。Template 端透過 base.html 內的小型 JS 片段在 `<head>` 最頂端讀取 `localStorage.theme` 並立即套用，避免 FOUC（Flash of Unstyled Content）。

### Toast UI Editor 取代 EasyMDE

Toast UI Editor（`toastui.Editor`）提供原生 dark mode 支援（theme 參數）、WYSIWYG 與 Markdown 原始碼雙模式切換、程式碼語法高亮，且 bundle 更完整。EasyMDE 對 dark mode 的支援需要大量 CSS 覆蓋。TUI Editor 透過 `uicdn.toast.com` CDN 載入，不需要 npm。預設設為 Markdown 原始碼模式（`initialEditType: 'markdown'`）符合技術型使用者習慣，右側即時預覽（`previewStyle: 'vertical'`）提供所見即所得體驗。toolbar 擴充透過 `toolbarItems` 陣列的程式碼註解說明。

### Dashboard 採用三層複合佈局

頂部 Widget Grid 提供一覽數字（積分、徽章、連續天數、任務數），中部 Card Grid 按班級組織核心動作（簽到、提交任務、教師工具），右側 Activity Feed 呈現時間軸動態。這三層對應不同使用情境：快速掃描 → 執行動作 → 回顧歷程，避免單一資訊密度過高。教師檢視 dashboard 時，Widget Grid 切換為班級統計（學生總數、今日簽到數、任務提交數），班級卡片新增教師工具列。

### RWD 導覽：Mobile Bottom tab / Tablet Top nav / Desktop Sidebar

- **Mobile（< 768px）**：Bottom tab bar（4 個主要項目），符合拇指操作習慣
- **Tablet（768px–1024px）**：Top navbar（水平清單），空間足夠但不需要 sidebar
- **Desktop（≥ 1024px）**：可收合 Sidebar（預設展開，icon + 文字）+ Top bar（搜尋、通知、使用者）
- Sidebar active 狀態：`bg-brand-50 dark:bg-brand-900/20 text-brand-700 font-semibold`

### 設計 Token 集中在 base.html 的 `tailwind.config` 腳本

將 `brand` 色彩系統（violet 50–950）、字型（Poppins heading + Open Sans body）定義在 `base.html` 的 inline `<script>` Tailwind 設定中，所有繼承 template 自動取得一致的 token。`setup.html` 改為繼承 `base.html` 以共享設計系統。

## Risks / Trade-offs

- [Tailwind Play CDN 在首次載入時需掃描 DOM] → 可能在低速網路有短暫延遲。Mitigation：CDN 有全球節點，且 Play CDN 在 `<head>` 優先載入，實測延遲 < 500ms。
- [TUI Editor bundle 約 600KB minified] → 比 EasyMDE（約 200KB）大。Mitigation：僅在包含 `markdown` 欄位的頁面載入，`submit_task.html` 為唯一需要的 template。
- [FOUC 風險（dark mode 初始閃爍）] → 透過在 `<head>` 最頂端的 inline script 立即套用 `dark` class 解決。
- [Tailwind `dark:` prefix 需要精確的 class 名稱才能被 Play CDN 識別] → Play CDN 掃描 DOM 中所有 class，但動態拼接的字串（如 `"dark:bg-" + color`）不會被識別。Mitigation：所有 class 均需完整書寫，不使用字串拼接。

## Migration Plan

1. 更新 `shared/base.html`：移除 Pico CSS，加入 Tailwind Play CDN、Google Fonts、`tailwind.config` token 腳本、dark mode init 腳本、RWD 導覽結構
2. 更新 `setup.html`：改為繼承 `base.html`（移除獨立 CSS）
3. 依序更新各 template：`login.html` → `student/dashboard.html` → `student/submit_task.html`（含 TUI Editor 整合）→ `student/badges.html` → `teacher/templates_list.html` → `teacher/template_form.html` → `teacher/points_manage.html` → `community/feed.html` → `community/leaderboard.html`
4. 無資料庫 migration、無 Python code 變更、無 rollback 複雜度
5. 每個 template 更新後可透過瀏覽器即時驗證，不影響其他 template

## Open Questions

（無）
