# 官方文件查核Skill-like模組規格

此處的Skill-like是課程任務模組設計，不是Codex／Claude或平台Skills的安裝檔，也不是宣稱API會自動讀取此文件。

| 項目 | 本週契約 |
|---|---|
| 目的 | 回答Python／Streamlit官方文件可支持的問題，附可查原文的來源 |
| 模型可提出的函式 | prepare_search；只有這個名稱可由程式執行 |
| 本機對應 | build_search_task(topic, scope)，Notebook與App相同 |
| 輸入 | topic去首尾空白後1～300字元；scope為Python或Streamlit |
| 輸出 | query字串與allowed_domains清單；無答案、網頁內容或API副作用 |
| 使用規則 | 模型參數必須與本次問題／範圍相符；程式驗證後才呼叫本機函式 |
| 網路步驟 | 程式回傳function_call_output，再提供內建web_search與官方網域篩選 |
| 成功證據 | completed搜尋事件、查閱來源、有效url_citation、非空答案，再人工核對 |
| 失敗 | 輸入錯誤、拒答、提案或搜尋未完成、無引用、來源不符：不保存舊結果 |
| 費用／停止 | 固定最多2次Responses＋1次內建工具；無平行函式、無重試、無無限loop |

本週強制唯一工具是為了讓學生先讀協定，不把它當成多工具自主選擇。第14週才加入有限次數、觀察與停止的Agent流程。
