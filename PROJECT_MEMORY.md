# 專案工作記憶

此檔用來保存可隨專案移動的工作狀態，方便在不同電腦或不同 AI 工具中接續處理。請勿在此檔寫入 API key、密碼、信用卡、學生個資或其他機密資料。

## 第7週課堂簡化版（2026-10-19，另存教材）

- 依使用者「另外製作簡化版教材，保留原教材」，新增 `week07/生成式AI應用開發_第07週_Streamlit_Web_App_課堂簡化版_學生版.ipynb`／教師版與同名Markdown、`第07週_課堂簡化版_教師導讀與修訂紀錄.md`，配套為 `week07/week07_streamlit_simple/`。原第7週雙版、Git補充、原App及Claude參考檔案保留。
- 雙版各40格（33 Markdown、7 code），所有標題各自起始文字格；Notebook是閱讀講義，App不在Colab／Notebook直接執行。配套student／teacher各7份完整獨立.py，不互相import，不需剪貼code cells：01輸入／按鈕、02rerun／state、03表單活動Structured Outputs、04非串流聊天、05完整串流對照、06文字檔預覽／選用摘要、07側欄／分頁。教師版各11–72行，只有串流版有一個generator，不先建立通用helper呼叫鏈。
- A/B/C只修改標題、歸零、活動名稱／未知負責人顯示，其他API／驗證／history／串流／檔案處理完整提供；學生與教師只有這三個程式格不同。03沿用第6週五欄event Schema，04／05只送最近五輪已完成訊息、成功後保存配對，模式切換會清空離線紀錄，避免送出固定假回答。06先驗UTF-8／64KB／6000字元，換檔清舊結果；07設定有直接畫面效果。
- API預設關閉，離線模式逐處標明固定卡／固定回覆／原文片段不代表抽取、摘要或模型記憶。啟用後每次有效提交／問題／摘要按鈕最多1次，SDK max_retries=0、timeout=60；規劃教師真實示範03一筆＋04兩輪＋05一輪＝4次，06選讀另1次，額外操作另計。第8週真Structured Outputs要求保留，離線卡不能充當成果。配套有requirements、.env.example、忽略規則、Secrets範例、虛構文字檔與README；本次未建立真實金鑰檔。
- 重建 `scripts/build_week07_simple.py`，驗證 `scripts/verify_week07_simple.py`。本次既有Python3.14.0／Streamlit1.60.0／OpenAI2.49.0／python-dotenv1.2.2做離線檢查，未安裝套件；requirements沿用原目標Python3.12／Streamlit1.63.0／OpenAI2.49.0／python-dotenv1.2.3，目標環境未新驗證。
- 已通過：雙版JSON／唯一ID／標題分格／AST／清空輸出／Markdown與配套原碼對齊／三處答案分離／重建一致；AppTest 14份App初啟動0請求、輸入與歸零、表單提交與結果保存、兩輪／五輪聊天視窗／清空／模式隔離、串流完成與失敗不保存／關閉連線；假SDK請求格式、history、store=False、重試／timeout、拒答／未完成／空回應／JSON與欄位失敗、缺金鑰與空輸入；替代上傳物件的編碼／空檔／大小／長度／離線與假摘要分支。UTF-8、Markdown本機連結與git diff --check通過。AppTest使用可寫忽略暫存目錄重跑，排除系統沙箱暫存清理權限錯誤。
- 未執行：真實API／網路串流、真人瀏覽器（含檔案選擇與實際Ctrl+C）、目標套件安裝、Cloud部署或150分鐘試教；不把AppTest或假回答當作這些驗證。接續先依教師導讀在課堂環境實測，再記錄實際內容與時間。
- 本次基準main／HEAD `643b80a`，開始時既有工作目錄乾淨；本次只新增第7週簡化版檔案與腳本、更新本檔。未commit／push／fetch／pull或啟動對外伺服器。原第7週檔案以工作前雜湊逐檔核對；第6週與專案skill本次未改。

## 2026-10-19工作重點與後續教材預設

使用者明確要求記住今天工作，並確認：**後續程式教材的設計與修改，以今天第6週課堂簡化版原則為預設；授課容易理解、學生掌握單元重點優先。** 下方「講義製作原則」已加入此長期要求。此要求適用之後的工作，不代表現在自動改寫其他週次。

同日同步更新 `skills/course-material-authoring/SKILL.md`：入口明確要求讀取「程式教材簡化原則」，補上短小獨立範例、直接資料流、減少框架與跨格依賴、同資料對照及標題分格等設計要求，並連結本檔與第6週教師導讀。完整規則以本檔為準，skill只保留關鍵執行指引；沒有變更skill名稱、觸發範圍或其他週教材。系統Python執行skill-creator的quick_validate通過（專案venv缺PyYAML，未另裝套件），本機參照連結、UTF-8與git diff --check通過。

今天交付第6週課堂簡化版學生／教師Notebook與Markdown、教師導讀、重建／驗證腳本；保留原150分鐘版與原逐格講稿。現行雙版各90格（64文字、26程式），N1放在事件Schema單元，以兩筆活動說明array/items；M1/M2後的N2使用相同資料做Pydantic完整對照，18行、獨立執行、無TODO與API。所有標題各自起始text cell；前例結果與下一節標題分格。主線G/A必做、B/C擇一，固定7次API，付費開關預設False。

本機／靜態／假回應驗證已通過，未測真實API、Colab目錄與操作、瀏覽器或150分鐘試教。分支main／HEAD `6c7ec6b`，今天成果仍未提交或推送；後續先讀簡化版導讀與本檔，再按指定範圍工作。詳細檔案、驗證與歷次調整見下一節。

## 第6週課堂簡化版（2026-10-19，另存授課教材）

- 同日依使用者確認在M1、M2後新增N2「用Pydantic表示同一份活動清單」：完整18行code cell，含EventItem／EventList、與N1相同的兩筆活動、自帶匯入、model_validate、物件屬性讀取與model_dump，無TODO／0次API／可獨立執行；另有前置對照表與結果判讀兩個text cells，均遵守標題各自起始一格。雙版現在各90格（64 Markdown、26 code，25普通Python），原87個ID順序與25個code cells逐一比對完整保留，教師程式總行數538。同步雙版Notebook／Markdown、流程表、C銜接、教師導讀與格號、重建及檢查腳本。通過全部離線／假API與N2同資料、物件／dump、缺owner／錯型別／多欄負例及空清單邊界；未呼叫真實API，未實測Colab顯示。
- 同日依使用者確認拆分標題文字格：10格多標題與12格「上一例判讀＋下一節標題」均已拆開；學生／教師版由64格改為87格（62 Markdown、25 code），每個標題各自起始一格，內文與表格隨所屬標題。原64個cell IDs與相對順序保留，新增23個文字格ID；全部code cells含metadata／TODO與原文字串逐一比對完全相同。同步雙版Markdown格號、教師導讀位置表、重建來源及驗證腳本。雙版JSON／標題分格／AST／離線與假API檢查、內容指紋與git diff --check通過；未在Colab實測目錄呈現，沒有呼叫真實API。
- 同日依使用者確認更新N1：把原Pydantic區的作業Schema移到第2節事件Schema之後、API比較之前，改成`event_list_schema`／`event_list_data`的兩筆活動（title、nullable owner）；Pydantic單元只講class→驗證→物件→dump，C再口頭對照array/items與list[OrderItem]。同步雙版Notebook／Markdown、流程表、教師導讀與重建來源，保留既有cell IDs與64格／25 code，沒有新增API請求。已驗證N1順序、資料與獨立執行、全部原有離線／假API檢查、Markdown對齊及git diff --check；未執行真實API或Colab。
- 使用者指出現有程式過難、前後code cell牽連複雜，要求以理解單元重點為主；先完成簡化規劃，再依明確指示新增課堂簡化版。新增 `week06/生成式AI應用開發_第06週_Structured_Outputs_課堂簡化版_學生版.ipynb`／教師版及同名Markdown閱讀版，另有 `第06週_課堂簡化版_教師導讀與修訂紀錄.md`。原150分鐘修訂版、原逐格講稿及其他教材全部保留，原C01–C36講稿不可直接套用簡化版格號。
- 雙版目前各90格（64 Markdown、26 code，其中25普通Python；初版64格、標題拆分後曾87格）。主線保留JSON Schema先教、required／nullable、deepcopy、真正text.format、完成／拒答／解析失敗、客服欄位與人工覆核、Pydantic、array／items、B/C擇一、課後版本／會議／重試。教師程式631→538行，最長格63→45行；API直接展開，主線僅保留一個短客服validator，無假client或通用safe框架供學生閱讀。
- 多數本機格自帶匯入與資料；A3只依賴A2，API格只依賴Z1與本節規格／模型，A4/A5不讀彼此變數。需求記在各格文字及teaching metadata。G、A1、A2、B1、C1五個答案格有學生TODO與教師答案；result成功固定dict或物件、失敗None，錯誤另放error；失敗重跑不沿用舊資料。原A2六項假client契約改為教師離線驗證，學生記錄為直接資料正負例，舊report語意不可混用。
- 重建來源 `scripts/build_week06_simple.py`；檢查 `scripts/verify_week06_simple.py`。本次新增7檔（雙版Notebook／Markdown、教師導讀、兩支腳本），並更新本檔；先前未提交的逐格講稿與其腳本保持不動。
- 本次使用專案Python 3.14.0／Pydantic 2.13.4，未安裝套件。驗證雙版JSON／唯一ID／清空輸出／各24格AST／預設False、無金鑰順序、24格按宣告前置在乾淨namespace執行、五處答案分離、Markdown原碼對齊、重建一致、G/A/B/C正負例；假API六種活動1/1/1/3/1/1次與請求參數、拒答／未完成／failed／空回應／解析／欄位／無解析物件、成功後再失敗清舊結果，以及學生TODO未完成時0次假請求通過。UTF-8、Markdown圍欄／本機連結、既有Notebook內容未變、git diff --check通過。
- 固定主線仍7次API（B/C只開一題），未納入原選讀作業抽取的額外1次API；N1目前是多筆活動的本機示範。尚未執行安裝格、真實API／SDK網路、Colab Secrets與畫面、瀏覽器呈現或150分鐘試教，不能用假回應當真實模型成果。
- 分支main、HEAD `6c7ec6b`；上述新增與本檔更新尚未提交，未fetch、pull、commit或push。接續修改以使用者指定簡化版為準；課前依導讀在教學帳號／Colab確認模型、套件、回應與時間，再保存實測證據。

## 第6週逐格教師講稿（2026-10-19）

- 依使用者要求，新增 `week06/第06週_150分鐘修訂版_逐CodeCell教師講稿.md`，以現行150分鐘學生／教師Notebook為準，完整涵蓋36個code cells（含安裝格與課後選讀）。原Notebook、TODO與輸出未修改。
- 講稿C01–C36對應Notebook總格號（從1起算、包含Markdown）、cell ID、cell內L行號；附完整教師原碼與逐段口述。G、A1、A2、B1、C1/C2所在5格另附學生骨架S行號，標明教師答案揭示時機。每節包含開場、操作、預期、失敗回查與提問；維持G／A必做、B/C擇一、主線7次API與選讀額外1次。
- 重建來源為 `scripts/build_week06_code_lecture.py`，保留人工撰寫的逐格講稿並讀取原Notebook產生原碼與索引。若Notebook改版，須重新核對講解行號與內容，不能只重建即視為語意同步。
- 本次靜態驗證：36格全覆蓋、雙版位置／ID一致、36段教師原碼與5段學生骨架逐行相符、講解行號合法、章節與錨點、來源SHA-256、腳本語法、UTF-8與git diff --check。確認Notebook相對HEAD未變；未呼叫API、未安裝套件、未新增模型實測，Colab、瀏覽器呈現與150分鐘試教仍待驗證。
- 開始時工作目錄乾淨；目前分支main、HEAD `6c7ec6b`，本次新增講稿與重建腳本並更新本檔，尚未提交。未fetch、pull、commit或push，不將既有遠端資訊視為本次同步證據。課前先以教師版確認G／A離線活動與B/C選題流程，再做教學帳號真實API與Colab驗證。

## 公司接續摘要（2026-10-14）

使用者確認昨晚在家裡沒有工作。本次以公司`E:\Git Repos\115_1_GenAI-App-Development-Tutorial`的`main`／`c4aa207`接續；昨天第5週修改已包含在合併提交內，開始時已追蹤檔案乾淨，只有既有未追蹤`.claude/settings.local.json`。下方10月13日摘要的`Home_Test`／未提交描述是歷史快照，不再代表目前Git狀態。本次未fetch、pull、commit或push，不將既有origin/main資訊稱為今天新查驗的遠端狀態。

### 本次完成

