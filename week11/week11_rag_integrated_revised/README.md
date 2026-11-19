# 第9～11週整合：看得見每一步的RAG文件問答

完整可執行的示範App。上傳一份文件後，依序看見**抽取 → 清理 → 切塊 → 文件向量 → 問題向量 → 排名 → context → 回答與來源**。同一份文件的向量可供多個問題使用。

- [學生操作與觀察講義](../第11週_第09至11週整合RAG_App_操作與觀察講義_修訂版.md)
- [教師導讀與驗證紀錄](../第11週_第09至11週整合RAG_App_教師導讀與驗證紀錄_修訂版.md)
- [既有第11週練習App](../week11_rag_revised/README.md)：原有A與學生TODO繼續在這裡完成。整合示範不增加必做程式作業。

## 1 本機啟動（Windows／Python 3.14）

在課程儲存庫根目錄執行：

```powershell
cd week11/week11_rag_integrated_revised
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
python -m streamlit run app.py
```

已有環境可直接使用，不要覆蓋自己的`.venv`；建立新環境時可改名`.venv-py314`。安裝套件需要網路。離線操作不需要API金鑰。

若直接使用課程根目錄既有環境，在根目錄執行：

```powershell
.\.venv\Scripts\python.exe -m streamlit run week11/week11_rag_integrated_revised/app.py
```

## 2 先跑離線，認識每一步

1. 保持「使用真實API」未勾選，資料來源選「內建範例」，選`sample.txt`；切塊方式保持「空白行分段」。
2. 按「處理文件」，查看抽取與清理後的文字、完整片段及來源位置。
3. 按「建立文件向量」，展開查看四維人工關鍵字計數（每筆只列前5個數字）。
4. 輸入「活動地點在哪裡？」，按「找證據／依目前參數重新排名」，查看問題向量、各片段排名與實際context。

切塊方式有兩種。**空白行分段**（預設）沿用第10、11週App的`split_chunks`，一個空白行一段；內建`sample.txt`切成3段，4題離線取回的片段是`[[0], [], [2], []]`，和第10、11週相同。**固定字元**沿用第9週的`chunk_text`，依片段長度與重複字元切；適合沒有空白行的長文件，空白行分段時某段超過1000字元也要改用它。同一題換切法比較排名表，就能看到切塊如何影響檢索。

向量只列每筆的前5個數字與維度：真實向量每筆上千維，全部印出會拖慢頁面，也看不出意義。
5. 展開規則與input，確認來源標籤及原文。下載離線檢索紀錄。

**離線是四組活動關鍵字規則，不是語意模型；不產生模型答案。** 對自己上傳的任意文件，可能得到全零向量或找不到證據，這不代表真實Embedding的能力。

## 3 自行上傳文件與真實問答

1. 在本資料夾把`.env.example`複製為`.env`，填入自己的金鑰。
2. 勾選「使用真實API」，選「上傳檔案」，上傳文件。TXT／MD／CSV可選`utf-8-sig`或`cp950`。
3. 按「處理文件」，確認文字正確；再按「建立文件向量」（1次Embedding）。
4. 輸入問題並找證據（新問題1次Embedding），確認完整排名、入選片段與送出前預覽。
5. 按「依證據回答」（有證據時1次Responses），逐項核對答案引用的原文，再下載問答紀錄。

畫面上的每個付費按鈕都由使用者主動操作；預設關閉。切換模式後必須重建文件向量。模型名稱沿用既有教材，教師課前仍需確認帳號權限與可用性。

| 操作 | 真實API送出次數 |
|---|---:|
| 讀檔、清理、切塊、顯示與下載 | 0 |
| 按「建立文件向量」（全部片段合批） | 1次Embedding；再次按會重建 |
| 同一文件的新問題按「找證據」 | 1次Embedding |
| 同一問題調整top_k、門檻或context上限，再按「重新排名」 | 0；沿用問題向量 |
| 按「依證據回答」 | 有證據1次Responses，無證據0次；再次按會再生成 |

同一文件三個新問題各回答一次，最多為**1＋3＋3＝7次API**；額外重建或重答另計。畫面顯示本次連線送出嘗試次數，包含失敗，不能當作帳單或token數。SDK使用`max_retries=0`、`timeout=60`，Responses設定`store=False`。

