## 1. 在 service 層加入 membership 驗證

- [x] 1.1 在 `src/tasks/submissions/service.py` 的 `submit_task()` 加入 ClassMembership 驗證，非班級成員拋出 ValueError（Submission endpoint validates class membership）
- [x] 1.2 在 `src/tasks/submissions/router.py` 的 `submit_task_endpoint` 捕捉 membership ValueError 並返回 HTTP 403
- [x] 1.3 在 `src/tasks/checkin/service.py` 的 `do_checkin()` 加入 ClassMembership 驗證，非班級成員拋出 ValueError（Checkin endpoint validates class membership）
- [x] 1.4 在 `src/tasks/checkin/router.py` 的 `checkin` 和 `checkin_browser` 端點捕捉 membership ValueError 並返回 HTTP 403

## 2. 在 router 層加入 class ownership 驗證 (checkin config)

- [x] 2.1 在 `src/tasks/checkin/router.py` 的 `configure_checkin` 加入 `can_manage_class()` 所有權驗證（Checkin config endpoints validate class ownership）
- [x] 2.2 在 `src/tasks/checkin/router.py` 的 `create_override` 加入 `can_manage_class()` 所有權驗證
- [x] 2.3 在 `src/tasks/checkin/router.py` 的 `checkin_config_page` 改用 `can_manage_class()` 替代直接 bit flag 檢查

## 3. 防禦性檢查

- [x] 3.1 在 `src/core/classes/router.py` 的 `update_discord_webhook` 加入 Discord webhook URL 用正則驗證，僅接受 Discord Webhook 格式或空字串（Discord webhook URL format validation）
- [x] 3.2 在 `src/core/system/router.py` 的 `post_setup` 加入 setup 密碼長度最低 8 字元驗證（Setup wizard enforces minimum admin password length）
- [x] 3.3 在 `src/core/system/startup.py` 或 `src/core/auth/jwt.py` 加入 JWT secret 檢查用 warning log，不用硬性阻擋（JWT secret safety check on startup）

## 4. 測試

- [x] 4.1 為 submission membership 驗證撰寫測試（非成員提交返回 403、成員提交正常）
- [x] 4.2 為 checkin membership 驗證撰寫測試（非成員打卡返回 403、成員打卡正常）
- [x] 4.3 為 checkin config ownership 驗證撰寫測試（其他班老師返回 403、本班老師正常、全局管理員正常）
- [x] 4.4 為 Discord webhook URL 驗證撰寫測試（有效 URL、無效 URL、空字串）
- [x] 4.5 為 setup 密碼長度驗證撰寫測試（短密碼被拒、長密碼通過）
- [x] 4.6 為 JWT secret warning 撰寫測試（預設值產生 warning、自訂值不產生）