- 依昨天第5週討論重新檢視第6週150分鐘學生／教師版，並依使用者「該說明的知識點要詳細說明」要求，同步補強18個既有Markdown cells：JSON／dict／Schema、required／null／缺欄／空字串、API參數與strict、巢狀深拷貝、完成／拒答／解析／validator分工、假回應用途、A2六項離線規則與失敗回查、真實三題判讀、Pydantic class／物件／dict與兩種strict、array/items，以及成果證據與App銜接。
- 第6週仍各70 cells（34 Markdown、36 code，35格普通Python）；全部code、學生TODO／教師答案、ID／順序、metadata、清空輸出與修改前一致。G／A必做、B/C擇一，固定主線7次API、作業選讀另1次。詳細說明集中既有文字格，未增加必做題或付費活動。
- 同步`scripts/build_week06_revision.py`與`week06/第06週_150分鐘修訂版_修訂與驗證紀錄.md`。本次5個已追蹤修改檔案為第6週Notebook雙版、builder、修訂紀錄及本檔，尚未提交；其他週次、原始第6週及Claude參考版未改。

### 本次驗證與接續

- 使用公司既有`.venv`的Python 3.14.0／Pydantic 2.13.4，未安裝新套件。系統Python缺Pydantic與`.venv`可執行兩者同時成立，後續先確認實際使用的解譯器。
- 第6週離線檢查與第5、6週共同檢查通過：Notebook JSON／ID／輸出／AST／TODO分離、無金鑰／假SDK順序執行、教師成功／失敗行為、A2六項檢查、各活動假請求數、逾時／第5週CLI模擬及第6週重建比對。另確認第6週程式格完全未改、中文亂碼與git diff --check通過。
- 尚未執行真實付費API、Colab安裝／顯示／操作、瀏覽器或150分鐘試教。詳細知識說明供教師備課與學生回查，實際課堂可依示範讀法與固定練習帶課；授課時間仍須試教。第5週實際Ctrl+C／Colab停止操作亦仍未驗證。
- 接續第6週以現有150分鐘雙版為準：先完成G與A的離線流程，再真實單筆／三題、B/C擇一與逐欄原文核對。第12週語音增補仍未開始，下一步依使用者指定，不自動展開其他週次。

## 歷史：回家接續摘要（2026-10-13，離開公司前）

此節保留當時離開公司的快照；目前接續以最前方10月14日公司摘要為準。當時第5週現行150分鐘雙版已由63增至64 cells，第6週仍各70 cells；第5、6週語音預告已移除，第12週語音增補仍未開始。

### 工作區與Git狀態

- 公司工作區：`E:\Git Repos\115_1_GenAI-App-Development-Tutorial`。目前分支`Home_Test`，HEAD為`842f212`（Update PROJECT_MEMORY.md），前一提交`236043e`為刪除第5、6週語音文字說明。
- 今日第5週修訂仍在工作目錄，尚未commit或push；本次只記錄狀態，沒有執行commit、push、pull或fetch，遠端最新狀態未查驗。回家僅切到同名分支或只取得842f212，不能保證拿到今天的未提交修訂。
- 本次聊天修改的5個檔案：本檔、第5週150分鐘學生版／教師版Notebook、第5週修訂與驗證紀錄、`scripts/verify_colab_runtime_guidance.py`。
- 另有本次工作開始前已存在的未提交修改：`PROJECT_MEMORY_claude.md`、`week12/生成式AI應用開發_第12週_Vision_Claude與Codex版比較.md`；本次未改，已以雜湊確認保留。另有未追蹤`.claude/`，未處理。
- 家裡上次路徑為`K:\115_1_GenAI-App-Development-Tutorial`，回家須確認實際路徑與檔案同步，不沿用公司的Python環境或絕對路徑。

### 今天已完成

正式接續版本：

- `week05/生成式AI應用開發_第05週_對話狀態_Streaming與聊天機器人實作教材_150分鐘修訂版_學生版.ipynb`
- 同主題`150分鐘修訂版_教師版.ipynb`
- 詳細紀錄：`week05/第05週_150分鐘修訂版_修訂與驗證紀錄.md`

| 位置 | 完成內容 | 留給後續工作的重點 |
|---|---|---|
| 第6節／第38格 | 補stream=False／stream=True對照、response與事件串流差異、逐片顯示與完成保存；連回離線片段示範與正式函式 | stream=True不會自動print，也不保證整段更快或變成非同步；callback預設逐片print，最後join供驗證／回傳／保存。示範另印一次完整文字是核對。 |
| 第8節／第47格起 | 改名「驗證聊天功能：離線程式檢查與真實 API 回答觀察」；重寫目的、老師／學生任務、假client用途、旗標順序、五項規則／失敗回查、分階段證據紀錄 | 假回答不能證明模型記得；先看input與state，再看回答。五行PASS只有整組完成後才印出，不是模型品質分數。 |
| 第54格 | 新增真實API測試前文字指引，原run_live_chat_checks移至第55格 | 三次非串流請求，逐輪保留input／回答並人工判讀；不是完整模型評測或真實串流驗證。reset後usage不是三次完整帳單。 |
| 第9節／第57、58格 | CLI加入外層KeyboardInterrupt與EOFError處理，啟動操作提示；支援Ctrl+C停止整個CLI | 保留/exit、/reset與單輪錯誤重試。終端機Ctrl+C、Colab停止按鈕須實測；串流尚未完成時中止不保存部分回答。 |
| 驗證腳本 | 接受第5週新增的指定Markdown格，依ID核對既有cell；增加check_cli_interrupts五組離線檢查 | 此函式需教師版已完成A／B環境；不呼叫真實API，不能冒充真實鍵盤測試。 |

兩版目前各64 cells（37 Markdown、27 code，26普通Python）；原63個ID與順序保留，新增`w05r-live-check-guide`。學生A／B TODO、教師完整答案、固定測試器與metadata／清空輸出保留。付費旗標仍預設False，`# run_console_chat()`預設註解；固定活動各跑一次仍15次請求，CLI額外問答與手動重跑另計。原始版與Claude參考版保留，後續在這組修訂版續改。

另依主課綱整理過API需求：OpenAI文字／Vision／工具呼叫可共用Responses API，RAG另需Embeddings，後續語音增補需STT與TTS；Realtime、圖片生成、託管搜尋／工具及Claude／Gemini為依需求選用。只提供建議與官方文件查核，未採購、儲值或修改主課綱；模型、價格與帳號權限需在實作／採購前重新確認。

### 驗證與尚未完成

- 公司本次使用Python 3.14，兩版JSON、唯一ID／順序、清空輸出、各26格普通Python AST、雙版說明與CLI對齊、TODO保留及亂碼檢查通過；驗證腳本可編譯，git diff --check通過。
- 兩版無金鑰／假SDK順序執行通過；教師一筆假串流、五項離線行為規則、兩項逾時保護及五組CLI檢查通過。CLI含等待輸入時中斷／EOF、/exit、/reset、單輪錯誤重試、成功一輪後再於下一輪串流途中中斷；最後一項state維持上一成功回合，不保存部分回答。
- 共同第5、6週驗證曾在第6週因公司環境缺少Pydantic中止，後來改單獨調用第5週檢查函式。未安裝套件，也未宣稱本次第6週完整驗證通過；家裡既有第6週歷史驗證保留。
- 沒有呼叫真實OpenAI API；尚未實測Ctrl+C實際按鍵、真人CLI互動、Colab輸入／停止按鈕、Notebook雲端顯示、瀏覽器或150分鐘試教。KeyboardInterrupt模擬不能當作上述環境驗證。

### 回家接續順序

1. 確认今天未提交的5個檔案及本記憶已同步到家裡；先看Git狀態，保留其他既有修改，不假設遠端已有今天工作。
2. 先讀本節、「講義製作原則」、`skills/course-material-authoring/SKILL.md`及`references/conventions.md`，再讀第5週最新修訂紀錄。
3. 繼續檢視第5週時使用64-cell的150分鐘雙版；若要實測，先完成A／B與離線檢查，再在教學帳號確認一般／串流與三輪真實回答，以及終端機／Colab的停止操作，記錄套件版本、input／輸出與未完成項目。
4. 家裡若有Pydantic，可按實際環境執行`python -X utf8 scripts/verify_colab_runtime_guidance.py`檢查第5、6週；先確認依賴，不沿用公司的缺套件結論或假設所有環境都通過。
5. 第1週語音增補修訂版仍23頁，實際示範音檔未製作；第6週150分鐘雙版仍70 cells。第12週語音實作／主課綱同步仍為待規劃，下一個修改週次尚未指定，不自動開工。

回家可直接使用此提示：

> 我已回家。請先讀PROJECT_MEMORY.md最前方「回家接續摘要」與講義製作原則，確認Git狀態及今天修訂是否已同步。第5週150分鐘雙版目前各64 cells，已補stream=True說明、重寫第8節驗證流程、加入第9節Ctrl+C／EOF中止處理；真實API、Colab及實際按鍵尚未驗證。第12週語音增補仍未開始，接著依我指定的工作繼續。

## 歷史：公司電腦接續摘要（2026-10-13，離開家裡前，含公司接續補充）

此節保留早上家裡交接內容與公司接續補充；目前接續工作請以最前方「回家接續摘要」為準。若10月12日紀錄仍提到第5、6週語音銜接，以10月13日「已刪除」為現行決策。

### 工作區與同步狀態

- 家裡專案位置：`K:\115_1_GenAI-App-Development-Tutorial`。公司以實際專案位置為準，不直接沿用家裡絕對路徑或Python環境。
- 寫入本摘要前：分支 `Home_Test`，最新提交 `236043e`（刪除第5，6周語音文字說明），工作目錄乾淨。摘要寫入後，`PROJECT_MEMORY.md`會有新的未提交修改。
- 本次只保存專案內記憶，沒有執行commit、push、pull或跨電腦同步；遠端是否包含最新提交尚未查驗。到公司需先確認最新教材與本記憶檔已帶到該電腦，不能只靠聊天歷史或假設遠端已更新。

### 已完成與現行版本

| 週次 | 接續修改的版本 | 現況 |
|---|---|---|
| 第1週 | `week01/生成式AI應用開發_第01週教材_語音增補修訂版.md`、`生成式AI應用開發_第01週投影片_語音增補修訂版.md`／`.html` | 23頁；STT→確認文字→文字回答→TTS概念、10分鐘預錄示範腳本與設備調查。評量40／20／25／10／5%，期末至少RAG或Function Calling。原始三檔保留。尚未製作實際音檔。 |
| 第5週 | `week05/`檔名含`對話狀態_Streaming與聊天機器人實作教材_150分鐘修訂版_學生版／教師版.ipynb` | 各64 cells；文字對話與Streaming主題，第8節已釐清離線程式檢查與真實回答觀察。完成%pip、Secrets與重啟順序、套件版本顯示、max_retries=0及可調整60秒timeout。已刪除語音預告，固定活動各跑一次規劃15次請求。 |
| 第6週 | `week06/`檔名含`Structured_Outputs_JSON_Schema與資料抽取實作教材_150分鐘修訂版_學生版／教師版.ipynb` | 各70 cells；JSON Schema先教，G與A必做、B/C擇一，主線7次請求、選讀另1次。完成事件欄位驗證、A2六項離線契約、Colab提示與60秒timeout。已刪除語音預告與無關修訂作業說明。 |

公司接續補充（2026-10-13）：第5週第6節已補`stream=True`基礎對照；第8節已重寫驗證目的、兩階段操作與判讀，新增真實API測試前的文字指引。第9節CLI另已加入Ctrl+C／EOF中止處理與環境說明。兩版目前各64 cells，A／B及測試器保留；詳見最近工作進度。

第5、6週原始版與Claude參考版保留，後續在上述150分鐘雙版本續改，不另建重複修訂版。學生TODO與教師答案分工、ID、順序、付費旗標預設False均保留。

### 使用者已確認的教學取捨

- 第5、6週沒有語音API範例或練習，不能只因「未來可以整合」就加入STT／TTS文字預告；兩週現行教材已完全移除該段。更新與重建腳本也不會加回。
- 第6週Schema版本管理、巢狀會議模型有本機範例，重試R有明確設計規格，保留為課後延伸。第7／8週App銜接對應本週抽取、成功／失敗分流與欄位驗證，以及期中真structured output要求，保留。
- 語音概念保留在第1週；第12週增補語音輸入與輸出是後續規劃。目前第12週仍是Vision教材與App，尚未修改第12週、主課綱或第7週App以加入語音功能。
- 60秒是待課前實測的網路等待起始值，不是整段串流總時間上限；套件版本顯示供紀錄，Colab驗證後再固定安裝版本，不能直接套用Windows完整快照。

### 驗證狀態與腳本

