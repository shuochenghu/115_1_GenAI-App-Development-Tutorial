# 第9週文件處理｜課堂簡化版

授課主線是「讀取 → 清理 → 觀察片段 → 回查來源 → 匯出」，為第10週搜尋與第11週RAG作準備。切塊函式完整提供，學生練習使用與判讀。搭配上層檔名含「課堂簡化版」的學生／教師Notebook與Markdown閱讀版；原教材及原App保留比較。

## 學生從這裡開始

1. Notebook先看短示範，完成引導練習A（清理）與自測；活動B使用完整切塊函式，執行固定比較並填寫片段觀察，不重寫迴圈。
2. 只把已完成的A清理函式放入`student/app.py`對應位置，保留`import re`。切塊、讀取與UI已完整提供，不必再寫第二套程式。
3. 啟動學生App，先跑內建TXT，再上傳`sample_data/events.csv`。學生TODO未完成時會提示，沒有假成功結果。
4. 同份文件固定chunk_size，只改overlap；下載兩份JSON並讀回，挑一個問題指出支持答案的片段與原文，核對日期或數字。這是人工回查，還沒執行搜尋。
5. 回家作業沿用App，換一份無敏感資料文件、比較兩組參數並記錄一個錯誤／邊界案例。完整規格與評分在Notebook第7節。

教師使用`teacher/app.py`完整參考；請勿把教師程式或教師Notebook放入學生發放資料。

Notebook依序拆解app.py：先用`Path("sample.txt").read_bytes()`取得bytes，再用`data.decode("utf-8-sig")`轉成文字。TXT／CSV／PDF／Word都沿用App的相同處理方法，CSV用StringIO、PDF與Word用BytesIO；第3-4節整理為與App相同的extract_text，最後接清理、切塊、檢查與JSON。Notebook用print觀察，App再加表單、狀態與畫面，不另外教一套讀取流程。

範例為[sample.txt](../sample_tata/sample.txt)及同資料夾的CSV／PDF／Word。執行前先複製到Notebook目前工作目錄，Colab直接上傳；範例程式只寫檔名、不含路徑。第6節以sample.txt與App預設size=120／overlap=20整合；App若選內建範例會讀course_notes.txt，請上傳sample.txt才是比較同份資料。

## Windows／Python 3.14安裝與啟動

在課程Repo根目錄先進入本資料夾；若已開啟本資料夾，可略過第一行。

```powershell
cd week09/week09_document_simple
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip --version
python -m pip install -r requirements.txt
python -m pip check
python -m streamlit run student/app.py
```

已有`.venv`先確認版本；不要覆蓋原環境，可改建`.venv-py314`。VS Code選取該環境的`Scripts/python.exe`；安裝與啟動須用同一環境。若PowerShell阻擋啟用，可直接使用`.\.venv\Scripts\python.exe -m pip ...`與`.\.venv\Scripts\python.exe -m streamlit run student/app.py`。

教師啟動命令為`python -m streamlit run teacher/app.py`。也可從整個課程Repo根目錄啟動`python -m streamlit run week09/week09_document_simple/student/app.py`；範例檔依程式位置讀取，不受工作目錄影響。

Colab僅執行Notebook短例子；平台Python與Windows不同，套件安裝／顯示仍需課前實測。本文不要求在Colab開Streamlit服務。部署是選做，共通操作見[第7週起Git指南](../../week07/生成式AI應用開發_第07週_Git實作教材_學期共用Repo版.md)。

## 檔案與責任

| 檔案 | 內容 |
|---|---|
| `student/app.py` | 學生A清理骨架；完整切塊、reader與UI |
| `teacher/app.py` | 相同流程的完整參考答案 |
| `sample_data/course_notes.txt` | 內建無敏感資料活動文字 |
| `sample_data/events.csv` | UTF-8 BOM、含引號逗號的CSV |
| `requirements.txt` | 核心App與PDF／Word讀取套件 |
| `requirements-api.txt` | Notebook選做AI摘要套件 |
| `.gitignore` | 排除環境、快取與真實金鑰設定 |

## 規格與預期操作

App沒有API功能，全程0次請求，也不需要`.env`或Secrets。上傳與參數放在表單，按「處理文件」才讀取；「使用內建TXT範例」預設勾選，若要處理上傳檔案請先取消。參數未重新提交時，畫面明示為上次成功結果。

新提交先清掉舊結果，全部通過才保存。清除、TODO未完成、空白、解碼錯誤、損壞文件或不合法參數都不保留舊下載。預覽chunk或下載只使用已保存資料，不重讀檔案。

