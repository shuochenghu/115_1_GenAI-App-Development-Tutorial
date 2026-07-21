# 生成式AI應用開發 第07週｜Git 與 GitHub 實作教材

## 本單元定位

- **時間**：第七週前段（約 30 分鐘），接續 Streamlit 開發
- **目標**：完成 Streamlit 專案的 Git 版本管理流程，並部署至 Streamlit Community Cloud
- **前提**：學生應已在 Week 1 完成 GitHub 帳號建立與 GitHub Desktop 安裝
- **不要求**：branch 管理、merge conflict 處理、CI/CD 流程

---

## 一、為什麼這門課需要 Git 與 GitHub？

期中和期末專題都需要：

```
本機開發  →  版本紀錄  →  雲端備份  →  部署上線
   ↓              ↓              ↓             ↓
 寫程式        Git commit     GitHub repo   Streamlit Cloud
```

Git 解決三個問題：

| 問題 | 沒有 Git | 有 Git |
|------|---------|--------|
| 改壞程式怎麼辦 | 只能手動還原，或放棄 | 回到任何一個 commit |
| 多人共同開發 | 互相蓋掉彼此的檔案 | 各自開發後合併 |
| 部署到網路上 | 要手動上傳檔案 | Streamlit 直接讀 GitHub |

---

## 二、核心概念

| 名詞 | 用一句話理解 |
|------|------------|
| **Git** | 安裝在電腦上的版本控制工具 |
| **GitHub** | 存放程式碼的雲端平台，像 Google Drive 但專為程式設計 |
| **Repository（Repo）** | 一個專案的程式碼資料夾 |
| **Commit** | 一次「有說明的存檔」，可以日後還原 |
| **Push** | 把本機的 commit 上傳到 GitHub |
| **Clone** | 把 GitHub 上的 repo 複製到本機 |
| **README.md** | 專案說明文件，期中與期末都必須撰寫 |
| **GitHub Desktop** | 讓你用滑鼠操作 Git，不需打指令 |
| **.gitignore** | 告訴 Git 哪些檔案不要追蹤（如 API key） |

---

## 三、前置確認

本週開始前，請確認以下項目（Week 1 應已完成）：

- [ ] GitHub 帳號已建立並可登入
- [ ] GitHub Desktop 已安裝並登入帳號
- [ ] VS Code 已安裝