- 第1週：Markdown內容／亂碼、HTML共23頁及全部頁面渲染檢視通過，技術地圖頁尾重疊已修正。
- 第5、6週：四份Notebook JSON、122格普通Python AST、唯一ID、清空輸出、TODO保留、缺金鑰順序執行、假SDK建構參數與Secrets未授權、模擬逾時處理通過。10月13日刪文前後所有code cells完全一致，各只改一格Markdown；第6週重建內容比對通過。
- 更新入口：`scripts/update_colab_runtime_guidance.py`；共同離線驗證：`scripts/verify_colab_runtime_guidance.py`。
- 第6週重建／檢查：`scripts/build_week06_revision.py`、`scripts/verify_week06_revision.py`；第1週來源：`scripts/build_week01_voice_revision.py`。
- 上述第5、6週檢查使用家裡Python 3.13與既有Pydantic，OpenAI SDK以假模組替代；沒有執行真實OpenAI SDK或付費API，沒有Colab／教室試跑或150分鐘試教。不得把離線通過寫成真實模型或雲端驗證成功。

### 到公司後的接續順序

1. 確認專案同步與Git狀態，先讀本節與「講義製作原則」，再讀 `skills/course-material-authoring/SKILL.md`、`skills/course-material-authoring/references/conventions.md`及相關週修訂紀錄。
2. 修改第1週時用語音增補修訂版；修改第5、6週時用150分鐘學生／教師版。各週詳細紀錄：`week01/第01週_語音增補修訂與Colab檢視紀錄.md`、`week05/第05週_150分鐘修訂版_修訂與驗證紀錄.md`、`week06/第06週_150分鐘修訂版_修訂與驗證紀錄.md`。
3. 下一個要修改的週次尚未指定。待辦可由「第12週語音實作及主課綱同步規劃」或「第5、6週Colab課前實測」接續；本次不把規劃視為已完成或自動開始新修改。
4. Colab實測應確認安裝、Secrets授權／重啟、模型可用性、一般／串流／Structured／Pydantic成功與失敗，記錄套件版本並調整逾時。真實API與試教未完成項目繼續保留。
5. 課程原則仍沿用第4、5週：概念與程式緊密對應、必要語法選讀連回正式程式、TODO具體規格、雙版本同步、付費開關緊鄰活動、保留原檔並同步記憶。

公司可直接用此提示接續：

> 我已到公司。請先完整讀取PROJECT_MEMORY.md，尤其「公司電腦接續摘要」與「講義製作原則」，確認教材製作skill及專案目前Git狀態，再依我指定的週次繼續。第5、6週已刪除無實作支撐的語音預告，第12週語音實作仍未開始。

## 專案定位

本資料夾是 115 學年度上學期課程大綱與教材工作區，主要正在製作「生成式AI應用開發」課程教材。課程主線以 Python、OpenAI API、Google Colab、Streamlit 為核心；Claude API 與 Gemini API 作為比較或補充版本，不作為主要教學主線。

## 目前教材狀態

目前 notebook 教材只保留「學生版」與「教師版」。原始版 notebook 已刪除，避免和教師版內容重複。

- `生成式AI應用開發_16周課程大綱.md`：課程主大綱，目前實際規劃為 18 週，含 16 週授課與第 17、18 週自主學習。
- `week01/生成式AI應用開發_第01週教材_語音增補修訂版.md`、同名主題投影片Markdown／HTML：第1週新修訂主線，原始三檔保留。23頁Marp加入STT／文字回答／TTS概念、10分鐘預錄示範與背景調查；150分鐘核心教學、10分鐘休息、20分鐘彈性排障。評量與期末最低要求對齊主課綱。第12週語音為後續增補規劃，尚未更新該週或主課綱。
- `week02/生成式AI應用開發_第02週_Python複習_學生版.ipynb`：第 2 週學生版，保留 TODO 骨架。
- `week02/生成式AI應用開發_第02週_Python複習_教師版.ipynb`：第 2 週教師版，保留完整參考答案。
- `week03/生成式AI應用開發_第03週_OpenAI_API入門_學生版.ipynb`：第 3 週 OpenAI API 學生版，保留 TODO 骨架。
- `week03/生成式AI應用開發_第03週_OpenAI_API入門_教師版.ipynb`：第 3 週 OpenAI API 教師版，保留完整參考答案。
- `week03/生成式AI應用開發_第03週_Gemini_API入門_學生版.ipynb`：第 3 週 Gemini API 學生版，保留 TODO 骨架。
- `week03/生成式AI應用開發_第03週_Gemini_API入門_教師版.ipynb`：第 3 週 Gemini API 教師版，保留完整參考答案。
- `week03/生成式AI應用開發_第03週_Claude_API入門_學生版.ipynb`：第 3 週 Claude API 學生版，保留 TODO 骨架。
- `week03/生成式AI應用開發_第03週_Claude_API入門_教師版.ipynb`：第 3 週 Claude API 教師版，保留完整參考答案。
- `week04/生成式AI應用開發_第04週_Prompt_Engineering_教師版.ipynb`：第 4 週 Prompt Engineering 教師版，保留完整參考答案（35 cells）。
- `week04/生成式AI應用開發_第04週_Prompt_Engineering_學生版.ipynb`：第 4 週 Prompt Engineering 學生版，四大功能與課堂練習保留 TODO 骨架。
- `week04/生成式AI應用開發_第04週_Prompt_Engineering實作教材_教師版.ipynb`：依原規劃重建的 40-cell 教師版，包含完整參考答案。
- `week04/生成式AI應用開發_第04週_Prompt_Engineering實作教材_學生版.ipynb`：依原規劃重建的 40-cell 學生版，三組綜合練習保留 TODO 骨架。
- `week05/生成式AI應用開發_第05週_對話狀態_Streaming與聊天機器人實作教材_教師版.ipynb`：第 5 週 40-cell 教師版，包含完整聊天 session、Streaming 與三組練習答案。
- `week05/生成式AI應用開發_第05週_對話狀態_Streaming與聊天機器人實作教材_學生版.ipynb`：第 5 週 40-cell 學生版，三組綜合練習保留 TODO 骨架。
- `week05/生成式AI應用開發_第05週_對話狀態_Streaming與聊天機器人實作教材_150分鐘修訂版_學生版.ipynb` 與教師版：目前各64 cells，後續第5週修訂在此雙版接續；第8節已明確區分離線程式檢查與真實回答觀察。第5、6週150分鐘雙版皆補Colab操作、可調整的60秒網路逾時、版本顯示；2026-10-13已移除無當週實作支撐的語音預告。SDK自動重試關閉，課前仍需實測Colab並確認版本。
- `week06/生成式AI應用開發_第06週_Structured_Outputs_JSON_Schema與資料抽取實作教材_教師版.ipynb`：第 6 週 40-cell 教師版，包含 Structured Outputs、JSON Schema、資料抽取、Pydantic、巢狀模型、refusal handling 與練習答案。
- `week06/生成式AI應用開發_第06週_Structured_Outputs_JSON_Schema與資料抽取實作教材_學生版.ipynb`：第 6 週 40-cell 學生版，保留 JSON Schema、Pydantic 與重試練習 TODO 骨架。
- `week06/生成式AI應用開發_第06週_Structured_Outputs_JSON_Schema與資料抽取實作教材_150分鐘修訂版_學生版.ipynb` 與教師版：目前各70 cells，G、A必做與B/C擇一；原始版保留，後續第6周修訂以此雙版接續。
- `week07/生成式AI應用開發_第07週_Streamlit_Web_App入門實作教材_教師版.ipynb`：第 7 週 40-cell 教師版，主軸為 VS Code、本機 Python、Streamlit、OpenAI Responses API、session state、streaming、secrets、表單與檔案上傳。
- `week07/生成式AI應用開發_第07週_Streamlit_Web_App入門實作教材_學生版.ipynb`：第 7 週 40-cell 學生版，保留 Streamlit App、API helper、session state、streaming 與期中小專題規劃 TODO。
- `week07/week07_streamlit_app/`：第 7 週可直接用 VS Code 開啟的 Streamlit 範例專案，包含 `app.py`、`requirements.txt`、`.env.example`、`.gitignore`、`README.md` 與 `.streamlit/secrets.example.toml`。
- `week08/生成式AI應用開發_第08週_期中個人小專題_內容規劃.md`：第 8 週教材內容規劃，定位為期中個人小專題整合週；正式教材策略改採 Markdown 專題說明書 + `week08/week08_midterm_starter/` + 教師 demo 範例，不優先製作 notebook pair。
- `week08/生成式AI應用開發_第08週_期中個人小專題_專題說明書.md`：第 8 週正式專題說明書，包含專題目標、繳交要求、設計表、starter 使用方式、檢核清單、README 規格、rubric、課堂流程與常見問題。
- `week08/week08_midterm_starter/`：第 8 週學生 starter Streamlit 專案，保留 TODO，引導學生完成專題名稱、system prompt、JSON Schema、prompt builder、表單欄位、structured output 與結果顯示。
- `week08/week08_midterm_example_summarizer/`：第 8 週教師 demo Streamlit 專案，提供完整 AI 摘要器，示範 OpenAI Responses API、Structured Outputs、錯誤處理、API key 安全管理與結果區塊化呈現。
- `week09/生成式AI應用開發_第09週_文件處理與資料前處理實作教材_學生版.ipynb`：第 9 週 36-cell 學生版，涵蓋 PDF、DOCX、CSV、TXT／MD reader、文字清理、固定長度 chunking、文件品質檢查、選擇性 AI 摘要與 Streamlit 專案銜接；段落優先切割、文件品質報告與 App 改造規劃保留 TODO。
- `week09/生成式AI應用開發_第09週_文件處理與資料前處理實作教材_教師版.ipynb`：第 9 週 36-cell 教師版，提供三組練習完整參考答案與觀察重點。
- `week09/week09_document_processor/`：第 9 週可直接以 VS Code 開啟的 Streamlit 文件處理專案，支援 PDF、DOCX、CSV、TXT、MD 抽取、文字清理、可調 chunking、chunk 預覽與 JSON 下載；只有使用者明確按下按鈕才呼叫 OpenAI Responses API 產生摘要。
- `week11/生成式AI應用開發_第11週_RAG基礎與文件問答實作教材_學生版.ipynb`：第 11 週 40-cell 學生版，從 ChromaDB 正式索引銜接 context、prompt contract、證據不足拒答、來源顯示、基本引用評估與完整 RAG pipeline；五組核心函式保留 TODO scaffold。
- `week11/生成式AI應用開發_第11週_RAG基礎與文件問答實作教材_教師版.ipynb`：第 11 週 40-cell 教師版，提供 ChromaDB、context、prompt、來源、基本評估與可注入假檢索／假生成的完整參考實作，付費 Responses API 示範預設關閉。
- `week11/week11_rag_app/`：第 11 週正式 Streamlit 文件問答專案，支援 PDF、DOCX、CSV、TXT、MD 前處理、離線／OpenAI embeddings、ChromaDB in-memory 索引、top-k 與分數門檻、受限 context、Responses API 生成、來源片段顯示與基本引用檢查。
- `week12/生成式AI應用開發_第12週_多模態應用_Vision_API與圖片理解實作教材_學生版.ipynb`：第 12 週 40-cell 學生版，主線為圖片 bytes／MIME 驗證、Base64 data URL、Responses API `input_image`、detail 選擇、圖片 prompt、收據／表單 Structured Outputs、錯誤分流與基本評估；四組 helper 練習保留 TODO scaffold。
- `week12/生成式AI應用開發_第12週_多模態應用_Vision_API與圖片理解實作教材_教師版.ipynb`：第 12 週 40-cell 教師版，提供四組練習完整參考答案、離線虛構收據 fixture 與預設關閉的付費 Vision API 示範。
- `week12/week12_vision_app/`：第 12 週正式 Streamlit 圖片理解專案，支援 PNG、JPEG、WEBP、非動態 GIF，提供 8 MB／格式／尺寸／影格驗證、圖片描述、圖片問答、截圖檢查、收據／表單 strict structured output、拒答／未完成分流、隱私與人工覆核提醒。

## 最近工作進度

- 2026-10-13 離開公司前：在本檔最前方保存「回家接續摘要」，整理第5週64-cell雙版的stream=True補強、第8節驗證目的／兩階段操作、第9節Ctrl+C／EOF、驗證腳本與所有離線檢查、真實API／Colab／按鍵未實測、第6週缺Pydantic限制，以及Home_Test／842f212與未提交修改狀態。只更新PROJECT_MEMORY.md，未commit、push、pull、fetch或跨電腦同步；家裡須確認今天工作目錄修改已帶回。

