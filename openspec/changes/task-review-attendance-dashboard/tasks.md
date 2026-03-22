## 1. 資料模型

- [ ] 1.1 在 `src/tasks/submissions/models.py` 新增 `TaskSubmission` 的 review 欄位：`status`（預設 `"pending"`）、`rejection_reason`、`resubmit_deadline`、`parent_submission_id`；積分仍立即入帳不變（TaskSubmission stores review state / TaskSubmission 加 status 欄位，積分仍立即入帳）
- [ ] 1.2 在 `src/tasks/checkin/models.py` 新增 `AttendanceCorrection` Beanie document，包含 `class_id`、`student_id`、`date`、`status`、`partial_points`、`created_by`、`created_at`（AttendanceCorrection document）
- [ ] 1.3 在 `src/gamification/points/models.py` 的 `PointTransaction.source_event` 補充 `"checkin_manual_late"`、`"checkin_manual_revoke"`、`"submission_rejected"`、`"submission_reapproved"` 文件註解

## 2. 簽到重複提交防護調整

- [ ] 2.1 在 `src/tasks/submissions/service.py` 修改查重邏輯：只有 `status != "rejected"` 的記錄才計入一日唯一限制（Student submits daily task / Duplicate submission rejected when active submission exists / Resubmission allowed after rejection）

## 3. 出席管理後端

- [ ] 3.1 在 `src/tasks/checkin/router.py` 新增 `GET /pages/teacher/classes/{class_id}/attendance` 頁面路由，讀取指定日期的班級成員與 `CheckinRecord`、`AttendanceCorrection` 資料（Teacher views daily attendance list）
- [ ] 3.2 在 `src/tasks/checkin/router.py` 新增 `POST /api/classes/{class_id}/attendance/correct` 端點，處理遲到補分（`status: "late"`）與撤銷（`status: "absent"`），建立或更新 `AttendanceCorrection`，並建立對應 `PointTransaction`（Teacher marks absent student as late / Teacher revokes check-in for student who was actually absent / Existing correction is overwritten）
- [ ] 3.3 驗證遲到補分數量範圍（1 ≤ partial_points ≤ checkin_points），超出範圍回傳 HTTP 422（Partial points must be between 1 and checkin_points）

## 4. 作業審查後端（AttendanceCorrection 記錄例外，不修改 CheckinRecord）

- [ ] 4.1 在 `src/tasks/submissions/router.py` 新增 `POST /api/submissions/{submission_id}/approve` 端點：設定 `status="approved"`；若前狀態為 `"rejected"` 則補發積分（Teacher approves a task submission / Teacher approves a previously rejected submission）
- [ ] 4.2 在 `src/tasks/submissions/router.py` 新增 `POST /api/submissions/{submission_id}/reject` 端點：設定 `status="rejected"`、儲存 `rejection_reason` 與 `resubmit_deadline`，建立負數 `PointTransaction`；`rejection_reason` 為空時回傳 HTTP 422（Teacher rejects a task submission / Rejection without reason is rejected）
- [ ] 4.3 在退回後，建立動態 feed 事件（`submission_rejected`）；在確認後建立 `submission_approved` 事件（Student sees submission review status in activity feed / Approved submission appears in feed / Rejected submission appears in feed）

## 5. 作業審查前端

- [ ] 5.1 重構 `src/templates/teacher/submission_review.html`：為每筆提交新增狀態 badge（pending/approved/rejected）、「確認」按鈕（呼叫 approve 端點）、「退回」inline panel（含原因欄位與補繳期限選擇器）（Teacher can view all student submissions for a class / Teacher approves submission from review page / Teacher rejects submission from review page / Teacher opens reject panel / Empty rejection reason blocked / Submission list shows status badge）
- [ ] 5.2 確認 page 留在審查頁不跳轉，操作後局部更新 badge（Teacher clicks approve / Teacher confirms rejection）

## 6. 學生退回通知

