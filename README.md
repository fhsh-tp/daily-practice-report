# Daily Practice Report System

管理每日練習報告的後端 API，適用於教學場域。教師可以建立班級、指派每日任務，並透過遊戲化機制——點數、徽章與排行榜——提升學生學習動力。學生提交練習報告、每日簽到，並在社群牆上分享學習進度。

## 功能

- **Auth** — Session 式本地認證，角色分為教師與學生
- **班級管理** — 建立班級、將學生加入班級
- **Task Template 與指派** — 可重複使用的任務範本；依日期指派給各班級
- **練習報告提交** — 每位學生每次指派僅能提交一次；提交時會快照當下的範本版本
- **每日簽到** — 可設定簽到時間區間，並支援單日覆蓋設定
- **點數系統** — 簽到與提交事件觸發對應的 Reward Provider
- **徽章** — 教師自訂徽章定義，搭配可插拔的觸發條件
- **排行榜** — 以班級為範圍，依累積點數排名
- **獎品預覽** — 顯示與點數里程碑對應的獎品
- **社群牆** — 貼文與 Reaction 互動
- **Extension Registry** — 支援 Auth Provider 與 Reward Provider 的插件架構

## 技術堆疊

| 層次 | 技術 |
|---|---|
| Runtime | Python 3.13+ |
| Framework | FastAPI |
| ODM | Beanie（非同步 MongoDB ODM） |
| Driver | Motor（非同步 MongoDB Driver） |
| Database | MongoDB 8.0 |
| 套件管理 | uv |
| 容器化 | Docker + Docker Compose |

## 快速開始

### 前置需求

- [Docker](https://docs.docker.com/get-docker/) 與 Docker Compose
- 或：Python 3.13+ 與 [uv](https://github.com/astral-sh/uv)（本機開發）

### 使用 Docker Compose 執行

```bash
cp .env.example .env   # 視需要調整設定值
docker compose up
```

服務對應埠號：

| 服務 | URL |
|---|---|
| API | http://localhost:8000 |
| Mongo Express | http://localhost:8081 |

### 本機執行

```bash
# 安裝相依套件
uv sync

# 啟動 MongoDB（需要已在執行中的 MongoDB）
export MONGO_URL=mongodb://localhost:27017
export MONGO_DB_NAME=dprs

# 啟動開發伺服器
uv run fastapi dev src/main.py
```

## 環境變數

| 變數 | 預設值 | 說明 |
|---|---|---|
| `FASTAPI_APP_ENVIRONMENT` | `dev` | `dev` 啟用熱重載；`prod` 以正式模式執行 |
| `SESSION_SECRET` | 自動產生 | Session 簽名金鑰；正式環境請明確設定 |
| `MONGO_URL` | `mongodb://localhost:27017` | MongoDB 連線字串 |
| `MONGO_DB_NAME` | `dprs` | 資料庫名稱 |
| `ME_USER` | `admin` | Mongo Express Basic Auth 帳號 |
| `ME_PASSWORD` | `pass` | Mongo Express Basic Auth 密碼 |

## 資料庫 Migration

```bash
# 初始化 Migration 追蹤 Collection（僅需執行一次）
uv run python scripts/migrate.py init

# 套用所有待執行的 Migration
uv run python scripts/migrate.py up

# 回滾最近一筆 Migration
uv run python scripts/migrate.py down

# 查看 Migration 狀態
uv run python scripts/migrate.py status
```

詳細 API 使用方式請參閱 [Usage.md](Usage.md)，開發指引請參閱 [CONTRIBUTE.md](CONTRIBUTE.md)。

## 貢獻

歡迎提交 Pull Request！詳細流程請參閱 [CONTRIBUTE.md](CONTRIBUTE.md)。

## 授權

[ECL-2.0](LICENSE)
