"""第 12 週｜圖片驗證、Vision prompt 與 Responses API helper（Claude 版）。

這個模組不畫 Streamlit 畫面，讓圖片驗證、data URL 組裝、prompt、回應分流
都能在不開瀏覽器、也不呼叫付費 API 的情況下單獨測試。

helper 命名（`detect_image_mime` / `validate_image` / `image_to_data_url` /
`build_task_prompt` / `get_refusal_reason` / `require_completed_response` /
`analyze_image` / `RECEIPT_SCHEMA`）與 Codex 版 `week12_vision_app/` 一致，
兩版可互換對照。Claude 版另外多了：
- `build_request()` + `preview_request()`：只看送出的 request 結構（data URL 截短），不呼叫 API。
- `analyze_image(..., offline=True)`：離線示範模式，回傳標註「示範用」的固定樣本。
- `choose_detail()` / `normalize_receipt()` / `evaluate_vision_answer()`：課堂練習 helper。
"""

from __future__ import annotations

import base64
from io import BytesIO
import json
import os
from typing import Any

from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError


DEFAULT_MODEL = "gpt-5.4-mini"
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
SUPPORTED_MIME_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
TASK_MODES = ("圖片描述", "圖片問答", "截圖檢查", "收據／表單抽取")
DETAIL_LEVELS = ("auto", "low", "high")
OFFLINE_DEMO_NOTICE = "（離線示範：這不是模型分析結果，只用來驗證流程與畫面）"

SYSTEM_INSTRUCTIONS = (
    "你是謹慎的圖片理解助理。回答使用繁體中文；區分圖片直接證據與推論；"
    "無法確認的文字、數字、人物身分或情境不可猜測。"
)

RECEIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "document_type": {
            "type": "string",
            "description": "文件類型，例如 receipt、invoice、form 或 unknown。",
        },
        "merchant": {
            "type": ["string", "null"],
            "description": "可從圖片辨識的商家或機構名稱；無法確認時為 null。",
        },
        "date": {
            "type": ["string", "null"],
            "description": "文件日期，保持圖片中的格式；無法確認時為 null。",
        },
        "currency": {
            "type": ["string", "null"],
            "description": "可確認的幣別；無法確認時為 null。",
        },
        "total": {
            "type": ["number", "null"],
            "description": "可確認的總額數值；不得推測。",
        },
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "quantity": {"type": ["number", "null"]},
                    "amount": {"type": ["number", "null"]},
                },
                "required": ["name", "quantity", "amount"],
                "additionalProperties": False,
            },
        },
        "visible_text": {
            "type": "array",
            "items": {"type": "string"},
            "description": "圖片中確實可讀的重要文字片段。",
        },
        "warnings": {
            "type": "array",
            "items": {"type": "string"},
            "description": "模糊、遮擋、欄位矛盾或無法確認之處。",
        },
    },
    "required": [
        "document_type",
        "merchant",
        "date",
        "currency",
        "total",
        "items",
        "visible_text",
        "warnings",
    ],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# 金鑰與 client
# ---------------------------------------------------------------------------
def get_secret(name: str, default: str | None = None) -> str | None:
    """讀取 Streamlit Secrets 或 `.env`，不把秘密印出或寫入 log。"""
    try:
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        # 本機沒有 secrets.toml（或不在 Streamlit 內執行）時改讀 .env。
        pass
    load_dotenv()
    return os.getenv(name, default)


def create_client():
    """建立 OpenAI client；缺少金鑰時先轉成可操作的課堂錯誤。"""
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 OPENAI_API_KEY，請先設定 `.env` 或 Streamlit Secrets。")
    from openai import OpenAI

    return OpenAI(api_key=api_key)


# ---------------------------------------------------------------------------
# 圖片驗證與編碼
# ---------------------------------------------------------------------------
def detect_image_mime(file_bytes: bytes) -> str:
    """依檔案 signature（magic bytes）判斷圖片格式，不只相信副檔名或瀏覽器 MIME。

    參數：
        file_bytes: 圖片原始 bytes。

    回傳：
        "image/png"、"image/jpeg"、"image/gif" 或 "image/webp"。

    可能錯誤：
        ValueError: 不是支援的四種格式。

    教學重點：
        上傳器的 type= 篩選只看副檔名；把 .txt 改名成 .png 一樣能通過。
    """
    if file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if file_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if file_bytes.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if len(file_bytes) >= 12 and file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP":
        return "image/webp"
    raise ValueError("檔案內容不是支援的 PNG、JPEG、WEBP 或非動態 GIF 圖片。")