## 4 狀態與檢索結果的讀法

- 文件、向量與目前問題只放在各使用者的`session_state`，不用全域快取；關閉連線或伺服器重啟後需重建。
- 換檔、改編碼、切塊方式或切塊參數：舊文件成果、向量與答案立即清除，重新按「處理文件」。同檔名但不同內容也會辨識。
- 換模式或向量模型：保留文件，清除向量與問答。換問題：清除舊問題向量、檢索與答案。
- 改top_k、門檻或context上限：隱藏舊檢索與答案，按「重新排名」；同一問題向量仍可使用。任何參數變更不會自動送付費請求。
- 「通過門檻」不等於「入選top_k」；「入選top_k」也不一定放進context。上限包含來源標籤與空白行，放不下就停止，不切斷原文。
- `start/end`是清理後文字的字元位置，end不包含；PDF頁碼標記來自抽取結果，不提供原PDF精確座標。CSV保留欄名與列號，DOCX讀本文段落與表格；圖片、註解、頁首頁尾不在讀取範圍內。
- 相似度不是正確機率；「有標來源」只代表引用格式有效，仍須人工核對結論。

## 5 文件限制與下載

單一文件，最大1MB；清理後1～20000字元，最多100段；空白行分段時每段最多1000字元。支援TXT、MD、CSV、文字型PDF、DOCX；CSV最多200列、PDF最多50頁，沿用第9週限制。掃描PDF須先OCR，本App不提供OCR。若超過100段，請縮小文件或增加片段長度。

可下載清理後文字、`document_record.json`與`rag_record.json`。問答紀錄包含原文、片段、完整排名、設定、實際sources/context、回答與格式檢查，不含金鑰或完整向量。紀錄可能含整份文件，分享前自行確認內容。

`rag_record.json`保留既有第11週10-1讀回格需要的`hits/context/answer/check`。將檔案放回Notebook資料夾（Colab拖進檔案窗格），可用該格檢查context的來源原文一致性；這不是答案內容正確性的自動判定。

## 6 Streamlit Community Cloud

Main file path：`week11/week11_rag_integrated_revised/app.py`。入口同層有`requirements.txt`，不需要跨週import。將`.streamlit/secrets.example.toml`的格式貼到Cloud的Secrets設定，換成自己的值。設定讀取順序為平台Secrets → 環境變數／App資料夾`.env`。

真正的`.env`與`secrets.toml`不提交Git。Cloud部署與瀏覽器檔案選擇操作尚未實測；需依下列驗證紀錄區分本機測試與實際部署。

## 7 重建、驗證與依據

在儲存庫根目錄執行：

```powershell
.\.venv\Scripts\python.exe -B -X utf8 scripts/build_week11_integrated_rag_revised.py
.\.venv\Scripts\python.exe -B -X utf8 scripts/verify_week11_integrated_rag_revised.py
```

生成來源是上述build與`scripts/templates/week11_integrated_rag.py`。build直接讀第9、10、11週建置來源的共用函式，生成可獨立執行的App；README與雙版講義為手寫檔，不會覆蓋。修改既有Notebook入口後，仍需執行原`build_week11_revised.py`與`verify_week11_revised.py`。

本機驗證環境與未測項目見教師導讀；requirements保留課程目標版本，不把既有環境測試等同於重新安裝目標組合。

2026-11-18已通過新整合版與原第11週修訂版完整離線驗證，包括真實SDK＋MockTransport、AppTest、各格式讀取、狀態與下載讀回。實測為Python3.14.0／Streamlit1.60.0／OpenAI2.49.0／python-dotenv1.2.2／pypdf6.18.1／python-docx1.2.0；未另安裝目標版本。真實付費API為0次，真人瀏覽器、真實模型品質、Colab、Cloud與試教未測。

API介面依據：[OpenAI Embeddings](https://developers.openai.com/api/docs/guides/embeddings)、[Responses文字生成](https://developers.openai.com/api/docs/guides/text)；核對日期2026-11-18。Streamlit狀態依據：[Session State](https://docs.streamlit.io/develop/concepts/architecture/session-state)。
