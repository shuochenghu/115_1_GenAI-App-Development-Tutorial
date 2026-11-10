# 第11週｜RAG文件問答・修訂版App

流程：**找證據 → A組成context → 只依證據回答 → 核對來源與資訊不足**。
搭配上層檔名含「RAG文件問答_課堂簡化版_修訂版」的學生／教師Notebook。原課堂簡化版（`week11_rag_simple/`）保留未改。

## 學生操作

1. 開啟學生Notebook，完成A的`build_context`並通過自我檢查。
2. 把同一個函式貼到`student/app.py`的同名函式；其他函式與畫面都已完整提供。
3. 先用預設的**離線模式**（0次API）：App用第10週的關鍵字規則依問題找證據、A組context，並顯示「送出前預覽」，也就是真實模式會送給模型的input。離線不會產生回答。
4. 有金鑰後選一條路線、勾選真實API，問正常、資訊不足、文件外三種問題，下載問答紀錄並回原文核對。沒有API時，真實欄寫「未測」，或引用老師的實測紀錄（要標明來源）。

## 資料：直接接第10週

- 預設文字`sample_data/week09_cleaned_text.txt`與第10週修訂版完全相同（第9週`sample.txt`清理後的3段）。
- `sample_data/questions.json`是第10週同樣的4題（原句、改寫、資訊未提供、文件外），另加「好的回答應該」。
- 也可以在文件欄貼上自己的文件（空白行分段）。File Search路線則要用同一份文件建立索引，見下文。

## 安裝與啟動

沿用Windows／Python 3.14；直接依賴版本在`requirements.txt`。既有環境先確認，不要覆蓋原本的`.venv`。

```powershell
cd week11/week11_rag_revised
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m streamlit run student/app.py
```

- 教師版改成`teacher/app.py`。也可從Repo根目錄啟動`python -m streamlit run week11/week11_rag_revised/student/app.py`；範例檔與`.env`依App位置讀取，不受目前目錄影響。
- 部署是選做，步驟沿用[第7週起Git指南](../../week07/生成式AI應用開發_第07週_Git實作教材_學期共用Repo版.md)。Colab只執行Notebook，不架Streamlit。

## 金鑰：本機、Streamlit Cloud與Colab都能執行

App用`read_setting`讀設定：**平台Secrets優先，沒有時讀環境變數，`.env`在啟動時載入成環境變數**。同一份程式不用改，本機與Cloud都能跑。

| 執行位置 | 金鑰放哪裡 | 說明 |
|---|---|---|
| 本機App | 本資料夾的`.env`（由`.env.example`複製） | 學生版、教師版、Notebook與`resources.py`共用。也可放`student/`或`teacher/`的`.env`，或用環境變數；兩處都有時以本資料夾的`.env`為準 |
| 本機Notebook | 同上 | 先讀`week11_rag_revised/.env`，再找Notebook所在資料夾往上的`.env` |
| Streamlit Cloud | App設定的**Secrets** | 格式見`student/.streamlit/secrets.example.toml`，寫在最外層，不加區段標題 |
| Colab Notebook | Colab的Secrets，並授權Notebook | 只跑Notebook，不架Streamlit |

部署到Streamlit Community Cloud時：
1. **Main file path**填`week11/week11_rag_revised/student/app.py`（依自己Repo的實際路徑）。
2. 入口同層已附`requirements.txt`；Cloud先找入口同層，再找Repo根目錄，不會往上一層找。
3. 在Advanced settings → Secrets貼上：

```toml
OPENAI_API_KEY = "你的金鑰"
OPENAI_MODEL = "gpt-5.4-mini"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
```

選File Search路線時，還要加上`resources.py --create`最後印出的三行（見下文）。真正的`.env`、`secrets.toml`與資源紀錄檔都不要提交到GitHub。

## 路線一：自行建置

1. 文件各段與問題合成1次Embeddings請求（第10週的`embed_texts`檢查：筆數、順序、維度、有限數字、非全零）。
2. 用第10週的`rank_chunks`依top_k與門檻排名，再交給A組context。
3. 沒有證據時，本機直接回固定的不足句，**不呼叫生成**。
4. 有證據才呼叫1次Responses：規則放instructions，問題與context放input，答案要標`[來源n]`。

每題最多2次API。為了讓流程簡單直線，每次提交都重新向量化文件；正式服務應保存文件向量，查詢時只向量化新問題。

## 路線二：OpenAI File Search

**啟動App、一般rerun或直接執行Notebook，都不會上傳文件或建立索引。** 索引只由`resources.py`明確建立：

```powershell
python resources.py
python resources.py --create
```

第一行只顯示說明，0次API。第二行會：

1. 建立專用Vector Store，最後活動後1日過期；收到ID就保存。
2. 上傳`sample_data/week09_cleaned_text.txt`，保存file ID與文件內容指紋（SHA-256，統一換行並去掉頭尾空白後計算）。
3. 把檔案加入索引，最多查詢10次狀態、每次間隔2秒。這是查詢次數上限，不保證20秒內完成；每次網路等待另有60秒上限。

只有狀態為`completed`才供Notebook與App使用。失敗或逾時仍保留已收到的ID；本機還有未清理的紀錄時，再次`--create`會停止，避免重複建立。若某次寫入因網路逾時而沒有收到ID，要到平台確認，不能假定完全沒有建立。

資源紀錄存在本資料夾的`.file_search_resources.json`（不含金鑰，已被Git忽略）。App比對「文件欄的文字」和建立索引時的指紋，不同就停止並提示清理重建，避免新文字配到舊索引。