def validate_image(file_bytes: bytes) -> dict[str, Any]:
    """在呼叫付費 API 前檢查大小、格式、影格與像素量，回傳可供 UI 顯示的 metadata。

    參數：
        file_bytes: 圖片原始 bytes。

    回傳：
        dict，含 mime_type、format、width、height、megabytes。

    可能錯誤：
        ValueError: 空檔、超過 8 MB、格式不支援、檔案損壞、動態 GIF、像素過多。

    教學重點：
        `st.file_uploader(type=...)` 只是第一層篩選；正式程式仍要檢查收到的 bytes，
        才不會把錯誤副檔名、損壞檔或過大的圖片送進付費 API。
    """
    if not file_bytes:
        raise ValueError("圖片內容是空的，請重新選擇檔案。")
    if len(file_bytes) > MAX_FILE_BYTES:
        raise ValueError("圖片超過 8 MB，請縮小尺寸或降低品質後再試。")

    detected_mime = detect_image_mime(file_bytes)
    if detected_mime not in SUPPORTED_MIME_TYPES:
        raise ValueError("目前不支援這個圖片格式。")

    try:
        with Image.open(BytesIO(file_bytes)) as image:
            width, height = image.size
            image_format = image.format
            is_animated = bool(getattr(image, "is_animated", False))
            image.verify()
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise ValueError("圖片檔已損壞或無法解碼，請換一個檔案。") from exc

    if width <= 0 or height <= 0:
        raise ValueError("圖片尺寸無效。")
    if width * height > MAX_IMAGE_PIXELS:
        raise ValueError("圖片像素過多，請縮小到 2,000 萬像素以內再試。")
    if detected_mime == "image/gif" and is_animated:
        raise ValueError("Vision 範例只接受非動態 GIF，請轉成單張 PNG 或 JPEG。")

    return {
        "mime_type": detected_mime,
        "format": image_format,
        "width": width,
        "height": height,
        "megabytes": round(len(file_bytes) / (1024 * 1024), 3),
    }


