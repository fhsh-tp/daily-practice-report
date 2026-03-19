## Context

現有 `TaskAssignment` model 是 `template_id + class_id + date`（一對一），每次指派只能選一天。`template_assign.html` 頁面已有基本日期選擇器。簽到後端已有 `CheckinConfig`（weekdays + window）和 `DailyCheckinOverride`，但 `/classes/{id}/checkin-config` 和 `/classes/{id}/checkin-overrides` 都是純 API，無對應頁面。

## Goals / Non-Goals

**Goals:**
- 支援四種任務排程模式，批次產生 TaskAssignment records
- 每個排程規則可設提交次數上限（per student）
- 教師可透過 Web 頁面設定、查看班級簽到時間窗口與單日 override

**Non-Goals:**
- 不引入 cron job 或背景工作——所有排程在教師儲存時同步展開
- 不支援學生自選提交日期（日期由排程決定）
- 不修改 CheckinConfig 的後端邏輯（只加 UI）

## Decisions

### TaskScheduleRule 展開後批次建立 TaskAssignment records

建立 `TaskScheduleRule` document 儲存規則參數；儲存時同步展開（`expand_schedule_rule()`）產生對應的 `TaskAssignment` records，與現有查詢邏輯完全相容。

```
TaskScheduleRule:
  template_id: str
  class_id: str
  schedule_type: "once" | "range" | "open"
  date: date | None          # once 模式
  start_date: date | None    # range / open 模式
  end_date: date | None      # range 模式（open 時為 None）
  weekdays: list[int]        # [] = 每天，[0,1,3,4] = 週一二四五
  max_submissions_per_student: int  # 0 = 不限
  created_at: datetime
```

選擇「同步展開」而非「lazy generation」：現有 get_template_for_date 不需修改，測試覆蓋更直接。

### 指派頁面重新設計為四模式排程表單

`template_assign.html` 改為有模式切換（once / range / open），根據模式顯示對應欄位（date picker / start-end / weekday checkboxes）。送出後呼叫新的 `POST /classes/{class_id}/schedule-rules` API。

### 教師簽到設定頁：讀取現有 config 並允許更新

新增 `GET /pages/teacher/classes/{class_id}/checkin-config` 頁面，顯示現有 `CheckinConfig`（若無則顯示預設），教師可：
- 勾選開放星期（週一到週日多選）
- 設定時間窗口（開始時間、結束時間，UTC）
- 新增/覆蓋單日 override（`POST /classes/{class_id}/checkin-overrides`）

## Risks / Trade-offs

- [open 模式無 end_date] 若教師設定了開放式排程，assignments 可能累積過多 → 限制 open 模式最多展開未來 90 天
- [展開時間] 大範圍日期區間展開可能產生大量 records → 限制 range 模式最多 365 天
- [週期修改] 修改已展開的規則不會自動同步既有 assignments → 文件說明需手動刪除舊 assignments（本次不實作 sync）
