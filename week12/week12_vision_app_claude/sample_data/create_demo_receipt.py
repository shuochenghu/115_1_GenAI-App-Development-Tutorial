"""產生完全虛構、無個資的課堂測試圖片（Claude 版）。

會建立兩張圖：
- demo_receipt.png：清楚的虛構收據，測試結構化抽取。
- demo_receipt_blurry.png：同一張收據加上模糊與旋轉，示範 Vision 看不清楚時
  應該回 null / warnings，而不是猜答案。

生成的 PNG 已列入 .gitignore，不提交到 repo。
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


OUTPUT_DIR = Path(__file__).resolve().parent
CLEAR_PATH = OUTPUT_DIR / "demo_receipt.png"
BLURRY_PATH = OUTPUT_DIR / "demo_receipt_blurry.png"

LINES = [
    "DEMO CAFE - CLASSROOM FIXTURE",
    "Date: 2026-09-16",
    "--------------------------------",
    "Coffee          2 x 80      160",
    "Sandwich        1 x 95       95",
    "Notebook        1 x 45       45",
    "--------------------------------",
    "TOTAL TWD                    300",
    "This is fictional test data.",
]


def draw_receipt() -> Image.Image:
    image = Image.new("RGB", (900, 1100), "white")
    draw = ImageDraw.Draw(image)
    y = 100
    for line in LINES:
        draw.text((90, y), line, fill="black", font_size=32)
        y += 90
    return image


def make_blurry(image: Image.Image) -> Image.Image:
    rotated = image.rotate(7, expand=True, fillcolor="white")
    return rotated.filter(ImageFilter.GaussianBlur(radius=3))


if __name__ == "__main__":
    receipt = draw_receipt()
    receipt.save(CLEAR_PATH, format="PNG")
    make_blurry(receipt).save(BLURRY_PATH, format="PNG")
    print(f"Created {CLEAR_PATH}")
    print(f"Created {BLURRY_PATH}")
