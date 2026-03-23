## Why

安全審計發現多個授權檢查缺口：學生提交與打卡端點缺少班級成員資格驗證、教師端點缺少班級所有權驗證、JWT 預設 secret 無啟動時強制檢查、Discord Webhook URL 未驗證可能被 SSRF 利用、Setup Wizard 未設定密碼最低長度。這些問題允許已登入用戶操作不屬於自己的班級資料，需立即修正。

## What Changes

- 在 `submit_task_endpoint` 與 `checkin` 端點加入 ClassMembership 驗證，拒絕非成員操作
- 在 checkin 設定 API (`configure_checkin`, `create_override`, `checkin_config_page`) 改用 `can_manage_class()` 驗證班級所有權
- JWT 啟動時檢查 `SESSION_SECRET` 是否為預設值，log 警告或在 production mode 拒絕啟動
- Discord Webhook URL 驗證僅允許 `https://discord.com/api/webhooks/` 或 `https://discordapp.com/api/webhooks/` 開頭的 URL
- Setup Wizard 管理員密碼加入最低 8 字元驗證

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `task-submissions`: 新增 class membership 驗證要求，非班級成員提交應返回 HTTP 403
- `checkin`: 新增 class membership 驗證要求（打卡）與 class ownership 驗證（設定 API）
- `discord-webhook`: 新增 URL 格式驗證，僅接受 Discord Webhook URL 格式
- `setup-wizard`: 新增管理員密碼最低長度要求
- `user-auth`: 新增 JWT secret 啟動時安全檢查

## Impact

- Affected specs: `task-submissions`, `checkin`, `discord-webhook`, `setup-wizard`, `user-auth`
- Affected code:
  - `src/tasks/submissions/router.py` — 提交端點加入 membership 驗證
  - `src/tasks/checkin/router.py` — 打卡端點加入 membership 驗證、設定端點改用 `can_manage_class()`
  - `src/tasks/checkin/service.py` — `do_checkin()` 加入 membership 驗證
  - `src/core/classes/router.py` — Discord Webhook URL 驗證
  - `src/core/system/router.py` — Setup 密碼長度驗證
  - `src/core/auth/jwt.py` — 啟動時 secret 安全檢查
  - `src/core/system/startup.py` — 啟動時 secret 安全警告
