"""另存第1週語音增補教材與Marp來源；HTML由Marp CLI輸出，原檔保留。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / "week01"
PREFIX = "生成式AI應用開發_第01週"


def replace_once(text, old, new):
    """來源變動時停止，避免靜默漏改或重複插入。"""
    assert text.count(old) == 1, old[:80]
    return text.replace(old, new, 1)


slides = (WEEK / f"{PREFIX}投影片.md").read_text(encoding="utf-8")
slides = replace_once(slides, "- 串接文件、圖片、資料表與外部工具", "- 串接文件、圖片、語音、資料表與外部工具")
voice_slides = """# AI 應用的輸入與輸出

| 資料形式 | 輸入範例 | 輸出／處理範例 |
|---|---|---|
| 文字 | 問題、文件內容 | 回答、摘要、JSON |
| 圖片 | 截圖、收據照片 | 圖片說明、欄位抽取 |
| 語音 | 錄音、口頭問題 | 辨識文字、回答朗讀 |

- **語音辨識（STT）**：把音檔轉成文字
- **語音合成（TTS）**：把文字轉成可播放的音訊

> 錄音、辨識、合成、播放是不同步驟。

<!-- 教師：先請學生指出音檔、文字、JSON的不同用途。語音辨識與語音合成的API實作留到後續多模態教材。依據：https://developers.openai.com/api/docs/guides/voice-agents 和 https://developers.openai.com/api/docs/guides/text-to-speech 。 -->

---

# 語音問答 App 的處理流程

```text
錄音 → STT 辨識文字 → 使用者確認或修正
     → 模型產生文字回答
     → TTS 合成音訊 → 播放回答
```

**示範提問**：請用生活中的例子解釋什麼是 API。

- 畫面保留辨識文字與回答，方便核對
- 本課程先學分段處理，每段可分別檢查錯誤與用量
- 第 5 週 Streaming 是**文字片段**，語音合成是後續步驟

> 本週觀察流程。後續語音實作預計增補於第 12 週。

<!-- 教師10分鐘示範：1分鐘聽預錄問題，2分鐘讀辨識結果並修正「A P」為「API」，2分鐘讀文字回答，2分鐘播放事先準備的合成音訊，3分鐘討論錯誤應在哪一段修正。未準備音訊時改用文字流程演練，明示尚未播放語音。範例文字是離線教學資料，不冒充現場API回應。音訊應標示「AI生成語音」。學生本週不需金鑰、錄音或付費。 -->

---

"""
slides = replace_once(slides, "# 本課程的技術地圖", voice_slides + "# 本課程的技術地圖")
slides = replace_once(slides, ">Vision API</td>", ">Vision / 語音（增補規劃）</td>")
slides = replace_once(slides, "</table>\n\n---\n\n# 什麼是 RAG？", "</table>\n\n<!-- 第12週語音部分為後續增補規劃，正式教材尚待製作；同時見前一頁的可見說明。 -->\n\n---\n\n# 什麼是 RAG？")
slides = replace_once(slides, "- 必須包含 OpenAI API 與至少一種資料來源\n- 建議包含 RAG、Tool Calling、Agent 或 Vision", "- 必須包含 OpenAI API、至少一種資料來源\n- 至少包含 **RAG 或 Function Calling** 其中一項\n- 語音延伸例：課程文件語音助手、語音會議紀錄整理\n- 語音功能可選，作品仍須符合上述最低要求")
slides = replace_once(slides, "- 以指定低成本模型練習；依呼叫次數、輸入／輸出 token 與當時單價估算，期間核對實際用量", "- 使用指定低成本模型，依文字用量與當時單價估算\n- 語音辨識與合成需另依所選服務估算費用")
slides = replace_once(slides, "4. 想一個自己想做的 AI Web App 題目</td>", "4. 想一個 AI Web App 題目<br>可加入語音輸入／朗讀</td>")
slides = replace_once(slides, "第 1 週    瀏覽器展示（今天）", "第 1 週    瀏覽器展示、語音流程概念（今天）")
slides = replace_once(slides, "           Python 複習、API 呼叫、Prompt、結構化輸出", "           Python、API、Prompt、文字對話、結構化輸出")

# 保留Marp既有版型與所有原頁面，只新增兩張概念頁。
slides_path = WEEK / f"{PREFIX}投影片_語音增補修訂版.md"
slides_path.write_text(slides, encoding="utf-8")

lesson = (WEEK / f"{PREFIX}教材.md").read_text(encoding="utf-8")
lesson = replace_once(lesson, "# 生成式AI應用開發 第01週教材", "# 生成式AI應用開發 第01週教材｜語音增補修訂版")
lesson = replace_once(lesson, "本週不要求學生撰寫程式，也不使用付費 API。", "本週不要求學生撰寫程式，也不使用付費 API。語音部分以預錄／預先產生素材示範，認識語音辨識、文字回答與語音合成的分工。")
lesson = replace_once(lesson, "Structured Outputs、RAG、Vision、Tool Calling", "Structured Outputs、RAG、Vision、語音辨識／合成、Tool Calling")
lesson = replace_once(lesson, "7. 完成開發環境與帳號準備清單的確認。", "7. 完成開發環境與帳號準備清單的確認。\n8. 說明語音辨識（STT）、模型文字回應與語音合成（TTS）的分工，指出辨識錯誤的修正位置。")
lesson = replace_once(lesson, "- 電腦教室環境檢查清單。", "- 一段無個資的預錄提問、辨識文字、文字回答及事先準備的合成音訊；音訊旁標示「AI生成語音」。未備妥音訊時，使用第十一節的文字流程演練，明示沒有實際播放。\n- 電腦教室環境檢查清單，另確認教師端喇叭可播放。")
lesson = replace_once(lesson, "- 本週不需準備 API key。", "- 本週不需準備 API key、麥克風或耳機；設備狀況先填背景調查，後續語音實作可用提供的音檔。")
start = lesson.index("## 四、3小時課程流程")
end = lesson.index("## 五、投影片大綱")
lesson = lesson[:start] + """## 四、150分鐘有效授課流程

