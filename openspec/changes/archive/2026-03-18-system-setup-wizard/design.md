## Context

系統目前在 `lifespan` 中只做 MongoDB 初始化與 Extension 註冊，沒有啟動時的設定狀態檢查，也沒有系統級設定的資料模型。Docker Compose 目前只包含 MongoDB 與 mongo-express，缺少 Redis 服務。

## Goals / Non-Goals

**Goals:**

- 新增 Redis 到基礎設施，作為系統狀態的快取層
- 在 `lifespan` 中加入啟動檢查：讀 Redis flag → 決定載入設定或進入 setup
- 提供 `SystemConfig` Beanie Document 儲存系統級設定
- 提供內建 Jinja2 HTML 設定頁面，供首次部署使用
- 設定完成後可由系統管理員透過 API 修改（權限控管由 change 2 的 RBAC 負責）

**Non-Goals:**

- 不設計多租戶（multi-tenant）系統設定
- 不實作 RBAC 權限控管（由 `rbac-permission-flags` change 負責）
- 不提供 CLI 設定工具

## Decisions

### 使用 Redis 字串 key 儲存 setup 狀態

**決定**：以 `system:configured` 作為 Redis key，值為 `"true"`（字串）。

**理由**：簡單可靠，Redis TTL 可選擇不設定（persistent），重啟不消失。不需要 hash 或複雜結構，只需要一個存在性檢查。

**替代方案**：存在 MongoDB 一個 meta collection — 但啟動順序上 Redis 更快，且可以把「是否已設定」與「設定內容」分離（前者在 Redis，後者在 Mongo）。

### SystemConfig 使用單例 Document

**決定**：`SystemConfig` 只有一筆 document（使用固定 `_id = "global"`），透過 `find_one()` 取得。

**理由**：系統設定是全局唯一的。避免多筆設定造成不一致。

**替代方案**：key-value collection（每個設定一筆）— 靈活但查詢複雜，不如單筆 Document 直觀。

### Setup 頁面用 Jinja2 HTML，不依賴前端框架

**決定**：Setup wizard 用 FastAPI + Jinja2 直接 serve HTML form，提交後重導向。

**理由**：系統目前已有 Jinja2 設定（`main.py` 第 67-68 行），不需要額外依賴。Setup 是一次性流程，不需要複雜互動。

**替代方案**：Vue/React SPA — 過度複雜，且 setup 階段前端可能尚未部署。

### Redis client 以 async 模式注入 app.state

**決定**：在 `lifespan` 中建立 `redis.asyncio.Redis` client，存入 `app.state.redis`，shutdown 時關閉。

**理由**：FastAPI 的 lifespan 是管理連線資源的標準方式，與現有 MongoDB client 做法一致。

## Risks / Trade-offs

- [Risk] Redis 重啟後 `system:configured` key 消失 → 系統誤認為未設定，重新顯示 setup 頁面
  → Mitigation：startup 時若 Redis flag 不存在但 MongoDB 中已有 `SystemConfig` document，自動重設 Redis flag
- [Risk] Setup 頁面在已設定後仍可訪問
  → Mitigation：`/setup` route 檢查 Redis flag，已設定時重導向到首頁（`/`）
