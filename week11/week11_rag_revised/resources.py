"""第11週修訂版File Search資源管理：預設0請求；只在明確--create／--cleanup時操作平台。

在本資料夾（week11_rag_revised）執行：
  python resources.py                          只顯示說明，0次API
  python resources.py --create                 上傳預設文件並建立索引（可能產生費用）
  python resources.py --create --document 檔案.txt   作業換文件時使用
  python resources.py --cleanup                刪除本機紀錄內的索引與原始檔案
讀本資料夾的.env；只管理本機紀錄裡的專用索引與檔案，不列舉或刪除帳號的其他資源。
"""
import argparse
import json
import os
from pathlib import Path
import time

from dotenv import load_dotenv
from openai import OpenAI, NotFoundError

PACKAGE = Path(__file__).resolve().parent
MANIFEST = PACKAGE / ".file_search_resources.json"
DEFAULT_DOCUMENT = PACKAGE / "sample_data/week09_cleaned_text.txt"


def text_digest(text):
    """完整提供：文件內容指紋；統一換行、去掉頭尾空白後計算（Notebook、App與resources.py同一規則）。"""
    import hashlib
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def save(data):
    """每一步收到ID就保存；之後失敗仍可依紀錄清理。不保存金鑰。"""
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def check_document(document):
    """與App相同的範圍：UTF-8的TXT／MD，1～6000字元、最多12段、每段1000字元。"""
    if document.suffix.lower() not in (".txt", ".md"):
        raise ValueError("本週只上傳UTF-8的.txt或.md小文件")
    text = document.read_bytes().decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not text.strip() or len(text) > 6000 or len(paragraphs) > 12 or any(len(p) > 1000 for p in paragraphs):
        raise ValueError("文件限6000字元、12段、每段1000字元；請先核對並縮小範圍")
    return text


def create_resources(client, document=DEFAULT_DOCUMENT):
    if MANIFEST.exists():
        previous = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if previous.get("vector_store_id") or previous.get("file_id"):
            raise ValueError("已有本次資源紀錄；請先cleanup，不重複建立")
    text = check_document(document)
    data = {"document": document.name, "sha256": text_digest(text),
            "vector_store_id": None, "file_id": None, "status": "starting"}
    save(data)
    # 1. 建專用索引，閒置1日後過期；過期不等於原始檔案已刪除。
    store = client.vector_stores.create(
        name="week11-revised-teaching", expires_after={"anchor": "last_active_at", "days": 1},
        metadata={"course": "week11_revised"},
    )
    data["vector_store_id"] = store.id
    data["status"] = "store_created"
    save(data)
    # 2. 上傳文件。儲存與問答分開計費；App重跑不會走到這裡。
    with document.open("rb") as file:
        uploaded = client.files.create(file=file, purpose="assistants")
    data["file_id"] = uploaded.id
    data["status"] = "file_uploaded"
    save(data)
    # 3. 加入索引，再有限次查詢狀態（不用可能無限等待的poll helper）。
    client.vector_stores.files.create(vector_store_id=store.id, file_id=uploaded.id)
    for attempt in range(10):
        indexed = client.vector_stores.files.retrieve(uploaded.id, vector_store_id=store.id)
        data["status"] = indexed.status
        save(data)
        if indexed.status == "completed":
            return data
        if indexed.status in ("failed", "cancelled"):
            raise ValueError("索引處理失敗，請依本機紀錄cleanup後再查原因")
        if attempt < 9:
            time.sleep(2)
    raise TimeoutError("索引尚未完成；已保存ID，請先檢查或cleanup，不要重複create")


def cleanup_resources(client):
    if not MANIFEST.exists():
        return {"status": "no_local_record"}
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = []
    # 只用本機紀錄裡的ID；不掃描帳號、不自動找其他索引。
    for field in ["vector_store_id", "file_id"]:
        identifier = data.get(field)
        if not identifier:
            continue
        try:
            deleted = (client.vector_stores.delete(identifier) if field == "vector_store_id"
                       else client.files.delete(identifier))
            if not deleted.deleted:
                raise ValueError("平台未確認刪除")
            data[field] = None
        except NotFoundError:
            data[field] = None   # 已刪除或已過期，不把404當成仍存在
        except Exception as exc:
            failures.append(type(exc).__name__)
        save(data)
    data["status"] = "cleanup_pending" if data.get("vector_store_id") or data.get("file_id") else "cleaned"
    save(data)
    if failures:
        raise RuntimeError("部分清理未完成；已保留未刪除的ID，可稍後再cleanup")
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description="第11週修訂版File Search資源管理；不加參數時0次API")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--create", action="store_true", help="上傳文件並建立索引；可能產生費用")
    group.add_argument("--cleanup", action="store_true", help="清理本機紀錄內的索引與原始檔案")
    parser.add_argument("--document", type=Path, default=DEFAULT_DOCUMENT, help="要上傳的.txt或.md（預設為範例文字）")
    args = parser.parse_args(argv)
    if not args.create and not args.cleanup:
        print("未操作平台，0次API。讀完README後，再明確加上--create或--cleanup。")
        return
    load_dotenv(PACKAGE / ".env")
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise ValueError("請先在本資料夾的.env或環境變數設定OPENAI_API_KEY")
    with OpenAI(api_key=key, max_retries=0, timeout=60.0) as client:
        result = create_resources(client, args.document) if args.create else cleanup_resources(client)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.create and result.get("status") == "completed":
        # 紀錄檔不提交；部署到Streamlit Cloud或在Colab使用時，把這三行貼到Secrets（本機也可寫進.env）
        print("\n部署或Colab：把下面三行貼到Secrets（.env請把「 = 」改成「=」並去掉引號）")
        print(f'OPENAI_VECTOR_STORE_ID = "{result["vector_store_id"]}"')
        print(f'OPENAI_FILE_ID = "{result["file_id"]}"')
        print(f'FILE_SEARCH_SHA256 = "{result["sha256"]}"')


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("操作未完成：", type(exc).__name__, exc, "；請保留資源紀錄，依README檢查或清理。")
        raise SystemExit(1)
