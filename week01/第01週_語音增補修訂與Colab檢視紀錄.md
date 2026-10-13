# 第01週語音增補修訂與第5、6週Colab檢視紀錄

日期：2026-10-12。第1週原檔保留；第5、6週僅檢視，未修改。

> 後續狀態：使用者確認建議後，已於同日同步修改第5、6週150分鐘學生／教師版的Colab操作、API設定與簡短語音銜接。下方保留當時檢視結果；最新修改與驗證以兩週各自的「150分鐘修訂版_修訂與驗證紀錄」為準。未執行真實SDK／API或Colab。

## 第1週交付

- `生成式AI應用開發_第01週教材_語音增補修訂版.md`
- `生成式AI應用開發_第01週投影片_語音增補修訂版.md`
- `生成式AI應用開發_第01週投影片_語音增補修訂版.html`

投影片沿用原Marp字型、色彩與版型，由21頁增為23頁。在基本架構後新增「AI應用的輸入與輸出」及「語音問答App的處理流程」，說明STT、文字回答、TTS，以及文字Streaming的分工。

教材新增學習目標、10分鐘預錄示範腳本、固定示意辨識文字與回答、錯誤修正討論、學生檢核、設備與使用經驗調查。沒有產生實際音檔，也沒有呼叫STT／TTS；教師需課前準備音訊，或依備援方式進行文字流程演練。範例明示為離線教學資料。

第1週流程整理為150分鐘核心教學、10分鐘休息與20分鐘彈性答疑／排障。語音示範使用既有案例展示時段。教材投影片大綱改為逐頁對應23頁，避免原18項大綱與Marp頁次錯位。

評量與主課綱統一為40／20／25／10／5%，期末至少包含RAG或Function Calling其中一項。語音功能為可選延伸，不能取代最低要求。

第12週語音實作明示為「後續增補規劃」，尚未製作；本次不修改主課綱、第7週或第12週教材。

## 第5、6週Colab檢視結論

兩週150分鐘修訂版仍適合使用Colab。語音功能加入整體課程後，本週的文字輸入、對話history、文字Streaming與Structured Outputs主線都可以保留。沒有必要把麥克風、瀏覽器錄音或TTS串流加入這兩週的必做內容。

| 檢視項目 | 現況 | 建議的下一次修改 |
|---|---|---|
| 安裝方式 | 第5週`!pip install -q --upgrade openai`；第6週`%pip install -q --upgrade openai "pydantic>=2,<3"` | 第5週統一為`%pip`；兩週先在Colab實測後固定套件版本，並顯示實際版本。不直接套用Windows整份相依快照。 |
| 金鑰 | 兩週已使用Colab Secrets／環境變數，缺金鑰時client為None | 補Secrets命名、Notebook存取授權及設定後重跑環境格的明確步驟，維持不顯示金鑰。 |
| Runtime與重跑 | 有依序執行與付費旗標說明，但重啟後恢復流程較簡略 | 補「安裝→環境→共用定義→練習定義→離線檢查→指定付費活動」清單；說明變數、history與client需重建，執行練習定義格不等於重新編輯程式。開啟過的旗標先恢復False。 |
| 第5週狀態 | 手動history、reset、delta／completed皆已具備 | 語音轉成已確認文字後，可送進既有聊天函式；TTS只使用完整且可用回答。補文字Streaming與語音播放的區別即可。 |
| 第6週資料契約 | JSON Schema、Pydantic、欄位驗證與人工覆核皆已具備 | 可預告後續抽取已確認的逐字稿。需回查辨識文字、原錄音；格式正確不代表人名、日期、金額正確。 |
| 請求與重試 | 第6週client已`max_retries=0`；第5週client未明訂SDK重試設定 | 若第5週要以標示呼叫數作為請求上限，需明訂重試設定與重跑另計；不能只以假API函式呼叫數推定實際傳送次數。 |

以上屬建議，尚未套用到第5、6週Notebook。本次不新增付費呼叫，也不改TODO、cell順序或教學時間。

官方依據：[IPython `%pip`](https://ipython.readthedocs.io/en/stable/interactive/magics.html#magic-pip)在目前kernel執行套件管理；[Colab FAQ](https://research.google.com/colaboratory/faq.html)說明執行狀態位於有生命週期限制的虛擬機。[OpenAI語音工作流程](https://developers.openai.com/api/docs/guides/voice-agents)支持分段檢視文字與替換各處理階段。語音辨識與合成的參數、模型與費用，製作實作教材時再依官方文件確認。

## 已執行驗證

- 第1週兩份Markdown的語音術語、評量比例、期末要求、程式區塊配對與常見亂碼檢查通過。
- Marp HTML重新輸出，共23個slide sections；全部23頁渲染並檢視。技術地圖的額外說明移至教師備註，修正與頁尾重疊；最後重新檢查第9、17頁。
- 第5週兩版各63 cells，第6週兩版各70 cells，JSON、唯一ID、清空輸出與共122個普通Python cells的AST檢查通過。頂層RUN旗標均預設False。
- `git diff --exit-code`確認第1週原始三檔、第5、6週及主課綱沒有變動。
- 未在Colab操作、未測真實SDK／API、未做語音播放或課堂試教。靜態檢查不代表目標環境與真實模型已驗證。

## 重建方式

於專案根目錄執行`python scripts/build_week01_voice_revision.py`產生教材與Marp來源，再使用既有Marp CLI輸出HTML：

```powershell
marp 'week01/生成式AI應用開發_第01週投影片_語音增補修訂版.md' --html -o 'week01/生成式AI應用開發_第01週投影片_語音增補修訂版.html'
```
