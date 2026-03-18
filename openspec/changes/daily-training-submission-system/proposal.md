## Why

教師需要一個能讓學生每日回報任務進度的系統，並透過遊戲化機制（點數、徽章、社群分享）提升學生參與動機。現有專案僅有 FastAPI 骨架，無任何業務功能，是從零建構的最佳時機。

## What Changes

- 建立完整的後端架構：FastAPI + MongoDB (Beanie) 取代目前的 SQLModel + SQLite/MySQL
- 新增認證系統（自建帳號 + 預留 OAuth 擴充點）
- 新增班級管理（多班、跨班、老師控制可見度）
- 新增彈性任務模板系統（老師設計多欄位模板，學生依模板提交 Markdown WYSIWYG 內容）
- 新增簽到系統（全域排程 + 當日覆蓋機制）
- 新增點數系統（簽到 / 提交得點、老師追回）
- 新增成就徽章系統（BadgeTrigger Protocol 可擴充）
- 新增社群分享牆（學生分享任務結果）
- 新增獎品 Preview 功能（老師上傳線上 / 實體獎品）
- 新增排行榜（班級內部 + 跨班可見度控制）
- 新增 Beanie Migration script 框架
- 所有擴充點（RewardProvider、BadgeTrigger、SubmissionValidator、AuthProvider）以 Python Protocol 定義，透過 registry 注冊實作

## Capabilities

### New Capabilities

- `user-auth`: 使用者認證系統，自建帳號（JWT）+ AuthProvider Protocol 預留 OAuth 擴充
- `class-management`: 班級建立、學生加入、老師指派、可見度設定（公開 / 私密）
- `task-templates`: 老師建立彈性任務模板，定義多個子項欄位（名稱、型別、是否必填）
- `task-submissions`: 學生依模板提交每日任務，支援 Markdown WYSIWYG 內容
- `checkin`: 學生簽到功能，全域排程（星期幾 + 時間窗口）+ 當日老師覆蓋
- `points-system`: 點數發放（簽到 / 提交）與老師追回機制，RewardProvider Protocol 可擴充
- `badge-system`: 成就徽章，BadgeTrigger Protocol 定義觸發條件，支援自訂 badge
- `community-feed`: 學生分享牆，學生可發布任務結果分享供其他學生瀏覽互動
- `prize-preview`: 老師上傳並展示獎品（線上 / 實體），與點數系統連動
- `leaderboard`: 排行榜，支援班級內部與跨班兩種模式，老師控制可見度
- `migration-scripts`: Beanie 推薦的 migration script 框架，支援版本化資料遷移
- `extension-registry`: Protocol 定義與 registry 機制，統一管理所有可擴充的業務邏輯

### Modified Capabilities

（none）

## Impact

- **完全重寫**：`src/shared/database.py`（SQLModel → Beanie）、`src/main.py`（lifespan 初始化）
- **新增**：`src/core/`、`src/tasks/`、`src/gamification/`、`src/community/`、`src/extensions/` 目錄結構
- **新增**：`scripts/migrate.py` 及相關 migration 版本檔
- **相依套件**：移除 `aiomysql`、`aiosqlite`、`sqlmodel`、`greenlet`；新增 `beanie`、`motor`、`python-multipart`
- **前端**：Jinja2 模板 + 前端 WYSIWYG Markdown 編輯器（EasyMDE 或 Toast UI Editor）
