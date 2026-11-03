"""第11週File Search資源教學：預設0請求；只在明確create／cleanup時操作。

在本資料夾執行：python resources.py --create 或 python resources.py --cleanup。
讀共用.env；僅管理本機紀錄的專用vector store與file，不列舉或刪除其他資源。
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

from dotenv import load_dotenv
from openai import OpenAI, NotFoundError

PACKAGE = Path(__file__).resolve().parent
MANIFEST = PACKAGE / ".file_search_resources.json"
DOCUMENT = PACKAGE / "sample_data/activities.txt"


def save(data):
    """每一步收到ID就保存；後續失敗仍可依紀錄清理，不保存金鑰。"""
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def create_resources(client):
    if MANIFEST.exists():
        previous = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if previous.get("vector_store_id") or previous.get("file_id"):
            raise ValueError("已有本次資源紀錄；請先cleanup，不重複建立")
    content = DOCUMENT.read_bytes()
    text = content.decode("utf-8-sig")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not text.strip() or len(text) > 3000 or len(paragraphs) > 8 or any(len(p) > 1000 for p in paragraphs):
        raise ValueError("文件限3000字元／8段／每段1000；請先核對與縮小範圍")
    data = {"document": DOCUMENT.name, "sha256": hashlib.sha256(content).hexdigest(),
            "vector_store_id": None, "file_id": None, "status": "starting"}
    save(data)
    # 1. 建專用索引並設閒置1日過期；過期不等於原始file已刪除。
    store = client.vector_stores.create(
        name="week11-simple-teaching", expires_after={"anchor": "last_active_at", "days": 1},
        metadata={"course": "week11_simple"},
    )
    data["vector_store_id"] = store.id
    data["status"] = "store_created"
    save(data)
    # 2. 上傳同一TXT。儲存與問答分開計費／計次，App重跑不走這段。
    with DOCUMENT.open("rb") as file:
        uploaded = client.files.create(file=file, purpose="assistants")
    data["file_id"] = uploaded.id
    data["status"] = "file_uploaded"
    save(data)
    # 3. 加入索引，接著有限次輪詢；不用SDK可能無限等待的poll helper。
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
    raise TimeoutError("索引尚未完成；已保存ID，請先檢查或cleanup，勿重複create")


def cleanup_resources(client):
    if not MANIFEST.exists():
        return {"status": "no_local_record"}
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = []
    # 只用本機紀錄內ID；不掃描帳號、不自動找其他索引。
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
            data[field] = None  # 已刪除或已過期，不把404當成仍存在。
        except Exception as exc:
            failures.append(type(exc).__name__)
        save(data)
    data["status"] = "cleanup_pending" if data.get("vector_store_id") or data.get("file_id") else "cleaned"
    save(data)
    if failures:
        raise RuntimeError("部分清理未完成；已保留未刪除ID，可稍後再cleanup")
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description="第11週專用資源管理；無參數時0次API")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--create", action="store_true", help="上傳文件、建索引；可能產生費用")
    group.add_argument("--cleanup", action="store_true", help="清理本機紀錄內的專用索引與原始file")
    args = parser.parse_args(argv)
    if not args.create and not args.cleanup:
        print("未操作平台，0次API。讀README後才明確加--create或--cleanup。")
        return
    load_dotenv(PACKAGE / ".env")
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise ValueError("請先在本機.env或環境變數設定OPENAI_API_KEY")
    with OpenAI(api_key=key, max_retries=0, timeout=60.0) as client:
        result = create_resources(client) if args.create else cleanup_resources(client)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("操作未完成：", type(exc).__name__, "；請保留資源紀錄，依README檢查或清理。")
        raise SystemExit(1)
