# 第14週修訂版｜有限步數的官方文件查核助手

模型每一輪自己選：搜尋、閱讀候選頁面，或回答。程式負責檢查提案、用A擋下超額與重複，並把每一步記下來。

- [學生Notebook](../生成式AI應用開發_第14週_Agent基礎與工作流程_修訂版_學生版.ipynb)／[閱讀版](../生成式AI應用開發_第14週_Agent基礎與工作流程_修訂版_學生版.md)
- [教師導讀](../第14週_修訂版_教師導讀與修訂紀錄.md)、[工具契約](工具契約.md)、[B觀察與查核紀錄](觀察與查核紀錄.md)
- 學生起點：[student/app.py](student/app.py)；教師完整範例：[teacher/app.py](teacher/app.py)

## 1 資料怎麼走

1. 使用者輸入問題，選Python或Streamlit官方範圍。
2. 外層模型選`search_official`（搜尋）或`read_official_page`（閱讀），也可以直接回答。
3. 程式檢查提案，再問A：「這個工具可以執行嗎？」可以就執行，不行就擋下。
4. 工具結果用同一個call_id交回模型，模型再選下一步。
5. 最後答案只能引用成功讀到的頁面；人再打開原頁核對（B）。

**搜尋摘要不是原文。** 搜尋只給線索與候選頁面s1、s2…；閱讀工具用HTTP抓下官方HTML，留下本文、節錄前6000字元，才是原文片段。閱讀失敗代表這次讀不到，不代表官方沒有寫。

## 2 建立環境與啟動

在VS Code開啟`week14/week14_agent_revised`，於該資料夾的PowerShell執行：

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run student/app.py
```

套件版本和第13週修訂版相同（Streamlit 1.63.0、OpenAI 2.49.0、python-dotenv 1.2.3），另加本週的httpx 0.28.1與beautifulsoup4 4.14.3。沿用第13週的環境，裝這份requirements也不會降版。
教室若不允許執行啟用腳本，可改用該環境`python.exe`的完整路徑安裝與啟動。

教師啟動改為：

```powershell
python -m streamlit run teacher/app.py
```

## 3 完成A，再開始真實任務

唯一的程式練習是`stop_reason(search_count, max_searches, tool_name, is_repeat)`。把Notebook第7節完成的同一函式貼到student/app.py的同名位置，存檔後重新提交；其他函式不用改。

| 情況 | 回傳 |
|---|---|
| 這次是搜尋，而且已搜尋次數≥上限 | `"search_limit"` |
| 否則，這次和之前的動作完全相同 | `"repeated_action"` |
| 其他 | `None`（可以執行） |

兩條都成立時回傳`"search_limit"`。按「執行本次任務」時會先跑A的8筆檢查；A未完成或判斷錯誤時，不會送出任何請求。

被擋下不代表整題失敗：程式會把擋下原因交給模型，之後不再提供工具，模型用已有的資料回答或說明不足。

## 4 設定金鑰與操作

將[.env.example](.env.example)複製成本資料夾的`.env`，在自己的電腦填入金鑰；Notebook第9節也讀同一份`.env`。不要提交或分享真實檔案。

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4-mini
```

部署到Streamlit Cloud時，在平台Secrets填同樣兩個名稱（格式見`student/.streamlit/secrets.example.toml`），不上傳真實secrets.toml。讀取順序：平台Secrets→環境變數／.env；程式不顯示金鑰。

操作順序：

1. 預設離線：選「正常」「不足與重查」「重複後擋下」「搜尋已滿後擋下」看手寫步驟；按「執行本次任務」只會跑A的檢查。
2. 勾「啟用真實API」，選官方範圍，輸入1～300字元的問題。
3. 按一次「執行本次任務」，等它跑完；不要連按。
4. 看結束原因、次數與步驟表格。模型可能走不同路徑，不必剛好是搜尋→閱讀→回答。
5. 展開「候選頁面與原文片段」，打開引用網址，填[B表](觀察與查核紀錄.md)。
6. 下載`agent_record.json`，依下一節回Notebook檢查。

建議正常題：「在Streamlit表單裡，修改輸入值和按下提交按鈕，分別何時讓程式重新執行？請找官方依據。」
建議不足題：「Streamlit官方文件有沒有公布2.0版的確定發布日期？」（和第13週的不足題同類型）。模型若沒搜尋就說明不足，也照實記錄，不要為了多步驟而重跑。

