## Context

`security-audit-fixes` change 在 2026-03-23 封存，實作了 5 項安全行為。由於 delta specs 未在封存前撰寫，主 spec 文件未被同步更新。此 change 純粹補足文件，不含程式碼異動。

## Goals / Non-Goals

**Goals:**

- 為已實作的安全行為補寫 spec-level requirements（使用 SHALL/MUST 規範語言）
- 每個 delta spec 精準反映對應程式碼的實際行為
- 所有 delta spec 均添加 `@trace` 指向 `security-audit-fixes` 封存路徑

**Non-Goals:**

- 不修改任何應用程式碼
- 不新增原本未實作的功能要求
- 不重構 spec 文件的既有結構

## Decisions

### 以 ADDED Requirements 區塊追加，不覆寫既有內容

所有新增的 requirements 以 `## ADDED Requirements` 區塊追加在各 spec 文件末尾，保留既有 requirements 不變。這符合 Spectra delta spec 合併模式，且降低衝突風險。

### @trace 指向封存 change 路徑

delta spec 中的 `@trace` 使用 `source: security-audit-fixes`，`updated: 2026-03-23`，確保可追溯性。

## Risks / Trade-offs

- [Spec 與程式碼已同步，但 trace 缺失] → 透過此 change 補足 `@trace` 注入解決
- [Delta spec 寫錯可能產生 false requirements] → 以 `security-audit-fixes` 的 proposal 與實際 test cases 為依據驗證
