## Context

目前教師側邊欄將每個班級的「成員」與「模板」連結平鋪列出，每新增一個班級就增加兩個側邊欄項目。教師儀表板在班級卡片內嵌入工具按鈕（成員管理、簽到設定、任務模板、排行榜、積分管理），視覺雜亂。管理員班級列表無 tab 切換，封存班級混雜於運作中班級。

## Goals / Non-Goals

**Goals:**

- 建立班級 Hub 頁面作為每個班級的統一入口
- 側邊欄改為「班級清單」模式，進入班級後展示該班級的工具連結
- 班級列表加入「運作中 / 已封存」tab 切換
- 兩個 tab 各自提供前端搜尋（班級名稱、教師名稱）
- 全程使用 /ui-ux-pro-max 設計風格

**Non-Goals:**

- 不修改後端 API 結構（班級 CRUD 保持現有端點）
- 不處理學生端儀表板的 tab（學生沒有管理班級的需求）
- 不實作分頁（前端過濾足以應付預期班級數量）

## Decisions

### 班級 Hub 頁面路由設計

**決策**：新增 `GET /pages/teacher/class/<class_id>` 路由，對應 `teacher/class_hub.html` 模板。

**理由**：獨立路由讓 URL 可直接書籤，也讓側邊欄可以 highlight 當前班級。

### 側邊欄班級展開模式

**決策**：側邊欄列出班級名稱（每個班級一個連結到 hub 頁），點入 hub 頁後，側邊欄在該班級名稱下方顯示縮排的工具連結（成員管理、任務模板、簽到設定、排行榜、積分管理）。使用 URL 路徑偵測當前班級來決定哪個班級展開。

**理由**：比 JavaScript 手動 toggle 更穩定，不依賴 session 狀態，直接由 URL 驅動展開狀態。

### Tab 切換實作方式

**決策**：使用純 HTML + Tailwind + 少量 JavaScript（class toggle）實作 tab，不引入額外框架。

**理由**：系統目前已用此模式（admin panel tabs），一致且無新依賴。

### 搜尋實作方式

**決策**：前端 JavaScript input event 過濾列表項目（比對 data-name 與 data-teacher 屬性）。

**理由**：班級數量少（預期數十個以內），前端過濾足夠，避免後端 API 改動。

## Risks / Trade-offs

- [破壞性] 側邊欄連結結構改變後，現有從側邊欄直連「成員管理」頁的使用者需改從 hub 頁進入。Mitigation：hub 頁提供明顯的快速入口卡片。
- [工作量] 此 change 涉及多個 template 與一個新路由，是所有 change 中最大的一個。Mitigation：拆分為獨立子任務，可分批實作。