def image_to_data_url(file_bytes: bytes, mime_type: str) -> str:
    """把圖片 bytes 轉成 Responses API `input_image` 可用的 Base64 data URL。"""
    if mime_type not in SUPPORTED_MIME_TYPES:
        raise ValueError("不支援的圖片 MIME type。")
    encoded = base64.b64encode(file_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


# ---------------------------------------------------------------------------
# Prompt 與 detail
# ---------------------------------------------------------------------------
def build_task_prompt(mode: str, question: str = "") -> str:
    """集中管理四種圖片任務的 prompt，要求模型區分「可見證據」與「推論」。

    參數：
        mode: TASK_MODES 之一。
        question: 圖片問答模式的問題；其他模式忽略。

    回傳：
        送給模型的任務文字。

    可能錯誤：
        ValueError: 未知模式，或問答模式沒有輸入問題。

    教學重點：
        只問「這張圖是什麼？」容易得到過度概括的答案；好的 prompt 要指定任務、
        輸出順序、不可猜測的項目，以及看不清楚時的回覆方式。
    """
    if mode == "圖片描述":
        return (
            "請用繁體中文描述圖片。先列出直接可見的物件、人物、文字與場景，"
            "再用『可能的推論』標示不確定的解讀；看不清楚時要明確說明。"
        )
    if mode == "圖片問答":
        cleaned_question = question.strip()
        if not cleaned_question:
            raise ValueError("請先輸入想詢問圖片的問題。")
        return (
            f"請根據圖片回答：{cleaned_question}\n"
            "只把圖片中可見內容當作證據；若無法從圖片確認，請直接說明不足，"
            "不要補造日期、數字、身分或背景故事。"
        )
    if mode == "截圖檢查":
        return (
            "這是一張介面或錯誤畫面截圖。請依序整理："
            "(1) 可見文字，(2) 畫面目前狀態，(3) 可能問題，"
            "(4) 使用者可自行確認的下一步。不要假裝已操作畫面。"
        )
    if mode == "收據／表單抽取":
        return (
            "請抽取圖片中確實可見的收據、發票或表單資料。"
            "模糊欄位使用 null，並在 warnings 說明；不得自行補齊商家、日期、"
            "幣別、金額或品項。"
        )
    raise ValueError(f"未知的任務模式：{mode}")


def choose_detail(task: str) -> str:
    """依任務文字建議圖片細節等級：文件、小字、表單、截圖用 high；粗略分類用 low；其餘 auto。

    這是課堂規則，不是模型品質保證；目的是讓 App 的成本／品質選擇可以被測試與說明。
    """
    normalized = task.strip().lower()
    if any(keyword in normalized for keyword in ("收據", "表單", "小字", "截圖", "文件", "發票", "ocr")):
        return "high"
    if any(keyword in normalized for keyword in ("粗略", "大意", "分類", "有沒有")):
        return "low"
    return "auto"


# ---------------------------------------------------------------------------
# 回應分流
# ---------------------------------------------------------------------------
def get_refusal_reason(response: Any) -> str | None:
    """從 Responses API 的 output/content 找出拒答原因；拒答不一定出現在 output_text。"""
    for output_item in getattr(response, "output", []) or []:
        content = (
            output_item.get("content", [])
            if isinstance(output_item, dict)
            else getattr(output_item, "content", [])
        )
        for content_item in content or []:
            refusal = (
                content_item.get("refusal")
                if isinstance(content_item, dict)
                else getattr(content_item, "refusal", None)
            )
            if refusal:
                return str(refusal)
    return None


def require_completed_response(response: Any) -> str:
    """只接受已完成且有文字的回應，避免把拒答、半成品或空輸出當成正式結果。

    可能錯誤：
        RuntimeError: 拒答、未完成（長度限制／內容過濾）、狀態異常、沒有文字。
    """
    refusal = get_refusal_reason(response)
    if refusal:
        raise RuntimeError(f"AI 拒絕處理這張圖片：{refusal}")

    status = getattr(response, "status", None)
    if status == "incomplete":
        details = getattr(response, "incomplete_details", None)
        reason = details.get("reason") if isinstance(details, dict) else getattr(details, "reason", None)
        if reason == "max_output_tokens":
            raise RuntimeError("AI 回應因輸出長度限制而未完成，請縮小任務範圍。")
        if reason == "content_filter":
            raise RuntimeError("圖片或問題觸發內容過濾，請改用合適的課堂測試資料。")
        raise RuntimeError("AI 回應未完成，請稍後再試。")
    if status not in (None, "completed"):
        raise RuntimeError(f"AI 回應未成功（狀態：{status}）。")

    output_text = (getattr(response, "output_text", None) or "").strip()
    if not output_text:
        raise RuntimeError("AI 沒有回傳可顯示的文字結果。")
    return output_text


# ---------------------------------------------------------------------------
# 組 request、離線示範、正式呼叫
# ---------------------------------------------------------------------------
def build_request(
    file_bytes: bytes,
    *,
    mode: str,
    question: str = "",
    detail: str = "auto",
    model: str | None = None,
) -> dict[str, Any]:
    """驗證圖片並組出 `client.responses.create(**request)` 要用的參數 dict（不呼叫 API）。"""
    if detail not in DETAIL_LEVELS:
        raise ValueError("detail 只接受 low、high 或 auto。")
    metadata = validate_image(file_bytes)
    prompt = build_task_prompt(mode, question)
    data_url = image_to_data_url(file_bytes, metadata["mime_type"])

    request: dict[str, Any] = {
        "model": model or get_secret("OPENAI_MODEL", DEFAULT_MODEL),
        "instructions": SYSTEM_INSTRUCTIONS,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": data_url, "detail": detail},
                ],
            }
        ],
        # 不保存本次回應供之後 API 取回；但圖片仍會傳到外部服務處理。
        "store": False,
    }
    if mode == "收據／表單抽取":
        request["text"] = {
            "format": {
                "type": "json_schema",
                "name": "visual_document_result",
                "schema": RECEIPT_SCHEMA,
                "strict": True,
            }
        }
    return request


def preview_request(request: dict[str, Any], max_url_chars: int = 60) -> dict[str, Any]:
    """回傳把 Base64 data URL 截短後的 request 複本，方便印出來看結構而不洗版。"""
    preview = json.loads(json.dumps(request, ensure_ascii=False))
    for message in preview.get("input", []):
        for item in message.get("content", []):
            url = item.get("image_url")
            if isinstance(url, str) and len(url) > max_url_chars:
                item["image_url"] = f"{url[:max_url_chars]}...（共 {len(url)} 字元）"
    if "text" in preview:
        preview["text"]["format"]["schema"] = "（RECEIPT_SCHEMA，略）"
    return preview


