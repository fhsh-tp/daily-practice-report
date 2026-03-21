## Context

班級 model 目前無 Discord Webhook URL 欄位。任務指派透過 `template_assign.html` + `templates/router.py` 完成。Discord Webhook 是無驗證的 HTTP POST，使用 `httpx` 即可實作。

## Goals / Non-Goals

**Goals:**

- 每個班級可設定一個 Discord Webhook URL
- 任務指派時可選擇是否同步發到 Discord
- Discord 訊息格式為 embed，包含任務名稱、說明、日期

**Non-Goals:**

- 不支援多個 Webhook URL（每班一個）
- 不實作 Discord Bot（只用 Webhook）
- 不追蹤 Discord 訊息的已讀/回應狀態
- 不實作 Webhook 驗證（Discord Webhook URL 本身即為 secret）

## Decisions

### Webhook URL 儲存位置

**決策**：在 `Class` model 新增可選欄位 `discord_webhook_url: str | None = None`，由教師透過班級設定頁填入。

**理由**：最小改動，利用現有 Class model 機制。Webhook URL 需保密（不顯示在學生端）。

### Discord 訊息發送時機

**決策**：任務指派（`POST /api/templates/<id>/assign`）成功後，若班級有 Webhook URL 且使用者勾選「同步到 Discord」，則非同步（fire-and-forget）發送 Webhook 請求。

**理由**：Webhook 發送失敗不應阻擋任務指派成功；非同步可避免 Discord 服務延遲影響使用者體驗。

### Discord Embed 格式

**決策**：使用標準 Discord Embed 格式，包含 title（任務名稱）、description（任務說明截斷至 200 字）、fields（日期）、color（品牌紫 `0x7c3aed`）、footer（系統名稱）。

**理由**：Embed 格式在 Discord 中視覺效果佳，比純文字訊息更清楚。

## Risks / Trade-offs

- [安全性] Webhook URL 若洩漏可被濫用。Mitigation：URL 僅顯示給教師，不在學生端或公開 API 暴露；儲存時不加密（Discord Webhook 本身是 public URL，revoke 機制由 Discord 提供）。
- [可靠性] Discord Webhook 失敗時任務已指派成功，訊息靜默失敗。Mitigation：記錄 error log；可在未來版本加入重試或失敗通知。
