# Week 12 圖片理解工具

這是第 12 週正式 Streamlit 範例專案。它把前幾週的檔案上傳、Prompt Engineering、Structured Outputs、錯誤處理與 secrets 管理整合到圖片輸入，使用 OpenAI Responses API 完成圖片描述、圖片問答、截圖理解，以及收據／表單結構化抽取。

## 學習重點

- 讀取上傳圖片的 bytes，檢查檔案 signature、格式、尺寸、影格與 8 MB 上限。
- 把圖片轉成 Base64 data URL，放入 Responses API 的 `input_image`。
- 使用 `detail=auto/low/high` 比較圖片細節、成本與辨識需求。
- 用 prompt 區分「直接可見證據」與「不確定推論」。
- 以 JSON Schema + `strict` 取得可由程式讀取的收據／表單欄位。
- 分流拒答、未完成、空輸出與 JSON 解析失敗。
- 明確提示圖片會傳到外部 API，禁止上傳個資、機密、醫療影像、未授權內容或 CAPTCHA。

## 建議環境

課堂統一採 Python 3.12；Windows x86_64 的完整套件版本見[課堂環境與部署指南](../../docs/課堂環境與部署指南.md)。

Windows PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
python -m streamlit run app.py
```

macOS / Linux：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python -m streamlit run app.py
```

若要重現 Windows 課堂快照，可在本 App 目錄使用：

```powershell
python -m pip install -r requirements.txt -c ../../environments/classroom-windows-py312.txt
```

## API 設定

將 `.env.example` 複製為 `.env`，填入測試用 API key：

```text
OPENAI_API_KEY=你的測試用APIKey
OPENAI_MODEL=gpt-5.4-mini
```

部署時改用平台 Secrets；不要提交 `.env` 或 `.streamlit/secrets.toml`。`gpt-5.4-mini` 是本課程既有預設且支援圖片輸入與 Responses API，但上課前仍應確認帳號可用模型。

## 建立無個資測試圖片

專案不直接提交產生出的 PNG，避免把生成檔混入教材。安裝套件後執行：

```powershell
python sample_data/create_demo_receipt.py
```

它會建立 `sample_data/demo_receipt.png`，內容是完全虛構的英文收據，可測試 `high` 細節與結構化抽取。檔案已列入 `.gitignore`。

## 操作順序

1. 選擇任務模式與圖片細節。
2. 上傳 PNG、JPEG、WEBP 或非動態 GIF；單檔上限 8 MB。
3. 先閱讀本機檢查結果，確認尚未呼叫 API。
4. 圖片問答模式需輸入問題；其他模式使用教材預設 prompt。
5. 按下「分析圖片」才會送出 API 請求。
6. 抽取模式要對照原圖核對日期、金額、品項與警告，不能直接當成會計或決策依據。

## 檔案結構

| 檔案 | 內容 |
|---|---|
| `app.py` | Streamlit 上傳、預覽、表單與結果顯示 |
| `vision_utils.py` | 圖片驗證、data URL、prompt、API 與錯誤分流 |
| `sample_data/create_demo_receipt.py` | 產生虛構課堂測試收據 |
| `.streamlit/config.toml` | 8 MB 上傳限制與原生主題 |

## 教學限制

- `store=False` 表示本次回應不保存供後續 API 取回，不代表圖片沒有傳送或處理；仍須遵守資料與隱私政策。
- 圖片輸入會轉成 token 計費；圖片數量、尺寸、細節等級與模型都會影響成本。
- Vision 可能看錯小字、旋轉文字、圖表、物件數量與空間位置，也可能產生錯誤描述。
- 本工具不是 OCR 保證、醫療判讀、身分辨識、無障礙合規驗證或財務自動入帳系統。
- `st.file_uploader(type=...)` 只做便利性篩選，因此 helper 仍檢查實際 bytes 與 Pillow 解碼結果。

## 部署入口

| 使用方式 | 啟動指令／Main file path |
|---|---|
| 本機：工作目錄是本 App | `python -m streamlit run app.py` |
| 本機：工作目錄是課程 repo 根目錄 | `python -m streamlit run week12/week12_vision_app/app.py` |
| Community Cloud：使用整個課程 repo | `week12/week12_vision_app/app.py` |
| 把 App 內容獨立成 repo | `app.py` |

本機靜態、helper 與 AppTest 檢核不能取代瀏覽器、真實 Responses API、Colab 或 Community Cloud 驗證；上課前仍需用無敏感資料與測試金鑰完成這些檢查。

