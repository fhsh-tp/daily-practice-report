## Context

`User` model 目前有 `email` 欄位但為可選。側邊欄頭像用文字首字母。管理員建立使用者的表單在 `admin/user_form.html`，無 email 必填驗證。

## Goals / Non-Goals

**Goals:**

- 個人設定頁可修改 display_name 與密碼
- Gravatar 以 email MD5 hash 呈現，fallback 為 identicon
- 新建帳號時 email 必填（前端 + 後端驗證）

**Non-Goals:**

- 不實作 email 驗證流程（發送確認信）
- 不允許使用者自行修改 email（由管理員管理）
- 不實作上傳自訂頭像

## Decisions

### Gravatar URL 計算位置

**決策**：在 Jinja2 template 中透過 custom filter 計算 Gravatar URL，或在 `webpage_context` 中為每個 request 計算並注入。選擇在 template filter 層計算（`gravatar_url(email, size=40)`）。

**理由**：不需要修改所有路由；在 template 層計算足夠，email 已在 `current_user` 物件中。

### 個人設定頁表單設計

**決策**：設定頁分兩個獨立表單：「更新顯示名稱」與「修改密碼」（各自 POST）。

**理由**：兩個操作性質不同（一個是資訊更新，一個是安全操作），分開表單更清楚也避免誤觸。

### 既有帳號 email 處理

**決策**：不強制既有帳號補填 email，但在個人設定頁頂端顯示「請更新您的 email 以啟用頭像功能」提示（若 email 為空）。

**理由**：強制遷移風險高；opt-in 提示讓使用者自行決定。

## Risks / Trade-offs

- [相容性] 若既有使用者 email 為空，Gravatar URL 產生 hash 為空字串的情況。Mitigation：template filter 中若 email 為空則直接回傳 identicon URL（`https://www.gravatar.com/avatar/?d=identicon`）。
