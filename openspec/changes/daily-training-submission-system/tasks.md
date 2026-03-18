## 1. 基礎建設與模組結構

- [x] 1.1 移除 SQLModel、aiomysql、aiosqlite、greenlet 相依套件，新增 beanie、motor、python-multipart 至 pyproject.toml
- [x] 1.2 依照模組結構採 Feature-based 而非 Layered 原則建立目錄：src/core/auth、src/core/users、src/core/classes、src/tasks/templates、src/tasks/submissions、src/tasks/checkin、src/gamification/points、src/gamification/badges、src/gamification/prizes、src/community/feed、src/extensions/protocols、src/extensions/registry
- [x] 1.3 重寫 src/shared/database.py 為 Beanie 初始化邏輯（init_beanie），移除 SQLAlchemy engine 與 session 依賴
- [x] 1.4 更新 src/main.py lifespan 函式以在 startup 呼叫 Beanie 初始化並完成 Startup registration in lifespan
- [x] 1.5 更新 Dockerfile 與 docker-compose.yml 新增 MongoDB service（motor 連接至 mongodb://mongo:27017）

## 2. Migration Script 框架

- [x] 2.1 建立 scripts/migrate.py CLI 入口點，支援 init、up、down、status 四個子指令（Migration CLI）
- [x] 2.2 設計 Migration script structure：每個 migration 為 scripts/migrations/YYYYMMDD_NNN_description.py，包含 async forward() 與 async backward()
- [x] 2.3 實作 Migration tracking collection：在 MongoDB 建立 migrations collection，記錄 filename、applied_at、direction
- [x] 2.4 實作 Migration idempotency check：up 指令跳過已記錄的 migration，全部完成時印出 "Nothing to migrate"
- [x] 2.5 建立第一個 migration 檔案 scripts/migrations/20260317_001_initial_indexes.py（建立常用查詢的 MongoDB indexes）

## 3. Extension Registry 與 Protocol 擴充點

- [x] 3.1 定義 Protocol definitions for extension points：在 src/extensions/protocols/ 建立 AuthProvider、RewardProvider、BadgeTrigger、SubmissionValidator 四個 Python Protocol（擴充點使用 Python Protocol + Registry 而非繼承）
- [x] 3.2 實作 ExtensionRegistry singleton：支援 register(protocol_type, key, impl) 與 get(protocol_type, key)，在 register 時以 isinstance 檢查 Protocol 相容性
- [x] 3.3 建立 FastAPI dependency injection via registry：提供 get_auth_provider()、get_reward_providers()、get_badge_triggers()、get_submission_validators() 等 Depends 工廠函式
- [x] 3.4 實作 Test registry helper：TestRegistry context manager，測試期間替換 singleton，結束後恢復

## 4. 認證系統（user-auth）

- [x] 4.1 建立 User Beanie Document（MongoDB 文件設計）：欄位包含 username、hashed_password、display_name、role（student/teacher）、created_at
- [x] 4.2 實作 LocalAuthProvider（AuthProvider extension point 的預設實作）：authenticate(credentials) 驗證帳號密碼並回傳 User
- [x] 4.3 實作認證：JWT + Cookie Session（JWT-based session management）：使用 PyJWT 發行含 exp、user_id、role 的 token，存入 HttpOnly Cookie
- [x] 4.4 建立 auth router：POST /auth/login（User login with credentials）、POST /auth/logout、GET /auth/me
- [x] 4.5 建立 auth middleware / dependency：validate_token Depends，expired token 重導向 login
- [x] 4.6 實作 Role-based access control：require_teacher()、require_student() Depends，拒絕非授權 role 時回傳 403
- [x] 4.7 建立 teacher admin router：POST /admin/users（User registration by teacher），老師建立學生帳號
- [x] 4.8 實作 Password change endpoint：POST /auth/change-password，驗證舊密碼後更新並失效現有 session

## 5. 班級管理（class-management）