- 2026-10-13 公司接續：依使用者要求，為第5週第9節CLI加入Ctrl+C停止對話的KeyboardInterrupt處理；外層涵蓋input與串流，另處理EOFError，收到中止後結束整個CLI。保留/exit、/reset與單輪錯誤後重試，補終端機／Colab操作區別及兩層例外責任。兩版各64 cells，本次各改一格文字與CLI code，A／B、測試器、付費旗標與CLI預設關閉保留。第5週JSON／AST、雙版對齊、無金鑰／假SDK、五組CLI模擬、原五項離線規則與兩項逾時檢查通過；串流尚未完成時模擬中斷不保存部分回答。未執行真實API、實際按鍵、Colab停止按鈕或試教，模擬KeyboardInterrupt不冒充GUI實測。詳細紀錄與共同驗證腳本已同步。

- 2026-10-13 公司接續：依使用者指示重寫第5週150分鐘雙版第8節，改名「驗證聊天功能：離線程式檢查與真實 API 回答觀察」，補目的、老師／學生任務、假資料與正式函式關係、旗標執行順序、五項行為證據／失敗回查、三輪真實input／回答人工判讀、分階段紀錄與教師帶課提示。新增一格真實測試前說明，兩版由63增至64 cells，原ID／順序、全部code、TODO及預設False保留，固定活動仍15次請求。同步第5週紀錄與共同驗證腳本的指定Markdown新增支援。JSON／AST、雙版對齊、無金鑰／假SDK、一筆假串流、五項離線規則及兩項逾時檢查通過；其他既有未提交修改未動。未執行真實API、Colab、CLI、Notebook雲端顯示或試教，本次未重跑第6週Pydantic檢查。

- 2026-10-13 公司接續：依使用者指示補強第5週150分鐘學生／教師版第6節的`stream=True`入門說明，加入非串流／串流回傳形式、顯示與保存對照，明確說明須讀取事件才可顯示文字、同步迴圈與背景執行的差別，並連回既有片段示範及正式函式。兩版各只修改一格Markdown，63 cells、全部code、TODO、ID及順序不變，固定活動仍15次請求。JSON／AST／配對與假SDK離線檢查通過；未執行真實API、Colab、CLI或試教。詳細內容見第5週修訂紀錄。

- 2026-10-13 離開家裡前已在本檔最前方建立公司電腦接續摘要，整理第1／5／6週現行版本、語音預告刪除決策、第12週尚未開工、驗證範圍、腳本入口與公司接續順序。記錄家裡Home_Test分支與236043e基準；本次僅保存記憶，未提交或推送，跨電腦同步需另外確認。

- 2026-10-13 依使用者指示移除第5、6週150分鐘學生／教師版的語音銜接預告：兩週沒有語音API活動，避免將後續構想混入當週教材。第6週逐段檢視後，Schema版本管理與巢狀會議有本機程式，重試為明訂輸入／回傳與假operation檢查的課後設計任務，均保留；第7／8週App銜接對應本週抽取與驗證成果，保留。另移除學生教材中的「本次不改第七周App或其他週次」修訂作業說明。四份Notebook各維持63／70 cells，所有code、TODO、ID、metadata與Colab／成本設定不變。更新腳本改為移除預告，第6週重建腳本不再加回；驗證腳本支援已提交的環境設定，新增預告缺席檢查。JSON、122格普通Python AST、程式完全未改、離線／假SDK及第6週重建比對通過；未執行真實API或Colab。詳見第5、6週修訂紀錄。本次以此狀態取代10月12日加入語音預告的決策，第1週語音概念與第12週增補規劃仍沿用。

- 2026-10-12 依使用者確認，同步修改第5、6週150分鐘學生／教師版的Colab操作與API設定：第5週改為max_retries=0及%pip；兩週新增API_TIMEOUT_SECONDS=60.0、SDK版本顯示（第6週另含Pydantic），並說明網路等待與串流總時間差異、Secrets授權、runtime重啟後執行順序及付費旗標復原。補簡短STT／TTS銜接，未增加語音API或練習。第5週各63、第6週各70 cells，ID／TODO／其他練習程式保留。四份Notebook共122格普通Python AST、無金鑰順序執行、假SDK初始化、Secrets未授權與逾時檢查通過；第6週既有離線／假API檢查與重建結果比對亦通過。原始教材保留。修改與檢查腳本為scripts/update_colab_runtime_guidance.py、scripts/verify_colab_runtime_guidance.py，第6週重建腳本已同步。詳細紀錄見兩週修訂紀錄；未執行真實OpenAI SDK／API或Colab，60秒及套件版本須於課前實測後調整／固定。此前「第5、6週僅檢視」為歷史狀態，本項為後續完成狀態。

- 2026-10-12 已另存第1週語音增補修訂教材與Marp Markdown／HTML，沿用原版型由21增為23頁；新增STT／TTS與輸入輸出概念、文字Streaming區分、固定示意文字／預錄示範腳本、錯誤修正與學生檢核、語音專題範例及設備調查。教材大綱逐頁對齊23頁；評量統一40／20／25／10／5%，期末至少RAG或Function Calling其中一項。兩份Markdown內容／亂碼、HTML頁數與全部23頁渲染檢視通過，技術地圖頁尾重疊已修正。第5、6週150分鐘雙版僅檢視，JSON／ID／輸出／122格普通Python AST／RUN旗標預設False通過；建議後續補%pip、課前實測版本、Secrets授權、runtime重啟順序及簡短語音銜接，第5週SDK重試設定亦須配合請求上限說明。原始第1週、第5、6週與主課綱未改，沒有產生實際音檔，未執行Colab、真實SDK／API、語音播放或試教。詳見`week01/第01週_語音增補修訂與Colab檢視紀錄.md`；重建來源為`scripts/build_week01_voice_revision.py`。

- 2026-10-12 自行檢查第6周150分鐘修訂雙版並改善：補事件欄位validator，區分解析成功與可用資料；一般prompt／Structured拆兩格獨立旗標，各1次請求；新增A2六項無金鑰契約檢查與參數轉交規格；G檢查原Schema副作用及原五欄保留；補B/C時間、選題及逐欄核對指引。兩版由64增至70 cells（34 Markdown、36 code，35普通Python），原64個ID與順序保留，固定主線仍7次請求。靜態、無金鑰順序、教師離線／假API及新增失敗情境通過；182份原始教材與專案檔案雜湊一致。詳細紀錄與腳本已同步，未執行真實SDK／API、Colab或150分鐘試教。

- 2026-10-12 在家裡電腦的 `Home_Test` 分支依第4、5周原則另存第6周150分鐘學生／教師修訂版，各64 cells（32 Markdown、32 code，含31格普通Python）。採JSON Schema first，G事件Schema引導與A客服抽取必做、B評論／C巢狀訂單擇一；版本管理、巢狀會議與重試移至選讀／延伸。補上TODO型別／回傳／保存規格、deepcopy與Pydantic正式程式對照、拒答／incomplete／failed／空回應分流、客服欄位與摘要驗證、固定三題與人工核對。缺金鑰仍可離線；各真實API旗標置於使用格且預設False，SDK自動重試關閉；主線固定7次請求，作業Schema選讀另1次。雙版JSON、唯一ID、清空輸出、AST、無金鑰順序執行、學生骨架分離、教師本機契約與六項假API活動檢查通過；未呼叫真實API、安裝OpenAI SDK、驗證Colab／教室環境或150分鐘試教。原始第6周及其他週次未改。詳見 `week06/第06週_150分鐘修訂版_修訂與驗證紀錄.md`；重建與離線檢查腳本為 `scripts/build_week06_revision.py`、`scripts/verify_week06_revision.py`。後續第6周修訂在此雙版續改，不自動取代原版。

- 2026-10-06 依使用者最新要求對照第四周精簡第五周細節選讀，兩版由75減為63 cells（36 Markdown／27 code，26普通Python）；刪12個重複或非必要語法cells，保留**request、history副本與reset、usage／假client的新需求說明及A/B任務。已教getattr／or、集合、函式物件／解包改前週回查；基礎環境、字串、型別、迴圈及CLI不另設長選讀，類別整併對照表。保留程式AST一致，靜態／離線順序、配對TODO、教師五項契約與七個活動假API（15次請求）通過，其他教材未變更，未驗證真實API／Colab。本次取代前次「全面展開語法」的呈現方式，講義原則第4項同步改為主動盤點但只補必要新選讀。

- 2026-10-06 已全面盤點第五周150分鐘學生／教師教材的非基礎Python語法：補條件運算式／短路／None、參數預設與例外鏈、生成器／列表與字典生成式、enumerate／餘數／bool與int、print／join／set、tuple回傳／解包、SimpleNamespace／閉包／**kwargs、assert／try-else／JSON副本及CLI／class-self選讀；每組連回正式code，新增4個有註解的離線示範。兩版各75 cells（43 Markdown、32 code），31個普通Python語法與離線順序執行、新示範、教師五項契約及七項假API開關通過，固定真實活動請求數仍15（以假API驗證）；原始版及其他週次保留，未呼叫真實API／Colab／班級試教。後續教材製作必須主動全面盤點語法缺口，已納入講義原則第4項。

- 2026-10-06 第五周150分鐘學生／教師修訂版第一部分新增`**request`細節選讀與有註解的離線參數展開示範，對照create_response建立字典、條件加入previous_response_id及API呼叫；解釋key限制、參數重複及與定義端`**kwargs`收集的差別。兩版各64 cells（36 Markdown／28 code），27個普通Python cells語法與無金鑰順序執行通過，新示範與教師五項離線契約通過；正式函式行為與API請求數不變，原始版保留，未驗證真實API／Colab。

- 2026-10-06 已確認上述「講義製作原則」為後續各週製作與修訂的共同要求，並在教材製作skill入口加入明確讀取／核對指引。第四周150分鐘學生／教師修訂版各72 cells（43 Markdown、29 code），第五周各63 cells（36 Markdown、27 code）；補強文字／程式對照、離線語法示範註解、TODO規格及繳交檢查。第四周A5含items／函式物件／外層版本與內層測試語法選讀；第五周七個真實API旗標移到使用cell，串流示範與B分格，單筆假串流先於五項契約檢查。原始版及其他週次保留。靜態與離線檢查通過；第五周假API固定活動仍15次請求。未執行真實API、Colab或150分鐘班級試教。詳細歷次紀錄見 `week04/第04週_150分鐘修訂版_修訂與驗證紀錄.md`、`week05/第05週_150分鐘修訂版_修訂與驗證紀錄.md`。過去「不修改PROJECT_MEMORY.md」僅描述當時保留原檔的操作，使用者本次已明確要求將原則記入本檔。

- 2026-09-22 已補齊第 2 週 lambda 先備教學：學生／教師 Notebook 各新增 6 cells（現為各 63 cells），於 List／Dict 後加入「3-3 用函式指定排序規則與 lambda」，規劃 10～15 分鐘，依序示範 def、函式傳入與呼叫的區別、sorted／key、降冪與切片，以及 lambda 等價寫法；加入離線使用量排序練習，學生保留 TODO、教師提供完整答案，兩種正確寫法均接受。練習 C 增加銜接提示與 def 對照，明訂字數為字元數；同步學習目標與小結。第 5 週雙版本補 callback 的建立／呼叫時機，第 10 週雙版本補 sort／sorted 差別與 top-k 排序複習。六份 Notebook 的 JSON、唯一 cell ID、亂碼掃描與 130 個普通 Python code cells 靜態語法檢查通過；新增排序範例離線執行、教師練習 C 假 HTTP 資料的排序／缺 body／空列表檢查通過，git diff --check 通過。保留使用者原有第 2 週修改及教師版 18 個已執行或含輸出的 cells；新增 cells 均清空輸出。本次未執行真實 HTTP／LLM API 或 Colab 顯示驗證。

- 2026-09-16 已依課綱與 `$course-material-authoring` 完成第 12 週正式教材：學生版／教師版 Notebook 各 40 cells（18 Markdown、22 code），並建立 `week12/week12_vision_app/`。教學主線為「圖片 bytes → signature／Pillow 本機驗證 → Base64 data URL → Responses API `input_image` → 文字或 strict JSON → 人工核對」，涵蓋圖片描述、圖片問答、截圖理解與收據／表單抽取；圖片 API 使用 `store=False`，但教材明確說明圖片仍會傳送與處理，禁止個資、機密、醫療影像、未授權內容與 CAPTCHA。官方文件已確認 `gpt-5.4-mini` 支援 image input 與 Responses API；App 使用目前 Streamlit 1.63.0 的 `max_upload_size`、`width`、`st.segmented_control`、`st.form` 與 session state 寫法。兩份 Notebook 已通過 JSON、唯一 cell ID、輸出清空、普通 Python AST、學生／教師 TODO 分離與離線順序執行；App 三個 `.py` 可編譯，Pillow signature／動態 GIF／8 MB 邊界、Base64、prompt、假 Responses API request、AppTest、兩種工作目錄的 CLI 設定與伺服器健康檢核通過。這些第 12 週實跑使用現有 Windows／Python 3.14 `.venv`；課堂指定的 Python 3.12 乾淨環境尚未建立。`docs/課堂環境與部署指南.md` 與 `scripts/verify_classroom_environment.py` 已擴充到第 12 週；完整七 App 回歸嘗試在第 9 週因目前 `.venv` 缺少 `python-docx` 中止，第 7、8 週重跑通過，第 7–11 週仍沿用先前 Python 3.12 驗證紀錄。未執行真實 OpenAI Vision API、瀏覽器互動、Colab、Community Cloud 或 macOS／Linux 驗證。

