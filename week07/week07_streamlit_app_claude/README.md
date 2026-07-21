# Week 7｜Streamlit AI Web App（Claude Code 版）

「生成式AI應用開發」第 7 週範例專案。把前幾週在 Colab 學到的 OpenAI Responses API
（問答、串流、對話記憶）整合成一個可部署的 Streamlit Web App。

搭配教材：
- `生成式AI應用開發_第07週_Streamlit_Web_App入門_學生版_Claude生成.ipynb`
- `生成式AI應用開發_第07週_Streamlit_Web_App入門_教師版_Claude生成.ipynb`
- `生成式AI應用開發_第07週_Git實作教材.md`（Git / GitHub / 部署流程）

## 功能

- 💬 聊天：session state 對話記憶 + 串流回覆（`st.chat_input` / `st.write_stream`）
- 📝 摘要：`st.form` 表單，選擇摘要風格
- 📄 檔案：上傳 `.txt` / `.md` 做重點摘要
- ⚙️ 側邊欄：自訂 system prompt、切換串流、顯示累計 token 與估算成本
- 🔑 金鑰管理：本機 `.env` 與雲端 `st.secrets` 雙軌

## 本機執行

```bash
# 1. 安裝套件
pip install -r requirements.txt

# 2. 建立 .env（複製範例後填入自己的 key）
cp .env.example .env

# 3. 啟動
streamlit run app.py
```

瀏覽器會自動開啟 `http://localhost:8501`。

## 部署到 Streamlit Community Cloud

1. 把整個資料夾推上 GitHub（**確認 `.env` 未被追蹤**）。
2. 到 <https://share.streamlit.io> 用 GitHub 登入 → New app。
3. 選 repo、branch `main`、Main file path 填 `app.py`。
4. Deploy 後到 App → Settings → **Secrets**，填入：

   ```toml
   OPENAI_API_KEY = "你的key"
   OPENAI_MODEL = "gpt-5.4-mini"
   ```

5. 之後改程式只要 commit + push，Streamlit 會自動重新部署。

## 安全提醒

- 絕不要把 `.env` 或 `.streamlit/secrets.toml` 推上 GitHub（已在 `.gitignore`）。
- 不要上傳個資、機密或敏感文件。
- API 會產生費用，測試時控制輸入長度與次數。
