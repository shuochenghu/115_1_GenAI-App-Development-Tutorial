# Week 12 圖片理解工具（Claude 版）

第 12 週 Streamlit 範例專案（Claude Code 產出）。把前幾週的檔案上傳、Prompt Engineering、
Structured Outputs、錯誤處理與 secrets 管理整合到**圖片輸入**，用 OpenAI Responses API 的
`input_image` 完成圖片描述、圖片問答、截圖檢查，以及收據／表單結構化抽取。

> 本專案的 helper 命名（`detect_image_mime` / `validate_image` / `image_to_data_url` /
> `build_task_prompt` / `get_refusal_reason` / `require_completed_response` / `analyze_image` /
> `RECEIPT_SCHEMA`）**已對齊 Codex 版 `week12_vision_app/`**，兩版可互換對照。
> Claude 版另外多了離線示範模式、request 預覽，以及 `choose_detail` / `normalize_receipt` /
> `evaluate_vision_answer` 三個練習 helper。

## 功能

- 上傳 PNG、JPEG、WEBP 或非動態 GIF，先做**本機驗證**（依檔案內容判斷格式、8 MB、像素量、動態 GIF）並預覽，這一步不花錢。
- 四種任務模式：圖片描述、圖片問答、截圖檢查、收據／表單抽取；prompt 集中在 `build_task_prompt()`，要求模型區分「可見證據」與「推論」。
- `detail` 可選 auto / low / high；側邊欄依任務模式用 `choose_detail()` 給建議值。
- 抽取模式用 JSON Schema（`strict=True`）取得可由程式讀取的欄位，經 `normalize_receipt()` 整理後顯示；無法確認的值顯示「無法確認」，不補假資料。
- 拒答、未完成、空輸出、JSON 解析失敗分流成可讀的錯誤訊息（`require_completed_response()`）。
- **API 只在按下「分析圖片」後呼叫**；結果存在 session state，切換控制項不會重送。
- **離線示範模式**：不需 API key，跑完驗證、prompt、request 預覽，回傳明確標註的樣本結果。

## 安裝與執行

```bash
cd week12/week12_vision_app_claude
pip install -r requirements.txt
python sample_data/create_demo_receipt.py
streamlit run app.py
```

`create_demo_receipt.py` 會產生兩張完全虛構的英文收據（清楚版與模糊旋轉版），
用來測試結構化抽取與「看不清楚時應回 null / warnings」。生成的 PNG 已列入 `.gitignore`。

## API 設定

複製 `.env.example` 為 `.env`：

```text
OPENAI_API_KEY=你的測試用APIKey
OPENAI_MODEL=gpt-5.4-mini
```

部署時改用 Streamlit Secrets（參考 `.streamlit/secrets.example.toml`）。
不得將 `.env`、`.streamlit/secrets.toml` 或真實 API key 推送到 GitHub。

## 檔案結構

| 檔案 | 內容 |
|---|---|
| `vision_utils.py` | 圖片驗證、data URL、prompt、`build_request` / `preview_request`、回應分流、`analyze_image`（含 offline）、`choose_detail` / `normalize_receipt` / `evaluate_vision_answer` |
| `app.py` | Streamlit UI：上傳、本機檢查、表單、結果顯示 |
| `sample_data/create_demo_receipt.py` | 產生虛構測試收據（清楚版 + 模糊版） |
| `.streamlit/config.toml` | 8 MB 上傳限制與主題 |

## 安全與限制

- 圖片會傳到 OpenAI API；只用自己製作或明確授權、且不含敏感資料的圖片。不得上傳身分證、成績、病歷、金融資料、公司機密、未授權人像或 CAPTCHA。
- `store=False` 表示本次回應不保存供後續 API 取回，**不代表圖片沒有傳送或處理**。
- 圖片輸入會轉成 token 計費；圖片數量、尺寸、`detail` 與模型都會影響成本。
- Vision 可能看錯小字、旋轉文字、數字、物件數量與空間位置；本工具不是 OCR 保證、醫療判讀或財務自動入帳系統，重要結果一定回看原圖人工核對。
- `st.file_uploader(type=...)` 只做副檔名篩選，`validate_image()` 仍檢查實際 bytes 與 Pillow 解碼結果。

## 建議測試

1. 先勾「離線示範模式」，上傳 `sample_data/demo_receipt.png`，選「收據／表單抽取」，看 request 預覽與樣本結果，確認流程不花錢就能跑完。
2. 上傳一個改了副檔名的文字檔（例如 `test.txt` 改名 `test.png`），確認本機驗證會擋下。
3. 取消離線並設 API key，用清楚版收據跑抽取，對照原圖核對日期、金額、品項。
4. 用模糊版 `demo_receipt_blurry.png` 再跑一次，觀察 `null` 與 `warnings` 是否出現。
5. 用自己的截圖跑「截圖檢查」，比較 `detail=low` 與 `high` 的差異與 usage。
