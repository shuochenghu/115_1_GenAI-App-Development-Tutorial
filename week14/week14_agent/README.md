# 第14週｜有限步數的官方文件查核助手

先用離線情境看「觀察結果後決定下一步」，再啟用真實API。模型可選搜尋、閱讀或回答；程式掌握官方範圍、步數及費用上限。

- [學生Notebook](../生成式AI應用開發_第14週_Agent基礎與工作流程_學生版.ipynb)／[閱讀版](../生成式AI應用開發_第14週_Agent基礎與工作流程_學生版.md)
- [教師導讀](../第14週_教師導讀與驗證紀錄.md)、[工具契約](工具契約.md)、[B觀察與查核紀錄](觀察與查核紀錄.md)
- 學生起點：[student/app.py](student/app.py)；教師完整範例：[teacher/app.py](teacher/app.py)。

## 1 先看懂資料怎麼走

1. 使用者決定問題及Python／Streamlit官方範圍。
2. 外層模型選`search_official`或`read_official_page`，也可以提早說明不足。
3. 程式驗工具、參數、停止規則及額度，才執行。
4. 工具觀察用同一個call_id回傳，模型再決定下一步。
5. 最後答案只能引用已成功閱讀的來源；人再開啟原頁查核。

搜尋後端採第13週內建web_search及官方範圍；閱讀工具另外以HTTP讀取已登記官方HTML，最多1MB，節錄前6000字元。搜尋摘要、網頁原文、最後答案分開顯示。閱讀失敗代表本次沒有取得本文，不代表官方沒有資料。

## 2 建立環境與啟動

在VS Code開啟`week14/week14_agent`，於該資料夾的PowerShell執行：

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run student/app.py
```

已有環境時先確認`python --version`與使用中的解譯器；不要直接覆蓋舊環境。教室若不允許啟用腳本，可改用該環境的`python.exe`完整路徑安裝與啟動。

本週固定的是本次實際驗證的直接依賴：Python3.14.0、Streamlit1.60.0、OpenAI2.49.0、python-dotenv1.2.2、httpx0.28.1、beautifulsoup4 4.14.3；Python由系統另行安裝。與第13週較早requirements的目標版本不同，本週不宣稱已在其1.63.0環境測過。其他Python版本、Colab及Cloud應另行實測。

教師啟動改為：

```powershell
python -m streamlit run teacher/app.py
```

若從Repo根目錄啟動，入口用`week14/week14_agent/student/app.py`。套件清單也放在student／teacher入口同層，方便後續部署查找。

## 3 完成A，再開始真實任務

唯一程式練習是`stop_reason(tool_count, max_tools, is_repeat)`。把Notebook完成的同一函式移到student/app.py，儲存後重新提交，不需搬動其餘函式。

| 規格 | 結果 |
|---|---|
| 已用次數達上限 | 回tool_limit |
| 尚未達上限但重複 | 回repeated_action |
| 其餘 | 回None |

保留型別檢查，先判次數、再判重複。按「執行本次任務」會先跑七筆A檢查；未完成或不合規格時，不會發API。預設離線模式可先測A，上方只顯示手寫情境，不產生假模型答案或真實紀錄下載。

## 4 設定金鑰與操作

將[.env.example](.env.example)複製為本資料夾的`.env`，在自己的電腦填入金鑰；不要提交或分享真實檔案。

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4-mini
```

API費用由個人帳號負擔。若未來部署Cloud，使用入口資料夾內的Secrets範本建立平台Secrets，不上傳真實secrets.toml。平台Secrets優先，其次環境變數／.env；程式不顯示金鑰。

操作順序：

1. 離線先選「正常」「不足與重查」「重複」「達上限」看步驟，完成A檢查。
2. 開「啟用真實API」，選官方範圍，再輸入1～300字元問題。
3. 按一次「執行本次任務」，等待有限流程完成；不連按以湊步數。
4. 看停止原因、次數、各步提案與觀察。模型可走不同路徑，不要求剛好搜尋→閱讀→回答。
5. 看來源原文節錄，打開引用網址，填[B表](觀察與查核紀錄.md)。
6. 下載`agent_record.json`，依下一節回Notebook檢查。

