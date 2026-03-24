## 1. 同步 task-submissions 與 checkin Delta Specs

- [x] 1.1 將「Submission endpoint validates class membership」requirement 以 ADDED Requirements 區塊追加至 `openspec/specs/task-submissions/spec.md`，不覆寫既有內容
- [x] 1.2 將「Check-in endpoint validates class membership」requirement 以 ADDED Requirements 區塊追加至 `openspec/specs/checkin/spec.md`，不覆寫既有內容
- [x] 1.3 將「Checkin config endpoints validate class ownership」requirement 以 ADDED Requirements 區塊追加至 `openspec/specs/checkin/spec.md`，不覆寫既有內容

## 2. 同步 discord-webhook、setup-wizard 與 user-auth Delta Specs

- [x] 2.1 將「Discord webhook URL format validation」requirement 以 ADDED Requirements 區塊追加至 `openspec/specs/discord-webhook/spec.md`，不覆寫既有內容
- [x] 2.2 將「Admin password minimum length」requirement 以 ADDED Requirements 區塊追加至 `openspec/specs/setup-wizard/spec.md`，不覆寫既有內容
- [x] 2.3 將「JWT secret safety check at startup」requirement 以 ADDED Requirements 區塊追加至 `openspec/specs/user-auth/spec.md`，不覆寫既有內容

## 3. 注入 @trace 並驗證一致性

- [x] 3.1 在每個 delta spec 檔案中新增 `@trace` 標記，指向 `security-audit-fixes` 封存路徑（`source: security-audit-fixes`，`updated: 2026-03-23`）
- [x] 3.2 確認所有 @trace 指向封存 change 路徑格式正確，確保可追溯性
- [x] 3.3 驗證所有 spec 更新均符合設計決策：以 ADDED Requirements 區塊追加，不覆寫既有內容
