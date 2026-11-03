# 第11週｜RAG與File Search・課堂簡化版

兩條路線在同一個App選擇，使用同一份`sample_data/activities.txt`與相同問題。主線為「證據 → A context → 回答 → 來源與不足判讀」，學生擇一路線完成，不要求兩套作品。

## 學生先做什麼

1. 開啟上層「課堂簡化版_學生版」Notebook，完成A的`build_context`，跑固定自測。它保留來源標籤與完整片段，超出長度時停止，不重新摘要。
2. 把同一個函式移入`student/app.py`。檢索、API、回應檢查與UI都完整提供，不重寫第9週reader或第10週排序。
3. 預設離線只看人工挑選前兩段的context，與問題無關，**沒有執行檢索或生成**。不把這個預覽填成RAG回答成果。
4. 準備API後選一路線，測正常／資訊不足／文件外三種問題，下載紀錄並人工核對引用。沒有API權限時真實欄寫未測，由老師安排共看實測。

## 安裝與啟動

新版沿用Windows／Python3.14基準；既有環境先確認，不覆蓋原`.venv`。需求不包含ChromaDB／FAISS。

```powershell
cd week11/week11_rag_simple
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m streamlit run student/app.py
```

教師入口`teacher/app.py`。已有課程環境可直接使用該環境的`python -m streamlit run student/app.py`；從Repo根目錄可用`python -m streamlit run week11/week11_rag_simple/student/app.py`。文件與共用`.env`依程式位置讀取，不受啟動目錄影響。

複製本資料夾`.env.example`為`.env`，只在自己的檔案填金鑰。App讀平台Secrets優先，本機讀這份共用`.env`；資源腳本只讀本機`.env`或環境變數。真正金鑰與本機資源紀錄不提交。

Notebook短例從自己的環境變數或Notebook工作目錄的`.env`取設定；File Search另填資源腳本輸出的`OPENAI_VECTOR_STORE_ID`與`OPENAI_FILE_ID`。Colab先在Secrets設定／授權，依Notebook環境格將金鑰讀入本次runtime，不要求在Colab架Streamlit。安裝／畫面／金鑰與真實模型需另實測。

## 路線一：自行建置

1. A完成後，選「自行建置」，勾啟用API並提交。
2. 先把同一文件各段與問題合批向量化，1次Embeddings API；相同模型／維度再算分數。
3. 只把通過門檻的片段交給A，產生含來源的context。沒有片段時在本機回固定不足句，0次生成。
4. 有證據才呼叫1次Responses API，使用共同規則＋context，答案只能引用本次實際納入的`[來源n]`。

每題最多2次API；不做大型索引或跨次向量快取。第10週已說明正式服務可保存文件向量、只計算新問題。這版用普通list讓學生先看懂流程，向量資料庫仍可參照原教材，非本週必裝。

## 路線二：OpenAI File Search

先讀本節，才明確建立資源。**啟動App、一般rerun或預設執行Notebook都不會上傳文件或建立索引。**

在本資料夾使用安裝好套件的同一個Python環境：

```powershell
python resources.py
python resources.py --create
```

第一行只顯示說明，0次API。第二行會執行：

1. 建立專用Vector Store，設定最後活動後1日過期；保存收到的ID。
2. 上傳本資料夾`sample_data/activities.txt`，保存file ID與檔案SHA-256。
3. 將file加入Vector Store，再最多輪詢10次、間隔2秒確認狀態。這是最多10次狀態查詢，不是保證20秒內完成；每次網路等待另有60秒設定。

只有`completed`才供App使用。失敗或逾時仍保留已收到的ID；有未清理資源時再次create會停止，避免重複建立。若某次寫入網路逾時而未收到ID，需到平台確認該次操作狀態，不能假定完全沒建立。

資源紀錄放`.file_search_resources.json`，不含key且被Git忽略。App只讀這份索引紀錄，不在rerun建立資源。若本機文件SHA與建立時不同，App會停止，需先清理舊資源再用新文件重建；比較兩路時保留相同文件SHA與問題。

選「OpenAI File Search」、勾啟用API再提交。每題1次Responses，強制`file_search`、最多1次工具呼叫，並以`include=['file_search_call.results']`取回檢索片段。檔案引用從`annotations`讀，不從模型文字猜檔名。

### 課後清理

