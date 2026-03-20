## Why

教師端目前的班級管理體驗零散：側邊欄平鋪所有班級的工具連結（成員、模板），工具項目隨班級增加而線性成長，難以維護；每個班級缺乏統一的入口頁；封存班級與運作中班級混在同一列表且無搜尋功能。需要一次性重構教師班級管理 UX，提升可擴充性與易用性。

## What Changes

- **班級 Hub 頁面**：每個班級擁有獨立首頁（`/teacher/class/<class_id>`），整合成員管理、任務模板、簽到設定、排行榜、積分管理等工具的快速入口。
- **側邊欄重構**：教師工具區改為列出班級名稱（加上「＋新增班級」按鈕），點入班級後側邊欄顯示該班級的工具項目。
- **班級列表 Tab 切換**：教師儀表板及管理員班級管理頁加入「運作中 / 已封存」tab，封存班級不再干擾主列表。
- **搜尋功能**：運作中與已封存的班級列表各自提供依班級名稱或教師名稱搜尋的輸入框（前端過濾）。
- **UI/UX 品質**：全程搭配 `/ui-ux-pro-max` 技能，確保設計一致性與視覺品質。

## Capabilities

### New Capabilities

- `class-hub-page`：班級 Hub 頁面，整合該班級的所有教師工具入口

### Modified Capabilities

- `web-pages`：側邊欄重構、班級 hub 路由、教師儀表板 tab 切換
- `class-management`：班級列表加入 tab 切換（運作中/已封存）與搜尋功能

## Impact

- Affected specs: `class-hub-page`（新）、`web-pages`、`class-management`
- Affected code:
  - `src/templates/shared/base.html`（側邊欄重構）
  - `src/templates/teacher/`（新增 class_hub.html、修改 class_members.html 等）
  - `src/templates/student/dashboard.html`（tab 切換）
  - `src/templates/admin/classes_list.html`（tab 切換 + 搜尋）
  - `src/pages/router.py`（新增 class hub 路由）
