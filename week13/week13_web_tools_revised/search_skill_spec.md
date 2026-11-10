# 官方文件查核Skill-like模組規格（修訂版）

這裡的Skill-like是課程的任務模組設計：把上學期Skill的用途、步驟、輸入輸出與錯誤處理，轉成Python程式中的元件。
它不是Codex／Claude或其他平台的Skill安裝檔，API也不會自動讀取這份文件。

## Skill組成與程式對應

| Skill的組成 | 本週對應 | 誰讀取／執行 |
|---|---|---|
| name、description | `TOOL`的name、description | 模型讀，用來決定參數 |
| 任務步驟與注意事項 | `INSTRUCTIONS` | 模型讀 |
| 輸入格式 | `TOOL`的parameters（strict JSON Schema） | 模型照格式產生參數 |
| 腳本（scripts） | `build_search_task(search_query, scope)`（A） | 程式執行，模型碰不到 |
| 錯誤處理 | A與`read_function_call`丟出的ValueError | 程式處理，失敗就停止 |
| 輸出格式 | A回傳的`query`與`allowed_domains` | 程式用來限制搜尋網域 |

## 模組契約

| 項目 | 本週契約 |
|---|---|
| 目的 | 回答Python／Streamlit官方文件可以支持的問題，並附上可打開原文的來源 |
| 模型可提出的函式 | 只有`prepare_search`；其他名稱程式一律不執行 |
| 模型的工作 | 把使用者問題改寫成官方文件常用的英文關鍵字`search_query`；`scope`照抄使用者所選 |
| 本機對應 | `build_search_task(search_query, scope)`，Notebook與App相同 |
| 輸入檢查 | `search_query`去掉首尾空白後1～80字元，不含網址或換行；`scope`為Python或Streamlit，且必須等於使用者所選 |
| 輸出 | `query`字串與`allowed_domains`清單；不含答案、網頁內容，也沒有API副作用 |
| 網路步驟 | 程式以同一call_id回傳`function_call_output`，再提供內建web_search並以`allowed_domains`篩選網域 |
| 成功證據 | 完成的搜尋紀錄、官方網域內的查閱來源、引用頁有被查閱、非空答案；最後仍要人工核對原文 |
| 失敗處理 | 輸入錯誤、拒答、提案或搜尋未完成、參數不符、無引用、來源不符：顯示錯誤、不保存舊結果 |
| 費用與停止 | 固定最多2次Responses＋1次搜尋工具；不平行呼叫、不自動重試、沒有無限迴圈 |

## 為什麼由模型填search_query

原課堂簡化版要求模型把原問題一字不改地抄回參數，學生會看不出模型在這一步的貢獻，模型改了一個標點也會被判失敗。
修訂版改成讓模型做一件看得見、又容易檢查的事：把中文問題改寫成官方文件常用的英文關鍵字。程式仍守住兩條界線：範圍由使用者決定，關鍵字的長度與格式由A檢查。

本週強制唯一工具，是為了讓學生先讀懂協定，不代表已完成多工具自主選擇。第14週才加入有限次數、觀察與停止的Agent流程。
