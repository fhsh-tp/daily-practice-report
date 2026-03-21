## Why

教師在佈置任務後需要另外手動在 Discord 頻道通知學生，流程繁瑣且容易遺漏。提供 Discord Webhook 串接讓任務發布可一鍵同步貼到指定頻道，降低教師操作負擔。

## What Changes

- **Discord Webhook 設定**：教師可在班級 Hub 頁或班級設定中填入 Discord Webhook URL，綁定到特定班級。
- **任務同步發布**：教師在建立或指定任務模板時，可勾選「同步發布到 Discord」，系統自動發送 embed 訊息到對應 Webhook URL。
- **訊息格式**：Discord 訊息包含任務名稱、說明、截止日期（若有）與系統連結。

## Capabilities

### New Capabilities

- `discord-webhook`：班級 Discord Webhook 設定與任務訊息發送能力

### Modified Capabilities

- `class-management`：班級 model 新增 `discord_webhook_url` 欄位
- `task-templates`：任務指派流程新增「同步到 Discord」選項

## Impact

- Affected specs: `discord-webhook`（新）、`class-management`、`task-templates`
- Affected code:
  - `src/core/classes/models.py`（新增 `discord_webhook_url` 欄位）
  - `src/tasks/templates/router.py`（任務指派時觸發 Discord 發送）
  - `src/templates/teacher/class_hub.html` 或班級設定頁（Webhook 設定 UI）
  - `src/templates/teacher/template_assign.html`（加入同步勾選）
  - 新增 `src/integrations/discord/service.py`（Webhook 發送服務）