3小時時段包含150分鐘核心教學、10分鐘休息與20分鐘彈性答疑／環境排障。語音示範納入原案例展示時段。

| 時間 | 單元 | 內容 | 產出 |
|---:|---|---|---|
| 0:00–0:15 | 課程開場 | 定位、上學期銜接 | 理解本課程的應用開發目標 |
| 0:15–0:35 | 應用案例 | 聊天工具／Web App 10分鐘，語音示範與討論10分鐘 | 分辨應用形式與STT／模型／TTS責任 |
| 0:35–1:00 | 基本架構 | 介面、Python、API、資料與語音流程 | 畫出基本架構，指出辨識文字的修正位置 |
| 1:00–1:10 | 休息 | 不計有效授課時間 | — |
| 1:10–1:35 | 技術地圖 | Python、文字對話、Structured Outputs、RAG、圖片、語音增補規劃、工具 | 理解本週概念與後續實作的銜接 |
| 1:35–1:45 | Git用途與帳號 | 帳號與工具準備，第7週操作預告 | 確認準備方向 |
| 1:45–2:05 | 評量與專題 | 統一比例、最低要求、含語音的專題範例 | 知道必做要求與可選功能 |
| 2:05–2:30 | 環境與背景調查 | Colab、VS Code、GitHub、帳號費用、語音經驗與設備 | 完成準備清單 |
| 2:30–2:40 | 總結與課後任務 | 流程覆述、下週Python準備 | 完成本週檢核 |
| 2:40–3:00 | 彈性時間 | 個別答疑、帳號／環境排障 | 依班級需求使用，不新增必做內容 |

""" + lesson[end:]

# 正式教材的投影片大綱直接對照Marp的23頁，避免原18項大綱與21頁投影片錯位。
body = slides.split("---", 2)[2].strip()
pages = re.split(r"\n---\s*\n", body)
outline = []
for i, page in enumerate(pages, 1):
    clean = re.sub(r"<!--.*?-->", "", page, flags=re.S).strip()
    title = re.search(r"^# (.+)$", clean, re.M).group(1)
    content = re.sub(r"^# .+\n", "", clean, count=1).strip()
    outline.append(f"### Slide {i}：{title}\n\n{content}\n")
assert len(pages) == 23
start = lesson.index("## 五、投影片大綱")
end = lesson.index("## 六、Git 與 GitHub 教學定位說明")
lesson = lesson[:start] + "## 五、投影片大綱\n\n" + "\n".join(outline) + "\n" + lesson[end:]
lesson = replace_once(lesson, "帳號準備（15 分鐘）", "帳號準備（10 分鐘）")
lesson = replace_once(lesson, "  + Vision\n", "  + Vision\n  + Speech（後續增補規劃）\n")
lesson = replace_once(lesson, "   - 圖片理解\n", "   - 圖片理解\n   - 語音問答或會議紀錄\n")
lesson = replace_once(lesson, "7. 你最擔心這門課的哪個部分？", """7. 你最擔心這門課的哪個部分？

