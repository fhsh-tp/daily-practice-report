## Why

`security-audit-fixes` change 已實作完成並封存，但 delta specs 在封存前未被撰寫，導致 5 個受影響的 spec 文件未反映已實作的安全行為。這次 change 補足缺失的規格文件，讓 specs 回到與程式碼一致的狀態。

## What Changes

- 將 `security-audit-fixes` 實作的 5 項安全行為補寫入對應 spec 文件
- 不涉及任何新的程式碼實作（spec-only change）

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `task-submissions`: 新增 class membership 驗證要求 — 非班級成員提交返回 HTTP 403
- `checkin`: 新增 class membership 驗證要求（打卡返回 403）；新增 class ownership 驗證要求（checkin config 端點限制班級 owner 或全局管理員）
- `discord-webhook`: 新增 Webhook URL 格式驗證要求 — 僅接受 discord.com / discordapp.com 開頭的 URL
- `setup-wizard`: 新增管理員密碼最低長度要求 — 短於 8 字元的密碼被拒
- `user-auth`: 新增 JWT secret 啟動時安全檢查 — SESSION_SECRET 使用預設值時 log WARNING

## Impact

- Affected specs: `task-submissions`, `checkin`, `discord-webhook`, `setup-wizard`, `user-auth`
- Affected code: none（純 spec 補足，對應實作已在 `security-audit-fixes` 完成）
- Reference: `openspec/changes/archive/2026-03-23-security-audit-fixes/`
