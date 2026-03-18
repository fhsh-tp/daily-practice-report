## 1. 基礎設施

- [x] 1.1 在 `docker-compose.yml` 新增 Redis service（`redis:7-alpine`），app service 加入 `REDIS_URL` 環境變數與 depends_on
- [x] 1.2 在 `pyproject.toml` / `requirements.txt` 新增 `redis[asyncio]` 依賴，重建 Docker image

## 2. SystemConfig Document

- [x] 2.1 建立 `src/core/system/` 模組，新增 `models.py` 定義 SystemConfig document stores global settings（Beanie Document，SystemConfig 使用單例 Document，固定 `_id = "global"`），欄位包含 `site_name`、`admin_email`
- [x] 2.2 將 `SystemConfig` 加入 `main.py` 的 `_collect_document_models()` 清單

## 3. Redis 連線

- [x] 3.1 在 `src/shared/` 新增 `redis.py`，提供 `get_redis_client()` 工廠函式，實作 Redis caches system configuration state（使用 Redis 字串 key 儲存 setup 狀態，key 為 `system:configured`，值為 `"true"`）
- [x] 3.2 在 `lifespan` 中初始化 `redis.asyncio.Redis` client，存入 `app.state.redis`，shutdown 時關閉（Redis client 以 async 模式注入 app.state）

## 4. 啟動檢查

- [x] 4.1 在 `lifespan` 中實作 Startup lifespan checks setup state：讀取 Redis `system:configured` flag；若不存在但 MongoDB 有 `SystemConfig` document，自動復原 Redis flag（Redis flag missing but config exists in MongoDB）
- [x] 4.2 設定完成時將 `SystemConfig` 載入 `app.state.system_config`（Startup with completed setup）
- [x] 4.3 未設定時 `app.state.system_config = None`，允許系統啟動但僅 `/setup` 可用（Startup without completed setup）

## 5. Setup Wizard 路由

- [x] 5.1 建立 `src/core/system/router.py`，實作 Setup wizard is shown on first deployment：`GET /setup`（Setup 頁面用 Jinja2 HTML，不依賴前端框架）已設定則 302 redirect 到 `/`；未設定則回傳 Jinja2 setup.html（Setup page blocked after configuration）
- [x] 5.2 新增 `POST /setup`（Setup wizard form submits initial configuration）：驗證表單（site name、admin username、admin password）；已完成則回傳 409 Conflict（Duplicate setup attempt via API）
- [x] 5.3 `POST /setup` 成功時：建立 `SystemConfig` document、建立 admin `User`、設 Redis `system:configured = "true"`、302 redirect 到 `/`（Successful setup submission）

## 6. Setup HTML 頁面

- [x] 6.1 建立 `src/templates/setup.html`（Jinja2），包含 site name、admin username、admin password 欄位，表單 action 指向 `POST /setup`

## 7. 整合與測試

- [x] 7.1 在 `main.py` 的 `include_router` 加入 system router；將 setup router 排在所有其他 router 之前
- [x] 7.2 撰寫 `tests/system/` 下的整合測試，覆蓋：首次啟動顯示 setup、設定完成後 `/setup` 重導向、重複提交 409、Redis flag 遺失自動復原（System config is updatable by system administrator — 待 RBAC change 完成後補上）