若尚未完成，請參考：
- GitHub 帳號：[https://github.com](https://github.com) → Sign up
- GitHub Desktop：[https://desktop.github.com](https://desktop.github.com)

---

## 四、Streamlit 專案的標準檔案結構

每個可部署的 Streamlit 專案，資料夾內應包含以下四個檔案：

```
my-streamlit-app/
├── app.py                  ← 主程式
├── requirements.txt        ← Python 套件清單（部署必要）
├── .gitignore              ← 告訴 Git 忽略哪些檔案
├── .env                    ← API key（本機用，不推上 GitHub）
└── README.md               ← 專案說明（期中期末必須撰寫）
```

### requirements.txt 是什麼？

Streamlit Community Cloud 部署時，會根據 `requirements.txt` 自動安裝套件。本週需要：

```txt
openai
streamlit
python-dotenv
```

> 每次新增 `import` 一個外部套件，就要把套件名稱加進 `requirements.txt`

---

## 五、.gitignore 設定（API Key 安全的關鍵）

`.gitignore` 告訴 Git 哪些檔案不要推上 GitHub。**這是 API key 安全的第一道防線。**

### 建立 .gitignore

在專案根目錄建立 `.gitignore` 檔案，輸入以下內容：

```
# API key 與環境變數
.env
*.env

# Python 暫存檔
__pycache__/
*.pyc
*.pyo

# Streamlit 本機設定
.streamlit/secrets.toml

# VS Code 設定
.vscode/

# 系統檔案
.DS_Store
Thumbs.db
```

### 為什麼 `.env` 不能推上 GitHub？

```
.env 檔案內容：
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx

若推上 GitHub（公開 repo）：
→ 任何人都能看到你的 API key
→ 有人可能盜用，導致你的帳號產生大量費用
→ OpenAI 偵測到洩漏的 key 會自動停用，但損失可能已造成
```

> **記住：先建立 `.gitignore`，再做第一次 commit，才能確保 `.env` 永遠不會被追蹤。**

---

## 六、實作步驟：建立 Streamlit App 的 Repository

### Step 1｜在 GitHub 建立新 Repository

1. 登入 GitHub 網頁
2. 點選右上角 **+** → **New repository**
3. 填寫以下資訊：

| 欄位 | 填寫內容 |
|------|---------|
| Repository name | `week07-streamlit-app` |
| Description | Week 7 Streamlit 練習 |
| Public / Private | **Public** |
| Add a README file | ✅ 勾選 |
| Add .gitignore | 選擇 **Python** |

4. 點選 **Create repository**

> 選擇 Python 的 `.gitignore` 模板，GitHub 會自動建立基本的忽略設定，再手動補上 `.env`

---

### Step 2｜用 GitHub Desktop Clone 到本機

1. 開啟 **GitHub Desktop**
2. 點選 **File → Clone repository**
3. 選擇 `week07-streamlit-app`
4. 選擇本機儲存路徑（建議：`C:\Users\你的名字\Documents\ai-course\week07`）
5. 點選 **Clone**

---

### Step 3｜在 VS Code 建立專案檔案

1. 在 GitHub Desktop 點選 **Open in Visual Studio Code**
2. 建立以下檔案：

**`.env`**（本機 API key，不推上 GitHub）
```
OPENAI_API_KEY=sk-proj-你的key
```

**`.gitignore`**（補上 `.env`，若模板未包含）
```
.env
*.env
.streamlit/secrets.toml
__pycache__/
```

**`requirements.txt`**
```
openai
streamlit
python-dotenv
```

**`app.py`**（本週 Streamlit 範例）
```python
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("我的第一個 AI 問答 App")

user_input = st.text_input("請輸入問題：")

if st.button("送出") and user_input:
    with st.spinner("思考中..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}]
        )
    st.write(response.choices[0].message.content)
```

---

### Step 4｜確認 .gitignore 正確運作

1. 回到 **GitHub Desktop**
2. 查看 Changes 欄位
3. 確認 `.env` **不在** Changes 清單中（代表已被 .gitignore 忽略）
4. `app.py`、`requirements.txt`、`.gitignore` 應出現在 Changes 清單

> 若 `.env` 出現在 Changes 清單，請先停下來，確認 `.gitignore` 是否正確設定，再繼續

---

### Step 5｜Commit

1. 在左下角 **Summary** 填入：
```
初始化專案：新增 app.py、requirements.txt、.gitignore
```
2. 點選 **Commit to main**

---

### Step 6｜Push 到 GitHub

1. 點選右上角 **Push origin**
2. 前往 GitHub 網頁確認檔案已上傳
3. 點開 `.gitignore`，確認 `.env` 列在其中
4. 確認 `.env` 檔案**不存在**於 GitHub repo 中

---

## 七、版本管理觀念

### 7-1 何時應該 Commit？

**原則：完成一個有意義的功能時就 commit，而不是改一行 commit 一次，也不是做完整個專題才 commit。**

| 適合 commit 的時機 | 範例 commit message |
|------------------|-------------------|
| 完成一個新功能 | `新增：串流輸出功能` |
| 修正一個 bug | `修正：修復送出按鈕無回應的問題` |
| 調整介面 | `更新：調整輸入欄位與按鈕排版` |
| 新增一個頁面 | `新增：加入歷史紀錄頁面` |
| 完成今天的開發進度 | `更新：完成 RAG 查詢功能初版` |

### 7-2 Commit Message 寫法

```
# 建議格式
動詞：具體說明做了什麼

# 好的範例
新增：支援 PDF 檔案上傳
修正：修復 API 回傳空字串時的錯誤
更新：將模型從 gpt-4o 改為 gpt-4o-mini

# 不好的範例
update
改了一些東西
aaa
test123
```

### 7-3 查看 Commit 歷史紀錄

**在 GitHub Desktop：**
1. 點選左側 **History** 分頁
2. 可以看到所有 commit 紀錄
3. 點選任一筆，右側會顯示該次修改的詳細差異

**在 GitHub 網頁：**
1. 進入 repo 頁面
2. 點選 **N commits**（顯示總 commit 數的連結）
3. 可以看到完整歷史，並點進去查看每次變更

### 7-4 回復到某個 Commit（基本操作）

若修改後程式出問題，想回到上一個正常版本：

**在 GitHub Desktop：**
1. 點選 **History** 分頁
2. 對想回復的 commit 按右鍵
3. 選擇 **Revert Changes in Commit**

> 這個操作不會刪除歷史紀錄，而是新增一個「取消這次修改」的 commit，是安全的做法

---

## 八、部署至 Streamlit Community Cloud

### 8-1 設定 Streamlit Secrets（取代本機 .env）

雲端部署時不能使用 `.env` 檔，要改用 Streamlit 的 secrets 功能：

1. 前往 [https://share.streamlit.io](https://share.streamlit.io)
2. 登入（使用 GitHub 帳號）
3. 點選 **New app**

### 8-2 部署步驟

| 欄位 | 填寫內容 |
|------|---------|
| Repository | 選擇 `week07-streamlit-app` |
| Branch | `main` |
| Main file path | `app.py` |

點選 **Deploy!** 後等待部署完成（約 1–2 分鐘）。

### 8-3 設定 API Key（Secrets）

部署完成後：

1. 點選 App 右上角 **⋮ → Settings**
2. 選擇 **Secrets**
3. 填入：

```toml
OPENAI_API_KEY = "sk-proj-你的key"
```

4. 點選 **Save**，App 會自動重新啟動

### 8-4 更新已部署的 App

之後每次修改程式碼，只需要：

```
修改 app.py
  → Commit（GitHub Desktop）
  → Push origin（GitHub Desktop）
  → Streamlit Cloud 自動偵測更新
  → 約 30 秒後公開網址自動更新
```

不需要手動重新部署。

---

## 九、課堂練習

### 練習 A｜確認 .gitignore 防護

1. 在專案中建立 `.env` 並填入一組假的 key：`OPENAI_API_KEY=sk-test-fake`
2. 回到 GitHub Desktop，確認 `.env` 沒有出現在 Changes
3. Commit 其他檔案並 Push
4. 到 GitHub 網頁確認 `.env` 不存在

### 練習 B｜修改功能並觀察 Commit 歷史

1. 在 `app.py` 新增一個功能（例如：加入 system prompt 設定）
2. 儲存後 commit，message 寫：`新增：支援自訂 system prompt`
3. 再做一次小修改並 commit
4. 在 GitHub Desktop 的 History 頁查看兩筆 commit 紀錄
5. 點進去確認每次的差異顯示正確

### 練習 C｜部署並取得公開網址

1. 完成 Streamlit App 基本功能
2. Push 到 GitHub
3. 在 Streamlit Community Cloud 部署
4. 設定 Secrets
5. 取得公開網址，確認 App 可正常運作
6. 將網址貼到課堂討論區

---

## 十、完整開發流程（本課程標準）

從本週開始，每次開發 Streamlit App 的流程：

```
1. 在 VS Code 撰寫或修改程式碼
        ↓
2. 在 GitHub Desktop 查看 Changes
        ↓
3. 確認 .env 不在 Changes 清單中
        ↓
4. 撰寫 commit message 並 Commit
        ↓
5. Push 到 GitHub
        ↓
6. Streamlit Community Cloud 自動偵測更新
        ↓
7. 約 30 秒後公開網址自動更新
```

> 期末專題每完成一個功能就 commit，讓老師和組員可以看到完整開發歷程，也方便出問題時回溯。

---

## 十一、常見問題

**Q1：Push 時出現「Authentication failed」？**
→ 在 GitHub Desktop 重新登入：File → Options → Accounts → Sign out 後再 Sign in

**Q2：Changes 沒有出現修改的檔案？**
→ 確認 VS Code 已儲存（標題列不應有白點 ●），並確認檔案在 clone 的資料夾內

**Q3：不小心 commit 了 .env 怎麼辦？**
→ 立刻到 OpenAI 後台撤銷（revoke）該 API key，重新申請一組新的 key
→ 在 GitHub Desktop 使用 Revert 並不夠，因為歷史紀錄中仍然存在
→ 事後可學習 `git filter-branch` 或 `BFG Repo Cleaner` 清除歷史，但預防遠比補救重要

**Q4：Streamlit Cloud 部署後顯示錯誤？**
→ 點選 App 右上角 **⋮ → Manage app** 查看 log，常見原因：
  - `requirements.txt` 少寫套件名稱
  - Secrets 的 key 名稱與程式碼中 `os.getenv()` 的名稱不符
  - `app.py` 路徑填錯

**Q5：Public repo 別人能看到我的程式碼嗎？**
→ 是的，但 `.env` 和 `secrets.toml` 不會推上去，所以 API key 是安全的
→ 期末專題需要 Public repo 才能部署到 Streamlit Community Cloud

---

## 十二、課後確認清單

本週結束後，請確認：

- [ ] 已建立 `week07-streamlit-app` repository
- [ ] `.gitignore` 已設定，`.env` 未被 Git 追蹤
- [ ] `requirements.txt` 包含所有使用的套件
- [ ] 已完成至少兩次有意義的 commit
- [ ] 在 GitHub 網頁可以看到 commit 歷史
- [ ] App 已部署至 Streamlit Community Cloud
- [ ] 公開網址可正常存取與使用

---

## 附錄：常用 Git 指令對照（命令列 vs GitHub Desktop）

| 動作 | 命令列 | GitHub Desktop |
|------|--------|---------------|
| 查看變更 | `git status` | 左側 Changes 欄 |
| 存檔（Commit） | `git commit -m "說明"` | 填 Summary → Commit |
| 上傳（Push） | `git push` | Push origin 按鈕 |
| 下載更新（Pull） | `git pull` | Fetch origin → Pull |
| 複製 repo | `git clone <url>` | File → Clone repository |
| 查看歷史 | `git log` | History 分頁 |
| 回復 commit | `git revert <hash>` | History → 右鍵 → Revert |
| 查看差異 | `git diff` | Changes 右側差異顯示 |
