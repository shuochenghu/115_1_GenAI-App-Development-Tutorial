# 第 8 週｜JSON Schema 與 Pydantic 擇一採用

2026-10-28。保留現有 JSON Schema 起點與教師範例，新增獨立 Pydantic 配套。
**兩種實作使用相同驗收標準，學生擇一即可；最低要求固定，題目與設計開放。**

## 先選一種起點

| 路線 | 學生起點 | 教師完整範例 | 適合的讀法 |
|---|---|---|---|
| JSON Schema | [原學生版](week08_midterm_simple_starter/README.md) | [原教師摘要器](week08_midterm_simple_teacher/README.md) | 想直接看 dict 規格、JSON 解析與欄位檢查 |
| Pydantic | [新學生版](week08_midterm_simple_pydantic_starter/README.md) | [新教師摘要器](week08_midterm_simple_pydantic_teacher/README.md) | 想沿用第 6 週的模型類別、驗證物件與 model_dump |

從自己選的資料夾安裝並啟動，不要把兩份 app.py 或 requirements 混在一起。
也可以自行實作，依[專題說明書](生成式AI應用開發_第08週_期中個人小專題_課堂簡化版_專題說明書.md)驗收。
不必兩版都做，不因使用 Pydantic 多加分，也不因使用 JSON Schema 扣分。

## 使用相同任務，比較規格的表達方式

兩份教師範例都是「課堂筆記重點整理器」，使用相同任務規則與標籤。
輸入同一筆虛構原文：「社團下週舉辦讀書交流，報名方式尚未決定。」

| 輸出欄位 | 規格 | 檢查重點 |
|---|---|---|
| `title` | 必填文字 | 非空白，符合原文主題 |
| `summary` | 必填文字 | 非空白，不補造報名方式或日期 |
| `key_points` | 必填文字清單 | 可為空清單；每個既有項目須非空白且有原文依據 |

欄位名稱與型別相同，不保證兩次 API 產生完全相同的文字。比較的是契約與處理流程，不是逐字相等。
教師三欄只是對照情境，**學生須設計自己的任務與至少兩個有用途的欄位**，不是全班抄同一份摘要器。

| 處理階段 | JSON Schema 版 | Pydantic 版 |
|---|---|---|
| 定義規格 | `SCHEMA` 字典 | `class ProjectResult(BaseModel)` |
| 定義文字／清單 | `type: string`／`array`＋`items` | `str`／`list[str]` 型別註記 |
| 必填／禁止多欄 | `required`／`additionalProperties=False` | 不提供欄位預設值／`extra="forbid"` |
| 送出請求 | `responses.create(text={"format": ...})` | `responses.parse(text_format=ProjectResult)` |
| JSON 與型別檢查 | `json.loads()`＋`check_result()` | SDK 解析並依模型驗證；不合格可能在 `parse()` 內拋錯 |
| 取得資料 | `data` 字典 | `response.output_parsed` 物件，再 `model_dump()` 成字典 |
| 補查空白文字 | `check_result()` | `check_result()`，不重寫欄位型別規則 |
| 保存與顯示 | 通過檢查後保存原文＋data | 相同 |

## 回查第 6 週，再閱讀 Pydantic 版

1. `ProjectResult` 是規格類別，不是一筆模型結果；定義類別不會送 API。
2. `model_fields` 列出欄位規格，供離線檢查未完成設計；它沒有生成摘要。
3. `responses.parse(text_format=ProjectResult)` 才送出請求。SDK 將類別轉成 JSON Schema，透過真正 Structured Outputs 取得回應並嘗試驗證，不只是 prompt 寫「請回 JSON」。
4. `output_parsed` 是解析後物件。例如教師版可用 `result.title` 讀標題；未取得解析物件不能當作成功。
5. `model_dump()` 將物件轉成 dict，之後使用與原版相同的保存與顯示方式；不是寫檔指令。

兩種 strict 分工：API 的 strict JSON Schema 由 SDK 產生；`ConfigDict(strict=True)` 是本機驗證型別的設定。
`extra="forbid"` 拒絕未定義欄位；不加預設值表示每個欄位都要存在。文字清單可存在但沒有項目。
`str` 只限制型別，不會自動排除全空白，因此 Pydantic 版仍補查非空文字。

目前兩種起點都聚焦文字與文字清單；自行擴充其他型別時，須調整起點的設計檢查、驗證與介面。
不要只修改模型、忽略原本只接受兩種型別的檢查。格式合格仍須人工查原文。

## 共用驗收與費用

沿用同一份[設計與驗收紀錄](第08週_課堂簡化版_專題設計與驗收紀錄.md)與評分比例：

- 空白、超過 6000 字元、未完成設計與缺金鑰應在請求前停止。
- 預設 API 關閉；有效提交最多 1 次，無自動重試。原文仍會傳到 API，失敗也可能計費。
- 拒答、未完成、空回應、非法 JSON、缺欄／多欄／型別錯誤與空白內容不得保存。Pydantic 版另確認有解析物件。
- 成功才保存原文與結果；一般 rerun 不重送，清除、切換模式或新提交失敗清掉舊成果。
- 至少記錄正常與資訊不足各一筆真實結果，逐欄查原文；教師規劃 1 次示範，學生選一版測試共 2 次，額外修正另計。

教師可先離線比較兩版，不必為展示對照重複呼叫付費 API。SDK／AppTest／模擬 HTTP 通過只證明程式行為，不代表真實模型、真人瀏覽器或部署通過。

## 教師驗證與依據

由課程根目錄，在具備對應套件的環境執行：

```powershell
python -X utf8 scripts/verify_week08_simple.py
python -X utf8 scripts/verify_week08_pydantic.py
```

第一支保留原 JSON Schema 驗證；第二支用真實 SDK＋模擬 HTTP 比較四份 App 的請求契約、解析、狀態與學生自訂欄位。
沒有對外 API 請求；實測環境與未測項目記於[教師導讀](第08週_課堂簡化版_教師導讀與修訂紀錄.md)。

- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses)
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)
- 第 6 週課堂簡化版 M1／M2／N2 與練習 B：規格→驗證→物件→dict。