建議正常題：「在Streamlit表單裡，修改輸入值和按下提交，分別何時重新執行？」
不足題：「只從Streamlit官方文件查本班下週上課教室。」不提供真實個資。若未搜尋即說明無法取得本班資訊，可如實記錄，不能為了多步驟而強迫重跑。

## 5 下載後回Notebook第11-1節

成功、不足及失敗都能下載本次紀錄，檔名固定`agent_record.json`，和第13週的web_search_record.json分開。

| 步驟 | 操作及完成條件 |
|---|---|
| 1 | 在本次結果下載JSON；保留當時模式、問題與結果，不手改成成功 |
| 2 | 放到Notebook目前工作資料夾；Colab拖到左側「檔案」窗格 |
| 3 | 執行11-1獨立讀回格，0次API；不用重跑前面活動 |
| 4 | 第二份檔名若為agent_record (1).json，修改格內path再執行 |
| 5 | 看到一致性通過後，仍要完成B的原文支持度與版本／數字／日期核對 |

讀回會查call_id、來源先搜尋再閱讀、片段雜湊、引用、計數、上限及停止後無新事件。沒有檔案只提示；失敗紀錄可通過一致性檢查，代表「如實記錄失敗」，不等於任務成功。欄位全部偽造仍可能前後一致，這不是身分或真實API的證明。

| 訊息或狀態 | 回查 |
|---|---|
| 沒有agent_record.json | 先下載，確認放在目前工作資料夾，核對檔名 |
| call_id或來源不一致 | 確認是第14週App本次原始JSON，沒有混用或手改 |
| 總計不同／超上限 | 保留紀錄與錯誤，請教師查執行器，不把上限改大來過關 |
| 原文片段雜湊不符 | 下載原檔重試；不要手動修改片段 |
| api_error | 記實際錯誤與次數，先查金鑰、額度或網路；不要反覆自動重送 |
| invalid_final | 模型沒有符合三欄規格，或引用未成功閱讀來源；如實記失敗 |

## 6 次數與狀態

| 活動 | Responses最多 | 內建搜尋最多 | 一般網頁HTTP最多 |
|---|---:|---:|---:|
| 離線情境／A／讀回 | 0 | 0 | 0 |
| 一題真實提交 | 6 | 2 | 2 |
| 正常與不足兩題 | 12 | 4 | 4 |

典型搜尋→閱讀→回答：外層3次＋搜尋後端1次＝4次Responses，另1次內建搜尋、1次HTTP。若換字詞重查：最多外層4次＋搜尋2次＝6次。工具總數上限3；上表各欄是保守上限，不能理解成搜尋2次與閱讀2次可以全部用滿。

最後輪次不開放工具，達上限或重複會停止；SDK的max_retries=0，60秒為網路等待。讀網頁10秒、不跟轉址、不重試。搜尋詞改寫是新的有計數步驟；usage未知保留None，不當成免費。內建工具一次不代表一條query或固定價格。

新提交、範圍／模式／模型切換及清除會清舊紀錄。表單內改問題要重新提交；一般rerun、展開及下載只讀本次紀錄。成功後再失敗會顯示新的失敗紀錄，不沿用舊答案。

## 7 作業與第15週

課後45～60分鐘，沿同一App完成A、正常／不足兩筆真實執行或失敗說明、B、一個離線停止／錯誤案例、11-1讀回及自己的README。課堂紀錄可直接沿用；額外重測另計。

評量：A與流程40%、B及來源／讀回30%、錯誤修正20%、可重現與限制10%。沒有API額度或網路時如實列待補，由教師安排補測／共看；不能用手寫情境冒充真實成果。

沿用學期Repo與既有登記；依公告Commit／Push並到GitHub確認。本週不新增部署要求，第15週再整合MCP概念、專題部署、Secrets、成本及錯誤紀錄。

## 8 重建與驗證

從Repo根目錄執行：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/build_week14.py
.\.venv\Scripts\python.exe -X utf8 scripts/verify_week14.py
```

生成來源為build_week14.py及templates/week14_agent_core.py；生成Notebook、閱讀稿、App、套件清單、設定範本與手寫素材，不覆蓋本README、工具契約、B表、教師導讀或真實設定。

離線驗證檢查程式與請求契約，不證明搜尋／答案品質。真實API、網頁可讀性、Colab、真人瀏覽器、Cloud及授課時間的狀態見[教師導讀](../第14週_教師導讀與驗證紀錄.md)。
