# 第7週Streamlit課堂簡化版範例

每個.py獨立啟動，彼此沒有import關係。student保留A/B/C小練習，teacher有參考答案；其餘範例完整提供。
原`../week07_streamlit_app/`保留整合參考；不要把這裡的程式拼到原app.py。

## 安裝與啟動

VS Code開啟本資料夾。Windows PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
python -m streamlit run student/01_inputs.py
```

macOS/Linux使用`python3.12 -m venv .venv`、`source .venv/bin/activate`，再安裝與啟動。
想換範例，先在終端機Ctrl+C停止，將命令檔名替換為下表檔案。教師示範把student改為teacher。
不使用Notebook或直接`python 某檔.py`執行App。若從課程根目錄操作，先`cd week07/week07_streamlit_simple`。

| 檔案 | 用途 | 預設模型請求 |
|---|---|---:|
| 01_inputs.py | 輸入、按鈕、顯示，A小練習 | 0 |
| 02_state.py | 普通變數與狀態，B小練習 | 0 |
| 03_form_ai.py | 表單與第6週五欄活動抽取，C顯示小練習 | 0 |
| 04_chat.py | 非串流聊天、最近五輪、清空 | 0 |
| 05_streaming.py | 完整串流對照，無需修改04 | 0 |
| 06_file.py | UTF-8文字檔預覽與選用摘要 | 0 |
| 07_layout.py | 側欄、分頁的獨立短例 | 0 |

## 真實API與資料

預設都離線。.env.example另存.env後私下填金鑰；啟動後勾選真實API，再有效送出才最多1次請求。
`load_dotenv()`從程式所在資料夾向上找.env；請把.env放在本README同層，勿在範例子資料夾再放另一份。
切換聊天模式會清空紀錄。固定離線回答不代表模型記憶；03離線固定卡不代表抽取輸入；06離線是原文片段而非摘要。
文字／活動資料均為虛構。不要提交.env或secrets.toml，不上傳個資與機密；store=False仍會把啟用API時的輸入送出。
每輪聊天限1000字元、只送最近10則完成訊息，03限3000字元，06限64KB／6000字元。字元不是token或費用估算。
API max_retries=0、timeout=60，60秒是網路等待起始值；手動重跑另計，失敗不代表免費。
03成功仍須對原文，04/05只有成功才保存完整一輪；上傳會先確認編碼與長度再處理。

## 課前與驗證

requirements沿用原第7週目標版本，請在課堂Python3.12環境確認安裝。現有本機離線檢查環境可能不同，詳見教師導讀。
檢查方式：在課程repo根目錄用已安裝Streamlit的環境執行`scripts/verify_week07_simple.py`。
未以真實API、真人瀏覽器、目標環境安裝、雲端部署或150分鐘試教驗證時，不宣稱這些已通過。
詳見上層雙版講義與[教師導讀](../第07週_課堂簡化版_教師導讀與修訂紀錄.md)。
