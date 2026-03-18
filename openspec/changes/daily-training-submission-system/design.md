## Context

本專案是全新開發（greenfield），目前僅有 FastAPI 骨架與 SQLModel + SQLite 的資料庫設定，無任何業務邏輯。使用者為 2-5 位老師與 50-200 位學生，分屬多個班級，學生可跨班加入。技術棧確定為 FastAPI + Jinja2（SSR）+ MongoDB + Beanie，採 Feature Modules + Protocol DI 架構。

## Goals / Non-Goals

**Goals:**

- 建立可運作的每日任務提交系統（Phase 1 核心）
- 設計可擴充的 Protocol DI 架構，讓新的獎勵 / 任務驗證機制可直接掛載
- 使用 Beanie 作為 MongoDB ODM，並提供版本化的 migration script 框架
- 提供 Jinja2 SSR 頁面，前端嵌入 WYSIWYG Markdown 編輯器（EasyMDE）
- 設計清晰的模組邊界，每個模組有獨立的 router、service、models

**Non-Goals:**

- 不實作 real-time 功能（WebSocket / SSE），通知以輪詢或靜態頁面處理
- 不實作 email 通知系統
- 不支援多租戶（multi-tenant）隔離，所有班級在同一 MongoDB database
- Phase 1 不實作 OAuth，AuthProvider Protocol 僅定義介面

## Decisions

### 模組結構採 Feature-based 而非 Layered

每個功能子系統（`core`、`tasks`、`gamification`、`community`）各自包含 router、service、models。跨模組依賴透過 service interface 而非直接 import 內部實作。

**為何不用 layered（router/service/repo 分離）？** Layered 在模組增多後容易讓 service 層膨脹，跨模組呼叫路徑不清晰。Feature-based 讓每個模組的邊界自明。

### 擴充點使用 Python Protocol + Registry 而非繼承

定義 `RewardProvider`、`BadgeTrigger`、`SubmissionValidator`、`AuthProvider` 四個 Protocol。透過 `ExtensionRegistry` 在 app startup 時注冊實作，FastAPI `Depends` 注入 registry 取得對應實作。

**為何不用抽象基類（ABC）？** Protocol 支援 structural typing，不需要 import 和繼承，第三方擴充更容易。Registry 模式讓多個實作可共存並按 key 選取。

### MongoDB 文件設計：嵌入 vs. 參照

- **嵌入**：任務模板的子項欄位（`fields: list[FieldDefinition]`）、簽到排程的時間窗口
- **參照**（使用 Beanie `Link`）：提交記錄參照模板、用戶、班級；點數紀錄參照提交或簽到事件

嵌入適合「永遠一起讀取、不獨立查詢」的資料；參照適合多對多或需獨立查詢的關係。

### 簽到排程：全域 + 當日覆蓋

全域設定存於 `CheckinConfig` document（每個班級一份），包含 `active_weekdays: list[int]`、`default_window: TimeWindow`。當日覆蓋存於 `DailyCheckinOverride`，欄位相同。判斷邏輯：先查當日是否有 override，有則用 override，否則用全域設定。

### 認證：JWT + Cookie Session

使用 PyJWT 發行 JWT，存放於 HttpOnly Cookie。`AuthProvider` Protocol 定義 `authenticate(credentials) -> User`，目前實作 `LocalAuthProvider`（帳號密碼）。未來 `GoogleAuthProvider`、`CustomOAuthProvider` 可注冊同一 registry。

### 前端 WYSIWYG Markdown 編輯器

採用 **EasyMDE**（CDN 引入），原因：純 JavaScript、零框架依賴、與 Jinja2 表單原生整合、license 友善（MIT）。提交時傳送 Markdown raw text，後端儲存，顯示時使用 `markdown-it` 渲染為 HTML。

### Migration Script 框架

採 Beanie 官方推薦的 free-migration 模式：每個 migration 為獨立 Python 檔案（`scripts/migrations/YYYYMMDD_description.py`），包含 `async def forward()` 和 `async def backward()`。`scripts/migrate.py` 為 CLI 入口，追蹤已執行的 migration 版本至 MongoDB `migrations` collection。

## Risks / Trade-offs

- **[Risk] Beanie Link 的 N+1 查詢** → 在列表頁使用 `fetch_all_links=True` 或 aggregation pipeline，避免逐筆 fetch。
- **[Risk] Protocol registry 在測試中需要手動注冊假實作** → 提供 `TestRegistry` helper，在測試 setup 注冊 mock 實作。
- **[Trade-off] SSR（Jinja2）限制了互動體驗** → WYSIWYG 編輯器以 JavaScript widget 嵌入彌補，其餘頁面 SSR 即可。若未來需要更豐富的互動，可在特定頁面引入 htmx。
- **[Risk] 彈性模板欄位型別增加後 schema 驗證複雜度上升** → Phase 1 支援 `text`、`markdown`、`number`、`checkbox` 四種型別，以 discriminated union 處理驗證，避免過早泛化。

## Migration Plan

1. 移除 `pyproject.toml` 中的 SQLModel / SQLite / MySQL 相依套件
2. 新增 `beanie`、`motor` 套件
3. 重寫 `src/shared/database.py` 為 Beanie 初始化邏輯
4. 建立各模組 Beanie Document models
5. 執行 `scripts/migrate.py init` 初始化 migration tracking collection
6. 後續每次 schema 變更新增對應 migration 檔案

## Open Questions

- Badge 的視覺資產（圖片）存放方式：本地 static files 或外部 object storage（S3/R2）？Phase 3 決定。
- 社群分享牆的排序演算法：依時間倒序 vs. 熱度排序？Phase 3 設計時確認。
- 八角框架（Octalysis）具體應用哪些 core drives？待老師確認後設計 badge 觸發條件。
