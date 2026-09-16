# Week 8 Midterm Starter

這是第 8 週期中個人小專題的學生 starter。請把它複製成自己的專題資料夾，再依照 `app.py` 裡的 TODO 改造成你的 App。

## 功能目標

這份 starter 已經提供：

- Streamlit 基本頁面。
- `.env` 與 Streamlit Secrets 雙軌設定。
- OpenAI Responses API helper。
- Structured Outputs 範例 schema。
- 可選 streaming helper，作為加分功能骨架。
- 基本輸入檢查與錯誤提示。
- 結果顯示區與原始 JSON 檢視。

## 快速開始

課堂採 Python **3.12**（本次測試為 **3.12.13**）。以下指令從本 App 資料夾執行；從課程 repo 開啟時，先進入 `week08/week08_midterm_starter`。

請先在你的專題資料夾建立虛擬環境，讓這個 Streamlit 專案使用自己的套件版本。

Windows PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
```

macOS / Linux：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

本機開發請複製 `.env.example` 成 `.env`：

```powershell
Copy-Item .env.example .env
```

macOS / Linux：

```bash
cp .env.example .env
```

然後在 `.env` 填入：

```text
OPENAI_API_KEY=你的OpenAIAPIKey
OPENAI_MODEL=gpt-5.4-mini
```

部署到 Streamlit Community Cloud 時，請把相同設定放到 Streamlit Secrets。不要把 `.env` 或 `.streamlit/secrets.toml` 上傳到 GitHub。

## 執行

```bash
python -m streamlit run app.py
```

尚未填 `OPENAI_API_KEY` 也可以開啟畫面，App 會顯示提醒；填好 key 後才會實際呼叫 API。

## Structured Outputs 的錯誤分流

`extract_structured()` 先檢查模型拒答與 `response.status`，確認回應完成後才讀取 `output_text` 並用 `json.loads()` 轉成 dict。這延續第 6 週的安全處理：不能把拒答或中斷時的部分文字當成專題結果。

| 情況 | App 的處理 |
|---|---|
| 模型拒答 | 顯示拒答原因，不顯示 structured result |
| `incomplete` | 依輸出長度限制、內容過濾或其他原因顯示提示，不解析部分文字 |
| 空 `output_text` | 提醒檢查 schema、prompt 或 API 回應 |
| JSON 無法解析 | 顯示格式錯誤，保留原有解析保護 |

改造自己的專題時，請保留這個檢查順序，並依題目調整使用者看得懂的錯誤文字。

## 你需要完成的 TODO

- 修改 `PROJECT_TITLE` 與 `PROJECT_DESCRIPTION`。
- 改寫 `SYSTEM_PROMPT`。
- 依你的專題設計 `DEFAULT_SCHEMA`。
- 在 `build_prompt()` 中設計任務指令。
- 修改 `render_project_form()` 的欄位。
- 調整 `render_structured_result()` 的顯示方式。
- 選做：把 `stream_ai()` 搭配 `st.write_stream()` 加入結果區，作為 streaming 加分功能。
- 補完自己的 README。

## 繳交前檢查

- [ ] App 可以用 `python -m streamlit run app.py` 執行。
- [ ] 已建立並啟用虛擬環境，例如 `.venv`。
- [ ] 至少一個功能會呼叫 OpenAI API。
- [ ] 至少一個功能使用真 structured output，不是只在 prompt 中要求「請用 JSON 回答」。
- [ ] `.env` 沒有上傳到 GitHub。
- [ ] `.gitignore` 有排除 `.env`、`.streamlit/secrets.toml`、`.venv/` 與 `__pycache__/`。
- [ ] README 說明專題目的、安裝方式、執行方式、輸出格式與限制。

## 安全紅線

API key 只能放在本機 `.env` 或 Streamlit Secrets。不得寫死在 `app.py`、README、notebook 或任何會上傳 GitHub 的檔案中。

## 啟動位置與 Community Cloud 部署

先啟用已安裝套件的 Python 3.12 虛擬環境，再選擇一種方式：

| 使用方式 | 啟動指令／Main file path |
|---|---|
| 本機：工作目錄是本 App 資料夾 | `python -m streamlit run app.py` |
| 本機：工作目錄是整個課程 repo 根目錄 | `python -m streamlit run week08/week08_midterm_starter/app.py` |
| 雲端：使用整個課程 repo | Main file path：`week08/week08_midterm_starter/app.py` |
| 雲端：把本 App 資料夾內容獨立成 repo | Main file path：`app.py` |

本 App 未提供自訂 `.streamlit/config.toml`，使用 Streamlit 預設設定。
`requirements.txt` 與 `app.py` 保持同一目錄；獨立成 repo 時也要保留 helper、範例資料與現有 `.streamlit` 範例檔。

在 Community Cloud 部署的 Advanced settings 選擇 **Python 3.12**，把 `.streamlit/secrets.example.toml` 的設定填入平台 Secrets；本機則使用 `.env` 或 `.streamlit/secrets.toml`。真實金鑰檔不可提交。

完整 Windows 課堂快照、設定優先順序、Colab 差異與部署檢核，見[課堂環境與部署指南](../../docs/課堂環境與部署指南.md)。若把 App 獨立成 repo，請一併保留指南副本或改成原課程 repo 的文件連結。
本次已測本機離線流程；實際 Community Cloud 安裝、瀏覽器互動與付費 API 仍待上課前確認。
