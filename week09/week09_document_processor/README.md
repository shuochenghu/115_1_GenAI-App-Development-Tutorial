# Week 9 文件處理與資料前處理

這是第 9 週正式 Streamlit 範例專案。它先在本機讀取與處理文件，再由使用者決定是否呼叫 OpenAI Responses API 產生摘要。

## 功能

- 上傳 PDF、DOCX、CSV、TXT、MD。
- 依格式抽取文字，並顯示掃描 PDF 等限制。
- 清理多餘空白並保留段落。
- 調整 `chunk_size` 與 `overlap`。
- 預覽任一 chunk，並下載含來源位置的 JSON。
- 明確按下按鈕後才產生 AI 摘要。
- App 與 Streamlit 設定都限制單檔上傳大小為 8 MB。
- 支援本機 `.env` 與 Streamlit Secrets。

## 安裝與執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

未設定 API key 時，本機文件抽取、清理、切塊、預覽與下載仍可使用。

## 檔案結構

| 檔案 | 內容 |
|---|---|
| `app.py` | Streamlit UI、API key 讀取、按鈕式 AI 摘要 |
| `document_utils.py` | 格式路由、reader、文字清理、chunking；全都在本機執行 |
| `requirements.txt` | Streamlit、OpenAI SDK 與文件 reader 相關套件 |
| `.env.example` | 本機 API key 設定範本；真正的 `.env` 不可上傳 |
| `.streamlit/secrets.example.toml` | Streamlit Community Cloud Secrets 範本 |
| `.streamlit/config.toml` | Streamlit 專案設定，目前限制上傳檔案大小為 8 MB |
| `sample_data/course_notes.txt` | 無敏感資料的測試文件 |

## API 設定

複製 `.env.example` 為 `.env`：

```text
OPENAI_API_KEY=你的測試用APIKey
OPENAI_MODEL=gpt-5.4-mini
```

部署時使用 Streamlit Secrets。不得將 `.env`、`.streamlit/secrets.toml` 或真實 API key 推送到 GitHub。

## 支援與限制

| 格式 | 處理方式 | 主要限制 |
|---|---|---|
| PDF | `pypdf` 逐頁抽取 | 掃描檔需 OCR；複雜版面順序可能不準 |
| DOCX | `python-docx` 段落與表格 | 圖片與複雜排版不會完整保留 |
| CSV | pandas，最多前 200 列 | 不適合把大型資料表全部送給模型 |
| TXT / MD | UTF-8／CP950 fallback | 其他編碼可能需要先轉檔 |

本週以字元長度 chunking 建立觀念。第 10 週會把 chunks 轉成 embedding，並加入語意搜尋。

## 建議測試

1. 上傳 `sample_data/course_notes.txt`。
2. 確認字元數、chunk 數與預覽。
3. 將 overlap 改為 0，比較 chunk 邊界。
4. 下載 JSON，確認能重新解析。
5. 使用掃描 PDF 時，確認 App 提示需要 OCR。
6. 有測試用 API key 時才按下 AI 摘要。
