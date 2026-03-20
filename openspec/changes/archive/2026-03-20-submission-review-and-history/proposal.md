## Why

教師目前無法查閱學生的提交內容，也無法給予回饋或糾正誤用積分的情況；學生也缺乏回顧自身學習歷程的介面。此 change 補足教師審閱流程與學生學習歷程兩個核心功能缺口。

## What Changes

- **教師審閱介面**：教師可在班級 hub 或班級成員管理頁進入「提交審閱」頁，查看每位學生的所有提交記錄，並可針對每筆提交留下 comment。
- **積分追回**：教師可在審閱頁對特定提交執行「追回積分」操作，從該學生扣除對應積分（並留下操作記錄）。
- **學生學習歷程頁**：學生可查看自己所有歷史提交的時間軸列表，每筆包含提交內容、任務名稱、時間、獲得積分，以及教師的 comment（若有）。

## Capabilities

### New Capabilities

- `submission-review`：教師審閱學生提交、留 comment、追回積分的能力

### Modified Capabilities

- `task-submissions`：提交資料模型新增 teacher_comment 欄位；學生端新增學習歷程頁
- `points-system`：新增教師主動扣分（積分追回）的操作類型

## Impact

- Affected specs: `submission-review`（新）、`task-submissions`、`points-system`
- Affected code:
  - `src/tasks/submissions/models.py`（新增 teacher_comment 欄位）
  - `src/tasks/submissions/router.py`（新增 comment API、學習歷程 API）
  - `src/gamification/points/service.py`（新增扣分操作）
  - `src/templates/teacher/submission_review.html`（新 template）
  - `src/templates/student/learning_history.html`（新 template）
  - `src/pages/router.py`（新增學習歷程路由）
