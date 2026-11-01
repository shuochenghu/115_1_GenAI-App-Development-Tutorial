# 第8週 Pydantic 串流對照範例（教師完整示範）

本範例為選讀，沿用原 Pydantic 教師摘要器的任務、原文、instructions、ProjectResult 與畫面標籤；不改期中專題最低要求。原非串流版保留。

## 啟動

進入本資料夾後，以自己的課程虛擬環境執行：

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

從課程根目錄啟動可用 `python -m streamlit run week08/week08_midterm_simple_pydantic_streaming_teacher/app.py`。
本機金鑰放本資料夾 `.env`（參考 `.env.example`），雲端使用 Secrets 範例；不要提交真正金鑰。
套件版本沿用原版；Python 3.14 為課程既有基準，本次驗證環境另見下方。

## 看什麼

1. 開啟 App，API 預設關閉；輸入原文並送出，只查設計，0次請求。
2. 設好金鑰並開啟 API，再送出：JSON 文字逐段出現在「生成中的 JSON 預覽」。實際片段大小由 API 決定，不保證每次一字。
3. 完成後預覽消失，顯示與原版相同的「標題／摘要／重點」及原始 JSON。一般 rerun 保留成功結果。
4. 拒答、中斷、未完成或解析失敗時移除預覽並顯示錯誤；不沿用舊成功結果。

範例原文：

> 今天課程介紹 Streamlit 表單與 session_state。表單集中提交輸入，session_state 保存重跑之間的結果。老師提醒先完成結構化摘要，再依需求擴充功能。

另以「好」測資訊不足；摘要仍須人工核對，格式通過不代表內容正確。

## 與原版對照

| 項目 | 原版 | 串流版 |
|---|---|---|
| 呼叫 | responses.parse | responses.stream + get_final_response |
| 生成中 | 等待完整回應 | 逐段更新 JSON 預覽 |
| 正式結果 | 完整驗證後逐欄顯示 | 相同 |
| 每次有效提交 | 最多1次請求 | 最多1次請求 |

本版刻意直接預覽原始 JSON，未加入部分 JSON 解析器。個別「標題／摘要／重點」元件是在完成驗證後顯示；它們不是各自逐字更新。這使新增程式集中在輸出流程，也能看出「畫面已顯示」與「正式結果已驗證」的差別。
Pydantic負責欄位與型別；程式仍查拒答、完成狀態、解析物件與空白文字。保留6000字元限制、60秒網路等待、max_retries=0、store=False與失敗清舊結果。store=False仍會把原文傳到API。

## 驗證範圍

Windows／Python 3.13.7 暫存隔離環境，Streamlit 1.63.0／OpenAI 2.49.0／Pydantic 2.14.1／python-dotenv 1.2.3：語法與假SDK AppTest（離線0請求、成功、rerun、清除、拒答、未完成、中斷、空白欄位、Pydantic型別失敗及串流關閉）通過。假SDK未驗證真實SSE傳輸。

尚未執行真實 API、真人瀏覽器、Cloud、Colab或試教；逐段出現速度須以教學帳號實測，短回應可能很快結束。離線檢查不代表真實模型品質。

參考：[OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses)。