```powershell
python resources.py --cleanup
```

只刪除本機紀錄內專用Vector Store與原始file，不列舉帳號其他資源。兩個物件分開刪除；404視為已不存在，部分失敗保留尚未刪除ID及`cleanup_pending`，修正後可再執行。確認紀錄為`cleaned`，再到平台核對費用與資源狀態。

索引過期不代表原始file已刪除；清畫面、關App或`store=False`都不會完成上述清理。儲存、模型、工具呼叫均可能產生費用，不把「一次問答請求」當作整段操作只收一次費用。[官方計價](https://developers.openai.com/api/docs/pricing)

## 共同規格與來源檢查

- 教學文件只用UTF-8小型TXT：1～3000字元、最多8段、每段1000；問題1～300字元。超限拒絕，不截斷。
- 文件同第10週活動文字；[問題清單](sample_data/questions.json)包含正常、未提供費用、文件外問題。換自己的文件時保留原檔，兩路仍使用同一份。
- 自行建置context至多4000字元，含標籤／換行，只納入完整片段；File Search內部context由平台控制，本機A僅整理取回證據供人工看，不宣稱控制平台context上限。
- 完成、非空、未拒答才取答案；自行建置只接受本次context的來源編號，File Search只接受本次預期file的檢索片段與相符file_citation。
- 沒有片段、引用缺失或不屬於本次來源時，不能存肯定答案。合理的固定不足句是「根據目前文件，無法確認這個問題。」；必須分清本機決定與模型生成。
- 檔案引用只證明指向某檔案，不等於每句受到某段支持；不虛構平台沒提供的頁碼或字元位置。分數不可跨兩路直接比較。
- 本機向量筆數、index、維度、有限數字與非零均檢查；生成／工具未完成、空文字、拒答或API失敗不沿用舊答案。SDK重試關閉，timeout=60不是總執行上限。

## 畫面狀態與成本紀錄

表單內改問題與參數後需重新提交。新提交先清舊結果，全部通過才保存；切路線、切API模式或清畫面也移除。rerun、顯示來源與下載不重呼叫API，也不建立資源。

下載`rag_record.json`含路線、模式來源、問題、模型、文件SHA、參數、答案、實際檢索片段、context預覽與引用；不含key或向量。清畫面不刪除平台資源。

老師先用同文件／同問題示範兩路；學生只選一路。三題正常規畫：自行建置最多3次Embedding＋3次生成；File Search 3次Responses＋最多3次工具，另計資源建立3次寫入、1～10次輪詢、清理最多2次刪除與儲存。失敗重試或額外測試另記；不直接判定哪條一定較便宜。

## 練習與作業

150分鐘核心另留休息10與排障20。A是共用context程式練習，B是原文／引用／不足判讀；File Search路線同樣用A整理本機證據，不要求改寫平台內部流程。

課後45～60分鐘，沿用同一App選一路，換合法無敏感文件，交學生Notebook、App、原文件、三類問答紀錄與README。至少核對一個日期／數字、一個引用的實際原文、一個錯誤／邊界的處理與重測。File Search附建立與清理結果說明，**不提交金鑰或實際本機資源紀錄**。

評量40／30／20／10為A來源與上限、B回答判讀、錯誤修正、可重現反思。題目自由、最低要求相同；學生不需完成兩路，也不額外做部署、資料庫或第二個App。沒有API者真實欄寫未測，由老師安排共看實測，不用人工預覽補造模型答案。

沿用整學期Repo與既有Google表單登記，不另交每週資料夾連結。教師答案不隨學生包發放。

## 重建與已測範圍

Repo根目錄重建`python -X utf8 scripts/build_week11_simple.py`；離線驗證`python -X utf8 scripts/verify_week11_simple.py`。重建不執行API、不建立／刪除資源、不覆蓋實際`.env`或資源紀錄；README與resources.py人工維護。

實際環境與已測／未測見[教師導讀](../第11週_課堂簡化版_教師導讀與修訂紀錄.md)。本機模擬不代表真實File Search索引、模型品質、Cloud或Colab通過；模型帳號權限與回應品質需課前實測。

依據：[File Search](https://developers.openai.com/api/docs/guides/tools-file-search)、[Retrieval](https://developers.openai.com/api/docs/guides/retrieval)、[GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini)。
