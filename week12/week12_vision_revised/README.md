# 第12週｜圖片理解與Vision・修訂版App

流程：**圖片 → 本機檢查 → A組成「文字＋圖片」content → 模型回答 → 檢查 → 回看原圖**。
搭配上層檔名含「圖片理解與Vision_課堂簡化版_修訂版」的學生／教師Notebook。原課堂簡化版（`week12_vision_simple/`）保留未改。

## 學生操作

1. 開啟學生Notebook，完成A的`build_image_content`並通過自我檢查，再看一次「送出前預覽」。
2. 把同一個函式貼到`student/app.py`的同名函式；圖片檢查、Schema、API與畫面都已完整提供。
3. 先用預設模式（0次API）：選一張範例並提交，看實際送出的PNG與content結構。這不是辨識結果。
4. 有金鑰後勾選真實API，每次選一張圖、一項任務。下載正常與資訊不足兩筆紀錄，回看原圖完成B。沒有API時模型欄寫「未測」，或引用老師的實測紀錄（要標明來源）。

## 範例圖片

`sample_data/`有兩張虛構英文收據與人工基準，和原簡化版逐位元相同：

| 檔案 | 內容 | 人工基準 |
|---|---|---|
| `receipt_clear.png` | DEMO CAFE、Date: 2026-11-11、三個品項、TOTAL TWD 300 | total = 300 |
| `receipt_missing_total.png` | 同上，但沒有總額那一行 | total = null（不可用品項加總推算） |
| `fixture_manifest.json` | 上面兩張圖的人工基準；老闆姓名、電話、地址都不在圖上 | — |

Notebook從`week12`資料夾開啟時會自動找到這些檔案；Colab請把它們上傳到目前資料夾。繁中、手寫與複雜版面都需要另外用合法圖片實測。

## 安裝與啟動

沿用Windows／Python 3.14；直接依賴版本在`requirements.txt`。既有環境先確認，不要覆蓋原本的`.venv`。

```powershell
cd week12/week12_vision_revised
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m streamlit run student/app.py
```

- 教師版改成`teacher/app.py`。也可從Repo根目錄啟動`python -m streamlit run week12/week12_vision_revised/student/app.py`；範例圖與`.env`依App位置讀取，不受目前目錄影響。
- 部署是選做，步驟沿用[第7週起Git指南](../../week07/生成式AI應用開發_第07週_Git實作教材_學期共用Repo版.md)。Colab只執行Notebook，不架Streamlit。

## 金鑰：本機、Streamlit Cloud與Colab都能執行

App用`read_setting`讀設定：**平台Secrets優先，沒有時讀環境變數，`.env`在啟動時載入成環境變數**。同一份程式不用改，本機與Cloud都能跑。

| 執行位置 | 金鑰放哪裡 | 說明 |
|---|---|---|
| 本機App | 本資料夾的`.env`（由`.env.example`複製） | 學生版、教師版與Notebook共用。也可放`student/`或`teacher/`的`.env`，或用環境變數；兩處都有時以本資料夾的`.env`為準 |
| 本機Notebook | 同上 | 先讀`week12_vision_revised/.env`，再找Notebook所在資料夾往上的`.env` |
| Streamlit Cloud | App設定的**Secrets** | 格式見`student/.streamlit/secrets.example.toml`，寫在最外層，不加區段標題 |
| Colab Notebook | Colab的Secrets，並授權Notebook | 只跑Notebook，不架Streamlit |

部署到Streamlit Community Cloud時：
1. **Main file path**填`week12/week12_vision_revised/student/app.py`（依自己Repo的實際路徑）。
2. 入口同層已附`requirements.txt`（含pillow）；Cloud先找入口同層，再找Repo根目錄，不會往上一層找。
3. 在Advanced settings → Secrets貼上：

```toml
OPENAI_API_KEY = "你的金鑰"
OPENAI_MODEL = "gpt-5.4-mini"
```

真正的`.env`與`secrets.toml`不要提交到GitHub。部署後上傳的圖片一樣會送到OpenAI，請提醒使用者不要上傳個資。

## 本機檢查與圖片處理

