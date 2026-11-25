"""重建第9～11週整合RAG示範；沿用三週生成來源，不安裝套件或呼叫API。"""
import ast
import json
from pathlib import Path
import runpy
import shutil

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "week11/week11_rag_integrated_revised"
TEMPLATE = ROOT / "scripts/templates/week11_integrated_rag.py"


def render_app():
    """共用函式從原建置來源取得；輸出App不需跨週import，可獨立部署。"""
    w9 = runpy.run_path(str(ROOT / "scripts/build_week09_revised.py"))
    w11 = runpy.run_path(str(ROOT / "scripts/build_week11_revised.py"))
    header = '''# 第9～11週整合：看得見每一步的RAG文件問答（完整示範）
# 啟動：進入week11/week11_rag_integrated_revised，執行python -m streamlit run app.py
# 預設離線，0次API；真實模式：文件合批1次，每個新問題1次Embedding＋最多1次Responses。
# 由scripts/build_week11_integrated_rag_revised.py生成；請修改生成來源與template後重建。

import csv
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO, StringIO
import json
import math
import os
from pathlib import Path
import re

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

PACKAGE = Path(__file__).resolve().parent
load_dotenv(PACKAGE / ".env")
st.set_page_config(page_title="看得見每一步的RAG", layout="wide")

# ---------- 1. 第9週：抽取、清理與固定字元切塊（完整參考） ----------
'''
    shared = [w9[name] for name in ("READER", "CLEAN", "CHUNK")]
    shared += ["# ---------- 2. 第10、11週：空白行分段、向量與排名、context與引用 ----------\n"]
    shared += [w11[name] for name in (
        "SPLIT", "DEMO", "COSINE", "RANK", "BUILD_TEACHER", "POLICY", "CHECK_ANSWER", "READ_SETTING")]
    source = header + "\n\n".join(shared) + "\n\n" + TEMPLATE.read_text(encoding="utf-8")
    ast.parse(source)
    return source


def main():
    (PACKAGE / "sample_data").mkdir(parents=True, exist_ok=True)
    (PACKAGE / ".streamlit").mkdir(exist_ok=True)
    (PACKAGE / "app.py").write_text(render_app(), encoding="utf-8")
    for name in ("sample.txt", "sample.csv", "sample.pdf", "sample.docx"):
        shutil.copyfile(ROOT / "week09/sample_tata" / name, PACKAGE / "sample_data" / name)
    # 學生問題清單不包含教師預期答案。
    questions = ["活動地點在哪裡？", "這場讀書交流辦在哪個空間？", "參加費用是多少？", "火星的平均氣溫是多少？"]
    (PACKAGE / "sample_data/questions.json").write_text(
        json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (PACKAGE / "requirements.txt").write_text(
        "# 課程目標組合；已測環境與未測項目見README。\n"
        "streamlit==1.63.0\nopenai==2.49.0\npython-dotenv==1.2.3\npypdf==6.18.1\npython-docx==1.2.0\n",
        encoding="utf-8")
    (PACKAGE / ".env.example").write_text(
        "OPENAI_API_KEY=your_api_key_here\nOPENAI_MODEL=gpt-5.4-mini\n"
        "OPENAI_EMBEDDING_MODEL=text-embedding-3-small\n", encoding="utf-8")
    (PACKAGE / ".streamlit/secrets.example.toml").write_text(
        'OPENAI_API_KEY = "your_api_key_here"\nOPENAI_MODEL = "gpt-5.4-mini"\n'
        'OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"\n', encoding="utf-8")
    (PACKAGE / ".gitignore").write_text(
        ".env\n.env.*\n!.env.example\n.streamlit/secrets.toml\n.venv/\n__pycache__/\n"
        "document_record.json\nintegrated_rag_record*.json\n", encoding="utf-8")
    print("第9～11週整合RAG App已重建；0次API。README與操作講義為手寫檔，不覆蓋。")


if __name__ == "__main__":
    main()