**部署到Streamlit Cloud或在Colab使用File Search：** 資源紀錄檔不會上傳到GitHub，所以`--create`完成時會多印出三行：

```toml
OPENAI_VECTOR_STORE_ID = "vs_..."
OPENAI_FILE_ID = "file-..."
FILE_SEARCH_SHA256 = "..."
```

把這三行貼到Cloud或Colab的Secrets。本機沒有紀錄檔時，也可以寫進`.env`（改成`名稱=值`，不加引號）。App與Notebook找不到紀錄檔時才讀這三個值，文件指紋一樣要相符。
建立索引與部署要用**同一個OpenAI帳號／專案的金鑰**，否則部署的App看不到這個索引。

作業換文件時：

```powershell
python resources.py --create --document 你的檔案.txt
```

只接受UTF-8的`.txt`或`.md`，範圍與App相同（6000字元、12段、每段1000字元）。App文件欄要貼入同一份文字。

問答時每題1次Responses，強制`file_search`、最多1次檢索，並以`include=['file_search_call.results']`取回片段。檔案引用從`annotations`讀，不從答案文字猜檔名；平台內部怎麼組context看不到，App裡的A只把取回的片段整理給人看。

### 課後清理

```powershell
python resources.py --cleanup
```

只刪除本機紀錄裡的Vector Store與原始檔案，不列舉帳號的其他資源。兩者分開刪除；404視為已不存在；部分失敗會保留未刪除的ID與`cleanup_pending`，修正後可再執行。確認紀錄為`cleaned`後，再到平台核對資源與費用。

索引過期不代表原始檔案已刪除；清除App畫面、關掉App或`store=False`都不會完成清理。儲存、模型與檢索都可能產生費用。[官方計價](https://developers.openai.com/api/docs/pricing)

## 共同規格與來源檢查

- 文件1～6000字元、最多12段、每段1000字元；問題1～300字元。超過就拒絕，不截斷原文。
- 自行建置的context最多4000字元（含標籤與換行），只放完整片段。
- `read_answer`：拒答、未完成、空白都不保存。
- `check_citations`：接受`[來源n]`與全形`【來源n】`；編號必須在本次context內。沒有來源時，只有以固定不足句開頭的回答可以保存（句號可省略）。
- File Search：檢索要完成、片段必須來自紀錄裡的file ID、檔案引用也要在本次結果內；肯定的答案缺片段或引用就不保存。
- 檢查通過只代表格式與編號對得上，不代表內容正確；檔案引用也不代表每一句都有原文支持。兩條路線的分數不能互比。

## 畫面狀態與請求次數

- 按「找證據並回答」才處理。新提交先清掉舊結果；全部檢查通過才保存。切換路線或模式、按清除、送出失敗都會移除結果。
- rerun、展開區塊與下載都不會再呼叫API，也不會建立資源。
- 下載的`rag_record.json`含路線、模式、模型、問題、原文、參數、取回片段、context、送出前預覽、回答與引用；不含金鑰或向量。

| 動作 | 請求次數 |
|---|---|
| 離線預覽 | 0次 |
| 自行建置，每題 | 1次Embedding＋最多1次Responses |
| File Search，每題 | 1次Responses（最多1次檢索） |
| `resources.py --create` | 3次建立＋最多10次狀態查詢 |
| `resources.py --cleanup` | 最多2次刪除 |

學生作業三題：自行建置最多6次；File Search 3次，另加建立與清理。額外重測另記。

## 教師實測紀錄（給沒有API的同學）

老師課前在Notebook第8、9節開啟`RUN_SELF_RAG`與`RUN_FILE_SEARCH`實跑，再開啟第10節的`SAVE_TEACHER_RECORD`，會在Notebook資料夾存下`teacher_rag_record.json`（日期、模型、每題的片段、回答與引用，不含金鑰與向量）。
把這個檔案發給學生，放在Notebook所在資料夾即可讀取。學生在B表要標明「教師實測紀錄」，不能寫成自己執行的結果。本資料夾不附這個檔案，因為它必須是真實執行的結果。

## 練習與作業

- A是唯一的程式實作；B是四種問題的人工判讀（檢索問題、生成問題、引用不支持、合理的資訊不足）。核心150分鐘＋休息10分鐘＋排障20分鐘。
- 課後45～60分鐘：同一個App選一條路線、換一份合法小文件；交學生Notebook、App、原文件、三份問答紀錄JSON與README。File Search另附建立與清理結果說明，**不交金鑰、`.env`或資源紀錄檔**。
- 評量40／30／20／10：A與來源、B與回答、錯誤修正、可重現與反思。學生不需完成兩條路線，也不需要部署、向量資料庫或第二個App。沿用整學期Repo與既有表單，教師答案不隨學生包發放。

## 重建與驗證

教師重建與檢查（Repo根目錄）：

```powershell
python -X utf8 scripts/build_week11_revised.py
python -X utf8 scripts/verify_week11_revised.py
```

重建會讀取第10週修訂版的資料、問題與三個函式，產生雙版Notebook／Markdown、雙版App、`resources.py`、範例資料與設定範本；不覆蓋本README與教師導讀，也不呼叫API或建立資源。已測與未測範圍見[教師導讀](../第11週_課堂簡化版修訂版_教師導讀與修訂紀錄.md)。

官方說明：[File Search](https://developers.openai.com/api/docs/guides/tools-file-search)、[Retrieval](https://developers.openai.com/api/docs/guides/retrieval)、[Responses](https://developers.openai.com/api/docs/guides/text)。
