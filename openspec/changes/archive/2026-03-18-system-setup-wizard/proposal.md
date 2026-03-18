## Why

系統目前缺乏初始設定流程與系統級配置管理。第一次部署時沒有入口點可以設定基本資訊，也無法從管理介面調整系統設定，導致系統無法直接交給終端使用者部署使用。

## What Changes

- 新增 Redis 服務至 docker-compose，作為系統狀態快取層
- 新增 `SystemConfig` Beanie Document，儲存系統級設定至 MongoDB
- 新增 Setup Wizard：內建 HTML 頁面（Jinja2），首次啟動時引導管理員完成初始設定
- 啟動時檢查 Redis `system:configured` flag，決定是否進入 setup 流程或載入既有設定
- 設定完成後，由系統管理員可透過管理介面調整系統設定

## Capabilities

### New Capabilities

- `system-config`: 系統級設定的儲存、讀取與管理，包含 Redis 快取與 MongoDB 持久化
- `setup-wizard`: 首次部署的引導設定流程，提供內建 HTML 頁面與 API 端點

### Modified Capabilities

（無）

## Impact

- 新增依賴：`redis`（Python client：`redis-py`）
- 新增服務：`docker-compose.yml` 加入 Redis container
- 新增檔案：`src/core/system/models.py`、`src/core/system/router.py`、`src/templates/setup.html`
- 修改檔案：`src/main.py`（lifespan 加入 Redis 初始化與 setup 檢查）、`docker-compose.yml`