- 2026-09-16 已完成教材檢視第 4 點「固定課堂測試環境與釐清部署路徑」：第 7–11 週六個正式 App 的 requirements 固定直接依賴，基準為 Windows x86_64／Python 3.12.13、Streamlit 1.63.0、OpenAI SDK 2.49.0、python-dotenv 1.2.3、NumPy 2.5.3、pandas 3.0.5、pypdf 6.18.1、python-docx 1.2.0、ChromaDB 1.5.9（各 App 只列所需套件）。新增 `environments/classroom-windows-py312.txt` 完整相依快照、`docs/課堂環境與部署指南.md` 及 `scripts/verify_classroom_environment.py` 離線檢核；第 10 週另有 `requirements-chroma.txt` 選讀安裝入口。六份 README、八份學生／教師 Notebook 的環境段落與第 8 週專題說明書已同步；第 7 週套件練習仍保留學生 TODO。第 9–11 週 file uploader 明訂 8 MB，保留收到檔案後的檢查。更正先前設定位置判斷：Streamlit 1.46 起支援入口程式旁的設定，本次 1.63.0 CLI 實測從 repo 根目錄與 App 目錄均載入各自 `.streamlit/config.toml`，無須搬到 repo 根目錄。完整快照已在新環境重建，六個 App 另各用乾淨環境依自己的 requirements 加快照 constraints 安裝；全部 `pip check` 通過，六個 App × 兩種工作目錄的 AppTest／實際伺服器健康檢查通過；第 9–11 週 reader、8 MB／超限邊界、第 10 週離線搜尋與 ChromaDB 選讀、第 11 週索引查詢／context／來源測試通過。八份 Notebook 維持原 cell 數、ID、清空輸出與 TODO，144 個普通 Python cells 通過 AST 檢查。未在瀏覽器、Community Cloud、Colab、macOS／Linux 實跑，也未呼叫付費 API；Windows 完整快照不可直接視為 Linux 雲端 lock。開課前需按指南完成這些目標環境檢核。

- 2026-09-15 已依教師確認的收費政策修正第 1 週 API 費用說明：Marp 投影片第 15 頁、正式教材 Slide 15 與課綱第十八節均明列 OpenAI API 實際費用由學生自行負擔，課程不提供免費 API 額度；教師開課前公告預估支出與建議上限，學生在第 3 週前確認付款設定，作業與專題另訂使用上限。投影片課後提醒改為先了解帳號與付款設定、付款有困難時提前聯繫教師，移除「需完成儲值」及 Gemini 免費方案替代主線的說法。Marp HTML 已按 Markdown 重新輸出，維持 21 頁；第 15 頁與課後任務頁 PNG 已檢視排版，相關文字掃描與 `git diff --check` 通過。Marp Markdown／HTML 在修改前即為未追蹤檔；未驗證真實帳單或學生帳號，預估金額仍待開課前依當時價格與教學用量公布。

- 2026-09-15 已依教材檢視第 3 點更新第 10、11 週正式 ChromaDB collection 設定：第 10 週學生版／教師版 Notebook 的 ChromaDB preview、第 11 週學生版／教師版 Notebook 的 `build_demo_collection()`，以及 `week10/week10_semantic_search_app/embedding_utils.py` 選讀 helper、`week11/week11_rag_app/embedding_utils.py` 正式索引 helper，均改用 `configuration={"hnsw": {"space": "cosine"}}`；每筆 chunk 的來源仍存於 `metadatas`。兩週 App README 已補設定與安裝後查詢檢核；Claude 參考版本未修改。四份 Notebook 均維持原 cell 數與 ID、清空輸出及學生 TODO，JSON、普通 Python cell AST、兩個 `.py` 靜態編譯及 `git diff --check` 通過。在隔離的 Python 3.12.13／ChromaDB 1.5.9 環境，用兩週無敏感資料範例文件和離線向量，已實跑兩個 App helper 的建 collection、寫入、查詢及來源 metadata，並實跑四份 Notebook 的相關函式；用原向量兩倍查詢仍取得接近 0 的 cosine distance，確認設定生效。未執行 Notebook 全部 cells、完整 Streamlit 瀏覽器流程或付費 OpenAI API；開課前仍需在教室環境安裝並跑 UI。現行 ChromaDB 文件採 `configuration` 範例，但本次沒有測試或宣稱舊 `metadata` 寫法失效。

- 2026-09-15 已依教材檢視第 2 點修正第 8 週正式學生 starter 與教師摘要器 demo 的 Structured Outputs 失敗分流：兩個 `app.py` 均先從 Responses API `output/content` 檢查拒答，再依 `response.status == "incomplete"` 與 `incomplete_details.reason` 區分輸出長度限制、內容過濾及其他未完成原因；明確的其他非完成狀態也不解析部分文字。只有通過上述檢查後才沿用空 `output_text` 與 `json.loads()` 保護。兩份 README 已補錯誤情境對照，學生 starter 原 TODO 保留，教師 demo 仍提供完整摘要器。兩個 App 的 `.py` 靜態編譯、`git diff --check` 與各 10 個假 API 回應分支檢查通過；未呼叫真實 OpenAI API，也未驗證瀏覽器畫面，上課前仍需用測試金鑰確認真實拒答、未完成與成功回應的 UI 顯示。

- 2026-09-15 已將課綱第十八節的新費用估算方式同步到第 1 週：正式 `week01/生成式AI應用開發_第01週教材.md` 的 Slide 15 大綱，及既有 Marp 投影片 Markdown／HTML 的 API 費用頁，均移除固定的新台幣課堂、作業、專題及整學期估算與固定 5 美元建議，改為教師開課前依預計呼叫、輸入／輸出 token 和當時官方價格公告課堂額度，作業與專題另訂上限；投影片採課堂指定低成本模型，並區分只通知的消費提醒與達額停用的硬性上限。教材附官方 Pricing／Spend limits 連結。HTML 已用本機 VS Code Marp CLI 依 Markdown 重新輸出，PNG 渲染共 21 頁，第 15 頁費用頁已檢視排版；三份檔案舊數字／舊模型文字掃描及 `git diff --check` 通過。Marp Markdown／HTML 在修改前即為未追蹤檔，本次未加入 Git；未用真實 API、學生帳號或實際班級用量試算，額度仍需開課前訂定。

- 2026-09-15 已完成教材檢視第 5 點的第二部分：第 3 週正式 Gemini API 入門學生版／教師版 Notebook 的多輪對話段落，依 Google Interactions API 官方文件補明 `previous_interaction_id` 只延續已完成且已儲存的對話內容，`system_instruction` 要每輪重送，以及預設 `store=true` 與 `store=false` 不能使用前次 ID 的取捨；原兩輪範例皆重送相同角色規則，沒有增加 API 呼叫次數。兩版仍各 33 cells、14 code cells，學生版原 TODO 與教師版完整答案分工維持；已通過 JSON、cell ID、清空輸出、普通 Python cell AST、TODO 分離、中文 replacement character 與範例參數靜態檢查。未用真實 Gemini API 或在 Colab 執行，上課前應以測試金鑰驗證兩輪回答與平台端保存設定。

- 2026-09-15 已依教材檢視第 5 點的第一部分，更新課程大綱第十八節 API 與平台費用說明：移除「每位學生約需新台幣 100 至 200 元」的固定課堂練習預算，改為開課前依預計呼叫次數、輸入／輸出 token 用量及當時官方模型單價估算並公布課堂額度，授課期間用 API `usage` 核對並調整預估；作業與期末專題仍另訂上限。本部分僅修改 Markdown 說明，已檢查段落內容與 `git diff --check`；正式額度仍需教師於開課前依實際價格與試跑用量訂定。

- 2026-09-15 已修正第 7 週正式 Streamlit 聊天教材與 `week07/week07_streamlit_app/`：App 的聊天請求現在使用 session state 中最近五輪已完成的 user／assistant 訊息加本輪問題組成 Responses API `input`，每輪明確重送 `instructions`；摘要表單與檔案工具仍保持一次性文字請求。聊天只在回覆完成且非空時一次保存完整訊息配對；串流會辨識 `response.completed`、`error`、`response.failed`、`response.incomplete` 與缺少完成事件的中斷情況，不把部分文字當成正式回答。第 7 週教師版／學生版 Notebook 已同步說明「畫面紀錄不等於模型上下文」、有限 history 與完成事件，兩版仍各 40 cells；學生版新增對應 TODO，教師版提供完整範例；App README 已補雙輪追問、清空及中斷測試步驟。已通過 Notebook JSON、cell ID 唯一性、輸出清空、普通 code cell AST、TODO 分離、`.py` 編譯、`git diff --check`，並以假 Responses API 的 Streamlit AppTest 驗證兩輪前文、串流中斷、清空、非串流模式及摘要一次性輸入。真實 OpenAI API、Colab 顯示與瀏覽器畫面尚未實跑，上課前仍需用測試用金鑰確認模型實際回答與串流行為。

