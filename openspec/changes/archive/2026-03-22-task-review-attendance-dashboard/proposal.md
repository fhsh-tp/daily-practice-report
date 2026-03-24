## Why

目前系統缺乏對學生出席與作業提交的審查機制：老師無法對簽到記錄進行手動校正（例如補發遲到積分或撤銷缺席），作業提交後積分立即入帳也沒有退回機制。學生端的 Dashboard 同時塞入班級資訊與任務，資訊密度過高；側邊欄的「新增班級」按鈕在非 Dashboard 頁面無法運作。

## What Changes

- 新增**出席管理**功能：老師可依日期查看班級出席狀況，對例外情況進行手動標記（遲到補分、缺席撤銷）
- 新增**作業審查**功能：老師可對任務提交進行確認或退回，退回時填寫原因並可設定補繳期限，退回後系統自動撤銷積分
- `TaskSubmission` 新增 `status`（pending/approved/rejected）、`rejection_reason`、`resubmit_deadline`、`parent_submission_id` 欄位
- 新增 `AttendanceCorrection` 文件記錄老師對出席的手動校正
- 學生**動態區**新增作業審查事件（確認、退回）
- 學生**Dashboard** 重構：僅顯示當天所有班級的任務（含搜尋），班級導航移至側邊欄
- 學生**側邊欄**新增「我的班級」區塊（含任務歷史、積分排行入口）
- 修正「新增班級」按鈕在非 Dashboard 頁面無作用的 Bug

## Capabilities

### New Capabilities

- `attendance-management`: 老師可查看每日出席列表，標記遲到（補部分積分）或實際未到（撤銷積分），以 `AttendanceCorrection` 文件記錄異常
- `submission-approval`: 老師可對已提交的作業進行確認或退回；退回需填原因與補繳期限；退回觸發積分撤銷；補繳為獨立新記錄

### Modified Capabilities

- `checkin`: 新增出席校正記錄（`AttendanceCorrection`），CheckinRecord 維持不變，積分追回/補發透過 PointTransaction 處理
- `task-submissions`: 新增 `status`、`rejection_reason`、`resubmit_deadline`、`parent_submission_id` 欄位；提交後預設 `status=pending`，積分仍立即給予
- `submission-review`: 從單純留評語擴充為完整審查流程（approve/reject），含退回通知頁面
- `web-pages`: 學生 Dashboard 重構（當天任務 + 搜尋）；學生側邊欄新增班級導覽；修正新增班級按鈕 Bug

## Impact

- **Affected specs**: `checkin`, `task-submissions`, `submission-review`, `web-pages`（修改）；`attendance-management`, `submission-approval`（新增）
- **Affected code**:
  - `src/tasks/submissions/models.py` — 新增欄位
  - `src/tasks/checkin/models.py` — 新增 AttendanceCorrection document
  - `src/tasks/submissions/router.py` — 新增 approve/reject endpoints
  - `src/tasks/checkin/router.py` — 新增出席管理 endpoints
  - `src/gamification/points/router.py` — 整合退回積分撤銷
  - `src/templates/teacher/submission_review.html` — 重構為 approve/reject 介面
  - `src/templates/teacher/points_manage.html` — 移除通用追回，拆分為簽到/作業兩個入口
  - `src/templates/student/dashboard.html` — 重構為當天任務 + 搜尋
  - `src/templates/shared/base.html` — 學生側邊欄班級導覽、修正新增班級按鈕
  - `src/templates/student/` — 新增被退回作業詳細頁、班級頁面
  - `src/templates/teacher/` — 新增出席管理頁面