8. 是否使用過AI語音功能？（可複選）
   - 未使用
   - 語音輸入／辨識
   - 回答朗讀
   - 即時語音對話

9. 上課設備的麥克風與耳機狀況？
   - 都可使用
   - 只有部分設備可使用
   - 無法使用或尚未確認

設備調查用於後續安排，不要求本週購買設備或提交個人錄音。""")
demo = """## 十一、語音應用示範與完成檢核

### 10分鐘示範腳本

本節文字是固定的离線教學素材，不是現場API成果。教師可提前準備對應音訊；只有文字時稱為「流程演練」，不宣稱已完成語音播放。

| 分鐘 | 教師操作 | 學生觀察 |
|---|---|---|
| 0–1 | 播放預錄提問：「請用生活中的例子解釋什麼是API。」 | 輸入是音檔 |
| 1–3 | 顯示示意辨識結果「請用生活中的例子解釋什麼是A P」，讓學生改為「API」 | 辨識文字可以確認、修正 |
| 3–5 | 顯示下方示意回答，指出模型接收的是修正後文字 | 語音辨識與回答生成是不同步驟 |
| 5–7 | 播放事先準備的回答音訊，保留同一份回答文字 | TTS讀取回答文字，播放器呈現音訊 |
| 7–10 | 討論辨識錯誤、回答錯誤與播放失敗各在哪一段檢查 | 分開判斷錯誤來源 |

示意回答：「API像餐廳的點餐窗口。你依規定送出訂單，窗口把需求交給廚房，再把結果交回來。程式也能透過API向服務提出請求並取得結果。」

教師備援：若無音訊，讀出提問並出示文字素材，讓學生完成流程排序與修正討論。這仍能檢核概念，但不能當作STT／TTS實跑證據。

### 學生檢核與教師判讀

- 能指出STT輸出是文字、TTS輸出是音訊，錄音與播放各有自己的責任。
- 能把「A P」改為「API」後才交給模型，不用TTS掩蓋辨識錯誤。
- 能說明第5週文字Streaming與語音合成的差別。入門語音流程先取得完整可用回答，再按鈕觸發朗讀。
- 能說明第6週Structured Outputs處理文字資料；後續可以抽取已確認的逐字稿。JSON符合格式仍要回看辨識文字及原錄音。
- 提交一張流程圖及一句錯誤修正說明即可，無須交付音檔或新增API呼叫。

### 後續銜接與成本

第5、6週繼續使用Colab學文字對話與資料抽取，第7週建立Web介面。語音辨識與合成預計在第12週多模態單元增補，實作教材尚待製作；本次不代表其他週教材已更新。

語音辨識、文字模型與語音合成分段記錄用量，各依所選服務的計費方式估算。STT、回答或TTS失敗應分段重試，不自動重跑整條流程。語音範例只用無個資素材，播放合成音訊時標示「AI生成語音」。

參考：[OpenAI語音工作流程](https://developers.openai.com/api/docs/guides/voice-agents)與[語音合成及AI語音揭露說明](https://developers.openai.com/api/docs/guides/text-to-speech)。本週只介紹分段架構，不指定語音模型或API參數。

""".replace("离線", "離線")
lesson = replace_once(lesson, "## 十一、教師備註", demo + "## 十二、教師備註")
lesson = replace_once(lesson, "- 第1週不要急著教 API 語法，先建立完整學習地圖。", "- 第1週先建立完整學習地圖；語音示範不新增程式、付費API或必備設備。\n- 語音資料流採分段教學；即時語音對話留後續進階探索，不列本週學習門檻。")
lesson_path = WEEK / f"{PREFIX}教材_語音增補修訂版.md"
lesson_path.write_text(lesson, encoding="utf-8")
print(f"已另存教材與Marp來源，投影片{len(pages)}頁。")