## 5 下載後回Notebook第11-1節

成功、資料不足與失敗都能下載本次紀錄，檔名是`agent_record.json`（和第13週的web_search_record.json分開）。

| 步驟 | 操作與完成條件 |
|---|---|
| 1 | 在本次結果按下載；不要手改內容 |
| 2 | 放到Notebook所在的資料夾；Colab拖到左側「檔案」窗格 |
| 3 | 執行Notebook第11-1節的讀回格，0次API；不用重跑前面的格子 |
| 4 | 第二份檔名若是`agent_record (1).json`，改格內的path再執行 |
| 5 | 通過後，仍要在B打開原文，核對主張與版本／日期／數字 |

讀回格檢查：是修訂版App的真實紀錄、最後一筆是結束事件、call_id不重複、閱讀的頁面都先搜尋過、次數和逐步紀錄相同、原文片段沒被改過、答案只引用讀到的頁面。它刻意保持精簡，不檢查每個網址的主機；整份前後一致的偽造紀錄仍可能通過，所以它不是身分或真實API的證明。

| 訊息 | 回查 |
|---|---|
| 尚未找到agent_record.json | 確認已下載、放在目前資料夾、檔名正確 |
| 不是第14週修訂版App的紀錄 | 是否用了Codex原版App或其他週的檔案 |
| call_id重複／沒有先經過搜尋 | 確認是本次App的原始JSON，沒有混用或手改 |
| 總計和逐步紀錄不同／超過本週上限 | 保留紀錄並告知教師，不要改上限來過關 |
| 原文片段和雜湊不符 | 重新下載原檔；不要手改片段 |

## 6 次數與狀態

| 活動 | Responses最多 | 內建搜尋最多 | 網頁HTTP最多 |
|---|---:|---:|---:|
| 離線情境、A檢查、下載讀回 | 0 | 0 | 0 |
| 一題真實提交 | 6 | 2 | 2 |
| 正常與不足兩題 | 12 | 4 | 4 |

- 常見路徑「搜尋→閱讀→回答」：外層3次＋搜尋1次＝4次Responses，另1次網頁HTTP。
- 最多的路徑「搜尋→換字詞再搜尋→閱讀→回答」：外層4次＋搜尋2次＝6次Responses。
- 4輪中最後一輪只能回答，所以一題最多3次工具。

API錯誤（逾時、429、認證失敗）不會自動重送：連線設定`max_retries=0`，`timeout=60`是每次請求的等待上限。讀網頁等待10秒、不跟轉址、不重試。usage拿不到時保留空白，不當成免費。

新提交、切換範圍／模式／模型、按清除都會清掉舊紀錄；表單內改問題要重新提交才會請求。一般rerun、展開與下載只讀本次紀錄，不會重新請求。

## 7 作業與第15週

課後45～60分鐘，沿用這個App完成：A、正常與不足兩筆真實紀錄（失敗也照實記）、B表、一個擋下或錯誤情況（可用離線情境）、11-1讀回與自己的README。課堂紀錄可直接沿用；額外重測另計次數。

評量：A的擋下規則與流程說明40%、B的路徑與原文查核及讀回30%、錯誤修正與邊界說明20%、可重現與限制說明10%。沒有API額度時照實寫「未測」，由教師安排共看；不要用手寫情境冒充真實結果。

沿用學期Repo與已登記的表單；本週不新增部署要求。第15週再談MCP、部署、Secrets、成本與專題測試。

## 8 重建與驗證（教師）

從Repo根目錄執行：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/build_week14_revised.py
.\.venv\Scripts\python.exe -X utf8 scripts/verify_week14_revised.py
```

生成來源是`scripts/build_week14_revised.py`與`scripts/templates/week14_agent_core_revised.py`，會產生Notebook、閱讀稿、App、requirements、設定範本與手寫情境；不覆蓋本README、工具契約、B表、教師導讀或真實設定。離線驗證只證明程式與請求契約，不代表搜尋或答案品質；尚未實測的項目見[教師導讀](../第14週_修訂版_教師導讀與修訂紀錄.md)。
