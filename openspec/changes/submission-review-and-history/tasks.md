## 1. 資料模型修改

- [ ] 1.1 修改 `TaskSubmission` model：套用設計決策「teacher_comment 欄位設計」，新增 `teacher_comment: str | None = None` 與 `reviewed_at: datetime | None = None`（TaskSubmission stores teacher comment）
- [ ] 1.2 撰寫 migration 確認既有 TaskSubmission 資料不受影響（New submissions have null comment）

## 2. 積分追回 API

- [ ] 2.1 實作 `POST /api/points/deduct` 端點：套用設計決策「積分追回操作設計」，新增 `teacher_deduct` entry type（Teacher can deduct points from a student、Teacher deduct entry type in point ledger）
- [ ] 2.2 驗證 reason 為必填，缺少時回 422（Deduction requires reason）
- [ ] 2.3 確認 `get_balance()` 正確計算含 `teacher_deduct` 的餘額（Student balance reflects deduction）

## 3. 提交 Comment API

- [ ] 3.1 實作 `POST /api/submissions/<submission_id>/comment` 端點（Teacher can leave a comment on a submission）
- [ ] 3.2 驗證 comment 可覆寫既有值（Comment can be overwritten）
- [ ] 3.3 驗證非班級教師無法留 comment（Unauthorized access is rejected）

## 4. 教師審閱頁面

- [ ] 4.1 在 `router.py` 新增 `GET /pages/teacher/class/<class_id>/submissions` 路由，套用設計決策「審閱頁入口設計」（Teacher can view all student submissions for a class）
- [ ] 4.2 建立 `src/templates/teacher/submission_review.html`，使用 /ui-ux-pro-max 風格，按學生分組顯示提交列表（Review page lists submissions）
- [ ] 4.3 在審閱頁加入 comment 輸入表單與積分追回按鈕（Teacher can leave a comment on a submission、Teacher can deduct points from a student）

## 5. 學生學習歷程頁面

- [ ] 5.1 在 `router.py` 新增 `GET /pages/student/history` 路由，套用設計決策「學習歷程頁入口設計」，初始載入最新 50 筆（Student can view their learning history）
- [ ] 5.2 建立 `src/templates/student/learning_history.html`，使用 /ui-ux-pro-max 風格，顯示提交時間軸（History page shows all submissions）
- [ ] 5.3 在學生側邊欄加入「學習歷程」連結
- [ ] 5.4 顯示 teacher_comment（若存在）（Teacher comment shown when present）

## 6. 測試

- [ ] 6.1 為 `teacher_deduct` 積分扣除撰寫單元測試（含餘額計算）
- [ ] 6.2 為 comment API 撰寫測試（含覆寫與權限驗證）
- [ ] 6.3 為學習歷程路由撰寫整合測試