- [x] 5.1 建立 Class、ClassMembership Beanie Documents（MongoDB 文件設計）：Class 包含 name、description、visibility、invite_code、owner_id；Membership 包含 class_id、user_id、role
- [x] 5.2 實作 Teacher creates a class：POST /classes，自動產生 invite_code，建立者成為 owner
- [x] 5.3 實作 Student joins a class via invite code：POST /classes/join，Student joins a class，驗證 code 後新增 membership
- [x] 5.4 實作 public class browse 與 join：GET /classes/public 列出公開班級，POST /classes/{id}/join 加入
- [x] 5.5 實作 Class visibility control：teacher 可設定 visibility=public/private
- [x] 5.6 實作 Teacher manages class members：DELETE /classes/{id}/members/{user_id} 移除學生，PATCH 升為 co-teacher
- [x] 5.7 實作 Class invite code regeneration：POST /classes/{id}/invite-code/regenerate，舊 code 立即失效

## 6. 任務模板（task-templates）

- [x] 6.1 建立 TaskTemplate、FieldDefinition Beanie Documents（MongoDB 文件設計，嵌入欄位）：FieldDefinition 包含 name、field_type（text/markdown/number/checkbox）、required
- [x] 6.2 實作 Teacher creates a task template：POST /classes/{id}/templates，至少一個欄位（Supported field types 驗證）
- [x] 6.3 實作 Teacher assigns template to a date：POST /classes/{id}/template-assignments，關聯 template_id 與 date
- [x] 6.4 實作 Teacher edits a template：PATCH /templates/{id}，更新模板但已提交資料保留 snapshot
- [x] 6.5 實作 Teacher deletes a template：DELETE /templates/{id}，有提交紀錄時拒絕刪除
- [x] 6.6 建立學生端 today's template endpoint：GET /classes/{id}/today-template，無模板時回傳適當訊息
- [x] 6.7 建立 Jinja2 模板管理頁面（老師）：template list、create、edit

## 7. 任務提交（task-submissions）

- [x] 7.1 建立 TaskSubmission Beanie Document（MongoDB 文件設計）：包含 template_snapshot、field_values、student_id、class_id、date、submitted_at
- [x] 7.2 實作 Student submits daily task：POST /classes/{id}/submissions，Required fields enforced，Duplicate submission rejected，提交成功後呼叫所有 RewardProviders
- [x] 7.3 實作 SubmissionValidator extension point：在提交前依序呼叫所有已注冊的 SubmissionValidator，任一回傳 invalid 則拒絕
- [x] 7.4 實作 Student views submission history：GET /students/me/submissions，依日期倒序列出
- [x] 7.5 實作 Teacher views class submissions：GET /classes/{id}/submissions?date=YYYY-MM-DD，含未提交學生列表
- [x] 7.6 建立 Jinja2 提交頁面：含 EasyMDE WYSIWYG Markdown 編輯器（前端 WYSIWYG Markdown 編輯器，CDN 引入）供 markdown 型別欄位使用

## 8. 簽到系統（checkin）

- [x] 8.1 建立 CheckinConfig、DailyCheckinOverride、CheckinRecord Beanie Documents（MongoDB 文件設計，簽到排程：全域 + 當日覆蓋）
- [x] 8.2 實作 Global check-in schedule：POST /classes/{id}/checkin-config，設定 active_weekdays 與 default_window
- [x] 8.3 實作 Per-day check-in override：POST /classes/{id}/checkin-overrides，老師設定當日覆蓋，優先於全域設定
- [x] 8.4 實作 Student check-in：POST /classes/{id}/checkin，驗證視窗開放、防止 Duplicate check-in，成功後呼叫 RewardProviders
- [x] 8.5 實作 Check-in status visibility：GET /classes/{id}/checkin-status，回傳 open/closed 狀態與關閉時間
- [x] 8.6 建立 Jinja2 簽到頁面：顯示狀態、按鈕、倒數提示

## 9. 點數系統（points-system）

