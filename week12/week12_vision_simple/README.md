# 第12週圖片理解・課堂簡化版

主線：圖片→本機檢查→A的文字＋圖片content→模型→回應檢查→原圖核對。原正式教材保留；本版一個App提供問答與收據抽取，學生作業選一項，不做第二套作品。

## 先做什麼

1. 在上層學生Notebook閱讀[方法比較](實作方法比較與建議.md)，完成A的build_image_content與自測。
2. 把同一函式移入student/app.py；圖片驗證、Schema、API、回應檢查與畫面已提供。
3. 預設API關閉；選內建收據範例並提交，先看本機驗證與實際傳送PNG。這不是圖片辨識成果。
4. 有API後每次選一張圖、一項任務。下載正常及不足兩筆紀錄，回看原圖完成B。

## 安裝與啟動

使用課程Python3.14與自己的環境；既有課程環境可沿用，不要覆蓋根目錄.venv。

```powershell
cd week12/week12_vision_simple
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m streamlit run student/app.py
```

教師改為teacher/app.py。從Repo根目錄也可用自己的Python執行：

```powershell
python -m streamlit run week12/week12_vision_simple/student/app.py
```

App以程式位置找sample_data與共用.env；Notebook則將receipt_clear.png、receipt_missing_total.png放在Notebook的目前工作目錄，直接讀檔名。Colab請上傳這兩張圖；不在Colab啟動Streamlit。

複製本資料夾.env.example為.env，填自己的金鑰。App優先讀平台Secrets，其次讀共用.env／環境變數；Secrets範本位於student／teacher的.streamlit。若從本資料夾啟動，真正secrets.toml放在本資料夾.streamlit；從Repo根目錄啟動則依Streamlit的目前目錄規則放置，勿誤認程式會自動讀入口同層Secrets。最簡單本機做法是使用共用.env。真實設定不提交。

Notebook在請求格讀目前目錄的.env或環境；Colab先在Secrets設定並授權，再開啟LOAD_COLAB_KEY格。INSTALL_PACKAGES、LOAD_COLAB_KEY與兩個API旗標均預設False，不因全部執行而安裝／讀金鑰／請求。

## 本機檢查與圖片處理

- 原始檔1 byte～2 MB，每邊1～2048像素；轉PNG後至多4 MB。這是課堂限制，不是平台最大值。
- 實際解碼確認PNG、JPEG、WEBP或單張GIF，不相信副檔名；拒絕動畫／多影格／損壞／超限，不自動裁切或縮圖。
- 依EXIF轉正、透明處合成白底，再建立新PNG，不保留原EXIF／文字metadata。畫面內資料仍存在，須自行確認適合傳送。
- 預覽和API使用同一份處理後PNG；紀錄保留原始與實際傳送SHA。Base64不是壓縮、加密或Embedding，不顯示完整字串。

只用自己製作或授權、無敏感內容圖片；課堂提供虛構英文收據。繁中、手寫、複雜版面與真實模型品質均須另外實測。

## 兩種任務，共同狀態規格

圖片問答可改任務文字，用於描述、問題或截圖；答案需分可見證據與推論。收據抽取使用固定任務與strict Schema，輸出merchant、date、total、visible_text、warnings。看不清楚／未提供前三欄保留null與原因；總額不由品項推算。幣別若可見放visible_text，不假設所有總額都是TWD。

每次有效提交最多1次Responses，無Files API或Vector Store操作；只有勾「啟用真實API」才傳送圖片。max_retries=0、timeout=60、max_output_tokens=1200、store=False；網路等待與生成仍可能失敗，逾時不保證服務端沒處理或沒費用。未完成、拒答、空回應、解析或欄位失敗都不保存；輸出上限可能使回應未完成，先縮小任務再評估是否需提高。

新提交先清舊結果，切任務／圖片來源／API模式及清除也清除。表單內換圖、問題、detail須再提交；畫面明示最後成功提交。rerun、顯示與下載不重新請求。下載vision_record.json含任務、問題、detail、模型、檔名、兩種SHA／尺寸、答案與usage，不含原圖、Base64或key；原圖另留。離線只有本機預覽，沒有假答案或成功辨識紀錄。

格式成功仍需核對日期、數字、幣別、原圖位置與缺值；visible_text同樣是模型輸出，不能當獨立驗證。不要將問答當作自動操作截圖，或將單圖Vision當影像檢索已完成。

## 練習與作業

A是唯一程式TODO；B為正常與不足的原圖證據查核。150分鐘核心另留休息10與排障20，課後45～60分鐘沿用同App選問答或抽取，換自製／合法圖片。

交學生Notebook、App、原圖、正常與不足兩份實際紀錄及README；至少核對一個日期或數字、一個原圖證據位置，及一個錯誤／邊界的預期→實際→處理→重測。評量40／30／20／10為A輸入、B證據、修正、可重現反思。題目自由，最低要求一致，不按模式或工具數量加分。

老師問答與抽取各示範1次共2次。學生兩次可同時計入課堂B與作業；若更換文件重做則另增2次，detail選做增加1次，重跑按實際記錄。無API者先交功能、原圖與預期，真實欄寫未測，由老師安排共看實測，不用手寫回答補造。沿用整學期Repo與既有表單，不另交每週資料夾連結。

## 重建與驗證範圍

Repo根目錄執行：

```powershell
python -X utf8 scripts/build_week12_simple.py
python -X utf8 scripts/verify_week12_simple.py
```

重建Notebook／Markdown、雙版App、設定與兩張人工測試圖片；不覆蓋README、方法比較、教師導讀、真實.env與Secrets。Pillow版本影響範例渲染，不將跨版本二進位相同當作平台保證。重建不請求任何API。

已測環境、結果與未測範圍見[教師導讀](../第12週_課堂簡化版_教師導讀與修訂紀錄.md)。本地模擬不證明真實辨識品質、Colab、Cloud或真人瀏覽器已通過；requirements固定版本的新環境亦須另驗證。教師答案不隨學生包發放。
