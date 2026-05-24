"""Quick smoke test: generate a sample PDF."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fortune_calculator import calculate_all
from pdf_generator import generate_pdf

# Test case 1: 炎の龍 candidate
data = calculate_all(1990, 3, 25, "O", "叢雲", "星詠み 花子")
print(f"Type: {data['type_id']} {data['type']['name']}")
print(f"Zodiac: {data['zodiac']['name']}  Chinese: {data['chinese']['name']}  LP: {data['life_path']['number']}")
print(f"Scores: {data['scores']}")

pdf = generate_pdf(data)
with open("output/test_output.pdf", "wb") as f:
    f.write(pdf)
print(f"PDF saved: output/test_output.pdf ({len(pdf):,} bytes)")

# Test case 2: All 4 navigators
for nav in ["叢雲", "ノヴァ", "フレイヤ", "グレイス"]:
    d = calculate_all(1995, 11, 15, "AB", nav, "テスト")
    pdf2 = generate_pdf(d)
    path = f"output/test_{nav}.pdf"
    with open(path, "wb") as f:
        f.write(pdf2)
    print(f"Navigator {nav}: Type {d['type_id']} {d['type']['name']}  -> {path}")

print("\n✦ All tests passed!")
