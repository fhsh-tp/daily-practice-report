## 1. 修復 Template Runtime Bug

- [x] 1.1 修復 `badges.html` 的 datetime slicing（badges.html datetime 修復）：將 `award.awarded_at[:10]` 改為 `award.awarded_at.strftime('%Y-%m-%d')`，確保 badge award date rendered correctly in HTML templates
- [x] 1.2 修復 `submit_task.html` 的 null template 存取（submit_task.html null guard）：加入 `{% if template %}...{% else %}<今日無任務模板提示>{% endif %}` 包覆表單區塊，確保 task submission page handles missing template gracefully

## 2. 統一頁面 Auth 依賴（All page routes use page-aware auth dependency）

- [x] 2.1 確保所有 `@webpage.page()` route 使用 `get_page_user`（All page routes use page-aware auth dependency）：修改 `src/gamification/badges/router.py` 的 `badges_page`，將 `get_current_user` 改為 `get_page_user`，確保 badges page redirects unauthenticated users
- [x] 2.2 修改 `src/gamification/leaderboard/router.py` 的 `leaderboard_page`：將 `get_current_user` 改為 `get_page_user`（頁面 auth 依賴統一；確保 leaderboard page redirects unauthenticated users）
- [x] 2.3 修改 `src/community/feed/router.py` 的 `feed_page`：將 `get_current_user` 改為 `get_page_user`（頁面 auth 依賴統一；確保 feed page redirects unauthenticated users）

## 3. 修復 Check-in PRG 行為

- [x] 3.1 修改 `src/tasks/checkin/router.py` 的 `checkin_browser`（checkin PRG 行為區分）：區分 `"Student has already checked in today"` 錯誤（redirect 無 error 參數）與其他 ValueError（redirect 帶 error 參數），符合需求：Student performs daily check-in via browser form — already checked in redirects to dashboard without error

## 4. 補足 Dashboard Context 變數

- [x] 4.1 在 `src/pages/router.py` 的 `dashboard_page` 中加入 `stats.badge_count`：使用 `BadgeAward.find(BadgeAward.student_id == user_id).count()` 查詢（對應需求：Dashboard is the unified authenticated entry point — Student views dashboard with full stats）
- [x] 4.2 加入 `stats.submission_count`：使用 `TaskSubmission.find(TaskSubmission.student_id == user_id).count()` 查詢
- [x] 4.3 加入 `stats.streak_days`：暫設為 `0`（streak 計算邏輯尚未實作，設計決策：Dashboard context 補足策略）
- [x] 4.4 加入 `badges`：使用 `get_student_badges(user_id)` 取最新 10 筆（badge strip 資料）
- [x] 4.5 加入 `recent_activities`：合併查詢 `CheckinRecord`、`TaskSubmission`、`BadgeAward` 三集合（各取最新 20 筆），轉換為統一格式 `{type, description, timestamp}` 並按時間降序排列，最多取 20 筆（對應設計決策：Dashboard context 補足策略）
- [x] 4.6 在 teacher 模式的 class loop 中加入 `member_count`：使用 `ClassMembership.find(ClassMembership.class_id == class_id).count()` 查詢，加入每個 class status 物件（對應需求：Teacher views dashboard with member counts）

## 5. Template URL 路徑統一（url_for 重構）

- [x] 5.1 重構 `src/templates/shared/base.html`：將 sidebar、tablet nav、mobile bottom bar、header 中所有硬編碼路徑改為 `url_for(...)` 呼叫（包含 `dashboard_page`、`badges_page`、`class_members_page`、`templates_list_page`、`admin_users_list_page`、`admin_classes_list_page`、`admin_overview_page`、`login_page`、`logout`）
- [x] 5.2 重構 `src/templates/student/dashboard.html`：將 checkin form action、submit 連結、teacher 工具欄等硬編碼路徑改為 `url_for(...)` 呼叫（含 `checkin_browser`、`submit_task_page`、`class_members_page`、`checkin_config_page`、`templates_list_page`、`leaderboard_page`、`points_manage_page`、`admin_users_list_page`、`admin_overview_page`）
- [x] 5.3 重構 `src/templates/student/submit_task.html`：back 連結改為 `url_for('dashboard_page')`；form action 改為 `url_for('submit_task_form', class_id=class_id)`
- [x] 5.4 重構 admin templates（`layout.html`、`index.html`、`users_list.html`、`user_form.html`、`system_settings.html`、`classes_list.html`）：所有路徑改為 `url_for(...)`；`download_import_template` 使用 `.include_query_params(type='student'/'staff')`
- [x] 5.5 重構 `src/templates/login.html`：form action 改為 `url_for('login_form')`
- [x] 5.6 重構 `src/templates/community/feed.html`：`delete_post`、`add_reaction` 等連結改為 `url_for(...)`
- [x] 5.7 重構 teacher templates（`class_members.html`、`template_assign.html`、`template_form.html`、`templates_list.html`、`points_manage.html`）：所有路徑改為 `url_for(...)`
- [x] 5.8 修復測試 fixture：補足 `tests/test_pages.py`、`test_dashboard_and_page_bugs.py`、`test_ui_polish.py`、`test_checkin_config_page.py`、`test_task_scheduling.py`、`test_setup_wizard.py`、`test_admin_pages.py` 中缺少的 router（`badges_router`、`points_router`、`checkin_router`、`templates_router`、`pages_router`、`auth_router`、`users_router` 等）及 Beanie 模型（`TaskScheduleRule`、`BadgeAward`、`BadgeDefinition` 等）