- 原檔1 byte～2 MB、每邊1～2048像素；轉成PNG後最多4 MB。這是課堂限制，不是平台上限。
- 實際解碼確認PNG、JPEG、WEBP或單張GIF，不相信副檔名；拒絕動畫、多影格、損壞或超限的圖，不自動裁切或縮圖。
- 依EXIF轉正、透明處補白底，另存新PNG，不保留原本的EXIF與文字metadata。畫面裡的資料仍然存在。
- 預覽與送出的是同一張PNG；紀錄保留原檔與送出PNG各自的SHA-256。Base64不是壓縮、加密或Embedding；畫面只顯示開頭。

## 兩種任務

| 任務 | 輸入 | 輸出與檢查 |
|---|---|---|
| 圖片問答 | 自己寫問題（1～300字元） | 文字回答；拒答、未完成、空白都不保存。內容要人回看原圖核對 |
| 收據抽取 | 固定任務（畫面不顯示問題欄） | strict JSON Schema五欄：merchant、date、total、visible_text、warnings。看不到填null並寫原因；total不由品項推算 |

- 每次有效提交最多1次Responses；只有勾選真實API才傳送圖片。沒有Files API或Vector Store操作。
- `max_retries=0`、`timeout=60`、`max_output_tokens=1200`、`store=False`。逾時不保證服務端沒處理、沒收費。
- 新提交先清掉舊結果；切換任務、圖片來源或模式、按清除、送出失敗都會移除結果。表單裡換圖、問題或detail要重新提交。rerun、展開區塊與下載都不會再呼叫API。
- 下載的`vision_record.json`含任務、問題、detail、模型、檔名、兩種SHA-256、尺寸、結果與usage；不含原圖、Base64或金鑰。原圖請另外保留供B核對。
- 格式通過仍要回看原圖：visible_text也是模型寫的，可能和值一起抄錯。

## 請求次數

| 動作 | 請求次數 |
|---|---|
| App本機檢查與送出前預覽 | 0次 |
| App真實模式，每次提交 | 1次Responses |
| Notebook第6節圖片問答（老師示範2題） | 2次 |
| Notebook第7節收據抽取（老師示範2張圖） | 2次 |

學生正常與不足兩筆共2次（課堂B與作業可共用）；detail選做加1次，額外重跑另記。

## 教師實測紀錄（給沒有API的同學）

老師課前在Notebook第6、7節開啟`RUN_VISION_API`與`RUN_RECEIPT_API`實跑，再開啟第8節的`SAVE_TEACHER_RECORD`，就會在Notebook資料夾存下`teacher_vision_record.json`（日期、模型、送出圖片的SHA-256、回答或抽取結果與usage，不含金鑰、原圖或Base64）。
把這個檔案發給學生，放在Notebook所在資料夾即可讀取；第9節的逐欄對照也能用它。學生在B表要標明「教師實測紀錄」。本資料夾不附這個檔案，因為它必須是真實執行的結果。

## 練習與作業

- A是唯一的程式實作；B是回看原圖判讀：看錯、補造、格式失敗、合理看不到要分開記。核心150分鐘＋休息10分鐘＋排障20分鐘。
- 課後45～60分鐘：同一個App選問答或抽取，換一張自己製作或有授權、沒有個資的圖片；交學生Notebook、App、原圖、正常與不足兩份紀錄與README。至少核對一個日期或數字及它在原圖上的位置，以及一個錯誤或邊界的處理與重測。
- 評量40／30／20／10：A與輸入、B證據、錯誤修正、可重現與反思。不需要部署、OCR或雲端資源。沿用整學期Repo與既有表單，教師答案不隨學生包發放。

## 重建與驗證

教師重建與檢查（Repo根目錄）：

```powershell
python -X utf8 scripts/build_week12_revised.py
python -X utf8 scripts/verify_week12_revised.py
```

重建會產生雙版Notebook／Markdown、雙版App、設定範本，並從`week12_vision_simple/sample_data`逐位元複製範例圖；不覆蓋本README與教師導讀，也不呼叫API。已測與未測範圍見[教師導讀](../第12週_課堂簡化版修訂版_教師導讀與修訂紀錄.md)；其他送圖方式的詳細比較見原版[方法比較](../week12_vision_simple/實作方法比較與建議.md)。

官方說明：[Images and vision](https://developers.openai.com/api/docs/guides/images-vision)、[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)、[GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini)。