- [ ] 6.1 在 `src/tasks/submissions/router.py` 新增 `GET /pages/student/submissions/{submission_id}/rejection` 頁面路由，驗證擁有者身分（Student views rejection detail page / Non-owner cannot access rejection detail）
- [ ] 6.2 新增 `src/templates/student/submission_rejection.html`，顯示退回原因、補繳期限與原始提交內容（Student views rejection detail）
- [ ] 6.3 修改 `src/templates/student/learning_history.html`：顯示 `status` badge，rejected 記錄顯示原因與退回詳情連結（History shows review status / Rejected submission shows link to detail）

## 7. 補繳流程

- [ ] 7.1 修改 `src/tasks/submissions/router.py` 的提交端點：若學生有 rejected 提交且 `resubmit_deadline` 未過，允許建立新提交並設定 `parent_submission_id`（Student resubmits a rejected task / No resubmit when deadline has passed or was not set）
- [ ] 7.2 在補繳頁（`submit_task.html`）顯示補繳截止日期提示（若有 rejected 提交且有期限）

## 8. 出席管理頁面

- [ ] 8.1 新增 `src/templates/teacher/attendance_manage.html`，依日期顯示學生出席狀態，支援日期選擇器，預設今日（Teacher views daily attendance list / Page defaults to today's date / AttendanceCorrection reflects current status on attendance page）
- [ ] 8.2 頁面內嵌各學生的遲到補分輸入（1 ~ checkin_points 範圍限制）與「撤銷已到」按鈕，操作後局部更新（Teacher marks absent student as late / Teacher revokes check-in for student who was actually absent）

## 9. 積分管理頁面整合

- [ ] 9.1 在 `src/templates/teacher/points_manage.html` 新增出席管理連結卡片或按鈕，導向 attendance 頁面（Teacher accesses attendance management from points manage page）

## 10. 學生 Dashboard 重構

- [ ] 10.1 修改 `src/pages/router.py` 的 dashboard 路由，回傳所有班級當天任務資料（含班級名稱、老師姓名、任務名稱、已繳狀態）（Student dashboard shows today's tasks across all classes with search）
- [ ] 10.2 重構 `src/templates/student/dashboard.html`：移除舊班級管理卡片，改為任務卡列表，新增 client-side 搜尋輸入（Student dashboard layout / Student searches tasks by task name / No tasks today shows empty state per class / Dashboard shows task cards not class management cards / 學生 Dashboard 搜尋為 Client-side）
- [ ] 10.3 Dashboard 偵測 `?create_class=1` query param，自動開啟新增班級 modal（Dashboard opens modal when param present）

## 11. 學生 Sidebar 與新增班級按鈕修正

- [ ] 11.1 修改 `src/templates/shared/base.html`：學生（非教師）sidebar 新增「我的班級」區塊，列出各班入口（展開後含任務歷史、積分排行連結）（Student sidebar shows class navigation / Student sidebar lists enrolled classes / Class entry links to task history）
- [ ] 11.2 修改「新增班級」按鈕 href 為 `?create_class=1` redirect 邏輯，移除 `dispatchEvent`（新增班級按鈕改為帶 Query Param 的連結 / Create class button navigates to dashboard with param / Create class button works from any page）

## 12. 學生班級頁面

- [ ] 12.1 新增學生班級任務歷史頁面路由與模板（`src/templates/student/class_history.html`），顯示該班歷史提交記錄與審查狀態（Student can view learning history with review status）

## 13. 測試

- [ ] 13.1 新增 `tests/test_attendance_management.py`：測試出席管理端點（遲到補分、撤銷、重複校正覆蓋、範圍驗證）
- [ ] 13.2 新增 `tests/test_submission_approval.py`：測試 approve/reject 端點（積分撤銷、重發、退回後再 approve、空原因驗證）
- [ ] 13.3 新增 `tests/test_resubmission.py`：測試補繳流程（parent_submission_id、期限過期、已有 pending 時不允許補繳）
- [ ] 13.4 更新 `tests/test_submissions.py`：補充新查重邏輯（rejected 不計入唯一性）的測試
- [ ] 13.5 更新 `tests/test_pages.py`：新增 rejection detail 頁面、attendance 頁面的存取控制測試
