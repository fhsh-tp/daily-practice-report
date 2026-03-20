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

- [ ] 4.1 在 `src/pages/router.py` 的 `dashboard_page` 中加入 `stats.badge_count`：使用 `BadgeAward.find(BadgeAward.student_id == user_id).count()` 查詢（對應需求：Dashboard is the unified authenticated entry point — Student views dashboard with full stats）
- [ ] 4.2 加入 `stats.submission_count`：使用 `TaskSubmission.find(TaskSubmission.student_id == user_id).count()` 查詢
- [ ] 4.3 加入 `stats.streak_days`：暫設為 `0`（streak 計算邏輯尚未實作，設計決策：Dashboard context 補足策略）
- [ ] 4.4 加入 `badges`：使用 `get_student_badges(user_id)` 取最新 10 筆（badge strip 資料）
- [ ] 4.5 加入 `recent_activities`：合併查詢 `CheckinRecord`、`TaskSubmission`、`BadgeAward` 三集合（各取最新 20 筆），轉換為統一格式 `{type, description, timestamp}` 並按時間降序排列，最多取 20 筆（對應設計決策：Dashboard context 補足策略）
- [ ] 4.6 在 teacher 模式的 class loop 中加入 `member_count`：使用 `ClassMembership.find(ClassMembership.class_id == class_id).count()` 查詢，加入每個 class status 物件（對應需求：Teacher views dashboard with member counts）
