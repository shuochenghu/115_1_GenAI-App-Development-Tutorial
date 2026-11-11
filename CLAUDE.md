# CLAUDE.md

115學年度上學期「生成式AI應用開發」16週課程教材（繁體中文）。主線：Python、OpenAI API、Colab、Streamlit。回覆使用繁體中文。

## 開工前

- 先讀`PROJECT_MEMORY.md`最前面的接續摘要與「講義製作原則」。它由Codex維護，是專案現況的權威來源；`PROJECT_MEMORY_claude.md`是鏡像加Claude版紀錄。兩者衝突時，以`PROJECT_MEMORY.md`和實際檔案為準。
- 若`git log -- PROJECT_MEMORY.md`比`PROJECT_MEMORY_claude.md`新，先同步再動工。
- 製作或修訂教材前，先讀`skills/course-material-authoring/SKILL.md`與`references/conventions.md`。
- 專案可能在兩台電腦上（`E:\Git Repos\...`、`K:\...`）。以實際位置為準，換電腦先看Git狀態。

## 版本規則

- **Codex版是正式主線**。Claude版（檔名含`_claude`／`Claude生成`）只作比較或備援。
- **原版不改**：使用者要求檢視或修改某週時，另存修訂版（檔名含「修訂版」，App資料夾為`weekNN_*_revised/`）。之後就在既有修訂版續改，不再另建重複版本。
- 學生版與教師版只在封面、TODO答案與教師提醒不同。格ID與順序保持穩定。

## 安全與費用

- 沒有明確要求就不commit、不push。
- 不在任何檔案、輸出或下載紀錄中寫入或印出API金鑰。
- 跑測試前清空環境中的`OPENAI_*`變數。用真實SDK加`httpx.MockTransport`離線驗證，**呼叫真實付費API前先問使用者**。
- 教材中的付費開關（`RUN_*`、`SAVE_TEACHER_RECORD`）預設一律是`False`；設定`max_retries=0`、`timeout=60`、`store=False`。
- 金鑰在本機（App資料夾的`.env`）、Streamlit Cloud（Secrets）與Colab（Secrets）都要讀得到。

## 修訂版的建置與驗證（第9～13週）

Notebook、閱讀版Markdown與App都由build腳本產生，**不要手改產物**，要改`scripts/build_weekNN_revised.py`後重建。在Repo根目錄執行：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/build_weekNN_revised.py
.\.venv\Scripts\python.exe -X utf8 scripts/verify_weekNN_revised.py
```

- 教師導讀（`第NN週_課堂簡化版修訂版_教師導讀與修訂紀錄.md`）與App的`README.md`是手寫的，build不會覆蓋。改了內容要一起更新格數、格號與驗證說明。
- Notebook與App共用的函式必須AST完全相同，verify會檢查。
- 程式格開頭第一行寫`# 用途：…；先備：…；N次API`。標註「用到前面的哪些名稱、出自哪一格」由`scripts/notebook_cell_notes.py`自動產生；新增程式格時，要在該週的`CELL_NOUNS`補上名稱。
- 主節標題寫成`## 2 標題`，不加句點，否則Colab目錄不顯示節次。
- 改了共用模組，第9～13週都要重建並驗證。

## 教材寫法

- 用自然、可直接口述的繁體中文，每格一個重點；JSON輸出用`ensure_ascii=False`。
- 一週只教一條主線；程式只留教學需要的檢查，不放大量防呆。替代做法（例如代管服務）放最後一節選讀。
- 每個程式格主要只接上一格的一個結果變數；真實API的格子沿用離線版的寫法與資料格式。
- 學生TODO用`raise NotImplementedError`；核心流程完整提供，只留少數練習。

## 改完之後

- 更新`PROJECT_MEMORY.md`與`PROJECT_MEMORY_claude.md`：寫下做了什麼、驗證結果、未測項目，以及有沒有commit。
- 回報時說清楚：真實API呼叫次數、哪些沒測（Colab、Cloud、真人瀏覽器、試教）。
