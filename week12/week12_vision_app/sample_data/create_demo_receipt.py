"""產生完全虛構、無個資的課堂收據圖片。"""

from pathlib import Path

from PIL import Image, ImageDraw


OUTPUT = Path(__file__).with_name("demo_receipt.png")

image = Image.new("RGB", (900, 1100), "white")
draw = ImageDraw.Draw(image)
lines = [
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

y = 100
for line in lines:
    draw.text((90, y), line, fill="black", font_size=32)
    y += 90

image.save(OUTPUT, format="PNG")
print(f"Created {OUTPUT}")

