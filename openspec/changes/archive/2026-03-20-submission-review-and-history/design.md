## Context

`TaskSubmission` model 目前記錄提交內容但無 teacher comment 欄位。積分系統（`PointLedger`）有 `reason` 欄位可記錄操作原因。學生儀表板只顯示今日資訊，無歷史回顧。

## Goals / Non-Goals

**Goals:**

- 教師可對每筆提交留一則 comment（可覆寫）
- 教師可對特定提交觸發積分追回（扣分），並附說明
- 學生可查看自己所有提交的歷史列表，含 comment

**Non-Goals:**

- 不實作多則 comment 或討論串（單一欄位即可）
- 不實作 comment 通知推播（可在 discord-integration 中補充）
- 不允許學生修改已提交的內容

## Decisions

### teacher_comment 欄位設計

**決策**：在 `TaskSubmission` model 新增可選欄位 `teacher_comment: str | None = None` 與 `reviewed_at: datetime | None = None`。

**理由**：最小侵入性。單一欄位滿足「讓學生了解內容」的需求；不需要複雜的 comment 模型。

### 積分追回操作設計

**決策**：新增 `POST /api/points/deduct` 端點（或擴充現有積分端點），傳入 student_id、class_id、amount（負數）、reason（必填），由教師發起。在 `PointLedger` 記錄新的 `entry_type: "teacher_deduct"` 類型。

**理由**：利用現有 `PointLedger` 機制，不需要額外的撤銷表；reason 欄位提供稽核軌跡。

### 審閱頁入口設計

**決策**：審閱頁從班級 Hub 頁的「提交審閱」卡片進入，路由為 `GET /pages/teacher/class/<class_id>/submissions`。

**理由**：符合 teacher-class-ux-refactor 後的 hub 中心化設計。

### 學習歷程頁入口設計

**決策**：學生側邊欄新增「學習歷程」連結，路由為 `GET /pages/student/history`。

**理由**：與現有「我的徽章」連結並列，為學生提供個人成長的完整視圖。

## Risks / Trade-offs

- [資料遷移] `TaskSubmission` 新增欄位。Mitigation：欄位為可選（`None`），不影響既有資料。
- [效能] 學習歷程頁可能載入大量提交記錄。Mitigation：前端分頁或限制初始載入筆數（最新 50 筆）。
