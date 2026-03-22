## Context

目前系統：學生簽到後立即獲得積分，作業提交後同樣立即獲得積分。老師端只有通用積分追回（直接從餘額扣分）。`TaskSubmission` 沒有審查狀態欄位，`CheckinRecord` 只記錄「有簽到」的事實，兩者都無法反映老師事後的裁量調整。學生 Dashboard 同時呈現班級卡片與任務，資訊密度過高。

## Goals / Non-Goals

**Goals:**

- 老師可對任意日期的班級出席做例外標記（遲到補分、到場確認撤銷）
- 老師可對已提交作業執行 approve/reject；reject 觸發積分撤銷並通知學生
- 補繳作業以獨立新記錄呈現，原 rejected 記錄保留
- 學生動態區顯示作業審查事件（approved/rejected）
- 學生 Dashboard 重構為「當天所有班級任務 + 搜尋」
- 學生 sidebar 新增班級導覽
- 修正「新增班級」按鈕在非 Dashboard 頁面無效的 Bug

**Non-Goals:**

- 簽到不引入審查流程（老師只處理例外）
- 不引入「暫定積分」機制（積分仍為立即入帳）
- 不重新設計任務模板或積分設定頁面

## Decisions

### AttendanceCorrection 記錄例外，不修改 CheckinRecord

CheckinRecord 繼續維持「有簽到」的事實記錄，不加狀態欄位。新增 `AttendanceCorrection` 文件，只在例外情況（遲到補分、撤銷已到）時建立記錄。這樣的設計確保簽到記錄的單一職責，且舊有測試不受影響。

積分校正透過 PointTransaction 處理：
- 遲到補分 → 正數 PointTransaction（source_event: "checkin_manual_late"）
- 撤銷已到 → 負數 PointTransaction（source_event: "checkin_manual_revoke"）

**替代方案考慮**：在 CheckinRecord 加 `override_status` 欄位——被否決，因為違反記錄的事實性質，且讓查詢複雜化。

### TaskSubmission 加 status 欄位，積分仍立即入帳

`TaskSubmission.status` 預設為 `"pending"`，積分在提交時立即入帳（維持現有 Option A 行為）。Teacher approve → status 改為 `"approved"`，積分不變。Teacher reject → status 改為 `"rejected"`，系統建立負數 PointTransaction 撤銷積分。

`parent_submission_id` 欄位追蹤補繳關係：補繳時原記錄維持 `"rejected"`，新記錄的 `parent_submission_id` 指向舊記錄。查重邏輯：`status != "rejected"` 的記錄計入一日唯一限制。

### 新增班級按鈕改為帶 Query Param 的連結

「新增班級」按鈕從 `dispatchEvent('open-create-class')` 改為 redirect 至 `GET /pages/dashboard?create_class=1`，由 Dashboard 偵測 query param 後自動開啟 modal。這樣任何頁面點擊都能正常運作。

### 學生 Dashboard 搜尋為 Client-side

當天任務數量有限（班級數 × 1），直接在前端 JS 對 task card 做 filter，無需額外 API。

## Risks / Trade-offs

- **積分撤銷後再 approve**：若老師先 reject 再 approve，需重新補發積分。系統須偵測此情況並建立正數 PointTransaction。→ 設計：approve 時若前一狀態為 rejected，補發積分。
- **補繳期限過期**：`resubmit_deadline` 超過後，系統 UI 層應隱藏補繳入口，但不硬性封鎖 API（避免前後端時間差問題）。
- **向後相容**：現有 `TaskSubmission` 記錄沒有 `status` 欄位 → Beanie 的 optional 欄位會以 `None` 讀取，邏輯上等同於 `"pending"`，不需 migration。