- [x] 9.1 建立 PointTransaction Beanie Document（MongoDB 文件設計，使用參照連結 student 與 class）：包含 student_id、amount、reason、source_event、class_id、created_at（Point balance computed from transactions）
- [x] 9.2 實作 CheckinRewardProvider 與 SubmissionRewardProvider（RewardProvider extension point 預設實作）：Points awarded on check-in and submission，從 ClassConfig 讀取點數設定
- [x] 9.3 實作 Teacher revokes points：POST /classes/{id}/students/{uid}/point-revoke，建立負數 transaction，金額上限為學生現有餘額
- [x] 9.4 實作 Student views point history：GET /students/me/points，回傳完整 transaction list
- [x] 9.5 實作 balance 計算函式：從 PointTransaction 加總（不存 balance 欄位）
- [x] 9.6 建立老師點數管理頁面（Jinja2）：顯示學生餘額列表、追回點數表單

## 10. 成就徽章（badge-system）

- [x] 10.1 建立 BadgeDefinition、BadgeAward Beanie Documents（MongoDB 文件設計）
- [x] 10.2 實作 BadgeTrigger extension point：定義 Protocol，評估 trigger 後自動授予（Badge awarded automatically on trigger）
- [x] 10.3 實作 ConsecutiveCheckinTrigger 與 SubmissionCountTrigger 內建觸發器（BadgeTrigger extension point）
- [x] 10.4 在每個 RewardEvent 後非同步評估所有 BadgeTriggers（Badge not awarded if already held）
- [x] 10.5 實作 Badge definition by teacher：POST /classes/{id}/badges，關聯 trigger keys
- [x] 10.6 實作 Teacher awards badge manually：POST /classes/{id}/badges/{bid}/award，可附 reason
- [x] 10.7 實作 Student views earned badges：GET /students/me/badges，含 award date
- [x] 10.8 建立學生徽章展示頁面（Jinja2）

## 11. 社群分享牆（community-feed）

- [x] 11.1 建立 FeedPost、Reaction Beanie Documents（MongoDB 文件設計）
- [x] 11.2 實作 Student shares a submission to feed：POST /classes/{id}/feed，學生明確選擇分享（Submission not shared by default）
- [x] 11.3 實作 Class members view the feed：GET /classes/{id}/feed，非成員回傳 403，依時間倒序（Non-member cannot view feed）
- [x] 11.4 實作 Reactions on feed posts：POST /posts/{id}/reactions，每人每文限一個，支援移除（Duplicate reaction rejected）
- [x] 11.5 實作 Teacher removes feed posts：DELETE /posts/{id}（teacher），不刪除底層提交
- [x] 11.6 實作 Student removes own post：DELETE /posts/{id}（自己的文章）
- [x] 11.7 建立社群分享牆 Jinja2 頁面

## 12. 獎品 Preview（prize-preview）

- [ ] 12.1 建立 Prize Beanie Document（MongoDB 文件設計）：包含 title、description、prize_type（online/physical）、image_url、point_cost、visible、class_id
- [ ] 12.2 實作 Teacher creates prize preview：POST /classes/{id}/prizes，支援 online 與 physical 兩種類型
- [ ] 12.3 實作 Students view prize showcase：GET /classes/{id}/prizes，只回傳 visible=true 的獎品
- [ ] 12.4 實作 Teacher manages prize visibility：PATCH /prizes/{id}，設定 visible true/false
- [ ] 12.5 實作 Teacher edits and deletes prizes：PATCH / DELETE /prizes/{id}

## 13. 排行榜（leaderboard）

- [ ] 13.1 實作 Class leaderboard：GET /classes/{id}/leaderboard，依 point balance 降冪排列，Tied students share rank
- [ ] 13.2 實作 Teacher controls leaderboard visibility：PATCH /classes/{id}/settings leaderboard_enabled，學生無權限查看時回傳訊息
- [ ] 13.3 實作 Cross-class leaderboard：GET /leaderboard，聚合所有 public + leaderboard enabled 班級的學生餘額（Cross-class leaderboard 可見度規則）
- [ ] 13.4 建立排行榜 Jinja2 頁面：顯示 Leaderboard rank display 資訊（rank 編號、display name、points、badge count），同分者共用相同名次