- 2026-08-11 已依 Claude 品質修正版的再次比較，補強第 11 週正式 Codex Notebook 的「檢索層評估」：學生版／教師版仍各維持 40 cells，在既有練習 D 中新增可注入 `retrieve_fn` 的 `evaluate_retrieval()`，以小型測試題檢查預期關鍵字是否被取回，並加入多組 `min_score` 的門檻敏感度觀察；同時保留 `evaluate_rag_answer()` 作為生成層引用檢查，明確區分 Retrieval 與 Generation 的錯誤來源。學生版保留兩個評估函式 TODO，教師版提供完整實作；學習目標、完成檢核與課後任務已同步。`week11/生成式AI應用開發_第11週_RAG_Claude與Codex版比較.md` 已更新 Claude 修正狀態、App 現況及正式整合結果；Claude 參考檔未修改。
- 2026-08-11 已依 `$course-material-authoring` 完成第 11 週正式教材：學生版／教師版 Notebook 各 40 cells，並建立 `week11/week11_rag_app/`。教學主線為「文件前處理 → embeddings → ChromaDB → top-k／門檻 → context → Responses API → 答案／來源／基本評估」，ChromaDB 從第 10 週 preview 提升為正式必要依賴，FAISS 仍留作延伸。所有正式程式註解與 docstring 採繁體中文教學型說明；學生版保留五組練習，教師版無 TODO。已通過 Notebook JSON、cell ID、輸出清空、code cell AST、學生／教師 TODO 分離、中文亂碼、疑似 API key、Python docstring 語言、`.py` 編譯與假 collection 純函式測試。OpenAI Responses API 與 Embeddings API 語法已依 2026-08-11 官方文件確認；正式預設仍採課程既有 `gpt-5.4-mini` 與 `text-embedding-3-small`，並可由環境變數覆蓋。現有 `week11/week11_rag_qa_claude/` 未修改，只視為替代版本。由於執行環境只有 Python 3.14 且禁止連線 PyPI，無法安裝 `chromadb`、`pypdf`、`python-docx`，因此 ChromaDB、文件 reader、Streamlit UI 與付費 API 尚未實跑；上課前應在 Python 3.11 或 3.12 虛擬環境安裝 requirements 後完成測試。
- 2026-08-05 已補齊 Python type hints 先備橋接：第 2 週學生版／教師版 Python 複習教材新增「函式型別註記（Type Hints）快速讀法」，放在預設參數後，說明 `text: str`、`chunk_size: int = 800`、`-> str`、`list[str]`、`dict`、`list[dict]` 與「提示不等於執行期防呆」；兩版目前各 54 cells。第 9 週學生版／教師版新增「快速複習：函式型別註記怎麼讀」，放在文件處理管線後、第一個 reader 函式前，專門解讀 `chunk_by_paragraph(text: str, chunk_size: int = 800) -> list[dict]`，讓 `chunk_text()`、`chunk_by_paragraph()` 與文件報告函式的簽名不再是未說明先備；兩版目前各 36 cells。
- 2026-07-30 已依 `$course-material-authoring` 與課程大綱完成第 9 週正式教材：學生版／教師版 Notebook 各 34 cells，並建立 `week09/week09_document_processor/` Streamlit 配套專案與無敏感資料範例文字。教學主線採「格式路由 → 文字抽取 → 清理 → chunking → 預覽／匯出 → 選擇性 AI 摘要」，明確銜接第 8 週檔案上傳與第 10 週 Embedding。已通過 Notebook JSON、cell ID 唯一性、輸出清空、code cell AST、`.py` 編譯、中文 replacement character、疑似 API key、學生／教師配對、TODO 分離與純函式邊界測試；教師版無待完成 TODO。由於目前 Python 環境未安裝 `python-docx` 等專案依賴，PDF／DOCX／CSV reader、Streamlit 啟動與付費 API 尚未完整實跑，需在安裝 `requirements.txt` 後以測試檔與測試用 API key 驗證。
- 2026-07-31 已完成第 9 週正式教材與 Claude 生成版比較後的小幅吸收：正式 `week09/week09_document_processor/README.md` 補上檔案結構表與 8 MB 上傳限制說明，新增 `.streamlit/config.toml` 將 Streamlit `maxUploadSize` 設為 8 MB，並將 `app.py` 的 sidebar 控制區拆成 `render_sidebar()` 以利教學閱讀；Claude 版 notebook 因文字 cell 使用非標準 `cell_type: "md"`，仍只保留為比較參考，不取代正式教材。
- 2026-08-04 已補強第 9 週正式教材的程式註解與 docstring：學生版／教師版 notebook 以及 `week09/week09_document_processor/app.py`、`document_utils.py` 皆統一採繁體中文教學型註解，補足目的、參數、回傳、可能錯誤、格式路由、編碼備援選項、本機前處理、chunk 中繼資料、Streamlit rerun、secrets、成本與 API 觸發邊界說明；學生版保留 TODO scaffold，教師版維持完整答案。已通過 notebook JSON、cell ID、輸出清空、code cell AST、TODO 分離、中文亂碼、舊英文 docstring 殘留掃描、`.py` 編譯與 `git diff --check`；尚未執行 Streamlit UI、PDF／DOCX 真檔 reader 與付費 API 實測。
- 2026-08-04 依 `week09/生成式AI應用開發_第09週_文件處理_Claude與Codex版比較.md` 再次整合第 9 週教材建議：正式版仍保留 Codex 主線，不用 Claude 版取代；比較檔已校正 Codex 版已有 `.streamlit/config.toml`、正式 docstring 已繁中結構化、TODO 統計應區分 raw TODO 與核心練習任務；正式 notebook 少量吸收 Claude callout 優點，於 OCR/安全、API 成本與進階挑戰處加入醒目提醒；README 快速開始補上 `cd week09/week09_document_processor`。練習 stub 仍保留 `NotImplementedError`，App 友善錯誤處理作為教師補充觀念。
- 2026-07-31 已補強第 8 週正式專題說明書、`week08/week08_midterm_starter/README.md` 與 `week08/week08_midterm_example_summarizer/README.md` 的虛擬環境教學步驟：學生與教師 demo 皆先在專案資料夾建立 `.venv`、啟用環境、升級 pip、再安裝 `requirements.txt`，並在檢核清單與 README 範本中提醒虛擬環境需求；既有 `.gitignore` 已排除 `.venv/` 與 `venv/`，未修改程式邏輯。
- 2026-07-30 已建立專案型 Codex skill：`skills/course-material-authoring/`。技能將本專案長期沿用的教材製作習慣整理為可重複工作流程，涵蓋專案記憶讀取、正式版本選擇、學生版／教師版分離、Notebook 與 Streamlit 教學設計、靜態驗證、秘密保護及完成後同步更新 `PROJECT_MEMORY.md`。詳細慣例置於 `references/conventions.md`，並提供 `agents/openai.yaml` 介面資訊。原預定放入 `.codex/skills/`，但該目錄在目前環境為唯讀，因此改放可版控的專案根目錄 `skills/`；官方 `quick_validate.py` 因環境缺少 PyYAML 未能執行，已改做 frontmatter、必要欄位、reference、metadata、預設 prompt 與 TODO 殘留的等價結構檢查。
- 進度紀錄點：第 6 週正式 40-cell 教師版與學生版已生成並完成 Claude 版本比較；正式版保留為主線，吸收 Claude 版的 Pydantic 欄位驗證表格、巢狀 `MeetingMinutes` 範例、`extract_structured()` wrapper 與 refusal handling 提醒。
- 第 6 週正式版與 Claude 生成版比較結論：正式版教學節奏較完整，適合保留 JSON Schema first；Claude 版較偏 Pydantic-first，只吸收適合 App 開發的補強點，不取代正式教材架構。
- 第 6 週學生版仍保留 TODO 分離；教師版提供完整答案。兩版皆維持 40 cells，付費 API cells 預設關閉。
- 2026-07-21 已針對實際閱讀時不易理解的第 6 週內容補強說明：學生版與教師版皆新增「輸入文字／輸出規格／程式檢查」三層讀法、JSON Schema 閱讀順序、array `items` 巢狀資料提示、`(ok, result)` 錯誤處理心智模型、JSON Schema 與 Pydantic 對照表、課堂練習解題順序，以及關鍵 code cell 的 API 參數、refusal parsing、validation、Pydantic wrapper 與 retry 註解；兩版仍維持 40 cells、輸出清空、學生版 TODO 分離、教師版無 TODO。
- 2026-07-21 依需求再次加深第 6 週 code cell 教學註解：學生版與教師版皆補強 setup fail-fast、API key 安全、`structured_response()` 職責分層、`text.format` 欄位契約、`response.output_text` 解析順序、一般 JSON prompt 的不穩定觀察、schema 欄位設計理由、巢狀 JSON 閱讀順序、程式端驗證同步、`(ok, result)` App 錯誤分流、批次測試結果判讀、schema registry 版本管理、`responses.parse()` / Pydantic 資料合約、wrapper 錯誤處理，以及練習 A/B/C 的解題提示；學生版仍只保留 TODO 引導，不填入教師版答案。
- 2026-07-28 已補強第 2 週學生版與教師版 Python 複習教材：在例外處理與 API key 管理之間新增 `with` / context manager 小節，說明 `with open(...)` 的自動關閉、`with st.sidebar:` / `with st.form(...)` 的 Streamlit 容器心智模型，以及其作為第 7 週 Streamlit 與第 9 週文件處理的先備橋接；2026-08-05 另補 type hints 快速讀法；兩版目前各 54 cells。
- 2026-07-21 參考 `comment_sample.txt` 的註解範例，將第 6 週正式學生版與教師版的核心 helper 改成教學型 docstring 與分段註解：`structured_response()`、`_read_attr_or_key()`、`get_refusal_reason()`、`parse_output_text()`、`print_json()`、validation helpers、`extract_structured_safe()`、`run_event_batch_tests()`、schema registry helpers、`parse_with_pydantic()`、`extract_structured()`、`extract_with_retry()`，以及 Pydantic class 皆補上用途、情境、參數、回傳、可能錯誤與「情況一／情況二」式流程說明；學生版仍只保留 TODO 引導。
- 2026-07-22 依需求補強第 6 週 Pydantic 說明：學生版與教師版皆在「Schema 改版紀錄與進階路線」加入 ReviewInsight / MeetingMinutes 的實際 schema 版本演進例子，明確連到後續 Pydantic code cell；「Pydantic 進階」章節新增 Pydantic 是資料驗證與資料模型工具、不是 AI 模型或資料庫的介紹，並補上最小 class 範例、JSON Schema / Pydantic 對照、BaseModel / Field / Literal / Optional / list[Model] / ValidationError 用途，以及讀下一個 code cell 的三層讀法。
- 2026-07-22 補第 6 週 schema registry 實際取用範例：學生版與教師版皆在 `get_schema(registry, name)` 定義後呼叫 `get_schema(schema_registry, selected_schema_name)`，列印 registry key 與 `selected_schema["properties"]` 欄位，避免 helper 只被定義但未示範用途；已修正 raw schema 沒有 `name` / `schema` 外層 key 的錯誤。
- 2026-07-22 補第 6 週錯誤測試範例：學生版與教師版皆在「安全解析與錯誤處理」新增不呼叫 API 的 `FakeResponse` 測試，涵蓋不是 JSON、沒有 `output_text`、模型拒答；在「批次測試」新增本機 validation cases，涵蓋正確資料、缺少 required 欄位 `owner`、多出不允許欄位 `status`，避免教材只示範成功案例。
- 第 7 週教材已依課程大綱改為「Streamlit Web App 入門」，不是 Git 主題；現有 `week07/生成式AI應用開發_第07週_Git實作教材.md` 保留作為 GitHub Desktop、GitHub 與 Streamlit Community Cloud 部署補充。
- 第 7 週正式教材採 notebook 作為教材與步驟說明，實作成果改為本機 `week07/week07_streamlit_app/` 專案；學生需在 VS Code 中執行 `streamlit run app.py`。
- 第 7 週 notebook 與 `week07/week07_streamlit_app/README.md` 已補上銜接對照表，明確標示每個 notebook 章節對應到 VS Code 專案中的 `app.py`、`requirements.txt`、`.env.example`、`.gitignore`、`README.md` 與 Streamlit 功能區塊。
- 2026-07-22 已補強第 7 週正式學生版與教師版 notebook 的 Streamlit 概念導入：學習目標與三堂課流程改為明確包含「Streamlit 是什麼」；第 1 節新增 Streamlit 是 Python Web App 框架、為何需要它、Notebook / Colab 與 Streamlit Web App 差異、`streamlit run app.py` 最小範例、rerun 心智模型、`st.session_state`、`.env` / `st.secrets` 與部署安全的說明。正式版仍維持 notebook 講解搭配 `week07/week07_streamlit_app/` VS Code 專案。
- 2026-07-28 已補強 `week07/week07_streamlit_app/app.py` 的教學型註解與 docstring：說明 Streamlit rerun 心智模型、`st.session_state` 聊天紀錄、`.env` / `st.secrets` 安全讀取、OpenAI Responses API 一次性與 streaming 呼叫、`st.write_stream()` 回傳完整字串、表單避免昂貴 API 重複觸發，以及檔案上傳的 UTF-8 解碼與輸入長度控制；未改變 app 行為。
- 2026-07-15 已同步 Codex 長期記憶更新：第 7 週教材定位、notebook / VS Code 專案雙軌銜接、40-cell 狀態、TODO 分離與 Responses API + Streamlit streaming 主線。
- 2026-07-21 已整合 Claude 第 8 週規劃與正式課程建議：第 8 週定位為「期中個人小專題」整合週，不新增大量 API；主教材優先產出 `week08/生成式AI應用開發_第08週_期中個人小專題_專題說明書.md`，再建立正式命名的 `week08/week08_midterm_starter/` 與教師 demo `week08/week08_midterm_example_summarizer/`，不使用 `_claude` 命名；starter 應延續第 7 週 Streamlit 專案結構與 helper，並保留學生 TODO。
- 2026-07-21 已生成第 8 週正式教材：專題說明書、學生 starter 與教師摘要器 demo。兩個 Streamlit 專案皆包含 `app.py`、`requirements.txt`、`.env.example`、`.gitignore`、`README.md` 與 `.streamlit/secrets.example.toml`；程式註解依第 5、6 週準則補上用途、情境、參數、回傳、API 流程、錯誤處理、輸入限制、secrets 安全與 structured output 設計說明。
- 2026-07-28 已依 Week 7 註解風格補強第 8 週正式程式檔：`week08/week08_midterm_starter/app.py` 與 `week08/week08_midterm_example_summarizer/app.py` 加強專題定位常數、JSON Schema 資料合約、`strict` structured output、API key fail-fast、表單/按鈕觸發 API、檔案上傳文字來源規則、streaming 加分定位、結果 UI 與錯誤分流的教學註解；`_claude` 參考副本未修改。
- 2026-07-21 已建立 `week01/` 到 `week08/` 週次資料夾，並將所有根目錄 `生成式AI應用開發_第NN週...` 教材檔與 `week07_...`、`week08_...` companion project 資料夾移入對應週次資料夾；之後引用正式教材請使用 `weekNN/...` 路徑。
- 2026-07-21 依 Claude 版第 8 週教材比較結果，已將正式 Week 8 吸收補強：說明書明列「真 structured output」硬性要求與 API key 外洩紅線；`week08/week08_midterm_starter/` 補 optional `stream_ai()` helper、快速開始指令與安全紅線；`week08/week08_midterm_example_summarizer/` 補 `.txt` / `.md` 檔案上傳與 optional streaming 摘要示範；`week08/生成式AI應用開發_第08週_期中個人小專題_內容規劃.md` 也已同步修正命名決策與 structured output 主線說法。正式 Week 8 仍保留 JSON Schema + `strict` 作為正式主線，Pydantic 只列為進階選項。

