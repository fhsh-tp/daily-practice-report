## 1. 資料模型修改

- [x] 1.1 修改 `Class` model：套用設計決策「Webhook URL 儲存位置」，新增 `discord_webhook_url: str | None = None`（Class stores optional Discord Webhook URL、New class has null webhook URL）

## 2. Discord 發送服務

- [x] 2.1 建立 `src/integrations/discord/service.py`，實作 `send_task_embed(webhook_url, task_name, description, date)` 函式，套用設計決策「Discord Embed 格式」（Task assignment optionally syncs to Discord）
- [x] 2.2 實作 fire-and-forget 非同步發送（套用設計決策「Discord 訊息發送時機」），發送失敗時記錄 error log（Discord send failure does not block task assignment）

## 3. 任務指派流程修改

- [x] 3.1 修改 `templates/router.py` 任務指派端點：接收 `sync_discord: bool` 參數，成功後有條件發送 Discord（Task assignment optionally syncs to Discord、No message sent when opt-out、No message sent when no Webhook URL）
- [x] 3.2 修改 `template_assign.html`：依班級是否有 Webhook URL 顯示「同步到 Discord」勾選框，使用 /ui-ux-pro-max 風格（Task assignment form includes Discord sync option、Sync checkbox shown when webhook is configured、Sync checkbox hidden when no webhook）
- [x] 3.3 驗證 Discord 失敗不影響任務指派成功（Task assignment succeeds despite Discord failure）

## 4. Webhook 設定 UI

- [x] 4.1 在班級設定頁（class hub 或獨立設定頁）加入 Discord Webhook URL 輸入欄位，使用 /ui-ux-pro-max 風格（Teacher can configure Discord Webhook URL for a class）
- [x] 4.2 實作 `PATCH /api/classes/<class_id>/discord-webhook` 端點儲存 URL（Webhook URL is saved）
- [x] 4.3 支援清空 Webhook URL（送空字串時設為 null）（Webhook URL can be cleared）
- [x] 4.4 確認 Webhook URL 不暴露於學生端（Webhook URL is only visible to class managers）

## 5. 測試

- [x] 5.1 為 `send_task_embed` 撰寫單元測試（mock httpx，驗證 embed 格式）
- [x] 5.2 為任務指派端點撰寫整合測試（有勾選 + 有 URL、無勾選、無 URL 三種情境）
- [x] 5.3 為 Webhook 失敗情境撰寫測試（httpx timeout/error，驗證任務仍成功指派）
