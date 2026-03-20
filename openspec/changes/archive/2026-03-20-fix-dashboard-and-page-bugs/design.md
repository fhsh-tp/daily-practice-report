## Context

系統審查（2026-03-20）發現儀表板及多個頁面存在 runtime bug 和 spec 不符問題。問題涵蓋：template 渲染崩潰（datetime slicing、null object access）、頁面 auth 依賴錯用（回 JSON 401 而非導向登入頁）、以及 `dashboard_page` router 缺少 template 所需的多個 context 變數。

## Goals / Non-Goals

**Goals:**

- 修復所有會造成 HTTP 500 的 template runtime bug
- 統一頁面 auth 依賴為 `get_page_user`（重導向行為）
- 完整提供 dashboard template 所需的 context 變數
- 符合 checkin PRG spec 對「已簽到」vs「時間關閉」的不同 redirect 行為

**Non-Goals:**

- 不改動 API（JSON）endpoint 的行為
- 不重新設計 UI 或新增頁面
- 不引入新資料模型

## Decisions

### Dashboard context 補足策略

`dashboard_page` route 需要提供以下額外資料：
- **`stats.badge_count`**：查詢 `BadgeAward.find(student_id=user_id).count()`
- **`stats.submission_count`**：查詢 `TaskSubmission.find(student_id=user_id).count()`
- **`stats.streak_days`**：暫設為 0（無現成 streak 計算邏輯，需保留 stub，不因缺少而崩潰）
- **`badges`**：查詢 `get_student_badges(user_id)` 取最新 10 筆
- **`recent_activities`**：整合查詢 `CheckinRecord`、`TaskSubmission`、`BadgeAward` 三集合，取最新 20 筆合併排序
- **`class_status.member_count`**（教師模式）：在 class loop 內加入 `ClassMembership.find(class_id).count()`

**為何 streak_days 暫設 0**：目前沒有跨日期的連續簽到計算邏輯。Template 已做 `if stats is defined else '—'` 保護，streak=0 是安全的 stub，不影響其他功能。

### 頁面 auth 依賴統一

所有使用 `@webpage.page()` 裝飾器的 route handler 必須使用 `get_page_user` 依賴。`get_page_user` 在未登入時回 HTTP 302 到 `/pages/login?next=<path>`；`get_current_user` 回 HTTP 401 JSON，不適用於 HTML 頁面。

受影響的三個 route 分別在 `badges/router.py`、`leaderboard/router.py`、`feed/router.py`。

### submit_task.html null guard

當 `template is None` 時，`{{ template.name }}` 會造成 Jinja2 UndefinedError。解法：在 template 頂部加入 `{% if template %}...{% else %}<提示訊息>{% endif %}` 包覆整個表單區塊。

### badges.html datetime 修復

`award.awarded_at` 是 Python `datetime` 物件，不支援 `[:10]` 切片。改為 `award.awarded_at.strftime('%Y-%m-%d')`。

### checkin PRG 行為區分

`do_checkin` 對兩種情況都拋 `ValueError`，需在 `checkin_browser` 中區分：
- `"Student has already checked in today"` → redirect to dashboard **無 error 參數**
- 其他 ValueError（視窗關閉等） → redirect to dashboard **帶 `?error=` 參數**

## Risks / Trade-offs

- **[Risk] `recent_activities` 效能**：三個 Collection 各自查詢後 Python 合併排序，O(N log N)。在小型班級環境（< 100 學生）可接受；大規模部署需 aggregation pipeline。→ Mitigation：目前取各 collection 最新 20 筆後合併，降低查詢量。
- **[Risk] streak_days stub 為 0**：使用者看到 0 天，功能視覺上不完整。→ Mitigation：這是已知限制，在設計上明確記錄。streak 功能需要獨立 change。
