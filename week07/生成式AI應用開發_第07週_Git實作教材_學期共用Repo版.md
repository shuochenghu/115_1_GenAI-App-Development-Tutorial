# 第 7 週｜Git 與 GitHub 實作教材：學期共用 Repo 版

2026-10-28 新版。原 [Git 實作教材](生成式AI應用開發_第07週_Git實作教材.md) 保留供比較。

從第 7 週開始，每位學生在自己的 GitHub 帳號建立 **`115_1_GenAI-APP-Development`**，作為本學期的教材與作業儲存庫。每週將老師提供的教材資料夾放進自己的 Repo，在 `student/` 完成課堂 TODO，再 Commit、Push。

本講義先帶你取得與保存教材，再接續老師的 Streamlit 講解；不用另外從零寫一份 AI 問答 App。Git 操作以 GitHub Desktop 為主，Python 安裝與啟動使用 VS Code 終端機。

## 一、這堂課要完成什麼？

| 階段 | 要做的事 | 完成證據 |
|---|---|---|
| 上課前段 | 建立自己的 Repo、Clone、加入本週教材 | GitHub 看得到 `week07-streamlit-app/` 與教材起點的 Commit |
| 課堂講解與實作 | 操作範例，完成 `student/` 的 TODO A／B／C | 本機能操作，能說明修改與觀察結果 |
| 下課前 | 檢查變更、Commit、Push、確認繳交連結 | GitHub 看得到最新作業與歷史紀錄 |
| 延伸 | 將一個已完成的範例部署至 Community Cloud | 可開啟的網址與實際驗證紀錄 |

Git 起步預留約 30 分鐘，下課前另留約 10 分鐘確認保存；由老師納入當週課程時間，安裝與登入仍須預留排障。部署先由老師示範，學生部署列為延伸，不取代 TODO 作業。第 8 週仍依專題說明書驗收，部署維持選做。

本週先學會 Clone、Pull、Commit、Push 與查看差異；分支協作、合併衝突與 CI/CD 留待需要時再學。

## 二、先分清楚四個動作

| 名詞 | 意義 | 在本課程何時使用 |
|---|---|---|
| Repository（Repo） | 受 Git 管理的專案資料夾及其歷史 | 整學期共用一個 Repo，裡面放各週資料夾 |
| Clone | 從 GitHub 建立本機副本，包含版本歷史 | 這台電腦尚未有自己的 Repo 時 |
| Pull | 把 GitHub 上的新提交同步到既有本機副本 | 家裡或其他電腦有更新時，上課先同步 |
| Commit | 把選取的變更記錄成本機版本 | 匯入教材、完成一項 TODO 或修正問題時 |
| Push | 把本機 Commit 上傳到 GitHub | 保存進度、離開電腦與繳交前 |
| `.gitignore` | 指定不納入 Git 追蹤的檔案 | 排除金鑰、虛擬環境與暫存內容 |
| `README.md` | 專案操作與成果說明 | 根目錄放作業索引，各週放操作與作業紀錄 |

**Commit 只存在本機，Push 後才會出現在 GitHub。** 老師發放新教材時，是把教材複製到自己的 Repo；Pull 同步的是自己 GitHub 上的提交，不會自動取得老師另外發放的教材。

```text
自己的 GitHub Repo
        │
        ├─ 這台電腦沒有副本 → Clone
        └─ 這台電腦已有副本 → Fetch／Pull
                         ↓
               複製老師發放的本週資料夾
                         ↓
               Commit／Push：保存教材起點
                         ↓
               聽講、操作、完成 student/ TODO
                         ↓
               檢查 → Commit → Push → 網頁確認
```

## 三、上課前確認

- [ ] 能登入自己的 GitHub 帳號。
- [ ] GitHub Desktop 已安裝，登入的是自己的帳號。
- [ ] 已安裝 VS Code 與 Python 擴充套件。
- [ ] 電腦有本週授課使用的 Python 3.14，或已向老師反映環境問題。
- [ ] 能取得老師發放的本週教材資料夾。
- [ ] 知道老師公告的繳交位置與期限。

