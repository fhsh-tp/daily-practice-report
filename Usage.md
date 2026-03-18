# 使用說明

本文件說明如何以教師或學生身份操作 Daily Practice Report System API。

## 認證

除登入端點外，所有 Endpoint 都需要有效的 Session。

### 登入

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=<username>&password=<password>
```

### 登出

```http
POST /auth/logout
```

---

## 教師操作流程

### 1. 建立班級

```http
POST /classes
Content-Type: application/json

{
  "name": "Web Dev 2026"
}
```

### 2. 建立學生帳號

```http
POST /users
Content-Type: application/json

{
  "username": "student01",
  "password": "secure-password",
  "display_name": "小明"
}
```

Username 不可重複。帳號預設 `role=student`。

### 3. 將學生加入班級

```http
POST /classes/{class_id}/members
Content-Type: application/json

{
  "username": "student01"
}
```

### 4. 建立 Task Template

```http
POST /templates
Content-Type: application/json

{
  "title": "第 1 天 — HTML 基礎",
  "description": "完成 HTML 基礎練習題。",
  "fields": [
    { "key": "answer", "label": "你的答案", "type": "text" }
  ]
}
```

### 5. 將 Template 指派給班級與日期

```http
POST /classes/{class_id}/assignments
Content-Type: application/json

{
  "template_id": "<template_id>",
  "date": "2026-03-18"
}
```

### 6. 設定簽到時間區間

```http
PUT /classes/{class_id}/checkin/config
Content-Type: application/json

{
  "start_time": "08:00",
  "end_time": "09:00"
}
```

### 7. 覆蓋特定日期的簽到時間

```http
POST /classes/{class_id}/checkin/overrides
Content-Type: application/json

{
  "date": "2026-03-20",
  "start_time": "09:00",
  "end_time": "10:30"
}
```

### 8. 定義徽章

```http
POST /classes/{class_id}/badges
Content-Type: application/json

{
  "name": "初次提交",
  "description": "首次提交練習報告時獲得",
  "icon": "star",
  "triggers": ["submission.first"]
}
```

---

## 學生操作流程

### 1. 每日簽到

```http
POST /classes/{class_id}/checkin
```

### 2. 提交當日練習報告

```http
POST /submissions
Content-Type: application/json

{
  "class_id": "<class_id>",
  "date": "2026-03-18",
  "data": {
    "answer": "我的答案"
  }
}
```

每位學生每次指派**僅能提交一次**，重複提交會回傳 `409 Conflict`。

### 3. 查看排行榜

```http
GET /classes/{class_id}/leaderboard
```

### 4. 查看獎品

```http
GET /classes/{class_id}/prizes
```

### 5. 查看社群牆

```http
GET /classes/{class_id}/feed
```

### 6. 對貼文加 Reaction

```http
POST /feed/{post_id}/reactions
Content-Type: application/json

{
  "emoji": "👍"
}
```

---

## 錯誤回應

所有錯誤皆遵循 FastAPI 標準格式：

```json
{
  "detail": "錯誤說明"
}
```

常見 HTTP 狀態碼：

| 狀態碼 | 說明 |
|---|---|
| `400` | 請求格式錯誤或驗證失敗 |
| `401` | 未登入 |
| `403` | 權限不足（角色錯誤） |
| `404` | 資源不存在 |
| `409` | 資料衝突（例如重複提交或 Username 已存在） |

---

## 互動式 API 文件

在 `dev` 模式下，FastAPI 的互動式文件可於以下位置存取：

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc
