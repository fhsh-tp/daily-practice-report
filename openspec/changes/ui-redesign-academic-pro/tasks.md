## 1. 基礎設計系統（shared/base.html）

- [x] 1.1 移除 Pico CSS CDN，加入 Tailwind CSS Play CDN；使用 Tailwind CSS replaces Pico CSS as the styling foundation
- [x] 1.2 在 `<head>` 最頂端加入 FOUC 防護 inline script，實作 Light and Dark mode controlled by `<html>` class（讀取 `localStorage.theme` 並立即套用 `dark` class）；設計 Token 集中在 base.html 的 `tailwind.config` 腳本
- [x] 1.3 加入 Google Fonts（Poppins + Open Sans）並在 `tailwind.config` 中配置 `fontFamily`；實作 Typography system uses Poppins and Open Sans
- [x] 1.4 在 `tailwind.config` 腳本中定義 `brand` 色彩 token（violet 50–950）與 `darkMode: 'class'`；確保使用 Tailwind CSS Play CDN 而非 PostCSS 構建
- [x] 1.5 實作 RWD navigation adapts to three breakpoints：Desktop sidebar（`lg:`）、Tablet top navbar（`md:`）、Mobile bottom tab bar（預設）；完成 RWD 導覽：Mobile Bottom tab / Tablet Top nav / Desktop Sidebar 設計
- [x] 1.6 在 sidebar 加入 active 狀態樣式 `bg-brand-50 dark:bg-brand-900/20 text-brand-700 font-semibold`
- [x] 1.7 加入 Dark mode 採用 `class` 策略而非 `media` 策略的主題切換按鈕，寫入 `localStorage.theme` 並更新 `<html>` class
- [x] 1.8 確認所有 class 均為完整字串，不使用字串拼接；遵守 All class attribute strings are written in full 原則

## 2. setup.html 遷移

- [x] 2.1 將 `setup.html` 改為繼承 `shared/base.html`，移除獨立 inline CSS；完成 setup.html inherits shared/base.html

## 3. 登入頁面（login.html）

- [x] 3.1 重新設計 `login.html`：置中卡片佈局，含行內錯誤訊息顯示（`?error=` 參數）

## 4. Dashboard（student/dashboard.html）

- [ ] 4.1 實作 Widget Grid（積分/徽章/連續天數/任務數 widget）；完成 Dashboard 採用三層複合佈局 — Widget Grid 層
- [ ] 4.2 實作班級 Card Grid，含今日簽到/提交狀態與快速動作連結；完成 Dashboard is the unified authenticated entry point 的班級卡片區塊
- [ ] 4.3 實作教師視角的 Widget Grid（學生總數、今日簽到數、提交數）與班級卡片教師工具列
- [ ] 4.4 實作 Activity Feed 時間軸（最多 20 筆最近活動）；完成 Dashboard 採用三層複合佈局 — Activity Feed 層
- [ ] 4.5 實作 Dashboard displays gamified badge strip（水平可捲動徽章條，未解鎖灰化）

## 5. 任務提交頁面（student/submit_task.html）

- [ ] 5.1 移除 EasyMDE CDN 與初始化腳本；完成 EasyMDE used for markdown fields（REMOVED）
- [ ] 5.2 加入 Toast UI Editor CDN（`https://uicdn.toast.com/editor/latest/`）；完成 Toast UI Editor 取代 EasyMDE 設計決策
- [ ] 5.3 實作混合欄位渲染：text → `<input type="text">`、number → `<input type="number">`、checkbox → `<input type="checkbox">`
- [ ] 5.4 實作 markdown 欄位：掛載 `toastui.Editor`（`initialEditType: 'markdown'`、`previewStyle: 'vertical'`）並在 `toolbarItems` 旁加入擴充用的程式碼註解（`['link', 'image']`、`['table']`）；完成 Student task submission HTML page 的 TUI Editor 整合
- [ ] 5.5 在表單 submit 前同步 TUI Editor 內容至對應 `<input type="hidden">`
- [ ] 5.6 支援 dark mode：依 `<html class="dark">` 切換 TUI Editor `theme: 'dark'` 或 `''`

## 6. 徽章頁面（student/badges.html）

- [ ] 6.1 重新設計 `badges.html`：Gamified 卡片格局，含未解鎖灰化狀態

## 7. 教師頁面群

- [ ] 7.1 重新設計 `teacher/templates_list.html`：Tailwind 表格/卡片佈局
- [ ] 7.2 重新設計 `teacher/template_form.html`：欄位表單，Tailwind 輸入元件
- [ ] 7.3 重新設計 `teacher/points_manage.html`：積分管理表格，Tailwind 樣式

## 8. 社群頁面群

- [ ] 8.1 重新設計 `community/feed.html`：活動動態 Feed，卡片時間軸佈局
- [ ] 8.2 重新設計 `community/leaderboard.html`：Medal podium + 自己高亮表格排行榜
