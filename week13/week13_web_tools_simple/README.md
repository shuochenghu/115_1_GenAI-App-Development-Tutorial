# 第13週｜Tool Calling與官方網路搜尋・課堂簡化版

主線：本機規格→模型提出prepare_search→程式執行白名單函式→web_search→來源查核。
先讀[實作方法比較](實作方法比較與建議.md)與[模組規格](search_skill_spec.md)。這不是第11週的文件File Search，也不是自由循環Agent。

## 先完成什麼

1. 讀上層學生Notebook，完成唯一程式TODO A：`build_search_task`，先看本機問題與網域規格。
2. 把Notebook同一個A移到student/app.py，不重寫API、引用解析或第二個App；教師版完整，不依賴學生TODO。
3. 預設API關閉，選Python或Streamlit、輸入無敏感問題後提交，只顯示規格。A未完成會停止，不產生假答案。
4. 明確啟用後跑兩階段，正常與不足各一筆；開啟引用來源做B，查詢時間與網頁日期分開記。

## 安裝與啟動

使用課程Python3.14與自己的環境，不覆蓋既有根目錄.venv：

```powershell
cd week13/week13_web_tools_simple
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m streamlit run student/app.py
```

教師改為teacher/app.py。Repo根目錄啟動可用：

```powershell
python -m streamlit run week13/week13_web_tools_simple/student/app.py
```

複製.env.example為.env，自己填金鑰。App依程式位置讀共用.env，平台Secrets優先；不要提交真實設定。
Secrets範本在student／teacher的.streamlit。若本機使用secrets.toml，依目前啟動目錄與Streamlit規則放置；最簡單本機做法為共用.env。
Notebook只在請求分支讀目前目錄.env／環境變數，Colab先在Secrets授權再開啟LOAD_COLAB_KEY；不在Colab跑Streamlit。
安裝、讀Colab金鑰、第一階段、第二階段與選讀直接搜尋的旗標都預設False。

## 固定流程與請求上限

| 階段 | 實際責任 | 請求 |
|---|---|---|
| A本機預檢 | 問題1～300字元、範圍與query／allowed_domains | 0次 |
| 模型提案 | strict function schema，強制prepare_search、不平行呼叫 | 最多1次Responses |
| 程式執行 | 檢查completed、拒答、名稱、call_id及參數；只執行白名單函式 | 0次 |
| 工具結果回傳與搜尋 | 帶回整份first.output及相符call_id，實際使用web_search | 最多1次Responses＋1次內建工具呼叫 |
| 來源與答案檢查 | 搜尋完成、sources與引用網域、非空答案；成功才保存 | 0次 |

一次有效提交最多2次Responses＋1次內建工具呼叫；第一階段失敗最多1次，第二階段失敗最多2次。
`max_tool_calls=1`限制內建工具呼叫，不等於只送一條搜尋query、只看一頁或固定計費。工具費及token另依[官方計價](https://developers.openai.com/api/docs/pricing)與實際usage記錄。
SDK `max_retries=0`、`timeout=60`，兩次各有等待；`max_output_tokens`為第一階段1200／第二階段1800，`store=False`仍會把問題送到服務。逾時不保證服務端沒處理或沒費用。
本週主線是教協定，故固定兩階段；只需要搜尋的產品可直接使用web_search，Notebook有預設關閉的選讀，另計最多1次Responses＋1次工具，不要求再做App。

## 來源、日期與不足

限定Python官方docs.python.org／www.python.org或Streamlit官方docs.streamlit.io及其子網域。A不能任意擴網域；來源範圍選擇由使用者控制，模型參數須與本次輸入相符。
答案依實際url_citation位置產生正文內可點擊引用，下方另有來源按鈕，不猜網址。查閱sources與引用可以不同筆數，但引用須屬於實際查閱網址及指定網域；同頁fragment差異可接受。
只有完成的搜尋事件、有效來源、引用與非空答案才保存。拒答、未完成、缺引用、來源不符或查無可引用資料都明確報錯，不用固定答案取代。
來源可能只提供摘要；不要宣稱App已下載完整網頁。B須自己點開原文，確認是否真的支持答案，以及版本／發布或更新日期。官方網域不保證資訊永遠最新。
下載的queried_at_utc是查詢時間，publication_date保留null，**不表示網頁沒有日期**；要由B查原頁填寫。無標示才寫未標示，不用模型猜或以查詢時間代填。
第一階段明確要求reasoning.encrypted_content，第二階段連同整份first.output回傳，以銜接store=False的工具流程；下載不保留這份原始reasoning內容。
網頁內容是不可信任資料，不把其中命令當成程式指令。問題不得含個資、機密或未授權資料。

## 狀態與下載

新提交先清舊結果；切官方範圍、API開關或按清除也清空。表單內改字須再提交，畫面註明最後成功提交。
一般rerun與下載不重新搜尋；下載web_search_record.json包含問題、範圍、模型、函式參數／結果、引用、查閱網址、UTC時間與兩次usage，不含key與原始reasoning內容。
失敗沒有成功下載紀錄，B可用文字如實記錄錯誤與預期。不要為填滿表格反覆打API。

## 作業與第14週

課後45～60分鐘沿用同App，自選Python或Streamlit官方資料，準備正常與不足兩個問題。
交學生Notebook、App、兩筆真實查核紀錄或失敗說明、[B紀錄表](來源查核紀錄.md)與自己的README；至少查一個版本／日期／數字、一個引用主張，以及一個錯誤／邊界的修正重測。
沿用整學期Repo與已登記表單，不另交每週資料夾連結。最低要求固定、題目開放；本週不新增部署、搜尋服務帳號或MCP作業。
評量A與輸入40%、B證據30%、修正20%、可重現與限制10%。教師完整示範1次最多2＋1；學生兩次最多4次Responses＋2次內建工具，可與課堂共用，額外重做另計。
沒有API先交功能、問題與預期，實際搜尋寫未測，由老師安排共看；人工答案或離線規格不能代替搜尋成果。
第14週才加入有限次數的模型選工具、觀察與停止；本週沒有自主規劃迴圈、任意程式執行或MCP連接。

## 重建與驗證

由Repo根目錄執行：

```powershell
python -X utf8 scripts/build_week13_simple.py
python -X utf8 scripts/verify_week13_simple.py
```

重建雙版Notebook／Markdown、單檔App與設定範本，不覆蓋README、模組規格、方法比較、B表、教師導讀及真實.env／Secrets。
本機離線／SDK HTTP模擬只驗證程式與請求契約；真實搜尋、引用品質、權限、費用、Cloud、Colab及真人瀏覽器仍需另測。版本與結果見[教師導讀](../第13週_課堂簡化版_教師導讀與修訂紀錄.md)。
