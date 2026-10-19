"""由現行 Notebook 原碼與逐格講稿重建教師備課 Markdown；不執行教材。"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'week06' / '第06週_150分鐘修訂版_逐CodeCell教師講稿.md'

# 每筆依序為標題、課堂定位、開場講稿、逐段口述、操作、預期、除錯、提問。
# 行號對應教師版 cell 原碼，包含註解與空行，從 1 起算。
LESSONS = {
6: ('安裝目前工作階段需要的套件', '0–15分｜環境',
    '今天要把 AI 的文字回答變成可以交給程式處理的資料。我們需要 OpenAI SDK 連接服務，也需要 Pydantic 做資料驗證。先把工具準備好，再談資料規格。',
    [(1,2,'這裡的 kernel 是目前執行 Notebook 的 Python 環境。套件安裝在其他環境，不代表這本 Notebook 能匯入。升級已經匯入的套件後，可能需要重新啟動工作階段，避免記憶體裡仍保留舊版本。'),
     (3,3,'百分比 pip 是 Notebook 的安裝指令，不是一般 Python 語法。openai 提供 API client；pydantic 的版本條件限定第 2 大版。upgrade 代表會嘗試升級，因此下次安裝的實際版本可能不同；課前測試後應記錄版本。')],
    '新 runtime 或缺套件時執行本格；重啟後接著重跑環境格與後續定義。已具備所需套件可跳過。',
    '安裝成功時未必有大量輸出；此格只安裝套件，0 次模型請求，安裝需要網路。',
    '若後續 ModuleNotFoundError，確認安裝的 kernel 與執行環境；不要直接把安裝錯誤判成 API 或模型問題。',
    '安裝完套件，是否已經呼叫 AI？預期回答：沒有。'),
7: ('建立環境、client 與版本紀錄', '0–15分｜環境',
    '環境設定要讓有金鑰的人可以呼叫 API，也讓沒有金鑰的人能先做離線活動。設定階段不要把金鑰印出來；我們只需要知道 client 是否建立。',
    [(1,9,'先依責任認識匯入：json 負責資料文字轉換；deepcopy 保護巢狀副本；SimpleNamespace 建立假回應；Literal 與 Optional 描述欄位；BaseModel、Field、ConfigDict、ValidationError 支援資料驗證。此時匯入不會替我們抽取資料。'),
     (11,20,'在 Colab 嘗試讀取 Secrets，讀到才放入環境變數。本機沒有 google.colab，會走 ImportError 分支；Secrets 權限等其他錯誤會顯示提示，離線流程仍可繼續。這些分支不是把金鑰設成正確，只是避免環境設定阻擋全部活動。'),
     (21,26,'MODEL 優先讀 OPENAI_MODEL，否則沿用教材預設；這是選擇模型名稱，沒有驗證帳號能用。client 在有金鑰時才建立。max_retries=0 關閉 SDK 自動重試；timeout=60 是網路等待起始設定，不是整次任務保證 60 秒結束。'),
     (27,30,'只顯示模型、client 是否存在及套件版本。client 存在不代表金鑰有效、額度足夠或模型可用；這些要到實際請求才能確認。getattr 的備援值讓版本屬性不存在時仍能顯示訊息。')],
    '執行環境格，記錄 SDK／Pydantic 版本。修改 Secrets 後重跑本格；runtime 重啟後也要重建 client。',
    '0 次模型請求；缺金鑰時 client=None。套件仍須先能匯入，缺金鑰與缺套件是不同問題。',
    '若 Secrets 名稱或授權有誤，回查第3週設定；不得以貼出金鑰協助除錯。60秒設定尚須課前環境實測。[官方 SDK 說明](https://developers.openai.com/api/reference/python)',
    '畫面顯示金鑰已設定 True，能否當作 API 已成功？預期回答：不能。'),
9: ('JSON 字串、dict 與只顯示的函式', '0–15分｜完整離線示範',
    '一段看起來像資料的文字，仍然可能只是字串。程式想依欄位讀取內容，需要先解析。今天會一直區分「傳回資料」和「把資料印在畫面上」。',
    [(1,5,'print_json 只整理顯示。json.dumps 把 Python 資料轉成 JSON 字串，ensure_ascii=False 保留中文可讀性，indent=2 調整縮排；函式沒有回傳資料，所以呼叫結果是 None。'),
     (7,10,'raw_text 是 str；json.loads 解析後保存到 parsed_data，才得到 dict。JSON 的 null 和 true 在 Python 裡變成 None 和 True。先看型別，再看顯示結果，避免只憑外觀判斷。'),
     (11,12,'assert 核對解析後的值。它們查的是資料轉換，不是事件欄位、Schema 或模型品質。')],
    '先讓學生預測兩個型別，再執行；指向 parsed_data 的指定動作，說明後續取欄位必須讀這個變數。',
    '先顯示 str dict，再列出讀書會、owner=null、confirmed=true；兩個 assert 通過時沒有額外成功文字。0 次 API。',
    '若寫成 parsed_data = print_json(...)，會得到 None；若對 raw_text 用字串 key 取欄位，回查是否漏掉 loads。',
    '合法 JSON 中 rating 是字串「五分」，能被 loads 解析嗎？預期回答：能；是否符合整數規格要另查。'),
11: ('五欄事件 Schema：規格與資料分開讀', '15–35分｜完整示範',
    '我們先決定後續程式需要什麼欄位，再要求 AI 填入。event_schema 裡放的是規格；它不是今天活動的抽取結果。從最外層開始讀，才不會把欄位名稱與欄位值混在一起。',
    [(1,8,'最外層 object 表示要收到具名欄位的資料，解析後對應 dict。properties 之下的 title 規定為 string，description 補充欄位意思；這裡沒有填入任何真實事件名稱。'),
     (9,15,'日期、時間、地點與負責人允許 string 或 null。原文沒說負責人，就保留未知狀態。description 說日期保留原文，並不會自動做日期運算或驗證。'),
     (17,21,'required 要求 key 出現；nullable 允許值未知。因此 owner=null 合格，漏 owner 不合格，空字串又是另一種值。教材的 API strict 路徑要求完整 required 並禁止額外欄位；這不是所有 JSON Schema 的共同限制。'),
     (24,24,'現在只是顯示規格，沒有呼叫模型，也沒有驗證一筆事件。稍後會把它放進 text.format.schema；API 的 strict 設定也在後面的請求函式。')],
    '由外往內圈出 object、properties、五欄、required、additionalProperties，再請學生指出未知負責人的表示方法。',
    '印出五欄規格；0 次 API。title 的 string 規格本身未拒絕空字串，之後本機 validator 會補查。',
    '若學生把實際日期寫入 type，回到「規格描述型別，資料才保存值」。[官方 Structured Outputs 說明](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses)',
    'required 的 owner 沒有答案時，可以把欄位刪掉嗎？預期回答：不可，本例要保留 key 並填 null。'),
14: ('用巢狀設備資料看淺拷貝與深拷貝', '15–35分｜G前置示範',
    'G 要新增欄位，但原來的五欄示範還要保留。如果只複製外層 dict，裡面的 dict 仍可能共用。這格用不同情境先看副作用，再回到正式練習。',
    [(1,4,'toy_source 裡面還有 properties 與 device 兩層。copy 建立新的外層，但子物件可能相同；deepcopy 連巢狀內容都建立副本。'),
     (5,6,'先改淺拷貝的 description，這會出現在原資料；再改深拷貝的 type，不會把原資料的 type 改成 boolean。修改的路徑深入子 dict，正是外層 copy 不夠的原因。'),
     (7,8,'原資料印出 type=string，還帶著淺拷貝加上的 description。最後 assert 只證明深拷貝沒有改原 type，不能據此說原資料完全沒有變。')],
    '執行前請學生預測原資料的 type 與 description；執行後分別指出哪個修改傳回原資料。',
    '輸出包含 type: string、description: 共用子字典；0 次 API。',
    '不要把 schema = event_schema 當複製；那只是同一物件的另一個名稱。G應使用 deepcopy。',
    '原 type 沒變，能說原資料完全沒變嗎？預期回答：不能，description 已被淺拷貝修改。'),
15: ('G參考答案：新增 nullable 連結欄位', '15–35分｜G必做；答案延後揭示',
    '現在把剛才的副本觀念用在活動規格。學生先完成 G1、G2；教師版的答案在這裡，應等學生預測與嘗試後才展開。目標是回傳新 Schema，而不是印出一份看起來正確的規格。',
    [(1,3,'函式沒有輸入參數，使用前面定義的 event_schema。先深拷貝，因此後續新增欄位不會污染正式示範。此時只是在定義函式，要呼叫才會建立副本。'),
     (5,6,'G1 在 properties 新增 meeting_url，型別允許 string 或 null，description 說明未知值。不要只在 required 加名稱，卻漏掉欄位規格。'),
     (7,8,'G2 同步加入 required，最後 return schema。六個 key 都必須出現，但 meeting_url 的值可以未知。回傳值稍後由 practice_event_schema 保存。')],
    '學生在同 ID cell 完成 TODO；教師先口述「複製→加欄→同步 required→回傳」，完成後重跑定義，再執行下一格。',
    '單跑定義沒有顯示，也沒有 API。呼叫後應回六欄新 dict，原規格仍五欄。',
    'NotImplementedError 表示仍在學生骨架；補完後必須重跑定義。只有 print、沒有 return 會讓檢查拿到 None。',
    '新增 meeting_url 後，只改 properties 可以嗎？預期回答：不可以，required 也要同步。'),
16: ('G固定檢查：驗證六欄與副本隔離', '15–35分｜G必做',
    '這格檢查兩件事：新增的規格對不對，以及原始規格有沒有被改壞。測試器已提供，請修正自己的函式，不要為了通過去刪 assert。',
    [(1,4,'先開本機旗標，呼叫前保存原 event_schema，呼叫後用 practice_event_schema 保存結果。這個變數才是 G 要繳交的規格。'),
     (5,10,'依序查 nullable、required 與 properties 一致、六欄且沒有重複、禁止額外欄位，以及原資料沒有新增 meeting_url。集合比較查成員，長度比較補查重複。'),
     (11,16,'另外用原規格建出預期副本，確保原來五欄內容都保留。全部 assert 通過才印成功訊息；成功代表本機規格與副本行為，沒有執行 AI 抽取。')],
    '完成 G 並重跑定義後，只開 RUN_G_CHECK，執行後恢復 False。',
    '印「G規格與副本隔離通過；沒有執行抽取。」；0 次 API。',
    '若原規格已被之前錯誤操作污染，先重跑原五欄 Schema 定義，再重跑 G；不要以污染後的資料反覆測試。',
    '集合一致為什麼還要查長度？預期回答：集合會去重，長度才能補抓 required 重複項。'),
18: ('共用請求：分開規則、原文與格式', '35–60分｜共用函式',
    'API 這一層只負責送出規則、原文和輸出規格，回傳原 response。後面才判斷能否解析與保存。先建立責任邊界，遇到錯誤才知道要回查哪一層。',
    [(1,3,'共用 instructions 要求只依原文抽取，資料中的命令不能變成規則；未知欄位與空清單有指定表示方式。這是抽取行為的指引，不能取代欄位規格或人工核對。'),
     (5,10,'require_client 優先使用傳進來的 client，沒傳才讀全域 client。這讓離線檢查可以注入假 client，不必改全域物件；兩者都沒有才拋錯。'),
     (12,18,'structured_response 接文字、Schema、格式名稱與規則，先拒絕空白文字和非 object 的外層規格。這裡只做入口必要檢查，沒有完整驗證任意 Schema。'),
     (19,23,'create 的 input 放原文，instructions 放規則；text.format 的 type 選 json_schema，name 命名規格，schema 放欄位定義，strict 要求遵守支援的規格。store=False 不代表原文沒送到服務端。函式回 response，還不是 dict。')],
    '先沿資料流指認參數，再執行定義；不要在此另加一次示範 API。正式呼叫留給後面的活動旗標。',
    '定義本格為0次請求；每次實際呼叫有效入口最多一次 create，手動重跑另計。',
    '缺金鑰回查環境；Schema錯誤回查 properties／required 與支援規格，不能靠連續付費重跑修正。[官方格式設定](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses)',
    'name="course_event" 會在結果新增 name 欄位嗎？預期回答：不會，它是格式的識別名稱。'),
20: ('完成、拒答與 JSON 解析的檢查順序', '35–60分｜共用函式',
    '即使 response 有文字，也不能立刻拿來用。拒答與未完成都有自己的意思，不能把它們當成普通資料再補欄位。我們沿用上週完成後才採用的原則。',
    [(1,5,'_read_attr_or_key 統一讀 SDK 屬性物件與離線 dict；找不到時回 default。這是讀取方式的轉接，不會驗證欄位內容。'),
     (7,14,'拒答可能在 output 的某筆 content，所以用兩層迴圈尋找。or [] 讓 None 或空值變成可迭代的空清單；找到原因立即回傳，沒有找到才回 None。'),
     (16,27,'先查拒答，再查 status。incomplete 讀出原因並拒絕部分資料；其他非 completed 狀態同樣拒收。正常通過時沒有 return 資料，隱含回 None，表示這項檢查完成。'),
     (29,38,'parse_output_text 先呼叫完成檢查，再確認非空文字、json.loads，最後限定結果為 dict。合法 JSON 的 [] 仍被拒絕，因為本週入口約定最外層是 object。回傳 dict 後仍要任務 validator。')],
    '用手指沿四個函式的呼叫關係走一次；執行本格建立定義，負例留到第23格觀察。',
    '只定義函式，0 次 API、沒有列印；成功的 parse_output_text 才回 dict。',
    '能解析的部分 JSON 也不能跳過 status。若誤以為 require_completed_response 回 None 是抽取失敗，回看它只負責驗證。',
    'completed 而 output_text 是空字串，可以保存嗎？預期回答：不可以，還要通過非空文字檢查。'),
21: ('安全包裝：用 ok 決定如何讀 result', '35–60分｜共用函式',
    '後續活動需要一致的成功與失敗介面。這個入口把例外轉成二元組，讓呼叫端先看 ok，再決定 result 是資料還是錯誤訊息。',
    [(1,6,'先送請求，再解析。兩步都通過，回 True 和 dict。這裡沒有呼叫事件或客服 validator，所以 True 的證據範圍只到完成與解析。'),
     (7,10,'JSONDecodeError 提供較明確的解析訊息；其他一般例外回錯誤類型與內容。先放特定例外，再放廣泛 Exception，才保留分流。KeyboardInterrupt 不屬於一般 Exception，不應當作正常抽取失敗繼續。')],
    '執行定義後，請學生口述成功與失敗兩種 result 型別；現在不要增加 API 呼叫。',
    '定義時0次 API。實際呼叫成功為 (True, dict)，失敗為 (False, str)。',
    '不可在 ok=False 時直接 result["title"]；錯誤文字不是 dict。safe 是錯誤介面包裝，不表示內容已被證明安全或正確。',
    '這個 True 是否表示客服摘要不超過30字元？預期回答：尚未，這裡沒有客服欄位檢查。'),
23: ('假回應：成功一項與八種負例', '35–60分｜完整離線示範',
    '我們故意準備失敗，不必為了看到一次拒答就反覆付費。這格把固定資料交給真正的解析器，檢查程式分支能否攔下問題。它沒有測模型。',
    [(1,5,'fake_response 用 SimpleNamespace 建一個可讀屬性的物件，預設有文字、completed 與空 output；changes 讓每個案例替換指定屬性。這不是 SDK 回應，也沒有發 HTTP。'),
     (7,16,'八個負例分別是拒答、兩種未完成原因、failed、缺狀態、空白文字、非 JSON、非 object。注意預設有可解析文字，但只要拒答或未完成，仍須先擋下。'),
     (17,25,'先驗證一項成功，再逐一呼叫解析器。except 印出預期原因；else 代表竟然沒有拋錯，必須主動 AssertionError。只有全部成功與負例行為成立，才印最後訊息。')],
    '執行前選 [] 與 incomplete 兩例請學生預測原因，執行後對照第20格的分支。',
    '八行負例原因，最後「完成1項成功與8項負例檢查。」；0 次 API。成功 fixture 只有 title，尚不符合完整事件五欄。',
    '若某項沒有被擋下，查完成與解析順序；不要把測試器的 fixture 當模型輸出或刪掉 else。',
    '只有 title 的假資料能通過這裡，為什麼稍後可能失敗？預期回答：解析器不檢查事件五欄。'),
25: ('事件 validator：補查五欄與本機規則', '35–60分｜完整離線示範',
    '能解析成 dict 只是第一步。後續程式會讀固定五欄，不能容忍少欄、多欄或把時間填成數字。我們再增加任務層的 validator，讓它回錯誤清單。',
    [(1,10,'先查 dict，再比 key 集合，接著查 title 是非空文字。先查 key 很重要：data.get("owner") 在缺 key 時也會得到 None，不能單靠 get 分清未知與漏欄。'),
     (11,15,'其餘四欄只能是 str 或 None。errors 空清單表示列出的本機規則都通過；函式不補欄位、不轉型，也不判斷原文事實。'),
     (17,26,'先測合法 fixture，再測缺 owner、空 title、數字 time、多出 status。負例的 assert 要求有錯誤，合法例要求沒有錯誤；同一個 assert 在兩個地方期待相反。')],
    '先讓學生分類四個負例，再執行。補充本 validator 對正式五欄 event_schema，不是 G 的六欄規格。',
    '印事件合法／缺欄／空title／型別／多欄檢查通過；0 次 API。',
    '若把 G 六欄結果交來，會多欄；回查使用了哪一份規格。合法的 A203 文字仍可能不是原文地點。',
    'errors=[] 能證明 A203 教室存在嗎？預期回答：不能，它只檢查指定欄位規則。'),
27: ('一般 prompt 的事件抽取基準', '35–60分｜真實比較，第1次',
    '比較要固定原文、模型、抽取規則和驗證方式，只改有沒有 API 層的格式設定。本格用一般文字要求五欄 JSON，沒有開 JSON mode。結果可以成功，我們照實記錄。',
    [(1,4,'先建立 event_text 與 EVENT_RULES。即使旗標 False，前兩行仍會定義資料，下一格可以直接使用；不必先成功執行一般 prompt。'),
     (5,9,'進入活動先清掉前一次結果，再呼叫 create。這次沒有 text.format，所以規格只存在於文字要求。清舊狀態避免重跑失敗卻誤看先前成功。'),
     (10,17,'先顯示原始文字，再解析與驗證五欄；ordinary_ok 含本機欄位檢查。例外轉成文字紀錄，不應算成內容答錯，也不能從一次結果推論全面穩定性。')],
    'helper、完成檢查、validator 與金鑰就緒後，開 RUN_EVENT_PLAIN 執行一次，立刻恢復 False；保存原始文字及 ordinary_result／ordinary_errors。',
    '預設0次；開啟為1次API。未知 owner 應為 null、日期保留「下週三」；這些是核對目標，並非本講稿實測輸出。',
    '若輸出有 Markdown 圍欄造成解析失敗，記下實際原文與錯誤；不要修改紀錄假裝成功。金鑰／網路失敗先處理環境。',
    '一般 prompt 這次成功，是否表示它具備 Schema 約束？預期回答：沒有，這次請求沒傳格式規格。'),
28: ('Structured Outputs 的同題抽取與成功層次', '35–60分｜真實比較，第2次',
    '現在使用同一段原文與同一套規則，另外送出 event_schema。觀察重點是請求設定與結果檢查，不是預先宣布這一版一定打敗上一版。',
    [(1,3,'本活動獨立開關，呼叫 safe helper 帶入原文、事件規格、格式名與規則。第27格前兩行必須已執行，但一般 prompt 旗標可以一直 False。'),
     (4,7,'event_ok 只表示完成與解析，event_errors 再查五欄，event_usable 才包含兩層都成功。若解析失敗，errors 雖是空清單，event_usable 仍是 False，不會誤判。')],
    '開 RUN_EVENT_STRICT 執行一次後恢復 False；保存 event_result、event_errors、event_usable，逐欄對照 event_text。',
    '預設0次，開啟1次API。結果應符合五欄及未知值規格，但仍須核對原文；沒有在此提供假想實測成果。',
    'ordinary_ok 與 event_ok 涵蓋層次不同；比較欄位是否合格應看 ordinary_ok 和 event_usable，並保留各自錯誤紀錄。',
    'event_errors=[]、event_ok=False，可否當成功？預期回答：不可，event_usable 還要求 event_ok。'),
31: ('客服規則與三題固定標準', '60–100分｜A必做，題目已提供',
    '第四週只做分類，本週一次抽取四個欄位。先讀規則再看資料，才知道答案的依據。分類、急迫性與是否回覆要各自判斷，不能全靠直覺。',
    [(1,7,'四個 category 固定。多類時帳務優先，再功能，再操作；明確要求今天處理是 high，沒有今天要求但服務無法用是 medium，其餘 low。求助或詢問需要回覆，純建議或稱讚不需要。摘要另有非空與30字元限制。'),
     (8,12,'三題原文與 expected 完整提供：重複扣款是帳務問題／high／True；匯出詢問是操作疑問／low／True；深色模式建議是其他／low／False。expected 沒列 summary，因為摘要可以有不同文字，仍須人工核對。')],
    '先不執行模型，請學生在紙上預測三題三欄，再對照規則。執行本格只建立常數。',
    '0 次API、沒有列印。SUPPORT_TESTS 稍後供離線入口檢查、單筆與三題活動使用。',
    '不要把 category 自創成「帳務」或「付款」；教材允許值是「帳務問題」。若不同意測試標準，先查規則，不改 expected 迎合這次模型。',
    '請求很客氣是否就等於 low？預期回答：應按明確規則，語氣不是本題急迫性判準。'),
33: ('A1參考答案：客服四欄 Schema', '60–100分｜A1必做；答案延後揭示',
    'A1 要把剛才的資料規格寫成 Schema。請把分類規則與欄位規格分開：規格限制有哪些選項，規則決定原文該選哪個選項。學生先完成 TODO，再看教師答案。',
    [(1,8,'函式回 dict，最外層 object，category 用 SUPPORT_LABELS，urgency 只允許 low、medium、high。enum 限制可選值，不能保證模型在這些值中選對。'),
     (9,10,'summary 是 string，description 說30字元內，但這裡沒有機器可檢查的 maxLength。稍後 Python 的 len 才真正補查。needs_reply 是 boolean，不能用文字 true 代替。'),
     (12,14,'四欄全列 required，禁止多餘 key。函式要 return 規格，不能只呼叫 print_json；執行定義沒有建立 support_schema，下一格呼叫後才保存。')],
    '學生填 A1，重跑函式定義，再開下一格 RUN_A_SCHEMA_CHECK；已提供資料與 helper 不必重寫。',
    '定義0次API。呼叫後回四欄規格，不是四欄抽取結果。',
    'NotImplementedError 回查學生骨架；布林寫成 string 或漏 required，修 A1 而非固定測試器。',
    'summary description 寫30字元，就會自動執行 len 檢查嗎？預期回答：不會，本機 validator 另做。'),
34: ('A1固定檢查與 support_schema 保存', '60–100分｜A1必做',
    '送到 API 前先確認自己寫的規格。這格不需要金鑰；規格有錯就先在本機修好，避免把程式問題帶到付費活動。',
    [(1,7,'開關內呼叫 A1 並保存 support_schema；查 object、properties 與 required 恰好四欄，另查 required 長度避免重複。'),
     (8,13,'查禁止額外欄位、兩組 enum，以及四欄的基本型別。最後的成功文字表示這些 assert 通過，沒有測真實模型，也不是任意 Schema 的完整驗證器。')],
    'A1完成後開 RUN_A_SCHEMA_CHECK，執行後恢復 False；保留 support_schema。',
    '印「A1契約通過；尚未測試模型。」；0 次API。',
    '錯誤停在哪個 assert，就回查對應欄位。若顯示先前版本，確認修改後是否重跑 A1 定義。',
    'A1檢查通過可否證明重複扣款一定會分對？預期回答：不能，這格只查規格。'),
36: ('客服 validator：型別、標籤與摘要字元數', '60–100分｜完整共用函式',
    '模型與 API 回來的資料仍要經過應用端檢查。validator 只回錯誤清單，不替模型改答案，不用自動轉型把上游問題藏起來。',
    [(1,11,'先要求 dict，查四個 key，然後核對 category 與 urgency 是否在允許值裡。這只能抓非法標籤；若帳務題選了合法的其他，仍須用 expected 與原文抓出。'),
     (12,15,'摘要先查 str，再做 strip 和 len。or 會短路，因此型別錯時不會硬做字串操作。strip 查全空白；len 查原字串長度，標點與空白也計入，這不是 token 數。'),
     (16,18,'needs_reply 必須是真正 bool。回 errors 空清單才表示本機列出的規則皆通過；這裡不檢查摘要是否忠於原文，也沒有修補或 API 呼叫。')],
    '執行定義；讓學生指出哪一行拒絕字串 true、哪一行拒絕31字元，接著跑下一格固定資料。',
    '定義本身無輸出，0 次API；呼叫回 list[str]。',
    '若把 not isinstance 或 len 的順序改壞，可能出現型別操作錯誤。不要把30字元當成30個 token。',
    '30字元內、分類合法的摘要能編造原因嗎？預期回答：仍可能，所以要查原文。'),
37: ('客服合法資料與六項負例', '60–100分｜完整離線示範',
    '這格直接測 validator，不依賴學生還沒完成的 A1、A2。先用能控制的資料知道程式會抓什麼，再討論模型會抽到什麼。',
    [(1,3,'support_fixture 是預寫好的合法客服資料。空 errors 是通過，這份資料不是任何人的真實模型成果。'),
     (4,15,'六項負例分別是缺 summary、多 status、非法 category、文字 true、31字元摘要、空白摘要。每次要求 errors 非空並印原因；如果負例竟然通過就停止。'),
     (16,17,'最後故意把帳務題改成合法類別「其他」，validator 仍回空清單。這個反例說明合法與正確的差別，是後面人工覆核的理由。')],
    '學生先預測每筆錯誤，再執行；保存或說明一個欄位失敗原因，勿把 fixture 填成 API 成果。',
    '六組錯誤清單，最後的合法但錯誤分類 assert 靜默通過；0 次API。',
    '只看到錯誤文字不代表程式壞了，本格正是預期負例。若最後 assert 失敗，查 validator 是否錯把原文判斷混進這份欄位函式。',
    '最後 category=其他為何沒有錯誤？預期回答：它是允許標籤，validator 未讀原文。'),
38: ('A2參考答案：把抽取、驗證與錯誤介面接起來', '60–100分｜A2必做；答案延後揭示',
    'A2 是本週要帶到後續 App 的核心入口。它不是只列印四欄，而是依序抽取、檢查，再回傳成功資料或失敗原因。請先完成學生骨架，再逐段核對教師實作。',
    [(1,4,'輸入 message 與可選 api_client；呼叫 safe helper 時，依序傳原文、A1規格、格式名、客服規則與 client。把 client 往下傳，離線假 client 才真的生效。'),
     (5,6,'safe helper 若失敗，立即回 False 與錯誤文字。此時不能繼續把 result 當 dict 送去取欄位。'),
     (7,10,'解析成功才跑客服 validator；有 errors 就組成錯誤字串。只有解析與欄位都通過，才回 True 與 dict。這個 True 比 safe helper 多了一層檢查，仍未證明內容忠於原文。')],
    '完成 A1、validator 與 A2 定義；不要在函式末尾只 print。接著先執行 A2離線檢查，還不開真實旗標。',
    '定義0次API；實際成功回 (True,dict)，失敗回 (False,str)。',
    '忘記 api_client 會讓假測試意外改走真實 client；漏 validator 會讓缺欄與過長摘要通過。由下一格固定測試定位。',
    'A2的 True 與第21格 safe helper 的 True 相同嗎？預期回答：不同，A2另外包含客服欄位規則。'),
40: ('A2固定測試器：假 client 與六項行為', '60–100分｜已提供測試器',
    '測模型恰好答對，不能證明自己的 A2 接對。我們把 A2 當正式函式照常執行，只把最底層 API 入口換成可控制的假 client，觀察參數與失敗處理。',
    [(1,10,'extractor 接的是函式物件。先準備五個回應：正常、缺摘要、摘要過長、拒答、未完成，對應一個 True 和四個 False。依賴前面的 fixtures、failure_cases 與 fake_response 都已建立。'),
     (11,21,'每個案例重設 local_calls，內層 local_create 收集請求；assert 核對原文、客服規則、Schema、strict 與 store。收到正確參數才回當前固定 response。這是本機函式呼叫，不是 HTTP。'),
     (22,30,'SimpleNamespace 把 responses.create 指到 local_create；把假 client 傳進 extractor。檢查二元組、成功旗標、一次假入口，以及成功值或非空錯誤文字。前五項的每次都必須確實走過假入口。'),
     (31,35,'第六項用空白輸入，必須失敗而且呼叫數不能增加。全部 assert 完成才回通過報告；五個固定回應加一項空白輸入，合計六項，不是六次真實模型測試。')],
    '先示範 extractor→A2→safe helper→假create→解析／validator 的路徑，再執行定義；實際檢查由下一格開關呼叫。',
    '單跑本格定義無輸出、0 次API；執行測試時也0次真實API。',
    '入口沒有被呼叫：查 A2 是否真的用 helper；參數不符：查 rules/schema/client；負例回 True：查 validator 或完成檢查。不要重寫測試器降低標準。',
    'fake client 回對了，能證明模型會分類嗎？預期回答：不能，回應是預寫的，只能證明程式行為。'),
41: ('執行自己的 A2離線檢查並保存報告', '60–100分｜A必做',
    '現在由你自己的 A2接受六項檢查。老師示範通過不等於你已通過；交件要保存自己的 support_local_report，並能解釋其中一個失敗分支。',
    [(1,2,'只開離線旗標，不需要金鑰；A1、A2與所有測試依賴要先完成並重新定義。'),
     (3,4,'傳入 extract_support_ticket 函式物件，這裡沒有先加括號執行。測試器內才會用不同假 client 呼叫；報告回來後用變數保存再列印。')],
    '開 RUN_A_LOCAL 執行，通過後恢復 False；記錄一項被拒絕的案例和負責函式。',
    '成功印「A2六項離線契約通過；這不是模型抽取成果。」；0 次API。',
    'NameError 查上游執行順序；NotImplementedError 查 TODO；AssertionError 查第40格停下位置。不要為了離線錯誤先開付費測試。',
    '為何傳 extract_support_ticket 而不是 extract_support_ticket()？預期回答：測試器需要稍後自行傳參數呼叫。'),
42: ('客服真實單筆：先確認資料可用', '60–100分｜A真實單筆，第3次',
    '離線通過後，才看模型對真正文字回什麼。先做一筆重複扣款，不要一開始就批次重跑。程式證據與模型內容證據分開保存。',
    [(1,3,'開旗標會把第一題原文送給 A2。support_ok 反映完成、解析與客服欄位檢查；support_result 成功是 dict，失敗是錯誤文字。'),
     (4,5,'三元條件只決定如何顯示；真正資料已保存到兩個變數。即使成功，仍查 category=帳務問題、urgency=high、needs_reply=True，並人工確認摘要沒有編造。')],
    'A1/A2離線通過且金鑰就緒後開 RUN_A_SINGLE，執行一次恢復 False；未執行就記「API未執行」。',
    '預設0次，開啟1次API；實際結果依本次回應記錄，本講稿不代填。',
    '錯誤文字先區分金鑰／網路、解析、欄位失敗；合法卻分類錯誤才回查原文與規則。',
    'print_json 顯示成功，是否代表已存到資料庫？預期回答：沒有，現在只保存在 Notebook 變數。'),
44: ('固定三題測試：extraction_ok 與 matches', '60–100分｜A真實三題，第4–6次',
    '單筆可用後再跑三題。這格一方面保留完整結果，一方面比對預先訂好的三個欄位。摘要不要求逐字相同，另外人工核對。',
    [(1,5,'cases 是測試清單，extractor 是函式物件。迴圈內每題呼叫一次，取得成功旗標與結果；不是把三題合併成一次請求。'),
     (6,10,'先看 ok，再用 all 對 expected 每個欄位比值。ok=False 會短路，避免對錯誤字串做 get。rows 保存原文、預期、結果與兩個旗標，最後 return 給呼叫端。'),
     (12,15,'開旗標後呼叫測試器並保存 support_rows。extraction_ok=False 是流程／欄位失敗；True 且 matches=False 是合法資料但答案不符；兩者 True 也還沒證明 summary 正確。')],
    '先確認單筆可用，再開 RUN_A_BATCH 執行一次後恢復 False。逐題對照原文，補摘要人工判讀與修改／保留理由。',
    '預設0次；開啟固定3次API。support_rows 為三筆 dict 的 list；三題通過僅代表這三題。',
    '不要改 expected 迎合模型。若不符，保留原始證據，先看哪個欄位；失敗例外已由 A2包成錯誤字串。',
    'matches=True 是否包含摘要的字句正確？預期回答：沒有，expected 只列三欄。'),
47: ('Pydantic入門：class、dict 與驗證後的物件', '100–110分｜共用完整示範',
    'Pydantic 是資料驗證工具，不是 AI 模型。前面手寫 Schema dict，現在改用 Python 宣告欄位。先用一張閱讀卡理解，再回到 B或C；本機驗證不會自動從文章抽取資訊。',
    [(1,8,'ReadingCard 是規格 class。BaseModel 提供驗證能力，不必寫 __init__ 或 self；ConfigDict 禁止多欄並開嚴格型別。pages 的 Field(ge=1) 是下限，不是預設1；Literal 固定值；Optional[str] 允許 None，但沒有預設值時 note 仍必填。'),
     (10,11,'傳入 dict，model_validate 成功才建立 toy_card 物件。用 toy_card.book_name 取屬性；model_dump 轉成 dict。一般 Python 型別註記本身不做執行期驗證，這裡是 BaseModel 使用宣告驗證。'),
     (12,22,'三個負例依序是字串10、pages=0、漏 note。預期都進 ValidationError；else 是沒有錯卻應該錯，主動停止。這裡的 strict 是本機型別檢查，與 API text.format.strict 的責任不同。')],
    '先讓學生預測三個負例，再執行。看正常物件與三行失敗訊息，帶回 B/C欄位宣告。',
    '顯示書名與 dict，再印3次「預期的欄位驗證失敗」；0 次API。',
    '若只看到 class 定義就以為有資料，指向第10行才真正建立物件。str 未設長度限制時仍可能接受空字串。[Models](https://docs.pydantic.dev/latest/concepts/models/)／[Strict Mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)',
    'note 可為 None，是否可以省略 key？預期回答：本例不可以，沒有給預設值。'),
49: ('Pydantic API入口：傳 class，回物件', '100–110分｜共用完整函式',
    '剛才 model_validate 是驗證手寫 dict。這格的 responses.parse 才會送原文與規格到 API，由 SDK 把資料模型接到輸出規格與解析流程。兩者都叫驗證，但有沒有模型請求必須分清楚。',
    [(1,7,'text 是原文，model_cls 是模型 class。先拒絕空白，再用 parse 的 text_format 傳 class；不能傳 ReadingCard()，那是在尚未提供必填值時建立資料物件。'),
     (8,12,'SDK 返回後仍查完成與拒答，再讀 output_parsed，必須非 None 且為指定 class 的物件。這裡回 parsed，不是 output_text 字串，也不是 dict，不需 json.loads。SDK 也可能在 parse 過程直接拋錯。'),
     (14,19,'外層 extract_structured 統一成 (True,物件) 或 (False,錯誤str)。呼叫端先看 ok，成功才用屬性或 model_dump；欄位驗證仍不能證明內容符合原文。')],
    '只建立定義；實際請求在 B或C的真實旗標。讓學生對照第18、21格的 dict 路徑。',
    '定義0次；有效入口實際呼叫一次 parse。成功回 BaseModel 子類物件。',
    '把物件丟 json.loads、對錯誤字串叫 model_dump 都是型別層次混淆。Field 所產生規格能否由教學帳號支援，仍須真實驗證。[官方 SDK解析路徑](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses)',
    'output_parsed 需要再 json.loads 嗎？預期回答：不需要，它已是解析後的資料物件。'),
51: ('B1參考答案：評論模型與固定欄位', '110–130分｜B/C擇一；B答案延後揭示',
    '第一次接觸資料模型，建議選 B。從評論抽姓名、評分、情緒與摘要。固定資料先供本機檢查，文章再供真實抽取，兩種證據不要混用。',
    [(1,2,'review_text 是待抽取原文；review_fixture 是人工預寫的合法資料。fixture 的存在不能證明模型會取得這些值。'),
     (4,11,'ReviewInsight 開 strict 與 extra forbid。姓名與摘要為 str；rating 是1到5整數，邊界包含；sentiment 是 positive、neutral、negative 三選一。學生只填欄位，不改共用 helper。')],
    '先補學生 B1，重跑 class 定義，再做本機檢查；先不開真實旗標。',
    '定義0次API、沒有顯示。完成模型才有四欄；學生 pass 雖可定義 class，並不代表完成。',
    '漏欄時 extra forbid 可能把 fixture 的欄位視為多餘；不要為了通過而關閉 forbid。str 宣告尚未限制摘要忠實性或空字串。',
    'Field(ge=1,le=5) 是預設幾分？預期回答：它不是預設值，而是合法範圍。'),
52: ('B本機檢查：合法物件與 rating=6', '110–130分｜選B者必做',
    '先證明模型宣告真的限制了資料，再呼叫 API。只測合法資料不夠，我們還故意放入超過上限的評分。',
    [(1,4,'開旗標後用 fixture 建立 review_local，再 model_dump 與原 dict 比對。review_local 是物件，dump 結果才是 dict。'),
     (5,10,'把 rating 換成6，預期 ValidationError；只有真的被擋下才印成功。else 用 AssertionError 抓出漏了評分限制的模型。')],
    '選B且完成B1後開 RUN_B_LOCAL，通過恢復 False；保存 review_local.model_dump() 與負例原因。',
    '印「B本機合法／超出評分範圍檢查通過」；0 次API。',
    '若合法 fixture 失敗，查四欄與標籤；若6通過，查 Field上下限。不要把這份手寫結果當真實抽取。',
    '這格通過是否證明 AI 看懂了五顆星？預期回答：沒有，沒有把原文送給模型。'),
53: ('B真實評論抽取與人工核對', '110–135分｜選B者真實活動，第7次',
    '現在把評論原文交給模型。成功後先把物件轉成 dict 顯示，再看評分與情緒。這兩項對了，姓名和摘要仍要回看原文。',
    [(1,4,'本機檢查通過與金鑰就緒後才開旗標。extract_structured 收 ReviewInsight class，成功 result 是物件；顯示時 model_dump，失敗顯示錯誤字串。'),
     (5,7,'這裡自動比較 rating=5、sentiment=positive，但沒有比姓名與摘要。人工查小明、五顆星、食物與服務敘述，不得把模型補出的新原因當成原文。')],
    '開 RUN_B_REVIEW 一次後恢復 False；保存實際 input、review_ok／review_result 與逐欄判讀。選B可直接跳到課堂覆核，C及作業區留課後。',
    '預設0次；開啟1次API。真實評分／情緒是否符合，以實際輸出為準。',
    'review_ok=False 時 result 是 str，不可叫 model_dump。沒有金鑰標未執行；不要用 review_fixture 代填。',
    '畫面評分／情緒符合 True，就能不看摘要嗎？預期回答：不行，這一行沒檢查摘要。'),
55: ('巢狀作業 Schema：array 與 items', '選C前導／課後選讀｜選B可跳過',
    '單一事件是一個 object；多筆作業需要一個清單。我們用外層 object 包住 assignments，再用 items 定義每一筆的欄位。這格是完整示範，不增加必做題。',
    [(1,10,'外層 properties 只有 assignments，它的 type 是 array。Schema 關鍵字 items 描述清單每一筆的規格，不是今天的實際作業內容。'),
     (11,22,'每筆是 object，包含 name、due_date、submission、late_policy。三欄允許 null，但四欄仍全部 required；內層 object 也禁止多欄，不是只處理最外層就完成。'),
     (23,34,'外層也有自己的 required 和 additionalProperties。後面的 assignment_text 是兩筆作業原文，print_json 顯示的仍是規格，不會自動解析這段文字。')],
    '選C者由 object→array→items object→四欄讀一次；選B者跳過本區。執行只定義與顯示。',
    '顯示巢狀規格；0 次API。空清單 [] 與 null 是不同值，本例允許 array 而非 null。',
    '別把 Schema 的 items、C訂單的 items 欄位、dict.items() 方法混為一談。每層的 required 都有自己的範圍。',
    '一份作業缺期限，應刪 due_date 嗎？預期回答：不可，本規格用 null。'),
56: ('讀巢狀規格與資料；額外API預設關閉', '選C前導／課後選讀｜額外請求不列主線',
    '先在本機讀一筆作業，再決定是否課後做真實抽取。這格同時有永遠會執行的離線示範與預設關閉的付費區，請看清楚縮排邊界。',
    [(1,4,'fixture 是 dict 包 list，第一筆再是 dict。第3行讀規格，得到 object；第4行讀資料，得到示範作業。範例已有一筆才可以用 [0]，若是空清單要先處理。'),
     (5,8,'RUN_ASSIGNMENT_DEMO 預設 False；開啟才把兩筆作業原文交給 safe helper。成功回 dict，但這段沒有另外的作業 validator，仍要人工逐筆核對。')],
    '課堂只跑離線前四行即可；課後如開真實旗標，完成後恢復 False並另記一次請求。',
    '預設印 object 與示範作業，0次API；開選讀旗標額外1次API，不包含在主線7次內。',
    '若 list 為空時索引錯誤，先查清單長度；不能因為 toy資料有一筆就假設所有資料都有。',
    '第3行與第4行都用中括號，為何一個是規格、一個是資料？預期回答：起點變數的責任不同。'),
58: ('C1/C2參考答案：商品子模型與完整訂單', '110–130分｜B/C擇一；C答案延後揭示',
    '選 C 的同學，要把一段訂單抽成可計算資料。先定義單筆商品，再用完整訂單包含商品清單。原文、手寫 fixture、資料模型是三種不同角色。',
    [(1,4,'receipt_text 是原文，order_fixture 是手寫測試資料：兩個耳機、單價990；一個保護殼、單價250；運費60。fixture 用 dict 與 list，還不是 Pydantic物件。'),
     (6,12,'先定義 OrderItem：品名 str、數量整數至少1、單價整數至少0。每筆商品都開嚴格型別與禁止多欄，避免計算前收到負數或錯型別。'),
     (15,22,'再定義 OrderInfo，items 為 list[OrderItem]，Pydantic 會逐筆驗證並建立商品物件；運費不得負數。這個模型未要求至少一筆商品，因此清單筆數和是否漏商品仍要對原文核對。')],
    '學生完成C1、C2，依子模型在前的順序重跑定義，再做第60格本機檢查。選B者不必完成C。',
    '0次API。驗證成功後 order.items 是商品物件清單，取 item.quantity，不是 item["quantity"]。',
    'OrderItem 尚未定義就用 list[OrderItem] 會出錯；若漏商品仍能通過型別檢查，回查原文，而非只看總額。',
    'list[OrderItem] 的中括號裡是今天的商品資料嗎？預期回答：不是，是每筆資料的型別規格。'),
60: ('C本機檢查：由程式計算金額與拒絕零數量', '110–130分｜選C者必做',
    '讓模型抽數量與單價，讓 Python 做乘加。先保證數值符合資料規格，再進行計算，計算結果才容易重現與查錯。',
    [(1,6,'calculate_order 接 OrderInfo物件，用 for 走過商品，以數量乘單價加總，回小計與含運費總額。它不改訂單、不呼叫模型，也沒有自行確認原文。'),
     (8,12,'本機旗標內先把 fixture 驗證成 order_local，再呼叫計算函式，用兩個變數接二元組。預期小計2230、總額2290。'),
     (13,20,'深拷貝後把第一筆數量改0，避免污染 fixture；預期 ValidationError。else 主動攔下錯誤規格。成功文字同時表示固定金額和零數量負例通過。')],
    'C1/C2完成後開 RUN_C_LOCAL，通過恢復 False；保存本機 dump 結果與非法數量原因。',
    '印「C本機金額／數量負例通過」；0次API。2×990+1×250=2230，再加60=2290。',
    '若算式不符，先查 fixture與欄位；item是物件，不能當dict讀。零數量通過則查 Field(ge=1)。',
    '金額算對，就能說商品名稱都對嗎？預期回答：不能，品名沒有參與這個算式。'),
61: ('C真實訂單抽取：先看欄位再信金額', '110–135分｜選C者真實活動，第7次',
    '本機公式正確之後，仍要確認真實模型抽到的數量與價格正確。公式只對輸入負責，錯資料也可能算出合理金額。',
    [(1,4,'開旗標送 receipt_text 與 OrderInfo class；成功物件先 dump顯示，失敗則顯示錯誤。這格不重用 fixture冒充模型結果。'),
     (5,8,'成功後用同一 calculate_order 計算，列印小計、總額與固定目標是否符合。除此之外仍逐欄查訂單編號、顧客、兩筆品名、數量、單價、運費。')],
    '本機通過與金鑰就緒後，開 RUN_C_ORDER一次並恢復False；記錄真實 input、order_ok／order_result、金額與人工覆核。',
    '預設0次，開啟1次API。2230／2290為核對目標，不是本講稿已取得的模型輸出。',
    '失敗結果是字串，不能傳進 calculate_order。若金額正確但品名錯，仍要記內容不符。',
    '為何不直接要求模型給總額就好？預期回答：抽取與確定性計算分工，便於重現與除錯。'),
64: ('Schema registry：取副本並保留版本', '課後選讀｜不列必交',
    'App 可能同時有事件與作業抽取。把規格集中登錄並命名版本，方便選用與追查。今天只看本機管理，不增加付費活動。',
    [(1,7,'registry 登錄兩份規格副本。這裡需要 assignment_schema；若選B時跳過作業區，課後讀本格前先執行第55格定義即可，不需開任何API旗標。v1只是字串命名，不會自動處理相容性。'),
     (10,24,'list_schema_names 接registry，排序後回名稱清單。docstring 解釋用途與輸出，執行時只跑最後的return；不是每行說明都會產生效果。'),
     (27,53,'get_schema 先確認名稱存在，不存在拋KeyError；存在回深拷貝。回傳副本讓呼叫端修改時不會改到正式登錄的巢狀內容，接回G的副本觀念。'),
     (56,63,'列出名稱，再實際取course_event_v1並顯示五個欄位。這裡不是只管理名稱，也拿到後續可用的規格，但沒有送API。')],
    '課後依賴就緒再執行；若要觀察副本隔離，可口頭追蹤修改selected_schema不改registry，勿在正式資料上直接修改。',
    '名稱依字母排序為course_assignments_v1、course_event_v1；取出event五欄，0次API。',
    'NameError查assignment_schema是否建立；KeyError查名稱是否登錄。這些都是本機規格選用問題，不是網路失敗。',
    '把v1欄位改掉就自動變v2嗎？預期回答：不會，要明確新增版本並管理使用端相容性。'),
66: ('巢狀會議模型：文字清單與物件清單', '課後選讀｜不列必交',
    '最後把相同觀念用到會議紀錄。出席名單是一串文字，待辦則是多筆有結構的資料。兩種list都很常見，但清單元素的責任不同。',
    [(1,6,'ActionItem是單筆待辦，負責人與工作為文字，due_date為Optional[str]且沒有預設值，所以必須提供key，可以填None。欄位宣告並沒有自動檢查是否編造負責人。'),
     (8,13,'MeetingMinutes的attendees為list[str]，action_items為list[ActionItem]，後者會逐筆驗證子欄位。先定義子模型，再定義外層模型。'),
     (15,17,'這裡傳入的是手寫dict，model_validate建立巢狀物件，再dump顯示。沒有從會議原文抽取、沒有API，也沒有原文可供事實判讀。')],
    '課後本機執行，觀察dump如何把巢狀物件轉回dict/list。若日後接parse，傳MeetingMinutes class，另計請求與真實驗證。',
    '顯示專題討論、範例小安與due_date=null的待辦；0次API。',
    '漏due_date會驗證失敗；不要為未知期限猜今天。這裡owner只有str規則，是否原文提供、是否空字串都不能只靠型別保證。',
    'attendees與action_items能互換資料嗎？預期回答：不能，一個要求字串元素，一個要求ActionItem結構。'),
}

def numbered(source):
    return '\n'.join(f'L{i:03d} │ {line}' for i, line in enumerate(source.splitlines(), 1))

def build():
    teacher = next((ROOT/'week06').glob('*150分鐘*教師版.ipynb'))
    student = next((ROOT/'week06').glob('*150分鐘*學生版.ipynb'))
    tn, sn = (json.loads(p.read_text(encoding='utf-8')) for p in (teacher, student))
    code = [(i+1,c) for i,c in enumerate(tn['cells']) if c['cell_type']=='code']
    assert {i for i,c in code} == set(LESSONS), '每一格都須有專屬講稿'
    assert len(code)==36 and len(tn['cells'])==len(sn['cells'])==70
    assert [c['id'] for c in tn['cells']]==[c['id'] for c in sn['cells']]
    header = f'''# 第06週｜150分鐘修訂版｜逐 Code Cell 教師講稿

製作日期：2026-10-19。用途：教師備課、對照投影與課堂口述。**內含教師參考答案，請勿直接作為學生未作答講義發放。**

## 使用方式與版本對應

- 教師版：[現行150分鐘教師Notebook]({teacher.name})。
- 學生版：[現行150分鐘學生Notebook]({student.name})。
- 範圍：以上兩份 Notebook 的全部36個 code cells；兩版各70個總 cells。不涵蓋原40格版本與Claude參考版。
- 本文 **C01–C36** 是只計code的講稿序號；**Notebook第N格**是從1起算、包含Markdown的總格序號；`cell ID`是穩定識別碼。Notebook顯示的`[ ]`或`[12]`是執行次數，不能拿來對應本稿。
- `L001`從各cell第一行起算，包含註解與空白行。原碼用`text`圍欄逐行附上行號，僅供對照；**請在原Notebook執行，不要連同L行號複製執行**。
- 每節先讀開場與逐段口述，再依操作演示。逐段口述的行號對應該節完整教師原碼；學生差異格另附S行號，避免把TODO骨架與答案混淆。
- 先修G、A，再做B/C擇一；教師答案在學生嘗試後才揭示。共用函式與固定測試器已提供，不要求學生全部重寫。
- 程式碼為製稿當下的原碼快照。後續若改Notebook，請重建並再核對講稿；以cell ID核對新版，避免只依舊格號。

## 授課節奏

| 時間 | 內容 | 對應講稿 |
|---|---|---|
| 0–15分 | 環境、JSON與dict | C01–C03 |
| 15–35分 | 事件Schema、深拷貝與G | C04–C07 |
| 35–60分 | 請求、完成／解析／欄位檢查、真實同題比較 | C08–C14 |
| 60–100分 | A1/A2、離線六項、真實單筆與三題 | C15–C24 |
| 100–110分 | Pydantic共同示範與API入口 | C25–C26 |
| 110–135分 | B評論或C訂單擇一；C先讀巢狀資料 | B：C27–C29；C：C30–C34 |
| 135–150分 | 同儕覆核、成果表與App銜接 | 文末收束；回Notebook成果紀錄文字格 |
| 課後 | registry、巢狀會議、重試設計 | C35–C36及原Notebook的R文字任務 |

休息另計。以下是備課完整講稿，不是要求150分鐘逐字念完。程式註解可略讀，依學生反應選用除錯與提問；B/C不要求兩題全做，延伸不列必交。

## 證據與請求數的讀法

本機fixture是手寫資料；假response/client是測程式用的固定回應；真實API結果必須由實際呼叫取得。本文「預期」是課堂觀察目標，沒有代填任何真實模型成果。旗標預設False時付費區不執行；本機定義、假測試與model_validate不呼叫模型。

完整主線各執行一次：一般事件1＋Structured事件1＋A單筆1＋A三題3＋B或C1＝**7次API請求**。作業清單選讀額外1次；重跑另計，請求數不是金額。若沒有金鑰，完成離線活動並標「API未執行」。

<a id="code-index"></a>

## 全部code cells對照索引

| 講稿 | Notebook總格號（雙版相同） | Cell ID | 主題 | 分工 |
|---|---:|---|---|---|
'''
    parts=[header]
    for seq,(nb,c) in enumerate(code,1):
        title,phase,*_=LESSONS[nb]
        changed=c['source']!=sn['cells'][nb-1]['source']
        parts.append(f'| [C{seq:02d}](#c{seq:02d}) | {nb} | `{c["id"]}` | {title} | {"學生TODO／教師答案" if changed else "雙版共用"} |\n')
    for seq,(nb,c) in enumerate(code,1):
        title,phase,opening,segments,operation,expected,debug,question=LESSONS[nb]
        source=''.join(c['source']); sc=sn['cells'][nb-1]; student_source=''.join(sc['source'])
        lines=source.splitlines()
        for a,b,words in segments:
            assert 1<=a<=b<=len(lines),(nb,a,b,len(lines))
        parts.append(f'\n---\n\n<a id="c{seq:02d}"></a>\n\n## C{seq:02d}｜{title}\n\n'
                     f'**對應位置：教師／學生Notebook第{nb}格；cell ID：`{c["id"]}`。**  \n'
                     f'**課堂定位：{phase}。**\n\n'
                     f'### 開場講稿\n\n> {opening}\n\n'
                     '### 完整教師原碼（L行號）\n\n```text\n'+numbered(source)+'\n```\n\n'
                     '### 逐段口述與程式對照\n\n')
        for a,b,words in segments:
            tag=f'L{a:03d}' if a==b else f'L{a:03d}–L{b:03d}'
            parts.append(f'**對應 {tag}：**\n\n> {words}\n\n')
        if source!=student_source:
            parts.append('### 學生版差異與揭示時機\n\n'
                         '學生版在同格、同ID保留以下骨架。S行號只對應學生原碼；上方L行號只對應教師原碼，兩者不可直接混用。先說明任務與回傳規格，讓學生嘗試後再展開教師答案。\n\n```text\n'
                         +numbered(student_source).replace('L0','S0')+'\n```\n\n')
        else:
            parts.append('**雙版對照：**學生版與上列教師原碼完全相同；本格不是額外TODO。\n\n')
        parts.append(f'### 操作、觀察與除錯\n\n'
                     f'- **帶做順序：**{operation}\n'
                     f'- **預期觀察／證據範圍：**{expected}\n'
                     f'- **失敗回查／限制：**{debug}\n\n'
                     f'### 課堂提問\n\n{question}\n\n[回全部code對照索引](#code-index)\n')
    parts.append('''
---

## 135–150分收束講稿：把程式證據與內容證據放回成果表

> 今天請先指出你完成的G、A，以及B或C。G要保存新增欄位的Schema並確認原規格未變；A要保存support_schema與自己的support_local_report，能說明一項失敗處理。離線通過的資料放在程式檢查紀錄，不要抄成真實模型回答。

> 如果你執行了真實API，請留下實際輸入與回應：A單筆的support_ok／support_result、三題的support_rows，以及你選題的review_result或order_result。沒執行就標API未執行，不用fixture補成果。摘要逐欄查原文，記錄至少一項修正或保留理由。

> 最後請同桌互問：required與null差在哪？A2的True檢查到哪一層？Pydantic成功回的是什麼型別？如果能指著程式回答，就已經把今天的資料流連起來。

> 下週會把文字功能接到介面，第八週再把抽取入口整合到自己的專題。這週的ok分流與驗證可以重用；Notebook的print只代表顯示，沒有自動完成App或寫進資料庫。使用Pydantic結果時，先視需要用model_dump轉為dict。

回原Notebook第45、62、68格文字區填成果與繳交檢核。第67格R重試任務只有Markdown設計規格，沒有code cell，所以不虛構第37個程式區；課後仍可依原任務設計假operation測試。

## 官方核對與講稿驗證邊界

- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses)：核對格式設定、required／nullable、拒答與Pydantic解析路徑；本稿C04、C08–C10、C26對照的是既有Notebook實作。
- [OpenAI Python SDK](https://developers.openai.com/api/reference/python)：核對max_retries與timeout責任；C02沿用既有設定，沒有把60秒當任務總時限。
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)與[Strict Mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)：核對class／instance／dump及本機嚴格型別；C25–C36沿用教材v2介面。

文件核對日：2026-10-19。本次產出是Markdown講稿，未改Notebook、未安裝套件、未呼叫付費API；文件與原碼對照不等於Colab、模型帳號可用性、瀏覽器呈現或150分鐘試教已驗證。講稿驗證只檢查36格覆蓋、雙版位置、原碼文字、行號範圍、Markdown結構與原Notebook未變。
''')
    # 雜湊記錄來源，避免後續只看日期就誤用過期講稿。
    parts.append('\n### 來源檔案SHA-256\n\n```text\n')
    for p in (teacher,student):
        parts.append(p.name+'\n'+hashlib.sha256(p.read_bytes()).hexdigest()+'\n')
    parts.append('```\n')
    result=''.join(parts)
    assert '\ufffd' not in result
    assert len(re.findall(r'^## C\d{2}｜',result,re.M))==36
    assert result.count('```')%2==0
    OUT.write_text(result,encoding='utf-8',newline='\n')
    print(f'已建立 {OUT.name}：36格專屬講稿，{len(result.splitlines())}行。')

if __name__=='__main__':
    build()
