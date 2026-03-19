## Context

系統目前在多個 HTML template 中直接呼叫瀏覽器原生 `alert()`、`confirm()` 共 16 處，分佈於 5 個 template。積分後端已完整（PointTransaction + ClassPointConfig），但 dashboard 未傳入積分數值。任務模板無封存機制，教師無法隱藏舊模板。徽章頁面因 URL 不符（`/pages/student/badges` vs `/pages/students/me/badges`）導致 404。

## Goals / Non-Goals

**Goals:**
- 修正所有已確認的 URL/連結 Bug
- 建立全站共用、非阻塞式的 Modal 元件，取代原生 dialog
- 積分從後端正確傳入 dashboard，提交任務後顯示獲得積分
- 任務模板支援封存（`is_archived`），封存後對未有提交記錄的學生隱藏

**Non-Goals:**
- 不重新設計積分系統架構
- 不引入前端框架（維持 vanilla JS + Tailwind）
- 不為 modal 提供動畫效果（可後續加入）

## Decisions

### Modal 元件定義在 base.html，全站共用

在 `shared/base.html` 的 `{% block scripts %}` 前新增 modal HTML 結構與 JS API：

```js
window.Modal = {
  confirm(message, onConfirm, onCancel),
  alert(message, onClose)
}
```

替換方式：`confirm(msg)` → `Modal.confirm(msg, () => { ... })`；`alert(msg)` → `Modal.alert(msg)`。

選擇此方式而非各頁面各自定義：確保外觀一致、只需維護一份程式碼。

### 積分資料在 dashboard_page 查詢後傳入 context

`dashboard_page` handler 目前已查詢 class 清單，新增一次 `PointTransaction` 彙整查詢取得學生總積分，傳入 `stats.total_points`。不建立獨立 API endpoint，直接 server-side render。

### 任務模板封存：`is_archived` flag + 軟隱藏

在 `TaskTemplate` 新增 `is_archived: bool = False`。封存後：
- `templates_list_page` 教師仍可看到封存的模板（標示灰色）
- `get_template_for_date()` 跳過封存模板（學生看不到）
- 有提交記錄的學生仍可在歷史中看到模板快照（`template_snapshot` 已有）

## Risks / Trade-offs

- [Modal 回呼替換] 原 `confirm()` 是同步阻塞，新 Modal 是非同步回呼 → 需逐一確認每處的邏輯正確替換
- [積分查詢] 每次 dashboard 載入多一次 DB 查詢 → 資料量小，可接受
