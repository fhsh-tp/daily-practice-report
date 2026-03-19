## 1. Bug Fix — Navigation links SHALL be correct and consistent

- [x] [P] 1.1 修正 `shared/base.html` sidebar 中「我的徽章」連結（Navigation links SHALL be correct and consistent）：`/pages/student/badges` → `/pages/students/me/badges`
- [x] [P] 1.2 修正 `shared/base.html` mobile tab bar 中「我的徽章」連結為 `/pages/students/me/badges`
- [x] [P] 1.3 修正 `student/dashboard.html` 中「我的徽章」連結為 `/pages/students/me/badges`
- [x] 1.4 新增測試：GET `/pages/students/me/badges` 回傳 HTTP 200（My Badges navigation link resolves correctly）

## 2. 全站 Modal 元件 — Shared modal component in base template

- [x] 2.1 在 `shared/base.html` 新增 modal overlay HTML 結構（confirm modal + alert modal）及 `window.Modal` JS API（`Modal.confirm`、`Modal.alert`）——Global non-blocking modal replaces browser dialogs；Shared modal component in base template；Modal component available in all pages；modal 元件定義在 base.html，全站共用
- [x] 2.2 替換 `teacher/class_members.html` 中所有 `confirm()` / `alert()` 呼叫為 `Modal.confirm()` / `Modal.alert()`（All existing browser dialog calls replaced）
- [x] 2.3 替換 `admin/users_list.html` 中所有 `confirm()` / `alert()` 呼叫為 Modal API
- [x] 2.4 替換 `admin/classes_list.html` 中所有 `confirm()` / `alert()` 呼叫為 Modal API
- [x] 2.5 替換 `student/dashboard.html` 中所有 `confirm()` / `alert()` 呼叫為 Modal API
- [x] 2.6 替換 `teacher/template_form.html` 中所有 `alert()` 呼叫為 Modal API（Delete confirmation uses modal）
- [x] 2.7 新增測試：驗證每個 template 不再包含直接呼叫 `window.confirm()` 或 `window.alert()`

## 3. 積分顯示 — Student sees point balance on dashboard

- [x] 3.1 在 `pages/router.py` 的 `dashboard_page` handler 中，查詢 `PointTransaction` 並計算 `total_points`，傳入 template context（Student sees point balance on dashboard；積分資料在 dashboard_page 查詢後傳入 context）
- [x] 3.2 確認 `student/dashboard.html` 的「總積分」stat card 正確顯示 `stats.total_points`（Dashboard shows correct total points）
- [x] 3.3 修改 `student/submit_task.html` 提交成功後顯示獲得積分數值（Points shown after task submission — Submission confirmation displays points earned）
- [x] 3.4 在 `tasks/submissions/router.py` 的提交 endpoint 回傳中加入 `points_earned` 欄位
- [x] 3.5 新增測試：dashboard_page context 包含正確的 `stats.total_points`

## 4. 任務模板封存 — Teacher can archive / unarchive a task template

- [x] 4.1 在 `tasks/templates/models.py` 的 `TaskTemplate` 新增 `is_archived: bool = False` 欄位
- [x] 4.2 在 `tasks/templates/service.py` 新增 `archive_template()` 和 `unarchive_template()` 函式
- [x] 4.3 在 `tasks/templates/router.py` 新增 `PATCH /templates/{template_id}/archive` 和 `PATCH /templates/{template_id}/unarchive` endpoints（Teacher can archive a task template；Teacher can unarchive a task template；任務模板封存：`is_archived` flag + 軟隱藏）
- [x] 4.4 修改 `tasks/templates/service.py` 的 `get_template_for_date()`：跳過 `is_archived=True` 的模板（Archived template hidden from students）
- [x] 4.5 修改 `teacher/templates_list.html`：已封存模板以灰色樣式顯示並標示「已封存」，新增「封存」/「取消封存」按鈕呼叫對應 API
- [x] 4.6 新增測試：archive_template 後 get_template_for_date 不回傳該模板；Teacher can unarchive a task template 後恢復正常
