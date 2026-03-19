## Why

任務排程目前只支援一次指派一個日期（`TaskAssignment = template + date`），無法批次排程或設定週期性任務。此外，教師無法透過 Web 介面設定班級的簽到時間窗口（後端 API 存在但無 UI），導致簽到功能實際上無法使用。

## What Changes

- **新增**：`TaskScheduleRule` model，支援四種排程模式：一次性（指定單日）、日期區間（每天）、日期區間 + 星期篩選（如週一二四五）、開放式（從某天起每天）
- **新增**：每個排程規則可設定 `max_submissions_per_student`（0 = 不限次數）
- **修改**：「指派日期」頁面改為「排程設定」頁面，支援上述四種模式選擇
- **新增**：教師簽到設定 UI 頁面（`/pages/teacher/classes/{class_id}/checkin-config`），可設定開放星期、時間窗口、以及單日 override

## Capabilities

### New Capabilities

- `task-schedule-rule`: 任務排程規則——定義排程模式、日期範圍、星期篩選、提交次數上限，批次展開為 TaskAssignment

### Modified Capabilities

- `task-templates`: 任務指派流程改為透過排程規則，而非單次指定日期
- `checkin`: 新增「教師可透過 Web 介面設定簽到時間窗口」需求

## Impact

- Affected specs: new `task-schedule-rule`、`task-templates`（modified）、`checkin`（modified）
- Affected code:
  - `src/tasks/templates/models.py` — 新增 `TaskScheduleRule` document
  - `src/tasks/templates/service.py` — 新增排程展開邏輯
  - `src/tasks/templates/router.py` — 新增排程 API、修改指派頁面路由
  - `src/templates/teacher/template_assign.html` — 改為排程設定頁面（支援四種模式）
  - `src/tasks/checkin/router.py` — 新增教師設定頁面路由
  - `src/templates/teacher/` — 新增 `checkin_config.html`
  - `src/templates/teacher/class_members.html` — 新增簽到設定連結