- 歷史紀錄點：第 4、5 週教材已完成建立、Claude 版本比較與優點整合，之後已接續完成第 6 週教材。
- 已比較第 4 週 40-cell 教師版與 Claude 生成版本，決定保留 40-cell 實作教材為主線，吸收 Claude 版的參數化函式與 prompt 並排比較優點。
- 第 4 週教師版與學生版已同步改良：補強 API key preflight、API 錯誤處理、`compare_prompts()`、摘要／分類／改寫／問答參數化、分類契約與字數檢查，以及預設關閉的批次付費測試。
- 第 4 週教師版保留完整答案與 baseline 觀察提示；學生版只在客服分類、初學者改寫與課程規定問答保留 TODO，兩版共用 cell 已對齊。
- 第 5 週教師版與學生版已新建完成，檔名採 `課程名稱_第NN週_主題實作教材_教師版／學生版.ipynb`，兩版皆為 40 cells。
- 第 5 週已完成多輪對話、手動 history、有限 context、簡易記憶、usage、reset、Streaming events、串流聊天 session、console chatbot 與三組練習。
- 第 5 週已依 Claude 版本的優點再次補強：學習目標改為「能力／後續應用」對照表、加入 `history_size()`、預設關閉的 `max_turns=1` 遺忘實驗，以及 Streaming 部分輸出的內容審核提醒；教師版與學生版維持 40 cells 且 TODO 分離不變。
- 第 5 週最終驗證結果：教師版與學生版皆為 40 cells、40 個唯一 cell IDs、26 個 Markdown cells、14 個 code cells，靜態語法與 JSON 解析通過，無執行輸出；教師版無 TODO，學生版只保留封面說明與原訂三組練習 TODO。
- 2026-07-21 參考 `comment_sample.txt` 的註解範例，將第 5 週正式學生版與教師版的核心聊天與 streaming 程式改成教學型 docstring 與分段註解：`create_response()`、`history_size()`、`MinimalChatSession`、`ResponseChatSession`、`stream_response()`、`StreamingChatSession`、`run_console_chat()`、`CourseAdvisorSession`、`ask_with_chunk_count()`、`WindowedMemoryChat`、`run_chatbot_smoke_test()`、`run_forgetting_experiment()` 皆補上用途、情境、參數、回傳、可能錯誤與「情況一／情況二」式流程說明；學生版仍只保留 TODO 引導。實際第 5 週檔案目前為 42 cells，這次保留既有 cell 結構不強行改回舊紀錄的 40 cells。
- 第 4、5 週的付費 API cells 尚未實際執行；目前已完成 JSON、cell ID、靜態語法、TODO 分離、教師／學生對齊與中文亂碼檢查。
- 第 4、5、6 週的付費 API cells 尚未實際完整執行；可先將學生版上傳 Colab 做顯示與實際 API 測試。

## 已完成的重要決策

- 第 2 週定位為 API 開發前的 Python 快速複習，內容包含函式、f-string、list / dict、type hints、JSON、例外處理、API key 管理與公開 API 呼叫。
- 第 2 週已加入 `with` 語法橋接，採入門說明即可：把它視為「縮排內程式在特定情境中執行，離開後自動收尾」，用 `with open(...)` 示範檔案自動關閉，並預告後續 Streamlit 的 `with st.sidebar:` / `with st.form(...)` 容器用法；不需在第 2 週深入 `__enter__()` / `__exit__()`。
- 第 2 週已分成學生版與教師版；學生版不直接提供主要練習答案。
- 第 2 週第六節已補上 Colab Secrets、環境變數設定、PowerShell、`setx`、macOS / Linux `export` 等 API key 設定方式。
- 曾發生 Colab / Windows 編碼流程造成中文被寫成大量 `?` 的問題；目前 notebook 需用 JSON Unicode escape 格式輸出以降低風險。
- 第 3 週 OpenAI API 版本主線使用 Responses API：`client.responses.create()` 與 `response.output_text`。
- 第 3 週 OpenAI API 預設模型已由 `gpt-5.5` 改為 `gpt-5.4-mini`，並保留 `OPENAI_MODEL` 環境變數覆蓋機制。
- 第 3 週 OpenAI API 版本已補上多輪對話示範：使用 `previous_response_id=response1.id` 延續上一輪 Responses API 對話。
- 第 3 週第十節已補強為三題：練習 A「Python 作業批改助教」、練習 B「usage 與費用估算」、練習 C「自由設計角色與 instructions」。
- 第 3 週另產生 Gemini API 與 Claude API 版本，用於跨平台比較。
- Gemini 版本使用 `google-genai`、`GEMINI_API_KEY`、`client.interactions.create()`、`system_instruction`、`interaction.output_text`、`previous_interaction_id`。
- Claude 版本使用 `anthropic`、`ANTHROPIC_API_KEY`、`client.messages.create()`、top-level `system`、`message.content[0].text`，並強調 Claude Messages API 每次需送出完整 messages history。
- 第 3 週三個平台的多輪對話比較：OpenAI 使用 `previous_response_id`，Gemini 使用 `previous_interaction_id`，Claude 送出完整 `messages` history。
- 第 3 週 OpenAI / Gemini / Claude 的學生版與教師版已做 markdown text cell 視覺美化：標題加入少量 emoji，學習任務、安全提醒、課堂練習與成本提醒加入 HTML 提示框。
- Colab 對 markdown cell 的 CSS `style` 支援不穩定；若要讓文字顏色更容易顯示，優先使用 `<font color="..."><b>文字</b></font>` 標示重點詞。
- 第 4 週 Prompt Engineering 為 OpenAI 主線（依課程大綱，不再做三平台版本），延續第 3 週的 Responses API 與 `ask_ai_safe(user_input, role=...)`（role 即 instructions/system prompt）。
- 第 4 週涵蓋：system prompt/角色設定、任務拆解、輸出限制與格式控制、few-shot（用 role/content 清單放範例對）、prompt 測試（`compare_prompts()`），實作 `summarize` / `classify` / `rewrite` / `answer_question` 四大功能。
- 第 4 週 `answer_question` 採「只依參考資料回答、找不到就說找不到」設計，作為第 11 週 RAG 的雛形。
- 第 4 週學生版將四大功能函式與三題課堂練習（A 會議記錄整理、B few-shot 垃圾郵件分類、C 選做 prompt 測試）保留 TODO；示範用的 demo cell（第二～六節）兩版皆完整可執行。
- 第 4 週沿用第 3 週 markdown 風格與 emoji/HTML 提示框；沿用預設模型 `gpt-5.4-mini`（`OPENAI_MODEL` 可覆蓋）。
- 第 4 週「實作教材」兩版已重建為 40 cells，包含三小時流程、baseline 對照、Prompt 五元素、`instructions` / `input` 分工、Markdown / XML 分隔、任務拆解、few-shot、四種應用、固定案例測試、版本紀錄、完成檢核與課後任務。
- 第 4 週「實作教材」學生版的客服分類器、初學者改寫器與課程規定問答保留 TODO；教師版提供完整答案。
- 第 4 週「實作教材」兩版已通過 JSON 解析、40-cell 數量、cell ID 唯一性、code cell 靜態語法、關鍵章節、保存輸出、中文問號亂碼與 TODO 分離檢查；付費 API cells 尚未實際執行。
- 未依本次需求修改原有 35-cell 正式版與檔名含 `Claude生成` 的副本；它們與 40-cell「實作教材」版本並存。
- 第 5 週延續 OpenAI Responses API 主線，涵蓋獨立請求、`previous_response_id`、手動 `user` / `assistant` history、有限對話視窗、簡易重要事實記憶、usage、reset 與 Streaming。
- 第 5 週 Streaming 使用 `stream=True`，處理 `response.output_text.delta`、`response.completed` 與 `error`；只有完成事件後才更新 response ID 與正式 transcript。
- 第 5 週提供 `ResponseChatSession`、`StreamingChatSession`、console chatbot、`WindowedMemoryChat` 與 guarded smoke test；互動式 `run_console_chat()` 預設註解，延伸付費練習預設關閉。
- 第 5 週 context 管理同時用 `history_size()` 觀察訊息／字元規模、用回應 `usage` 判讀實際 token，並提供預設關閉的 4-request 遺忘實驗；Streaming 章節明列部分輸出較難審核，正式應用需有審核與中止策略。
- 第 5 週學生版的課程諮詢 Session、delta 計數器與最近 N 輪記憶保留 TODO；教師版提供完整答案。
- 第 5 週兩版已通過 JSON 解析、40-cell 數量、cell ID 唯一性、code cell 靜態語法、教師／學生共用 cell 對齊、關鍵 API 字串、中文亂碼與 TODO 分離檢查；付費 API cells 尚未實際執行。
- 第 6 週延續 OpenAI Responses API 主線，先教 `text.format` + `json_schema` + `json.loads()`，再補充 Pydantic `client.responses.parse()`；不採 Claude 版 Pydantic-first 作為主線。
- 第 6 週 Structured Outputs helper 已加入 refusal / 空 `output_text` 檢查，避免模型拒答時直接 `json.loads()` 或寫入資料庫。
- 第 6 週 Pydantic 補強欄位驗證技巧表格、`ReviewInsight`、`ActionItem`、`MeetingMinutes` 巢狀模型、`parse_with_pydantic()` 與 App 可重用的 `extract_structured()` wrapper。
- 第 6 週學生版的 `ReviewInsight`、客服訊息 JSON Schema、收據資料 Pydantic 與 retry wrapper 保留 TODO；教師版提供完整答案。
- 第 6 週教材後續若再修訂，應保留目前新增的可讀性橋接：先用三層讀法定位每段程式，再用 schema 欄位規格、array `items`、Pydantic class 對照與程式端驗證說明輔助學生閱讀。
- 第 7 週延續 OpenAI Responses API 主線，Streamlit App 範例使用 `client.responses.create()`、`stream=True`、`response.output_text.delta`、`st.write_stream()`、`st.chat_input()`、`st.chat_message()`、`st.session_state` 與 `st.secrets`。
- 第 7 週聊天採第 5 週已教過的「手動有限 history」而非平台端 response 串接：`st.session_state.messages` 只保存已完成的訊息配對，API 請求帶入最近五輪，清空紀錄即開始新對話；streaming 必須確認完成事件才正式保存回答。
- 第 7 週學生版 TODO 保留在 API key helper、OpenAI helper、session state、Chat UI、streaming、sidebar、表單、檔案上傳、README 與期中小專題規劃；教師版無 TODO。
- 第 8 週正式採「專題說明書 + 學生 starter + 教師 demo」而非 notebook pair；學生 starter 保留 TODO 作為專題改造入口，教師 demo 只提供一個完整摘要器作為展示與完成度參考，避免學生直接複製多個完整答案。
- 第 9 週回到 Notebook 學生／教師雙版本並搭配 VS Code Streamlit 專案。文件抽取、清理與 chunking 採本機確定性處理；AI 摘要為使用者主動觸發的後段選項。基礎 chunking 先用字元滑動視窗與 overlap 建立可測試的心智模型，段落優先切割列為必做練習；第 9 週會先複習第 2 週 type hints 讀法，再進入 `chunk_text()` 與 `chunk_by_paragraph()`；Embedding、向量資料庫與語意搜尋留到第 10 週。
- 第 10 週正式教材已建立 Notebook 學生／教師雙版本並搭配 `week10/week10_semantic_search_app/` Streamlit 專案。主線採 `list[dict]` + NumPy + cosine similarity 建立最小語意搜尋索引，先讓學生看懂 embedding、query embedding、chunk embedding、metadata 與 retrieval 排序，再把 OpenAI Embeddings API 作為主動開啟的付費模式。已補入 ChromaDB preview 選讀 cell，示範 `EphemeralClient()`、`collection.add()`、`collection.query()` 與 metadata 查詢結果整理；但 ChromaDB 與 FAISS 仍不作為第 10 週必要依賴，Claude 生成版保留為 ChromaDB-first 參考資料。
- 第 11 週正式教材以 ChromaDB 作為必要向量資料庫，集中教 Retrieval、context 組合、來源引用、證據不足拒答與基本評估；使用 `EphemeralClient()` 避免持久化設定干擾三小時課堂。App 的索引與生成分成兩個明確操作，並以 session state 保存索引與最後回答；文件內容一律視為不可信任資料。FAISS、持久化索引、hybrid search、reranking 與語意型評估留到自主學習或進階 RAG。
- 第 12 週回到 Notebook 學生／教師雙版本並搭配 `week12/week12_vision_app/`。正式主線使用 Responses API `input_image` 與 Base64 data URL，不另走舊版 Vision 專用端點；本機先依 signature 與 Pillow 驗證格式、尺寸、像素量與非動態 GIF，再由表單按鈕觸發 API。一般圖片回文字，收據／表單沿用第 6 週 JSON Schema strict structured output；detail 只提供 `auto`、`low`、`high`，教學上強調成本與品質需依模型／圖片實測，且所有文字、數字、計數與重要決策都要人工回看原圖。