| 限制 | 處理方式 |
|---|---|
| 檔案1MB、PDF50頁、CSV200列資料 | 超限拒絕；不默默截斷 |
| 清理後1～20000字元 | 超限或無內容拒絕 |
| TXT／MD／CSV編碼 | 預設UTF-8-SIG；可選CP950，不自動猜測、不忽略錯誤 |
| CSV | 逗號分隔，保留欄名／列，拒絕空欄名、重複欄名或欄數不合 |
| PDF | 讀文字層；全無文字時提示可能需要OCR，部分無文字頁保留頁碼與提示 |
| Word | 本文順序讀段落與表格；不保證圖片、巢狀表格、頁首頁尾完整 |
| chunk來源 | `text == cleaned_text[start:end]`；end不含，位置不是PDF頁面座標 |

以上為課堂小文件處理範圍，不是公開服務完整防護。讀取成功仍要對照原檔核對日期、數字與順序。

下載JSON包含`filename/encoding/character_count/chunk_size/overlap/raw_text/cleaned_text/chunks`；每個chunk有`chunk_id/start/end/text`。保留清理後文字是為了可重現來源核對。現有第10週App仍重新讀取原文件，未提供直接匯入本JSON的功能；請一併保留原文件。

## 練習、作業與繳交

核心150分鐘另留休息10分鐘與排障20分鐘。A是清理實作，B是參數比較與來源判讀；App只需移入A。回家作業45～60分鐘，交同一App、完成A與B觀察紀錄的學生Notebook、原文件、兩組JSON與README；不另做第二個App或手寫切塊。題目與文件開放，最低驗收固定。

README至少寫：用途／來源、啟動方式與實際版本、兩組參數與邊界實例、一個問題及兩組支持答案的chunk_id／原文、一個錯誤／邊界與處理、查核的日期或數字、限制與未測項目。程式與結果推送整學期自己的Repo，由老師既有表單登記的Repo查閱，不另交每週資料夾連結。

## 選做摘要

Notebook第9節自帶短原文，預設`RUN_PAID_API=False`，0次；不需為基本作業開啟。

```powershell
python -m pip install -r requirements-api.txt
```

本機API key僅設定在環境變數或自己的`.env`；Colab使用Secrets並授權Notebook。不要把真實key、`.env`或`secrets.toml`上傳。沒有API設定範例檔是因為核心App完全不需要設定；不要誤以為安裝了SDK就會自動呼叫。

選做摘要每次有效執行最多1次請求、關閉自動重試、最多6000字元、不默默截斷。API文字仍傳送處理；`store=False`不表示資料留在本機。實際模型可用性與品質需課前用教學帳號確認。

## 教師驗證

在課程Repo根目錄、啟用安裝好套件的環境後執行：

```powershell
python -X utf8 scripts/verify_week09_simple.py
```

重建來源為`../../scripts/build_week09_simple.py`；以Repo根目錄執行`python -X utf8 scripts/build_week09_simple.py`。重建會產生兩份Notebook／Markdown、兩份App與TXT／CSV範例，README與教師導讀保留人工編修。

實際驗證版本、結果與未測環境以[教師導讀與修訂紀錄](../第09週_課堂簡化版_教師導讀與修訂紀錄.md)為準；不可把離線或AppTest當成真人瀏覽器、API、Colab、Cloud或試教通過。

## PDF與Word讀取範例

隨附[兩頁中文PDF](../sample_tata/sample.pdf)與[含段落及表格的Word](../sample_tata/sample.docx)，皆為虛構活動資料，不含個資。資料夾名稱為`sample_tata`。

Notebook短例只使用`sample.csv`、`sample.pdf`、`sample.docx`檔名；將`sample_tata`內範例複製到Notebook目前工作目錄，Colab直接上傳檔案。App請取消「使用內建TXT範例」，上傳PDF或Word後按「處理文件」。

核對活動日期2026年11月11日、時間14:00至16:00、每組4人、8組及總名額32人；Word需核對「段落 → 表格 → 段落」的本文順序。PDF含文字層，不是掃描檔，不能用來驗證OCR。


## RAG路線與本週界線（2026-11-03）

自行建置可用現成工具或自訂規則形成片段，之後交給Embeddings API與向量索引；OpenAI File Search則由平台處理支援文件的切塊、向量化、索引與檢索。兩者都要檢查原文件與回答證據；CSV可按整筆活動形成檢索單位，不必一律依字元切。

本週只做文件品質與片段觀察，不建立向量或平台資源。後續規畫在第11週用同文件／問題對照兩路；目前第10、11週尚未製作simple或File Search範例。本週JSON不直接匯入現有第10週App，也不保證可直接上傳File Search。File Search仍需處理支援格式、文件上傳及儲存／工具費用，不能當成完全離線或零成本。

官方依據：[OpenAI Retrieval](https://developers.openai.com/api/docs/guides/retrieval)、[File Search](https://developers.openai.com/api/docs/guides/tools-file-search)。