def offline_demo_result(mode: str) -> str | dict[str, Any]:
    """離線示範用的固定樣本；每個結果都明確標註不是模型輸出。"""
    if mode == "收據／表單抽取":
        return {
            "document_type": "receipt",
            "merchant": "DEMO CAFE",
            "date": "2026-09-16",
            "currency": "TWD",
            "total": 300,
            "items": [
                {"name": "Coffee", "quantity": 2, "amount": 160},
                {"name": "Sandwich", "quantity": 1, "amount": 95},
                {"name": "Notebook", "quantity": 1, "amount": 45},
            ],
            "visible_text": ["DEMO CAFE - CLASSROOM FIXTURE", "TOTAL TWD 300"],
            "warnings": [OFFLINE_DEMO_NOTICE],
        }
    samples = {
        "圖片描述": "可見：白底、黑色英文文字、數行金額。可能的推論：這是一張收據。",
        "圖片問答": "圖片中可見 TOTAL TWD 300；其他資訊無法從圖片確認。",
        "截圖檢查": "(1) 可見文字：略 (2) 狀態：略 (3) 可能問題：略 (4) 下一步：請自行確認。",
    }
    return f"{samples.get(mode, '（無樣本）')}\n\n{OFFLINE_DEMO_NOTICE}"


def analyze_image(
    file_bytes: bytes,
    *,
    mode: str,
    question: str = "",
    detail: str = "auto",
    model: str | None = None,
    offline: bool = False,
) -> str | dict[str, Any]:
    """驗證圖片後呼叫 Responses API，回傳文字或結構化抽取結果。

    參數：
        file_bytes: 圖片 bytes。
        mode: TASK_MODES 之一；抽取模式會附 JSON Schema。
        question: 問答模式的問題。
        detail: "auto" / "low" / "high"。
        model: 覆蓋預設模型。
        offline: True 時不呼叫 API，只跑驗證與 prompt 組裝，回傳標註過的示範樣本。

    回傳：
        文字（描述／問答／截圖）或 dict（抽取模式）。

    可能錯誤：
        ValueError: 圖片或參數不合法。
        RuntimeError: 缺金鑰、拒答、未完成、空輸出、JSON 解析失敗。

    教學重點：
        `store=False` 只表示不保存回應供後續取回，圖片仍會送到外部服務；
        因此課堂只用自製或明確授權、且不含敏感資料的圖片。
    """
    request = build_request(file_bytes, mode=mode, question=question, detail=detail, model=model)
    if offline:
        return offline_demo_result(mode)

    client = create_client()
    response = client.responses.create(**request)
    output_text = require_completed_response(response)
    if mode != "收據／表單抽取":
        return output_text
    try:
        return json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("AI 回傳的結構化資料無法解析，請檢查模型與 schema。") from exc


# ---------------------------------------------------------------------------
# 結果整理與基本評估（課堂練習 helper）
# ---------------------------------------------------------------------------
def normalize_receipt(result: dict) -> dict:
    """把抽取結果整理成 UI 可安全讀取的固定結構；缺清單補空 list，缺單值保留 None，不補假資料。"""
    return {
        "document_type": result.get("document_type") or "unknown",
        "merchant": result.get("merchant"),
        "date": result.get("date"),
        "currency": result.get("currency"),
        "total": result.get("total"),
        "items": list(result.get("items") or []),
        "visible_text": list(result.get("visible_text") or []),
        "warnings": list(result.get("warnings") or []),
    }


def evaluate_vision_answer(answer: str) -> dict:
    """用可解釋的關鍵詞規則檢查回答是否標示證據與不確定性；不代表語意正確，仍需人工覆核。"""
    cleaned = answer.strip()
    evidence_terms = ("可見", "圖片中", "畫面中", "文字顯示")
    uncertainty_terms = ("無法確認", "可能", "看不清楚", "資訊不足")
    return {
        "not_empty": bool(cleaned),
        "mentions_evidence": any(term in cleaned for term in evidence_terms),
        "marks_uncertainty": any(term in cleaned for term in uncertainty_terms),
        "needs_human_review": True,
    }