## 講義製作原則（2026-10-06確認，後續製作與修訂必須沿用）

適用本專案各週Notebook、實作講義與學生／教師教材。開始工作時先讀本節，規劃與交付前逐項核對；使用者當次明確指示優先。第四、第五周150分鐘修訂版為本次做法的參考，應依各週目標調整，不機械複製題型或cell數量。

1. **先確認課程銜接與時間安排。** 檢視前周先備、本周目標、後續應用與實際教材；150分鐘包含講解、示範、實作、除錯與討論，明確區分必做、擇一、選讀與延伸，不把所有內容列為必做。
2. **依理解與操作順序編排。** 採「概念→完整示範→引導練習→學生實作→結果檢查→反思」；新概念先解釋再使用，練習緊接相關主題。完整示範不依賴學生尚未完成的TODO；若有依賴，須明確標示先備及可用替代示範。
3. **文字cell與code cell緊密對應。** 程式前交代目的、輸入、回傳值、資料流與責任；程式後交代預期結果、判讀與常見錯誤。長程式依責任拆格，維持清楚的定義與執行順序，不為湊數增加cells。
4. **語法／細節選讀必須連回正式程式。** 新增或修訂教材時主動盤點兩版所有code cells中的非基礎Python語法，先對照前週實際教材確認已教內容；只有本週新出現、對完成核心任務有必要且難以從簡短註解理解的語法才新增選讀，不等使用者逐一指出。已教語法以一兩句用途提示或前週回查處理，基礎語法不另加長選讀；共用語法集中解釋，避免每種語法都變成獨立選讀或小示範。 指明對應函式、變數與原程式片段，提供「離線小示範→正式程式」對照、逐步讀法、預期觀察與限制；讀完能回到指定code cell理解用途。不要只孤立介紹Python語法，也不要用選讀示範揭露整題學生答案。
5. **程式註解解釋目的與原因。** 使用繁體中文，說明區塊責任、API與資料流、函式傳入／執行時機、狀態更新與錯誤處理。語法選讀配套code cells也必須有註解，標明正式程式的對應位置；避免只翻譯明顯語法或只在文字cell解釋。
6. **每項TODO都有具體規格。** 列出情境、已提供內容、學生負責項目、輸入型別、回傳值、結果保存變數、執行順序與完成條件；編號與說明逐項對應。指出哪些helper、資料及固定測試器不需修改。區分return、print、回傳物件與副作用，避免學生只顯示結果卻未保存。
7. **學生版與教師版同步製作。** 同章節、活動、程式責任及執行順序；學生版保留必要骨架、提示與TODO，教師版提供完整實作、預期結果及判讀標準。共用helper與固定測試器直接提供，練習集中在本周學習目標；未完成處明確提示，不以空值冒充完成。
8. **實驗與檢查條件明確。** 比較時固定資料與規則，指出操弄因素，測試題不混入few-shot範例。區分格式／標籤合法、答案正確、契約錯誤與API／回應失敗；不預設few-shot一定改善，也不以偶然回答證明記憶或reset。說清楚程式檢查、人工核對與測試限制。
9. **執行開關放在使用位置。** 真實API旗標與對應if操作放在同一code cell，預設False；同格標示先備、開啟方式與請求數。不同活動可獨立開啟與重跑，避免集中在環境cell宣告。互動CLI預設不啟動，先提供離線示範與檢查；新增解說不應無故增加付費呼叫。
10. **驗證、繳交與紀錄一致。** 列明交件、實際input／輸出、測試證據與反思；交付前檢查JSON、唯一ID、輸出、語法、執行順序、版本分工及必要的成功／失敗行為。區分靜態、離線、真實API、Colab與試教，未執行項目明確標記；假回應不能充當真實成果。保留原始教材，首次修訂另存，後續在使用者指定修訂版繼續修改；同步修訂紀錄及本專案記憶，不自動改動其他週次。

### 程式教材簡化原則（2026-10-19使用者確認，後續設計與修改預設沿用）

1. **以單元觀念與課堂理解為優先。** 保留學習目標，減少不必要的語法與程式架構負擔；不能只加長講稿或註解來補救複雜程式，也不能只把複雜度藏到helper。簡化不等於刪掉必要驗證。
2. **範例短小、前置需求少且明確。** 本機範例盡量自帶必要匯入與資料，可在乾淨環境獨立執行；必要時允許短小重複，避免為共用而跨多格、多層函式回查。每個活動標明要先跑哪幾格，不讀無關單元或上一個付費活動的結果。
3. **先直線資料流，再視需要整理函式。** 優先使用普通變數、dict/list、for與直接API呼叫，呈現輸入→規格→處理→檢查→結果；只引入對本單元必要的函式與類別。假client、依賴注入、通用safe wrapper、巢狀測試器與多層(ok,result)不作為一般課堂主線；完整測試可放教師驗證腳本。
4. **一個範例聚焦一項觀念，沿用熟悉情境做對照。** 不把新語法、測試框架與新領域同時引入。不同工具先各自介紹，再於適當位置用相同資料做完整短程式對照，例如N1活動Schema→M1/M2→N2同資料Pydantic。對照範例可完整提供，不一定再加TODO或API。
5. **操作與結果直接可見。** 程式前說明目的、輸入與操作順序；程式後說明預期結果、失敗回查與證據限制。學生TODO集中在欄位、限制、簡單規則及結果判讀，避免要求接框架。資料與錯誤分開保存，型別與責任清楚；失敗重跑不沿用舊成功資料。
6. **維持必要安全與證據邊界。** 拒答、未完成、解析與欄位失敗不可冒充成功；格式合格仍須查原文。付費預設False並就地標明先備與次數；手寫fixture、假回應與真實模型成果分列，不以離線通過替代真實API、Colab或試教。
7. **文件結構與雙版一致。** 每個標題各自起始一個text cell，相關內文跟隨該標題，前例判讀不混入下一節；方便Colab目錄定位。學生／教師Notebook、Markdown、導讀、格號與重建來源同步，保留原教材與學生TODO，不能只改教師版。

後續交付自查：學生能否在少量相鄰格內理解資料流，不必追蹤架構？是否聚焦單元觀念？是否知道改哪裡、傳入什麼、回傳／保存什麼、依序執行哪格、如何證明完成？選讀是否指出正式程式位置？API開關是否緊鄰活動？教師答案與學生規格是否一致？標題是否各自起始文字格？

## 編輯與驗證原則

- 2026-07-21 已新增專案層 `.codex/config.toml`，預設 `sandbox_mode = "workspace-write"`、`approval_policy = "never"`，目標是減少教材修改流程中的重複確認；此設定主要影響之後從本 repo 開啟的新 Codex session，且仍受系統、管理政策與高風險操作限制。
- 修改 notebook 時，優先用 Python `json` 模組讀寫 `.ipynb`。
- 輸出 notebook 時使用 `json.dumps(..., ensure_ascii=False, indent=1)`，保留可讀的繁體中文；寫入後必須重新解析 JSON 並檢查常見亂碼特徵。
- 修改學生版時，保留 TODO，不要把教師版完整答案貼回學生版。
- 修改教師版時，可保留完整答案與課堂示範程式。
- Codex 之後生成的正式教材檔案、專案資料夾與範例資料夾一律不加 `_claude` 或 `Claude生成` 後綴；這些後綴只保留給既有 Claude 產出的參考檔案，不用在 Codex 新產出上。
- 之後生成或修改教材中的程式碼時，都要加入適當註解：用註解說明區塊目的、API 呼叫、狀態管理、錯誤處理與安全注意事項；避免逐行解釋顯而易見的語法。
- 每次生成或修改完某一週教材後，必須同步更新本檔的教材狀態、最近工作進度、重要決策或下一步建議，避免專案記憶落後於實際檔案。
- 第 3 週 notebook 的 markdown 風格已採用少量 emoji、HTML 提示框與 `<font color>` 重點標籤；後續新增章節時可沿用此風格，但避免過度使用顏色。
- 每次修改 notebook 後，至少檢查：
  - JSON 可正常解析。
  - code cell 靜態語法檢查通過。
  - 沒有大量 `?` 亂碼 cell。
  - 學生版主要練習仍保留 TODO。

## 模型與環境變數

- OpenAI 版本預設模型：`gpt-5.4-mini`，可用 `OPENAI_MODEL` 覆蓋。
- Gemini 版本預設模型：`gemini-3.5-flash`，可用 `GEMINI_MODEL` 覆蓋。
- Claude 版本預設模型：`claude-haiku-4-5`，可用 `CLAUDE_MODEL` 覆蓋。
- 若任一預設模型在上課帳號不可用，課前改成實際可用模型。

## 下一步建議

- 第5、6週150分鐘雙版已完成Colab操作修訂；課前在新的Colab runtime驗證安裝、Secrets授權／重啟、一般與串流回應及逾時處理，記錄OpenAI SDK／Pydantic版本後固定安裝指令，依實測調整60秒設定。
- 優先檢視第6周150分鐘修訂版的G、A與B/C擇一流程；以教學帳號在Colab確認套件安裝、模型可用性、真實欄位／分類／金額與授課時間。固定假回應只驗證程式，不替代真實模型成果；原始版保留供比較。
- 實際上傳第 3 週學生版到 Colab 測試顯示與 API 執行。
- 比較 OpenAI、Gemini、Claude 三版的 API key、client、輸入格式、回應欄位與多輪對話差異，整理成一頁對照表。
- 產生第 3 週投影片或講義版 Markdown。
- 上傳第 4 週學生版到 Colab 測試顯示與 API 執行。
- 產生第 4 週投影片或講義版 Markdown。
- 上傳第 6 週學生版到 Colab 測試顯示，並實際執行 Structured Outputs 與 Pydantic parse API cells。
- 產生第 6 週投影片或講義版 Markdown。
- 上傳或本機開啟第 7 週教材，以測試用 API key 啟動 `week07/week07_streamlit_app/`，用兩輪追問、清空紀錄、串流／非串流切換確認真實 Responses API 行為與畫面顯示；假 API AppTest 已通過，但尚未代替真實 API 與瀏覽器測試。
- 第 8 週教材已完成初版；上課前可實際設定測試用 `OPENAI_API_KEY`，分別執行 `week08/week08_midterm_starter/` 與 `week08/week08_midterm_example_summarizer/` 的 `streamlit run app.py`，確認 API 回應、structured output 與畫面顯示符合預期。
- 安裝 `week09/week09_document_processor/requirements.txt` 後，以文字型 PDF、掃描 PDF、含表格 DOCX、UTF-8／CP950 CSV 各做一次 reader 與錯誤訊息測試；再啟動 Streamlit，確認 chunk 參數、預覽、JSON 下載及按鈕式 AI 摘要。付費 API 測試需使用測試用 key，並檢查摘要是否只根據抽取文字。
- 安裝 `week10/week10_semantic_search_app/requirements.txt` 後，先用 `sample_data/ai_course_faq.md` 跑離線索引與 top-k 搜尋，再使用測試用 `OPENAI_API_KEY` 關閉離線模式測試真實 Embeddings API；若要示範 ChromaDB preview，在 App 目錄安裝 `requirements-chroma.txt`；Notebook 選讀安裝已固定 ChromaDB 1.5.9。上課前應確認 chunk 大小、overlap、top-k 與分數門檻的示範問題都能產生可解釋結果。
- 依 `docs/課堂環境與部署指南.md` 使用 Python 3.12 與固定套件環境，先用 `sample_data/course_handbook.md` 測試離線 embedding、ChromaDB 建索引、文件內有答案／無答案／提示注入三種問題，再用測試用 `OPENAI_API_KEY` 實跑 OpenAI Embeddings 與 Responses API。確認不同 top-k、最低分數與 context 上限下，回答中的 `[來源 n]` 能對應到 UI 顯示的實際 chunk；完成後再評估 Streamlit Community Cloud 的 ChromaDB 安裝與記憶體限制。
- 在 Python 3.12 的全新虛擬環境安裝 `week12/week12_vision_app/requirements.txt`，執行 `sample_data/create_demo_receipt.py` 後測試圖片描述、圖片問答、截圖檢查與收據／表單抽取；用清楚圖片、小字／模糊圖片、圖片沒有答案與超限圖片核對錯誤分流。再以測試用 `OPENAI_API_KEY` 檢查真實 Vision 回應、structured output、detail 差異與 usage，並於 Colab、瀏覽器及 Community Cloud 驗證；全程只用無敏感資料。
