## Why

系統目前存在多個已確認的 Bug（徽章頁面 404、任務模板無刪除/封存功能）及 UX 問題（瀏覽器原生 alert/confirm 對話框、積分未在 UI 顯示），直接影響使用者體驗與操作信心。

## What Changes

- **修復**：修正「我的徽章」連結 URL 不符（`/pages/student/badges` → `/pages/students/me/badges`），三個位置（sidebar、mobile tab bar、dashboard）同步修正
- **新增**：任務模板封存功能：教師可將模板標記為封存，封存後對未曾提交過的學生隱藏，保留歷史記錄
- **新增**：全站共用 Modal 元件（`ConfirmModal` / `AlertModal`），取代所有 5 個 template 中共 16 處的 `alert()`、`confirm()` 瀏覽器原生呼叫
- **增強**：積分顯示強化——dashboard 的「總積分」從後端真正傳值；任務提交成功後顯示本次獲得積分；dashboard 統計區的積分顯示有動態效果

## Capabilities

### New Capabilities

- `modal-system`: 全站共用的非阻塞式 Confirm/Alert modal，在 `shared/base.html` 中定義，所有頁面可直接使用

### Modified Capabilities

- `ui-design-system`: 新增 modal 元件規範至設計系統
- `points-system`: 積分顯示需求——學生應能在 dashboard 上看到自己目前的積分餘額，提交任務後應看到獲得的積分
- `task-templates`: 新增模板封存需求——教師可封存模板，封存模板對無提交記錄的學生不可見

## Impact

- Affected specs: `ui-design-system`、`points-system`、`task-templates`、new `modal-system`
- Affected code:
  - `src/templates/shared/base.html` — 修正徽章連結、新增 modal 元件
  - `src/templates/student/dashboard.html` — 修正徽章連結、積分顯示
  - `src/templates/teacher/templates_list.html` — 新增封存按鈕
  - `src/templates/admin/classes_list.html` — 替換 alert/confirm
  - `src/templates/admin/users_list.html` — 替換 alert/confirm
  - `src/templates/teacher/class_members.html` — 替換 alert/confirm
  - `src/templates/teacher/template_form.html` — 替換 alert
  - `src/tasks/templates/models.py` — 新增 `is_archived` 欄位
  - `src/tasks/templates/service.py` — 封存邏輯
  - `src/tasks/templates/router.py` — 封存 API endpoint
  - `src/pages/router.py` — dashboard 積分資料傳值
