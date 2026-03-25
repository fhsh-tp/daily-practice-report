# DPRS 教師操作手冊

> **Daily Practice Report System (DPRS)** — 每日練習回報系統
>
> 本文件以教師視角，依序說明從建立班級到學期結束封存的完整操作流程。

---

## 目錄

1. [登入與 Dashboard](#1-登入與-dashboard)
2. [建立班級](#2-建立班級)
3. [邀請學生加入](#3-邀請學生加入)
4. [建立任務範本（Task Template）](#4-建立任務範本task-template)
5. [指派任務](#5-指派任務)
6. [設定每日簽到（Check-in）](#6-設定每日簽到check-in)
7. [審閱學生提交（Review Submissions）](#7-審閱學生提交review-submissions)
8. [出席管理（Attendance Management）](#8-出席管理attendance-management)
9. [遊戲化設定](#9-遊戲化設定)
10. [Discord Webhook 整合](#10-discord-webhook-整合)
11. [班級封存（Archive）](#11-班級封存archive)

---

## 1. 登入與 Dashboard

教師使用帳號登入後，系統會依據使用者的 Permission（權限）自動顯示教師版 Dashboard（儀表板）。Dashboard 提供以下資訊：

- **班級清單** — 教師擁有或協管的所有班級，含班級名稱與成員數量
- **今日簽到狀況** — 各班簽到率概覽
- **待審閱提交** — 需要教師審查的學生提交

> **提示：** 已封存（Archived）的班級不會出現在 Dashboard 主清單中。

---

## 2. 建立班級

### 操作步驟

1. 進入 Dashboard，點選「建立班級」
2. 填寫以下欄位：
   - **班級名稱**（`name`）— 必填
   - **班級說明**（`description`）— 選填
   - **可見度**（Visibility）— `public`（公開）或 `private`（私有），預設為 `public`
3. 送出後，系統自動產生一組 **Invite Code（邀請碼）**

### 對應 API

```
POST /classes
```

Request Body：

```json
{
  "name": "112 上學期體育訓練班",
  "description": "每日體能訓練紀錄",
  "visibility": "public"
}
```

Response（成功 `201`）：

```json
{
  "id": "class_abc123",
  "name": "112 上學期體育訓練班",
  "invite_code": "XK9F2M"
}
```

### 變更可見度

建立後可隨時切換班級的 Visibility：

```
PATCH /classes/{class_id}/visibility
```

```json
{
  "visibility": "private"
}
```

- **Public 班級**：學生可在公開班級清單中看到並直接加入
- **Private 班級**：學生必須持有 Invite Code 才能加入

---

## 3. 邀請學生加入

DPRS 提供兩種邀請方式：

### 方式一：分享 Invite Code

將邀請碼提供給學生（口頭、訊息、公告等），學生自行在系統中輸入邀請碼加入。

如需重新產生邀請碼（例如舊碼外洩），可使用：

```
POST /classes/{class_id}/invite-code/regenerate
```

> **注意：** 重新產生後，舊的邀請碼將立即失效。

### 方式二：批次邀請（Batch Invite）

教師可搜尋尚未加入班級的學生，再一次批量加入。

**步驟 1：搜尋學生**

```
GET /classes/{class_id}/invite/search?q=王&type=name
```

- `q` — 搜尋關鍵字
- `type` — 搜尋類型：`name`（姓名）或 `class_name`（行政班級名稱）

**步驟 2：批次加入**

```
POST /classes/{class_id}/invite/batch
```

```json
{
  "user_ids": ["user_001", "user_002", "user_003"]
}
```

Response：

```json
{
  "added": 3
}
```

### 成員管理

- **查看成員清單**：`GET /classes/{class_id}/members`
- **移除成員**：`DELETE /classes/{class_id}/members/{user_id}`
- **提升為教師（Co-teacher）**：`PATCH /classes/{class_id}/members/{user_id}/promote`

---

## 4. 建立任務範本（Task Template）

Task Template（任務範本）定義了學生每日需要填寫的表單結構。一個班級可擁有多個範本。

### 操作步驟

1. 進入班級管理頁 > 「任務範本」
2. 點選「新增範本」
3. 填寫以下欄位：
   - **範本名稱**（`name`）— 必填
   - **說明**（`description`）— 選填
   - **欄位定義**（`fields`）— 至少一個欄位

### 欄位類型（Field Type）

| 類型 | 說明 | 範例用途 |
|------|------|----------|
| `text` | 純文字 | 訓練內容摘要 |
| `markdown` | Markdown 格式文字 | 訓練心得 |
| `number` | 數值 | 跑步距離（公里） |
| `checkbox` | 勾選方塊 | 是否完成伸展 |

### 對應 API

```
POST /classes/{class_id}/templates
```

```json
{
  "name": "體能訓練日誌",
  "description": "每日體能訓練紀錄表",
  "fields": [
    { "name": "訓練項目", "field_type": "text", "required": true },
    { "name": "訓練時間（分鐘）", "field_type": "number", "required": true },
    { "name": "訓練心得", "field_type": "markdown", "required": false },
    { "name": "已完成收操", "field_type": "checkbox", "required": false }
  ]
}
```

### 編輯與封存

- **編輯範本**：`PATCH /templates/{template_id}` — 可更新 `name`、`description`、`fields`
- **封存範本**：`PATCH /templates/{template_id}/archive` — 不再使用但保留紀錄
- **取消封存**：`PATCH /templates/{template_id}/unarchive`
- **刪除範本**：`DELETE /templates/{template_id}` — 僅在無關聯資料時可刪除，否則回傳 `409 Conflict`

---

## 5. 指派任務

建立範本後，需要將範本「指派」到特定日期，學生才能在當天看到任務並提交。

### 方式一：單次指派

將範本指派到特定日期：

```
POST /classes/{class_id}/template-assignments
```

```json
{
  "template_id": "tmpl_abc123",
  "date": "2026-04-01"
}
```

### 方式二：排程規則（Schedule Rule）

使用 Schedule Rule（排程規則）可一次建立多筆指派，支援三種模式：

#### `once` — 單次

指定單一日期：

```json
{
  "template_id": "tmpl_abc123",
  "schedule_type": "once",
  "date": "2026-04-01"
}
```

#### `range` — 日期範圍

在 `start_date` 到 `end_date` 之間，依 `weekdays` 篩選指派日：

```json
{
  "template_id": "tmpl_abc123",
  "schedule_type": "range",
  "start_date": "2026-04-01",
  "end_date": "2026-04-30",
  "weekdays": [0, 1, 2, 3, 4]
}
```

> `weekdays` 對照：0 = 週一、1 = 週二、...、6 = 週日。空陣列 `[]` 代表每天。

#### `open` — 開放式

從 `start_date` 開始，無結束日期：

```json
{
  "template_id": "tmpl_abc123",
  "schedule_type": "open",
  "start_date": "2026-04-01",
  "weekdays": [0, 1, 2, 3, 4]
}
```

### 額外選項

| 參數 | 說明 |
|------|------|
| `max_submissions_per_student` | 每位學生最大提交次數，`0` 表示不限制 |
| `sync_discord` | 設為 `true` 時，建立排程後自動透過 Discord Webhook 發送通知（需先設定 Webhook，見[第 10 節](#10-discord-webhook-整合)）|

### 對應 API

```
POST /classes/{class_id}/schedule-rules
```

Response：

```json
{
  "assignments_created": 22
}
```

---

## 6. 設定每日簽到（Check-in）

Check-in（簽到）系統讓教師管控學生每日出席。教師可設定哪幾天啟用簽到，以及每日的簽到時間窗口（Time Window）。

### 全域設定（Global Config）

設定班級的常態簽到規則：

```
POST /classes/{class_id}/checkin-config
```

```json
{
  "active_weekdays": [0, 1, 2, 3, 4],
  "window_start": "08:00",
  "window_end": "09:30"
}
```

| 參數 | 說明 |
|------|------|
| `active_weekdays` | 啟用簽到的星期，0 = 週一 ... 6 = 週日 |
| `window_start` | 簽到開始時間（HH:MM，UTC） |
| `window_end` | 簽到結束時間（HH:MM，UTC） |

> 若不設定 `window_start` / `window_end`，則全天皆可簽到。

### 每日覆寫（Daily Override）

針對特殊日期覆蓋全域設定（如假日停止簽到、延長時間等）：

```
POST /classes/{class_id}/checkin-overrides
```

```json
{
  "date": "2026-04-05",
  "active": false
}
```

| 參數 | 說明 |
|------|------|
| `date` | 目標日期（YYYY-MM-DD） |
| `active` | `true` = 啟用、`false` = 停用 |
| `window_start` | 覆寫該日的開始時間（選填） |
| `window_end` | 覆寫該日的結束時間（選填） |

> **範例：** 清明節停止簽到 → `active: false`；補課日延長時段 → `active: true, window_start: "07:00", window_end: "10:00"`。

---

## 7. 審閱學生提交（Review Submissions）

### 查看提交

教師可依班級與日期查看所有學生的提交：

```
GET /classes/{class_id}/submissions?date_param=2026-04-01
```

不指定 `date_param` 時，預設顯示當日的提交。

Web 介面提供按學生分組的審閱頁面，顯示每位學生的提交記錄。

### 核准提交（Approve）

```
POST /api/submissions/{submission_id}/approve
```

- 核准後，系統自動發布至社群動態（Community Feed）
- 若該提交先前曾被退回，核准時會自動補回先前扣除的 Submission Points（提交點數）

### 退回提交（Reject）

```
POST /api/submissions/{submission_id}/reject
```

```json
{
  "rejection_reason": "訓練時間記錄不完整，請補充實際訓練分鐘數",
  "resubmit_deadline": "2026-04-03T23:59:00Z"
}
```

| 參數 | 說明 |
|------|------|
| `rejection_reason` | 退回原因（必填，不可為空白） |
| `resubmit_deadline` | 重新提交期限（ISO 8601 格式，選填） |

退回時系統會自動扣回該筆提交的 Submission Points。學生可在期限前重新提交。

### 新增評語（Comment）

```
POST /api/submissions/{submission_id}/comment
```

```json
{
  "comment": "跑步姿勢進步很多，繼續保持！"
}
```

---

## 8. 出席管理（Attendance Management）

教師可在出席管理頁面查看各日的簽到狀況，並對例外情況進行更正。

### 查看出席

進入班級管理 > 出席管理頁面，可選擇日期檢視。預設顯示當日出席狀態。每位學生會顯示：

- 是否已簽到
- 是否有出席更正紀錄（Attendance Correction）

### 出席更正（Attendance Correction）

```
POST /api/classes/{class_id}/attendance/correct
```

```json
{
  "student_id": "user_001",
  "date": "2026-04-01",
  "status": "late",
  "partial_points": 3
}
```

#### 更正類型

| Status | 說明 | 點數處理 |
|--------|------|----------|
| `late`（遲到）| 學生遲到但有出席 | 給予 Partial Points（部分點數），必須介於 1 至 `checkin_points` 之間 |
| `absent`（缺席）| 學生實際未出席但有簽到紀錄 | 自動扣回該日的 Checkin Points（簽到點數） |

> **注意：** 對同一學生、同一日期重複更正時，系統會覆蓋（Overwrite）先前的更正紀錄。

---

## 9. 遊戲化設定

DPRS 的 Gamification（遊戲化）系統包含四大模組，皆以班級為單位進行設定。

### 9.1 點數系統（Points）

每個班級可獨立配置自動獎勵的點數額度：

```
PATCH /classes/{class_id}/point-config
```

```json
{
  "checkin_points": 5,
  "submission_points": 10
}
```

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `checkin_points` | 每次成功簽到自動獲得的點數 | 5 |
| `submission_points` | 每次成功提交自動獲得的點數 | 10 |

#### 手動扣點

教師可對個別學生手動扣除點數：

```
POST /api/points/deduct
```

```json
{
  "student_id": "user_001",
  "class_id": "class_abc123",
  "amount": 5,
  "reason": "未依規定穿著訓練服裝"
}
```

#### 撤銷點數

針對特定學生撤銷點數（用途與扣點類似，但語意為「撤銷先前的獎勵」）：

```
POST /classes/{class_id}/students/{student_id}/point-revoke
```

```json
{
  "amount": 10,
  "reason": "誤發獎勵點數"
}
```

### 9.2 徽章（Badges）

Badge（徽章）是授予學生的成就標記。

#### 建立徽章

```
POST /classes/{class_id}/badges
```

```json
{
  "name": "連續簽到七天",
  "description": "連續七天完成每日簽到",
  "icon": "🔥",
  "trigger_key": "streak_7_days"
}
```

| 參數 | 說明 |
|------|------|
| `name` | 徽章名稱 |
| `description` | 徽章說明 |
| `icon` | 顯示圖示（Emoji） |
| `trigger_key` | 自動觸發規則的 Key。設定後，系統在學生簽到或提交時自動評估是否符合條件並頒發。設為 `null` 表示僅限手動頒發。|

#### 手動頒發徽章

```
POST /classes/{class_id}/badges/{badge_id}/award
```

```json
{
  "student_id": "user_001",
  "reason": "本月訓練表現最佳"
}
```

> 同一位學生不會重複獲得相同的徽章。若已持有，API 回傳 `409 Conflict`。

### 9.3 獎品（Prizes）

Prize（獎品）讓學生可用累積的點數兌換實體或線上獎勵。

#### 建立獎品

```
POST /classes/{class_id}/prizes
```

```json
{
  "title": "運動毛巾",
  "description": "DPRS 限定款運動毛巾",
  "prize_type": "physical",
  "image_url": "https://example.com/towel.jpg",
  "point_cost": 100,
  "visible": true
}
```

| 參數 | 說明 |
|------|------|
| `title` | 獎品名稱 |
| `description` | 獎品說明 |
| `prize_type` | `online`（線上獎品）或 `physical`（實體獎品） |
| `image_url` | 獎品圖片 URL（選填） |
| `point_cost` | 兌換所需點數 |
| `visible` | 是否對學生顯示。設為 `false` 可先建立但暫不公開 |

#### 管理獎品

- **編輯獎品**：`PATCH /prizes/{prize_id}` — 可更新任一欄位
- **刪除獎品**：`DELETE /prizes/{prize_id}`
- **查看獎品清單**：`GET /classes/{class_id}/prizes` — 教師可看到所有獎品（含隱藏的），學生僅看到 `visible: true` 的獎品

### 9.4 排行榜（Leaderboard）

Leaderboard（排行榜）根據學生的累積點數自動排名。

#### 啟用 / 停用

班級建立時，排行榜預設為**啟用**（`leaderboard_enabled: true`）。教師可在班級設定中調整此選項。

- 排行榜**啟用**時：所有班級成員（含學生）可查看排名
- 排行榜**停用**時：僅教師可查看，學生端不顯示排行榜

#### 查看排行榜

```
GET /classes/{class_id}/leaderboard
```

Response（啟用時）：

```json
{
  "visible": true,
  "leaderboard": [
    { "student_id": "user_001", "display_name": "王小明", "points": 150, "rank": 1 },
    { "student_id": "user_002", "display_name": "李小華", "points": 120, "rank": 2 }
  ]
}
```

#### 跨班排行榜

系統另提供跨班排行榜，彙總所有公開且啟用排行榜的班級：

```
GET /leaderboard
```

---

## 10. Discord Webhook 整合

DPRS 支援透過 Discord Webhook 將任務指派通知推送至 Discord 頻道。

### 設定 Webhook URL

```
PATCH /classes/{class_id}/discord-webhook
```

```json
{
  "webhook_url": "https://discord.com/api/webhooks/1234567890/abcdefg..."
}
```

**URL 格式限制：** 必須以下列前綴開頭，否則回傳 `422`：

- `https://discord.com/api/webhooks/`
- `https://discordapp.com/api/webhooks/`

### 清除 Webhook

將 `webhook_url` 設為空字串即可移除：

```json
{
  "webhook_url": ""
}
```

### 搭配排程規則使用

建立 Schedule Rule（排程規則）時，將 `sync_discord` 設為 `true`，系統會在建立指派後自動透過 Webhook 發送任務通知至 Discord。

```json
{
  "template_id": "tmpl_abc123",
  "schedule_type": "once",
  "date": "2026-04-01",
  "sync_discord": true
}
```

> **前提：** 該班級必須先設定好 Discord Webhook URL，否則通知不會發送（不會報錯，僅靜默跳過）。

---

## 11. 班級封存（Archive）

學期結束或班級不再使用時，可將班級封存。

### 封存班級

```
PATCH /classes/{class_id}/archive
```

封存後：

- 班級不會出現在 Dashboard 的主要班級清單中
- 學生無法再進行簽到或提交
- 所有歷史資料（提交紀錄、點數、徽章等）皆保留

### 取消封存

若需重新啟用班級：

```
PATCH /classes/{class_id}/unarchive
```

> **提示：** 任務範本也可獨立封存（`PATCH /templates/{template_id}/archive`），適用於範本已不再使用但班級仍在運作的情境。

---

## 快速參考：API 端點總表

| 分類 | 方法 | 端點 | 說明 |
|------|------|------|------|
| **班級** | POST | `/classes` | 建立班級 |
| | GET | `/classes/public` | 取得公開班級清單 |
| | PATCH | `/classes/{class_id}/visibility` | 變更可見度 |
| | PATCH | `/classes/{class_id}/archive` | 封存班級 |
| | PATCH | `/classes/{class_id}/unarchive` | 取消封存 |
| **成員** | GET | `/classes/{class_id}/members` | 成員清單 |
| | DELETE | `/classes/{class_id}/members/{user_id}` | 移除成員 |
| | PATCH | `/classes/{class_id}/members/{user_id}/promote` | 提升為教師 |
| | POST | `/classes/{class_id}/invite-code/regenerate` | 重新產生邀請碼 |
| | GET | `/classes/{class_id}/invite/search` | 搜尋可邀請的學生 |
| | POST | `/classes/{class_id}/invite/batch` | 批次邀請 |
| **範本** | POST | `/classes/{class_id}/templates` | 建立範本 |
| | PATCH | `/templates/{template_id}` | 編輯範本 |
| | DELETE | `/templates/{template_id}` | 刪除範本 |
| | PATCH | `/templates/{template_id}/archive` | 封存範本 |
| | PATCH | `/templates/{template_id}/unarchive` | 取消封存範本 |
| **指派** | POST | `/classes/{class_id}/template-assignments` | 單次指派 |
| | POST | `/classes/{class_id}/schedule-rules` | 排程規則 |
| **簽到** | POST | `/classes/{class_id}/checkin-config` | 設定簽到規則 |
| | POST | `/classes/{class_id}/checkin-overrides` | 每日覆寫 |
| **提交** | GET | `/classes/{class_id}/submissions` | 查看提交 |
| | POST | `/api/submissions/{submission_id}/approve` | 核准提交 |
| | POST | `/api/submissions/{submission_id}/reject` | 退回提交 |
| | POST | `/api/submissions/{submission_id}/comment` | 新增評語 |
| **出席** | POST | `/api/classes/{class_id}/attendance/correct` | 出席更正 |
| **點數** | PATCH | `/classes/{class_id}/point-config` | 設定點數配置 |
| | POST | `/api/points/deduct` | 手動扣點 |
| | POST | `/classes/{class_id}/students/{student_id}/point-revoke` | 撤銷點數 |
| **徽章** | POST | `/classes/{class_id}/badges` | 建立徽章 |
| | POST | `/classes/{class_id}/badges/{badge_id}/award` | 手動頒發 |
| **獎品** | POST | `/classes/{class_id}/prizes` | 建立獎品 |
| | GET | `/classes/{class_id}/prizes` | 查看獎品清單 |
| | PATCH | `/prizes/{prize_id}` | 編輯獎品 |
| | DELETE | `/prizes/{prize_id}` | 刪除獎品 |
| **排行榜** | GET | `/classes/{class_id}/leaderboard` | 班級排行榜 |
| | GET | `/leaderboard` | 跨班排行榜 |
| **Discord** | PATCH | `/classes/{class_id}/discord-webhook` | 設定 Webhook |
