# 貢獻指南

感謝你對 Daily Practice Report System 的貢獻意願。本文件說明開發流程、程式慣例與專案結構。

## 目錄

- [前置需求](#前置需求)
- [本機環境設定](#本機環境設定)
- [專案結構](#專案結構)
- [執行測試](#執行測試)
- [程式碼慣例](#程式碼慣例)
- [Extension 系統](#extension-系統)
- [資料庫 Migration](#資料庫-migration)
- [Spec 驅動開發](#spec-驅動開發)
- [Pull Request 流程](#pull-request-流程)

---

## 前置需求

- Python 3.13+
- [uv](https://github.com/astral-sh/uv)
- MongoDB 8.0（或 Docker）

---

## 本機環境設定

```bash
# Clone 專案
git clone https://github.com/fhsh-tp/daily-practice-report.git
cd daily-practice-report

# 安裝相依套件（自動建立 .venv）
uv sync

# 透過 Docker Compose 啟動 MongoDB（選用）
docker compose up mongo -d

# 啟動開發伺服器
MONGO_URL=mongodb://localhost:27017 uv run fastapi dev src/main.py
```

---

## 專案結構

```
src/
├── main.py                  # 應用程式進入點，Router 註冊
├── core/
│   ├── auth/                # 認證 — Local Provider、Session Middleware
│   ├── classes/             # 班級管理與成員
│   └── users/               # 使用者帳號與角色
├── tasks/
│   ├── checkin/             # 每日簽到，支援可設定時間區間
│   ├── submissions/         # 練習報告提交（每位學生每次指派限一次）
│   └── templates/           # 可重複使用的 Task Template 與指派
├── gamification/
│   ├── badges/              # 徽章定義與頒發
│   ├── leaderboard/         # 班級範圍排行榜
│   ├── points/              # 點數交易與班級設定
│   └── prizes/              # 獎品預覽
├── community/
│   └── feed/                # 社群牆與 Reaction
├── extensions/
│   ├── registry/            # Extension Registry（插件架構）
│   └── protocols/           # Protocol 定義（RewardProvider 等）
└── shared/                  # 資料庫初始化、Session Middleware、工具函式

scripts/
├── migrate.py               # Migration CLI
└── migrations/              # Migration 檔案（YYYYMMDD_NNN_<名稱>.py）

tests/                       # pytest 測試套件（每個模組對應一個測試檔）
openspec/
├── specs/                   # 各功能的現行規格
└── changes/                 # 變更提案（進行中與已封存）
```

每個模組通常包含：
- `models.py` — Beanie Document Model
- `router.py` — FastAPI Router
- `service.py` — 業務邏輯（視複雜度而定）

---

## 執行測試

```bash
# 執行完整測試套件
uv run pytest

# 執行單一測試檔
uv run pytest tests/test_submissions.py

# 詳細輸出
uv run pytest -v
```

測試使用 `mongomock-motor`，不需要執行中的 MongoDB。

---

## 程式碼慣例

- **Python 版本**：3.13+；使用現代型別標注（`list[str]`、`str | None`）
- **非同步**：所有資料庫存取透過 Motor / Beanie 以 async 執行
- **Model**：使用 Beanie 定義 Document Model；跨文件參考使用 `PydanticObjectId`
- **Router**：Router 只負責路由，業務邏輯委派給 `service.py`
- **錯誤處理**：以 `HTTPException` 搭配適當狀態碼；衝突情境使用 `409`
- **不在應用程式碼中使用 `print`**

---

## Extension 系統

Extension Registry（`src/extensions/registry/`）允許在不修改核心程式碼的情況下，插拔不同的 Protocol 實作。

### 註冊 Provider

```python
from extensions.registry import registry
from extensions.protocols.reward import RewardProvider

registry.register(RewardProvider, "my-provider", MyRewardProvider())
```

### 實作 RewardProvider

```python
class MyRewardProvider:
    async def award(self, event: str, user_id: str, class_id: str) -> None:
        # 自訂獎勵邏輯
        ...
```

Provider 在應用程式啟動時於 `main.py → _register_extensions()` 完成註冊。

---

## 資料庫 Migration

Migration 檔案放置於 `scripts/migrations/`，命名規則如下：

```
YYYYMMDD_NNN_<說明>.py
```

每個 Migration 檔案需提供兩個非同步函式：

```python
async def forward() -> None:
    """套用此 Migration。"""
    ...

async def backward() -> None:
    """回滾此 Migration。"""
    ...
```

執行 Migration：

```bash
uv run python scripts/migrate.py init    # 初始化（僅需執行一次）
uv run python scripts/migrate.py up      # 套用待執行項目
uv run python scripts/migrate.py down    # 回滾最近一筆
uv run python scripts/migrate.py status  # 查看狀態
```

---

## Spec 驅動開發

本專案採用 Spectra 進行 Spec-Driven Development（SDD）。規格文件放置於 `openspec/specs/`；變更提案放置於 `openspec/changes/`。

建議工作流程：

1. **Discuss**（選用）— 需求不明確時使用 `/spectra:discuss`
2. **Propose** — 使用 `/spectra:propose` 建立變更提案
3. **Apply** — 使用 `/spectra:apply` 依提案實作任務
4. **Archive** — 實作完成後使用 `/spectra:archive` 封存

完整工作流程請參閱 [CLAUDE.md](CLAUDE.md)。

---

## Pull Request 流程

1. Fork 專案後從 `main` 建立分支：`git checkout -b feature/<簡短說明>`
2. 若有行為變更，請同步更新 `openspec/specs/` 中的規格
3. 為新行為新增測試至 `tests/`
4. 確認 `uv run pytest` 全數通過
5. 向 [github.com/fhsh-tp/daily-practice-report](https://github.com/fhsh-tp/daily-practice-report) 的 `main` 分支發送 PR，說明變更內容與原因
6. 在 PR 說明中連結相關的規格或變更提案

---

## 回報問題

請至 [github.com/fhsh-tp/daily-practice-report/issues](https://github.com/fhsh-tp/daily-practice-report/issues) 開立 Issue，並附上：

- 清楚的問題標題
- 重現步驟
- 預期行為與實際行為
- 相關的 Log 或錯誤訊息