帳號與工具尚未準備好時，先參考 [GitHub](https://github.com)、[GitHub Desktop](https://desktop.github.com) 完成設定。不要假設前幾週已經完成所有登入與安裝。

電腦教室使用自己的本機資料夾，不接續同學遺留的 Repo，也不把帳號密碼或金鑰寫進教材。

## 四、建立整學期使用的 Repository

### 4-1 在 GitHub 網頁建立 Repo（只做一次）

登入 GitHub，選 **＋ → New repository**：

| 欄位 | 設定 |
|---|---|
| Owner | 自己的 GitHub 帳號 |
| Repository name | `115_1_GenAI-APP-Development` |
| Description | 115 學年度第 1 學期生成式 AI 應用開發：課堂實作與作業 |
| Visibility | 課堂建議使用 Public，方便老師檢視；若需 Private，先依老師指定方式提供檢視權限 |
| Add README | 勾選 |
| Add .gitignore | 選擇 Python，稍後補上課程規則 |

按 **Create repository**。若先前已建立同名 Repo，直接使用，不必每週另建一次。

Public 代表程式與提交歷史可供他人閱讀；是否保護好金鑰，要靠實際檢查追蹤檔案，不能只依賴 Repo 的可見性。

### 4-2 用 GitHub Desktop Clone 自己的 Repo

1. 開啟 GitHub Desktop，選 **File → Clone repository**。
2. 選擇自己帳號下的 `115_1_GenAI-APP-Development`。若未列出，可在 URL 分頁貼上自己的 Repo 網址。
3. 確認 Local path 最後一層是 `115_1_GenAI-APP-Development`，存放於自己可寫入的位置。
4. 按 **Clone**。
5. 選 **Repository → Open in Visual Studio Code**；若找不到，先確認 Desktop 的外部編輯器設定。

**預期觀察：** VS Code 左側根目錄是自己的 Repo，裡面有 GitHub 建立的 `README.md`、`.gitignore`。

下載 ZIP 不等於 Clone：ZIP 不包含可接續使用的 Git 版本歷史與遠端連線。本課程請使用 Clone。可回查 [GitHub Desktop 官方 Clone 說明](https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop)。

### 4-3 同一台電腦已經有自己的副本

先確認 GitHub Desktop 的 Current repository 是自己的 Repo，Branch 是 `main`，Changes 沒有尚未處理的變更，再按 **Fetch origin**；出現 **Pull origin** 時按下同步。若顯示有尚未 Push 的提交，先確認是自己的工作，再同步。

若有不明檔案、衝突或其他人的修改，先請老師協助；不要直接丟棄變更或強制覆寫。每台電腦各自 Clone 一份即可，不需每週重複 Clone 到不同資料夾。

## 五、把老師發放的本週教材放進 Repo

### 5-1 複製的位置

解壓縮老師提供的教材，將完整的 **`week07-streamlit-app/`** 資料夾複製到 Clone 回來的 Repo 根目錄，與根目錄 `README.md` 並列。

```text
115_1_GenAI-APP-Development/         ← VS Code 開啟這一層
├── README.md                      ← 整學期作業索引
├── .gitignore                     ← 第六節補上的共用規則
├── requirements.txt               ← 第九節部署時才加入
└── week07-streamlit-app/           ← 老師提供，複製整個資料夾
    ├── README.md
    ├── requirements.txt
    ├── .env.example
    ├── .env                       ← 需要 API 時自行建立，不上傳
    ├── .venv/                     ← 本機自行建立，不上傳
    └── student/
        ├── 01_inputs.py
        ├── 02_state.py
        ├── 03_form_ai.py
        ├── 04_chat.py
        ├── 05_streaming.py
        ├── 06_file.py
        └── 07_layout.py
```

圖中的 `.env`、`.venv/` 並非老師發放的內容；根目錄 `requirements.txt` 在準備部署時才加入。不要把資料夾複製成兩層 `week07-streamlit-app/week07-streamlit-app/`。

老師發放的教材不應包含 `.git/`、`.venv/`、真實 `.env`、真實 `secrets.toml` 或教師答案。若拿到的壓縮檔含有這些內容，先請老師確認，不要整包複製。

### 5-2 教材來源路徑與學生路徑

老師備課時使用 [第 7 週課堂簡化版](week07_streamlit_simple/README.md)，發放給學生時包裝為 `week07-streamlit-app/`。兩邊的檔案用途對應如下：

| 教師備課來源 | 學生自己 Repo 中的位置 |
|---|---|
| `week07/week07_streamlit_simple/student/` | `week07-streamlit-app/student/` |
| `week07/week07_streamlit_simple/requirements.txt` | `week07-streamlit-app/requirements.txt` |
| `week07/week07_streamlit_simple/.env.example` | `week07-streamlit-app/.env.example` |

讀本或程式檔頭若仍顯示教師端的來源路徑，在學生 Repo 操作時，以本講義的學生路徑為準。七份 `.py` 都獨立執行，不需要把它們合併成一份 `app.py`。

## 六、先設定忽略規則，再保存教材起點

### 6-1 補上 Repo 根目錄的 `.gitignore`

打開 **`115_1_GenAI-APP-Development/.gitignore`**，保留既有 Python 模板，補上以下規則。規則放在根目錄，可一併保護後續各週資料夾。

```gitignore
# 本機金鑰與環境設定；範例檔可提交
.env
.env.*
!.env.example
!.env.*.example
**/.streamlit/secrets.toml

# 各週自行建立的虛擬環境與 Python 暫存檔
.venv/
.venv-*/
venv/
__pycache__/
*.pyc

# 本機驗證暫存與系統檔案
.apptest-temp/
.DS_Store
Thumbs.db
```

`.env.example` 只能放欄位與占位文字；`secrets.example.toml` 也是範例，不可填入真實金鑰後提交。`.gitignore` 只對尚未追蹤的檔案生效，不能讓已提交的金鑰從歷史消失。

### 6-2 第一次 Commit：保存尚未改作業的教材

1. 回 GitHub Desktop 的 **Changes**。
2. 確認有當週 `student/` 程式、README、requirements 與範例設定。
3. 確認沒有真實 `.env`、`secrets.toml`、`.venv/`、其他人的資料或教師答案。
4. 查看差異，確認這次加入的確實是老師發放的教材。
5. Summary 填入：`第7週：匯入課堂教材與忽略規則`。
6. 按 **Commit to main**，再按 **Push origin**。
7. 在 GitHub 網頁打開自己的 Repo，確認看得到 `week07-streamlit-app/student/`。

**預期觀察：** GitHub 留下一筆教材起點，之後可比較自己的 TODO 修改。匯入教材的 Commit 不能當作已完成作業。

## 七、準備本機環境，接續課程講解

### 7-1 先確認終端機位置

在 VS Code 選 **Terminal → New Terminal**。以下指令從學生 Repo 根目錄開始：

```powershell
cd .\week07-streamlit-app
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
python --version
python -m pip --version
python -m streamlit run student/01_inputs.py
```

建立環境與安裝套件是這台電腦第一次使用本週教材時做的事；下次已有可用環境，只需進入本週資料夾、啟用環境並啟動。若 `.venv` 已存在但使用其他 Python 版本，保留它，改建 `.venv-py314`，並同步調整啟用路徑。

VS Code 按 `Ctrl+Shift+P` → **Python: Select Interpreter**，選本週資料夾 `.venv/Scripts/python.exe`。若啟用腳本被教室政策阻擋，先請老師協助；也可用 `.\.venv\Scripts\python.exe -m pip ...` 與 `.\.venv\Scripts\python.exe -m streamlit ...` 直接指定環境，不必更改全機安全設定。

目前第 7 週本機授課基準是 Python 3.14，教材套件清單為 Streamlit 1.63.0、OpenAI 2.49.0、python-dotenv 1.2.3。以老師發放的 `requirements.txt` 安裝，不自行改成其他版本。詳細背景見 [第 7、8 週 Python 3.14 環境指南](../docs/第07_08週_Python314環境指南.md)。

**預期觀察：** 瀏覽器打開本機 App，輸入稱呼、按送出後才顯示結果。本例不呼叫 API。不要用 `python student/01_inputs.py` 或在 Notebook 直接執行來代替 Streamlit 啟動方式。

### 7-2 操作各個範例並完成 TODO

切換範例時，在終端機按 `Ctrl+C` 停止，再更換啟動命令的檔名。下表任務沿用本週課堂簡化版，完整說明依老師提供的讀本與程式旁 TODO。

| 檔案 | 學習重點／學生任務 | 檢查方式 |
|---|---|---|
| `01_inputs.py` | TODO A：修改標題與說明，符合自己的用途 | 畫面反映修改，輸入與按鈕仍可正常操作 |
| `02_state.py` | TODO B：完成歸零按鈕的行為 | 連按加一兩次後，狀態次數為 2；按歸零後為 0 |
| `03_form_ai.py` | TODO C：顯示活動名稱與負責人，負責人為 `None` 時顯示「尚未指定」 | 兩個欄位可見，缺少負責人時有指定提示 |
| `04_chat.py` | 觀察聊天紀錄與送給模型的前文 | 能區分畫面紀錄與模型實際收到的訊息 |
| `05_streaming.py` | 觀察逐片顯示與完成後保存 | 能指出串流顯示、完成與失敗處理的位置 |
| `06_file.py` | 觀察文字檔預覽與輸入限制 | 能說明編碼、檔案大小與字數檢查 |
| `07_layout.py` | 觀察側欄、分頁與設定 | 能說明控制項如何影響畫面 |

只修改指定 TODO 與老師允許的延伸，不以教師完整答案覆蓋 `student/`，也不必重寫七份程式。TODO B、C 的具體寫法由學生完成，本講義只提供驗收條件。

### 7-3 先離線操作，再依課堂要求使用 API

本週範例預設不呼叫 API。TODO A／B／C 的基本介面與顯示檢查可先離線完成；`03_form_ai.py` 離線顯示的是固定活動卡，不能宣稱是模型從原文抽取的成果。

需要真實 API 時，先停止 App，在本週資料夾執行一次：

```powershell
Copy-Item .env.example .env
```

只在 `.env` 尚不存在時複製；已存在就直接編輯，不覆蓋原設定。私下填入自己的金鑰與老師公告可用的模型，再重新啟動 App、明確開啟 API 並提交。

`.env` 放在 `week07-streamlit-app/`，與本週 README 同層，不要在 `student/` 另放一份。啟用 API 後，每次有效提交最多一筆模型請求；重複送出另計。介面能顯示不等於真實 API、模型品質或雲端部署已驗證，實測與未測項目要分別記錄。

## 八、保存作業、Push 與繳交

### 8-1 先做一次忽略規則檢查

即使本週不使用 API，也可在 VS Code 的本週資料夾建立 `.env`，只填 `OPENAI_API_KEY=FAKE_KEY_FOR_GIT_CHECK`，用來檢查忽略規則。若已設定真實金鑰，不要為此覆蓋；也不要分享該檔內容。

回 GitHub Desktop 確認 `.env` 沒出現在 Changes；`.venv/` 也不應出現。若有出現，先修正根目錄規則並請老師確認，再繼續。假金鑰不能用來測試 API。

### 8-2 第二階段 Commit：保存自己的修改

1. 在 VS Code 儲存檔案，重新操作並檢查結果。
2. 回 GitHub Desktop，逐一查看 Changes 中 `student/` 的差異。
3. 確認沒有金鑰、虛擬環境或不明檔案。
4. 完成一項有意義的工作就 Commit，例如 `第7週：完成 TODO A 的標題與用途說明`、`第7週：完成 TODO B、C 並檢查操作結果`。
5. 在本週 `README.md` 加上自己的作業紀錄，再 Commit。
6. 按 **Push origin**，等待完成。
7. 到 GitHub 網頁確認最新 Commit 與程式內容。

至少保留「教材起點」與「自己的實作」兩個階段；可以依 A／B／C 分別提交，不必為湊次數製造無意義修改。看不出自己實作差異時，要檢查是否忘記儲存、選錯 Repo 或修改到 Repo 外的另一份檔案。

### 8-3 在本週 README 加入作業紀錄

保留老師提供的操作說明，在下方加入自己的紀錄：

| 項目 | 學生填寫 |
|---|---|
| TODO A／B／C | 各項完成、部分完成或未完成；修改了什麼 |
| 啟動方式 | 實際使用的資料夾、命令與 Python 版本 |
| 本機操作 | 測試輸入、操作順序、觀察結果與問題 |
| API 測試 | 有無執行；若有，記錄模型、請求次數與人工核對；沒有則寫未測 |
| AI 協助 | 使用工具、協助內容、自己修改與親自驗證事項；未使用則註明 |
| 部署 | 選做；網址與實測結果，或寫未部署 |

不要把「指令沒有報錯」寫成所有功能通過；離線固定卡、假資料與真實模型輸出要標示清楚，截圖不能露出金鑰或個資。

### 8-4 繳交連結

依老師公告繳交 **當週資料夾連結**，格式如下；把 `你的帳號` 換成自己的帳號：

```text
https://github.com/你的帳號/115_1_GenAI-APP-Development/tree/main/week07-streamlit-app
```

根目錄 `README.md` 另加一筆 `[第7週 Streamlit 課堂作業](week07-streamlit-app/)`，方便整學期檢視。若已部署，再附上 App 網址；尚未部署不以網址代替程式與作業紀錄。Private Repo 須確認老師有檢視權限。

## 九、延伸：從同一個 Repo 部署一個範例

先由老師示範，再由有餘裕的學生操作。本節以完成 TODO C 的 `03_form_ai.py` 為例；也可先選不使用 API 的 `01_inputs.py` 熟悉流程。

### 9-1 套件清單放對位置

Cloud 先找入口程式同層的套件清單，再找 Repo 根目錄。入口為 `week07-streamlit-app/student/03_form_ai.py` 時，**只放在中間一層的 `week07-streamlit-app/requirements.txt` 不會被自動找到**。見 [官方套件搜尋規則](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)。

本課程初期採 Repo 根目錄的共用 `requirements.txt`。從 Repo 根目錄執行以下命令；此時本週資料夾已存在，根目錄尚無同名檔案：

```powershell
Copy-Item .\week07-streamlit-app\requirements.txt .\requirements.txt
```

若根目錄已有套件清單，先比較內容，依老師提供版本整合，不直接覆蓋。現有第 7、8 週簡化版使用相同的三個直接套件版本，可以共用；以後各週需求不同時，再由老師指導把各 App 的套件清單放到入口程式同層。不要每週無條件覆蓋根目錄清單，以免影響其他已部署 App。

根目錄清單與本週清單都提交到 GitHub；前者供本例雲端部署，後者保留本週本機安裝入口。這個步驟只處理套件，不複製 `.env` 或 `.venv/`。

### 9-2 從 Repo 根目錄檢查啟動

Cloud 從 Repo 根目錄啟動，部署前也用相同位置檢查路徑。若目前仍在本週資料夾且已啟用本週虛擬環境，停止 App 後執行：

```powershell
cd ..
python -m streamlit run week07-streamlit-app/student/03_form_ai.py
```

先保持 API 關閉，確認畫面與 TODO C 的欄位可操作；這仍是離線檢查。之後讀取其他本機資料時，也要檢查相對路徑是否受啟動位置影響。見 [官方檔案配置與工作目錄說明](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization)。

將新增的根目錄 `requirements.txt` 與自己的最新修改 Commit、Push，再開始部署。

### 9-3 建立 Cloud App

1. 到 [Streamlit Community Cloud](https://share.streamlit.io) 登入並授權存取自己的 GitHub。
2. 選 **Create app**，選擇已有 App 的部署方式。
3. 填入下表。路徑使用 `/`，不要使用 Windows 的 `\`。

| 欄位 | 本例設定 |
|---|---|
| Repository | `你的帳號/115_1_GenAI-APP-Development` |
| Branch | `main` |
| Main file path | `week07-streamlit-app/student/03_form_ai.py` |
| App URL | 可選擇可用的名稱 |

一個部署指定一個入口；七份獨立 `.py` 不會自動變成七頁網站。同一個 Repo 可建立不同入口的 App，但本週先部署一個即可。Private Repo 也可在完成平台授權後部署，並非只支援 Public；可回查 [官方帳號與授權步驟](https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/quickstart)。

### 9-4 部署前設定 Python 與 Secrets

打開 **Advanced settings**，選擇老師已在 Cloud 實際驗證的 Python 版本與套件組合。若提供 3.14，可由老師先試部署；未提供時須另驗可選版本，不因 Windows／Python 3.14 本機通過就宣稱雲端相容。

若只操作離線模式，可以先不設金鑰。要驗證 API 時，在 Secrets 填入以下 TOML，占位文字須私下替換為自己的金鑰：

```toml
OPENAI_API_KEY = "填入你自己的API金鑰"
```

如需指定模型，可另加 `OPENAI_MODEL = "老師公告且帳號可用的模型名稱"`。不要照貼占位值，也不要把這段換成真金鑰後提交到 README。

頂層 Secrets 可作為環境變數供目前第 7 週範例的 `os.getenv()` 讀取；本機繼續使用未提交的 `.env`，Cloud 則在平台介面設定。金鑰不會隨 Clone／Push 自動帶過去。見 [官方 Secrets 說明](https://docs.streamlit.io/develop/concepts/connections/secrets-management)。

儲存設定後按 **Deploy**，查看部署紀錄與網址。初次安裝可能需數分鐘，不保證固定秒數。完整介面步驟見 [官方部署說明](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)。

### 9-5 驗證上線與後續更新

- 先關閉 API，檢查頁面與 TODO C 顯示；離線卡片不能當成真實抽取。
- 老師要求驗證 API 時，再開啟並提交一筆虛構資料，記錄實際請求與結果，逐欄對照原文。
- 發生問題時查看 Cloud log，確認套件、入口路徑、Python 與 Secrets；沒有實際驗證的項目寫未測。
- 之後修改已部署程式，Commit、Push 到該 App 指定分支，平台會處理更新；重新開啟網址確認結果，不以固定等待秒數作為完成證據。

**公開 App 的 API 開關不是登入或存取控制。** 若訪客開啟 API，會使用部署者設定的金鑰並產生請求。本週可以只公開離線展示；真實 API 示範依老師安排限制分享與開放時間，不能把預設關閉當成訪客無法使用的保證。

部署成功不表示所有測試已通過。網址、離線介面、真實 API 與內容正確性分別檢查；關閉教室電腦後，Cloud App 仍由平台執行。

## 十、下次上課、回家與後續週次

### 10-1 每次開始與離開電腦

| 情境 | 操作 |
|---|---|
| 第一次在這台電腦工作 | 登入自己的帳號 → Clone 自己的 Repo → 準備本機環境 |
| 這台電腦已有自己的 Repo | 確認未處理變更 → Fetch／Pull → 啟用本機環境 |
| 老師發放下一週教材 | 將新週資料夾複製進 Repo → 保存教材起點 → 開始實作 |
| 老師補發同週修正 | 先 Commit／Push 自己進度，依公告逐檔比較更新，不整包覆蓋已完成 TODO |
| 離開教室或換電腦前 | 儲存 → 操作檢查 → Commit → Push → GitHub 網頁確認 |

GitHub 不會保存被忽略的 `.venv/` 與 `.env`。換電腦後，用 requirements 重建環境，私下設定金鑰；不要把整份虛擬環境拷到不同電腦。課堂共用電腦離開前依教室規定登出 GitHub、Desktop 與 Cloud，並處理本機私密設定，避免下一位使用者接續自己的帳號。

### 10-2 第 8 週沿用同一個 Repo

新增例如 `week08-midterm-app/`，保留第 7 週資料夾與歷史。第 8 週是個人小專題，仍採「最低要求固定、題目與設計開放」，starter 可選，不是要求全班做同樣的 TODO 題目。

若自己的程式入口為 `week08-midterm-app/app.py`，選做部署時 Main file path 就填這個路徑；套件清單可放在該 `app.py` 同層。繳交時提供當週資料夾連結與自己的 README、設計與驗收紀錄，並依公告完成 Demo。完整標準回查 [第 8 週簡化版專題說明書](../week08/生成式AI應用開發_第08週_期中個人小專題_課堂簡化版_專題說明書.md)。

## 十一、常見問題與版本回復

| 問題 | 先檢查什麼 |
|---|---|
| Clone 或 Push 失敗 | Desktop 登入帳號、Repo 網址、網路與權限；不要貼出登入憑證 |
| Changes 沒有自己的修改 | 檔案是否儲存、Current repository 是否正確、檔案是否在 Clone 資料夾內 |
| 回家看不到教室作業 | 教室是否只有 Commit 而沒有 Push；家裡是否 Fetch／Pull 到最新版本 |
| Clone 後無法啟動 | `.venv` 與 `.env` 不會隨 GitHub 帶回；檢查本機環境、套件與啟動位置 |
| `.env` 出現在 Changes | 暫停提交，檢查根目錄 `.gitignore` 與是否已被追蹤 |
| Cloud 找不到套件 | requirements 是否在入口同層或 Repo 根目錄，是否已 Push |
| Cloud 找不到程式 | 檢查 Main file path、大小寫、`/` 與指定分支是否存在該檔 |
| Cloud 顯示缺少 key | Secrets 名稱、TOML 格式與程式讀取方式是否一致，不要在畫面印 key 排錯 |
| 程式有頁面但不是模型成果 | 是否仍為離線模式，是否真的送出請求，是否完成回應檢查 |

### 查看差異與取消一筆錯誤提交

GitHub Desktop 的 **History** 可以看到提交紀錄；選取一筆，查看修改的檔案與差異。先理解哪次修改造成問題，再選擇處理方式。

若需要取消某一筆已提交的修改，可在 History 對該筆提交按右鍵，選 **Revert Changes in Commit**。Revert 會新增一筆反向修改，並非直接切回所選提交當時的完整版本；取消較早的修改也可能與後續工作衝突。先保存目前進度，必要時請老師協助，再 Push。

若真實 API key 曾被 Commit 或 Push，立即到服務提供者後台撤銷並重新建立金鑰，請老師協助停止追蹤及清理歷史。事後補 `.gitignore`、刪檔或 Revert 都不能消除既有歷史中的金鑰。

## 十二、課後確認清單

- [ ] Repo 名稱為 `115_1_GenAI-APP-Development`，建立在自己的帳號下。
- [ ] 本機副本由 Clone 取得，VS Code 開啟正確 Repo。
- [ ] `week07-streamlit-app/` 在 Repo 根目錄，沒有多套一層同名資料夾。
- [ ] 根目錄忽略規則已檢查；真實金鑰、虛擬環境與教師答案未提交。
- [ ] 留下教材起點與自己的實作 Commit，能從差異說明自己改了什麼。
- [ ] TODO A／B／C 依實際完成情形記錄，操作結果可說明。
- [ ] 本週 README 記錄啟動方式、實測／未測項目及 AI 協助情形。
- [ ] 已 Push，並在 GitHub 網頁確認最新程式。
- [ ] 繳交當週資料夾連結；選做部署者另附網址與實際驗證結果。
- [ ] 離開共用電腦前依教室規定處理帳號與本機私密設定。

## 附錄 A：命令列與 GitHub Desktop 對照（選讀）

本課程以 Desktop 操作即可；命令列供理解同一件事的另一種操作方式。

| 動作 | 命令列 | GitHub Desktop |
|---|---|---|
| 取得本機副本 | `git clone <自己的Repo網址>` | File → Clone repository |
| 查看變更 | `git status`、`git diff` | Changes 與右側差異 |
| 選取本次要記錄的檔案 | `git add <檔案路徑>` | 在 Changes 勾選檔案 |
| 記錄版本 | `git commit -m "具體說明"` | 填 Summary → Commit to main |
| 上傳提交 | `git push` | Push origin |
| 查詢與下載更新 | `git fetch`，確認後 `git pull` | Fetch origin → Pull origin |
| 查看歷史 | `git log` | History |
| 取消指定提交的修改 | `git revert <提交編號>` | History → Revert Changes in Commit |

## 附錄 B：教師發放教材前檢核

1. 保留教師端原檔；以 `week07/week07_streamlit_simple/` 作為來源，另行整理學生教材包，發放資料夾命名為 `week07-streamlit-app/`。
2. 保留七份 `student/` 程式與原 TODO；提供本週 README、requirements、`.env.example` 與必要讀本。教師完整答案另外保存，不放進學生作業包。
3. 發放版 README、讀本與啟動提示改用學生端路徑；移除或補齊對教師專案其他資料夾、驗證腳本、教師導讀與原整合 App 的相對連結。不要只重新命名資料夾就宣稱發放包已完整可用。
4. 第一次上課依第六節建立 Repo 根目錄忽略規則；部署時再依第九節加入共用套件清單，避免學生手寫另一組未驗證版本。
5. 用全新學生資料夾演練 Clone → 複製教材 → 建環境 → 離線操作 → Commit／Push；另驗真實 API 與 Cloud，記錄環境、操作與結果。
6. 課前公告取得教材方式、TODO 要求、繳交期限與 Private Repo 檢視方式。第 8 週評分與部署選做規則仍沿用原專題說明書。

本次新增的是 Git 講義，學生發放包尚未另行產出；教師端既有 README、Notebook、程式檔頭與重建腳本也未因本講義自動改寫。實際發放前須完成上述整理與演練。本講義已核對現有檔案與官方操作文件；不代表已完成學生帳號操作、真實 API、真人瀏覽器、Community Cloud 或課堂試教。
