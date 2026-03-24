## Context

安全審計發現 branch `refactor/teacher-function-and-bug-fixed` 存在多個授權檢查缺口。核心問題是 **permission flag check ≠ resource ownership check**：現有 `require_permission(FLAG)` 只確認用戶「擁有某種能力」，但未驗證用戶「是否有權操作該特定資源」。

`classes/router.py` 已正確實作 `can_manage_class()` 所有權驗證，但 `checkin/router.py` 和 `submissions/router.py` 漏掉了此層檢查。

## Goals / Non-Goals

**Goals:**

- 修補 5 個安全缺口（2 HIGH、3 MEDIUM），不改變現有功能行為
- 所有資源操作端點加入適當的 membership/ownership 驗證
- 加入防禦性檢查（JWT secret、webhook URL、密碼長度）

**Non-Goals:**

- 不重構 permission system 架構（IntFlag + guards 設計正確）
- 不改變 submission approval 的跨班設計（spec 明確定義 MANAGE_TASKS 為全局權限）
- 不新增 rate limiting 或 CSRF token（屬不同安全層級）

## Decisions

### 在 service 層加入 membership 驗證

學生操作（提交、打卡）的 membership 驗證放在 service 層（`submit_task` 和 `do_checkin`），而非 router 層。原因：service 函式可能被其他 caller 呼叫，驗證放在 service 層確保不會被繞過。

替代方案：在 router 層加 dependency。缺點是需要在多個 router 重複，且其他 caller 可能忘記。

### 在 router 層加入 class ownership 驗證 (checkin config)

Checkin config 端點改用 `_require_manage()` 模式（與 `classes/router.py` 一致），在 router 層呼叫 `can_manage_class()`。原因：這是 teacher 管理操作，與 classes/router.py 的模式保持一致。

### JWT secret 檢查用 warning log，不用硬性阻擋

啟動時若 `SESSION_SECRET` 為預設值，log `WARNING` 層級訊息。不在 production 硬性阻擋，因為目前沒有 production/development mode 的判斷機制。

替代方案：直接 `raise RuntimeError`。缺點是開發環境也會被阻擋，需要額外的 mode 判斷。

### Discord Webhook URL 用正則驗證

只接受 `https://discord.com/api/webhooks/` 或 `https://discordapp.com/api/webhooks/` 開頭的 URL。用 `startswith` 比較即可，不需要完整正則。

### Setup 密碼長度最低 8 字元

與一般安全實務對齊。在 `post_setup` 的 Form handler 中驗證，返回錯誤導回 setup 頁面。

## Risks / Trade-offs

- [membership 驗證增加 DB 查詢] → 每次提交/打卡多一次 `ClassMembership.find_one` 查詢。影響極小，membership collection 已有 index。
- [checkin config ownership 驗證可能影響 MANAGE_ALL_CLASSES 用戶] → `can_manage_class()` 已處理此情境，MANAGE_ALL_CLASSES 用戶直接通過。
- [JWT warning 在 dev 環境產生噪音] → 開發環境使用預設 secret 是合理的，warning 層級可被 log config 過濾。
