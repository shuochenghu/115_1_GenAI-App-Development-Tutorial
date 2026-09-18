"""第 12 週圖片驗證、Vision prompt 與 Responses API helper。

這個模組不直接繪製 Streamlit 畫面，讓圖片檢查、data URL 組裝與回應分流
可以在不啟動瀏覽器、也不呼叫付費 API 的情況下單獨測試。
"""

from __future__ import annotations

import base64
from io import BytesIO
import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, UnidentifiedImageError


DEFAULT_MODEL = "gpt-5.4-mini"
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
SUPPORTED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
}

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


def get_secret(name: str, default: str | None = None) -> str | None:
    """讀取 Streamlit Secrets 或 `.env`，且不把秘密顯示或寫入 log。"""

    try:
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        # 本機沒有 secrets.toml 時，改讀取 App 目錄中的 `.env`。
        pass

    load_dotenv()
    return os.getenv(name, default)


def create_client() -> OpenAI:
    """建立 OpenAI client；缺少金鑰時先轉成可操作的課堂錯誤。"""

    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "找不到 OPENAI_API_KEY，請先設定 `.env` 或 Streamlit Secrets。"
        )
    return OpenAI(api_key=api_key)


def detect_image_mime(file_bytes: bytes) -> str:
    """依檔案 signature 判斷圖片格式，不只相信副檔名或瀏覽器 MIME。"""

    if file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if file_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if file_bytes.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if (
        len(file_bytes) >= 12
        and file_bytes.startswith(b"RIFF")
        and file_bytes[8:12] == b"WEBP"
    ):
        return "image/webp"
    raise ValueError("檔案內容不是支援的 PNG、JPEG、WEBP 或非動態 GIF 圖片。")


def validate_image(file_bytes: bytes) -> dict[str, Any]:
    """檢查大小、格式、影格與像素量，回傳可供 UI 顯示的 metadata。

    `st.file_uploader(type=...)` 只是第一層篩選；正式程式仍應檢查收到的 bytes，
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
    """把圖片 bytes 轉成 Responses API `input_image` 可用的 data URL。"""

    if mime_type not in SUPPORTED_MIME_TYPES:
        raise ValueError("不支援的圖片 MIME type。")
    encoded = base64.b64encode(file_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def build_task_prompt(mode: str, question: str = "") -> str:
    """集中管理不同圖片任務的 prompt，要求區分可見證據與推論。"""

    if mode == "圖片描述":
        return (
            "請用繁體中文描述圖片。先列出直接可見的物件、人物、文字與場景，"
            "再用『可能的推論』標示不確定解讀；看不清楚時要明確說明。"
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


def get_refusal_reason(response: Any) -> str | None:
    """從 Responses API 的 output/content 找出拒答原因。"""

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
    """只接受已完成且有文字的回應，避免把部分輸出當成正式結果。"""

    refusal = get_refusal_reason(response)
    if refusal:
        raise RuntimeError(f"AI 拒絕處理這張圖片：{refusal}")

    status = getattr(response, "status", None)
    if status == "incomplete":
        details = getattr(response, "incomplete_details", None)
        reason = (
            details.get("reason")
            if isinstance(details, dict)
            else getattr(details, "reason", None)
        )
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


def analyze_image(
    file_bytes: bytes,
    *,
    mode: str,
    question: str = "",
    detail: str = "auto",
    model: str | None = None,
) -> str | dict[str, Any]:
    """驗證圖片後呼叫 Responses API，回傳文字或結構化抽取結果。

    `store=False` 讓此回應不被保存供之後 API 取回，但圖片仍會傳到外部服務處理；
    因此教材仍禁止使用個資、機密、醫療影像或未授權內容。
    """

    if detail not in {"low", "high", "auto"}:
        raise ValueError("detail 只接受 low、high 或 auto。")

    metadata = validate_image(file_bytes)
    prompt = build_task_prompt(mode, question)
    data_url = image_to_data_url(file_bytes, metadata["mime_type"])
    client = create_client()

    request: dict[str, Any] = {
        "model": model or get_secret("OPENAI_MODEL", DEFAULT_MODEL),
        "instructions": (
            "你是謹慎的圖片理解助理。回答使用繁體中文；區分圖片直接證據與推論；"
            "無法確認的文字、數字、人物身分或情境不可猜測。"
        ),
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": data_url,
                        "detail": detail,
                    },
                ],
            }
        ],
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

    response = client.responses.create(**request)
    output_text = require_completed_response(response)
    if mode != "收據／表單抽取":
        return output_text

    try:
        return json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("AI 回傳的結構化資料無法解析，請檢查模型與 schema。") from exc

