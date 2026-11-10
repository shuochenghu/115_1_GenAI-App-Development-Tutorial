# 第13週｜Tool Calling與官方網路搜尋・修訂版App

本App的流程：**模型提出函式呼叫→程式檢查並執行A→把結果交回模型→web_search搜尋官方網域→人工核對來源**。
先讀[實作方法比較](實作方法比較與建議.md)與[模組規格](search_skill_spec.md)。這不是第11週的File Search，也不是會自己反覆循環的Agent。

## 先完成什麼

1. 在上層學生Notebook完成唯一的程式TODO A：`build_search_task`，並通過自我檢查格。
2. 把Notebook的A貼到`student/app.py`的同名函式；不必重寫API、來源檢查或狀態管理。教師版`teacher/app.py`已完整，不依賴學生完成。
3. 先不勾選API：在「離線練習」欄自己扮演模型填`search_query`，確認App顯示A產生的搜尋規格（0次API）。
4. 勾選API後，正常與不足問題各提交一次；打開引用來源完成B，查詢時間與網頁日期分開記錄。

## 安裝與啟動

使用課程Python3.14並建立本資料夾自己的虛擬環境，不覆蓋Repo根目錄既有的`.venv`：

```powershell
cd week13/week13_web_tools_revised
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m streamlit run student/app.py
```

教師示範改成`teacher/app.py`。從Repo根目錄啟動也可以：

```powershell
python -m streamlit run week13/week13_web_tools_revised/student/app.py
```

金鑰設定：同一份程式在本機、Streamlit Cloud與Colab都能執行，不用改程式。

| 執行位置 | 金鑰放哪裡 | 讀取方式 |
|---|---|---|
| 本機App | 本資料夾的`.env`（由`.env.example`複製）；也可放`student/`或`teacher/`的`.env`，或用環境變數 | `read_setting`：沒有Secrets時讀環境變數，`.env`在啟動時載入 |
| 本機Notebook | 同一份`week13_web_tools_revised/.env`；也可放Notebook所在資料夾往上的`.env` | API格先讀App資料夾的`.env`，再找目前資料夾往上的`.env` |
| Streamlit Cloud | App設定的Secrets（格式見`student/.streamlit/secrets.example.toml`，寫在最外層） | `read_setting`：平台Secrets優先 |
| Colab | Colab的Secrets並授權，再開啟`LOAD_COLAB_KEY` | 讀入本次runtime；Colab不啟動Streamlit |

部署時Main file path填`week13/week13_web_tools_revised/student/app.py`（依自己Repo的實際路徑）；入口同層已附`requirements.txt`。真正的`.env`與`secrets.toml`不要提交。
安裝、讀Colab金鑰、第一階段、第二階段與選讀直接搜尋的開關，預設都是False。

## 一次提交會發生什麼

| 階段 | 誰做、做什麼 | 請求 |
|---|---|---|
| 送出前預檢 | 程式檢查問題1～300字元、金鑰已設定，並試跑A確認已完成 | 0次 |
| 第一階段 | 模型依strict Schema提出`prepare_search`呼叫，把問題改寫成英文`search_query` | 最多1次Responses |
| 執行函式 | 程式檢查完成狀態、拒答、唯一名稱、call_id、欄位，以及scope是否等於使用者所選；通過才執行A | 0次 |
| 第二階段 | 程式帶回原輸入、第一次的完整輸出與同call_id的`function_call_output`；模型用web_search在A的網域內搜尋 | 最多1次Responses＋1次搜尋工具 |
| 來源檢查 | 程式確認搜尋完成、來源與引用都在官方網域、引用頁有被查閱、答案非空；全部通過才保存 | 0次 |

- 一次有效提交最多2次Responses＋1次搜尋工具；第一階段失敗只用1次，第二階段失敗共2次。
- `max_tool_calls=1`限制最多呼叫1次搜尋工具，但這1次內可能查好幾個關鍵字、看好幾頁，費用不一定固定。工具費與token請依[官方計價](https://developers.openai.com/api/docs/pricing)與實際usage記錄。
- SDK設定`max_retries=0`、每次等待`timeout=60`秒；第一階段`max_output_tokens=1200`、第二階段1800。`store=False`仍會把問題送到OpenAI，不是本機執行。逾時也不代表服務端沒有處理或沒有計費。
- 本週固定兩階段是為了學協定；只需要搜尋的產品可直接使用web_search，Notebook有預設關閉的選讀。

## 來源、日期與資料不足

- 範圍只有Python官方`docs.python.org`／`www.python.org`與Streamlit官方`docs.streamlit.io`（含子網域）。範圍由使用者選，模型提出不同範圍時程式不執行。
- 來源按鈕來自API的`url_citation`，不從答案文字猜網址。判斷引用頁是否被查閱時，忽略網址的`#`錨點與`?`追蹤參數，只比對主機與路徑。
- 拒答、未完成、沒有搜尋、來源超出網域、缺引用或答案空白，都會顯示錯誤且不保存，不用固定答案代替。
- 搜尋工具可能只讀到摘要；B要自己打開原文，確認是否真的支持答案，以及版本、發布或更新日期。官方網站也不保證永遠最新。
- 下載紀錄的`queried_at_utc`是查詢時間；`publication_date`保留null，**不表示網頁沒有日期**，要由B打開原頁填寫。
- 網頁內容是不可信任的資料，不把其中的命令當成指令。問題不得含個資、機密或未授權資料。

## 狀態與下載

- 新提交先清掉舊結果；切換範圍、切換API或按「清除結果」也會清空。表單內改字後要再按提交，畫面只顯示最後一次成功提交。
- 一般rerun與下載不會重新搜尋。下載的`web_search_record.json`包含問題、範圍、模型、模型提出的參數、A的結果、引用、查閱網址、實際搜尋字詞、UTC時間與兩次usage；不含金鑰與原始reasoning內容。
- 失敗時沒有可下載的紀錄，請在B表用文字記錄錯誤與預期。不要為了填表反覆呼叫API。

## 作業與第14週

- 課後45～60分鐘，沿用同一個App，自選Python或Streamlit官方資料，準備正常與不足兩個問題。
- 繳交學生Notebook、App、兩筆查核紀錄或失敗說明、[B紀錄表](來源查核紀錄.md)與自己的README；至少核對一個版本／日期／數字、一個引用是否支持答案，並記錄一個錯誤或邊界的修正重測。
- 評量：A與輸入檢查40%、B來源與日期30%、錯誤修正20%、可重現與限制10%。
- 學生兩筆最多4次Responses＋2次搜尋工具；課堂完成的兩筆可直接當作業，重做請另外記次數。沒有API額度時，交離線練習結果、問題與預期，實際搜尋欄填「未測」。
- 沿用學期Repo與已登記表單；本週不新增部署、搜尋服務帳號或MCP作業。第14週才讓模型在有限次數內自己選工具、觀察與停止。

## 重建與驗證

由Repo根目錄執行：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/build_week13_revised.py
.\.venv\Scripts\python.exe -X utf8 scripts/verify_week13_revised.py
```

重建會產生雙版Notebook／Markdown、單檔App與設定範本，不覆蓋本README、模組規格、方法比較、B表、教師導讀及真實`.env`／Secrets。
離線驗證只檢查程式與請求格式；真實搜尋、引用品質、帳號權限、費用、Cloud、Colab與真人瀏覽器仍需另外實測。結果見[教師導讀](../第13週_課堂簡化版修訂版_教師導讀與修訂紀錄.md)。
