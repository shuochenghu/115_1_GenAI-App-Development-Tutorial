# 第10週｜Embedding與語意搜尋・課堂簡化版

從第9週已確認的文字出發，只做「片段 → 向量 → 相似度 → 找片段 → 回查來源」，不生成回答。原第10週Notebook、App及Claude參考保留。

## 學生操作

1. 開啟上層「課堂簡化版_學生版」Notebook，先看完整cosine示範，再完成A的計分、來源複製、篩選、排序與top_k；跑固定自測。
2. 把同一個`rank_chunks`移入`student/app.py`，其他函式與UI完整提供，不重寫reader、切塊或第二個App。
3. 先用預設離線規則跑通流程；它是人工關鍵字計數，不是語意模型，不能用來證明同義句理解能力。
4. 設好API後可切真實模式，觀察原句／改寫／文件外三種問題。沒用API時真語意欄寫「未測」，由老師安排共看實測，不填假模型結果。
5. 固定問題，只改top_k或最低分數做兩組比較，回查原文並下載搜尋紀錄；滑桿重排與下載不新增API請求。

## 安裝與啟動

新版沿用Windows／Python3.14課程基準；直接依賴版本在`requirements.txt`。既有環境先確認，不覆蓋原`.venv`。

```powershell
cd week10/week10_semantic_search_simple
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m streamlit run student/app.py
```

已有課程環境可直接使用該環境的`python -m streamlit run student/app.py`。教師入口是`teacher/app.py`；從Repo根目錄也可啟動`python -m streamlit run week10/week10_semantic_search_simple/student/app.py`。範例依App位置讀取，不受工作目錄影響。

學生複製`student/.env.example`為`student/.env`，只在自己的`.env`填金鑰；教師範例則用`teacher/.env`。平台使用入口旁`.streamlit/secrets.example.toml`作格式參考，真正Secrets不提交。Colab只執行Notebook，不要求架設Streamlit，使用平台Secrets並授權Notebook；安裝與畫面需另外實測。

部署選做，沿用[第7週起Git指南](../../week07/生成式AI應用開發_第07週_Git實作教材_學期共用Repo版.md)。Cloud需確認Repo／分支／入口與實際採用的requirements；本機驗證不代表已部署。

## 資料、範圍與API次數

- 文件貼第9週已核對的文字，以空白行分段。最多6000字元、12段、每段1000字元；問題最多300字元。超限拒絕，不截斷原文。
- App沒有PDF／Word reader，也沒有匯入第9週JSON；不要把檔案複製或下載當作搜尋完成。可先用[虛構活動文字](sample_data/activities.txt)及[問題清單](sample_data/questions.json)。
- 每個片段保留`chunk_id/source/start/end/text`；`text == 本次貼入文字[start:end]`。位置不是PDF頁面座標。
- 預設離線0次API；真實模式每次有效新提交最多1次`embeddings.create`，同批包含文件片段與問題。A未完成、空／超限輸入或缺key時0次。
- Notebook教師固定3段＋3問題合批示範1次；學生App三種新問題各1次，共3次。改滑桿、清除、下載與一般rerun均0次；新提交與額外重測另計。
- 為保持小型範例直線流程，每次新提交都重新向量化文件；正式服務應保存文件向量，查詢只算新問題。這不是大型向量資料庫或跨次快取範例。
- 文件與問題同模型、同維度；離線規則與真實向量不可混用。回傳依index對齊，筆數、維度、非有限數字與零向量不合格不保存。
- SDK自動重試關閉，網路等待60秒；不代表總任務60秒內完成。Embeddings仍把文字送到API，不能對此端點照抄Responses的`store=False`。

## 畫面與成功資料

表單只在按「建立向量並搜尋」時處理。新提交先清舊結果；完成輸入、A、API與向量檢查才保存原文／問題／模式／模型／向量。失敗不沿用舊資料，切模式或清除也移除結果。

top_k與門檻在表單外，只用已保存的向量重排。表單未送出時顯示上次成功的原文與問題。來源結果沒有正確機率保證：高分可能無證據、門檻過高可能排掉相關片段、全零規則查詢回空結果。

下載`search_record.json`含模式、模型、問題、原文、參數及hits，不含key或整批高維向量；空結果仍可下載紀錄。下載後核對來源，不能僅看分數。

## 練習與作業

A是唯一程式實作；B是同資料的三類問題與兩組篩選參數觀察。150分鐘核心＋10分鐘休息＋20分鐘排障；課後45～60分鐘換一份合法小文件，沿用同一App。

交學生Notebook、同一App、原文件或貼入文字、兩組搜尋紀錄JSON、README。README至少記模式與實際版本、三類問題／預期來源／實際片段、兩組參數比較、一個證據不足、一個錯誤或邊界的處理與重測、一個日期或數字的人工核對、API次數與未測項目。

題目開放，最低要求固定；評量40／30／20／10為A功能來源、B比較判讀、錯誤修正、可重現反思。不以離線分數當真語意證據；未測欄位明寫未測。沿用整學期Repo與既有Google表單登記，不另交每週資料夾連結。教師答案不隨學生包發放。

## 第11週銜接與驗證

本週普通list索引用來理解文件／問題向量及排名；第11週才把檢索片段組context並生成答案。另一路OpenAI File Search由平台代管支援文件的切塊、Embedding、索引與檢索，仍需資料及來源判讀。本週不建立平台資源、不呼叫Responses或file_search，不要求ChromaDB／FAISS；有餘裕可回看[原第10週向量資料庫說明](../week10_semantic_search_app/README.md)。

重建：Repo根目錄`python -X utf8 scripts/build_week10_simple.py`；離線檢查：`python -X utf8 scripts/verify_week10_simple.py`。實際已測／未測範圍見[教師導讀](../第10週_課堂簡化版_教師導讀與修訂紀錄.md)。

依據：[OpenAI Embeddings](https://developers.openai.com/api/docs/guides/embeddings)、[Create embeddings](https://developers.openai.com/api/reference/resources/embeddings/methods/create)、[Retrieval](https://developers.openai.com/api/docs/guides/retrieval)。
