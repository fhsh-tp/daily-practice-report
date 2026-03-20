## Context

系統目前的側邊欄邏輯（`base.html`）、班級成員管理頁版面（`class_members.html`）、及學生儀表板（`student/dashboard.html`）各有一個獨立的 UI bug。這些問題不涉及資料模型或 API 設計變更，僅需修正 Jinja2 template 條件邏輯與 Tailwind CSS 佈局，以及 router 傳入額外欄位。

## Goals / Non-Goals

**Goals:**

- 修正系統管理員側邊欄顯示「建立第一個班級」的誤判邏輯
- 修正 `class_members.html` header flex 佈局跑版問題
- 在學生儀表板的班級卡片中顯示班級擁有者（教師）名稱

**Non-Goals:**

- 不重構側邊欄整體結構（此為 teacher-class-ux-refactor 的範疇）
- 不修改任何資料模型或 API 端點
- 不處理其他頁面的版面問題

## Decisions

### 側邊欄「建立第一個班級」條件修正

**決策**：在 `{% else %}` 分支（`classes` 為空）加入 `{% if not can_manage_all_classes %}` 保護條件。

**理由**：`can_manage_all_classes` 代表系統管理員，他們透過「管理工具 > 班級管理」管理班級，不需要教師工具的班級建立捷徑。若未有此條件，管理員即使看得到班級也會看到「建立第一個班級」，資訊矛盾。

### 班級成員管理頁 header 版面

**決策**：將兩個按鈕（任務模板、簽到設定）包入一個 `div.flex.gap-2` 群組，讓 header 成為「標題區 + 按鈕群組」兩個 flex 子元素。

**理由**：原本三個平行子元素搭配 `justify-between flex-wrap` 在視窗縮小時排版不可預期。群組化後 wrap 行為穩定。

### 學生儀表板帶入教師名稱

**決策**：在 `dashboard_page` router 的 `classes` 資料組裝迴圈中，透過 `User.get(cls.owner_id)` 查詢擁有者，並將 `owner_display_name` 加入 dict；若查詢失敗則 fallback 為空字串。

**理由**：最小侵入性修改。owner_id 已在 Class model 中，無需新增欄位或 API。

## Risks / Trade-offs

- [效能] dashboard_page 迴圈新增一次 `User.get()` 查詢 — 每個班級多一次 DB 查詢。Mitigation：班級數量通常很少（教師數個、學生數個），影響可忽略不計。
