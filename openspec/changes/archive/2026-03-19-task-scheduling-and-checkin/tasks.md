## 1. 資料模型 — TaskScheduleRule 展開後批次建立 TaskAssignment records

- [x] [P] 1.1 在 `tasks/templates/models.py` 新增 `TaskScheduleRule` document（欄位：`template_id`, `class_id`, `schedule_type` ("once"|"range"|"open"), `date`, `start_date`, `end_date`, `weekdays`, `max_submissions_per_student`, `created_at`）
- [x] [P] 1.2 在 `tasks/templates/service.py` 新增 `expand_schedule_rule(rule)` 函式，依 schedule_type 批次建立 TaskAssignment records（Teacher creates a one-time task schedule；Teacher creates a date-range task schedule；Teacher creates an open-ended task schedule）
- [x] 1.3 新增測試：`expand_schedule_rule` once 模式建立 1 筆 assignment；range + weekdays 模式只建立符合星期的 assignments；open 模式最多展開 90 天

## 2. 排程 API

- [x] 2.1 在 `tasks/templates/router.py` 新增 `POST /classes/{class_id}/schedule-rules` endpoint，接收排程規則、呼叫 `expand_schedule_rule()`、回傳建立的 assignment 數量（Teacher assigns template to a date via schedule rule）
- [x] 2.2 新增測試：POST schedule-rule range 模式回傳正確數量；weekday filter 正確過濾；open 模式上限 90 筆

## 3. 提交次數限制 — Teacher sets a per-student submission limit on a schedule rule

- [x] 3.1 在 `tasks/submissions/service.py` 的 `submit_task()` 中，查詢對應 `TaskScheduleRule` 的 `max_submissions_per_student`，若超出則拋出 ValueError（Teacher sets a per-student submission limit on a schedule rule；Submission rejected when limit reached）
- [x] 3.2 新增測試：已達提交上限時 submit_task 拋出 ValueError；`max_submissions_per_student=0` 時不限制（No limit when max_submissions_per_student is zero）

## 4. 排程設定頁面 — 指派頁面重新設計為四模式排程表單

- [x] 4.1 重新設計 `teacher/template_assign.html`：加入模式切換（一次性 / 日期區間 / 開放式），根據模式顯示對應欄位（date picker / start-end + weekday checkboxes），送出呼叫 `POST /classes/{class_id}/schedule-rules`（Template assign page shows four scheduling modes；Teacher assigns template to a date using range mode with weekday filter）
- [x] 4.2 新增測試：template_assign_page 載入回傳 HTTP 200

## 5. 教師簽到設定頁面 — 教師簽到設定頁：讀取現有 config 並允許更新

- [x] 5.1 在 `tasks/checkin/router.py` 新增 `GET /pages/teacher/classes/{class_id}/checkin-config` page route，查詢現有 `CheckinConfig`（若無則回傳預設值），傳入 template context（Teacher configures check-in schedule via web UI）
- [x] 5.2 建立 `templates/teacher/checkin_config.html`：顯示目前設定的開放星期（核取方塊）與時間窗口（時間輸入），送出表單呼叫 `POST /classes/{class_id}/checkin-config`（Teacher views current check-in configuration；Teacher updates active weekdays）
- [x] 5.3 在 `checkin_config.html` 頁面下方新增單日 override 區塊：輸入日期、是否啟用、可選時間窗口，送出呼叫 `POST /classes/{class_id}/checkin-overrides`（Teacher sets a single-day check-in override via web UI；Teacher disables check-in for a specific date）
- [x] 5.4 在 `teacher/class_members.html` 的教師工具列新增「簽到設定」連結至 `/pages/teacher/classes/{class_id}/checkin-config`
- [x] 5.5 在 `student/dashboard.html` 的教師工具列中同步新增「簽到設定」連結
- [x] 5.6 新增測試：GET checkin-config page 回傳 HTTP 200；未設定時使用預設值
