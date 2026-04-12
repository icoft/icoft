import sys
from pathlib import Path

sys.path.insert(0, "examples")
from watermark_hybrid import HybridWatermarkRemover

origin_dir = Path("examples/origin")
output_dir = Path("examples/processed_hybrid_v5")

files = ["cogist2.png", "cogst4.png", "cogst7.png"]

print("使用亮度阈值重新处理:\n")

for filename in files:
    img_path = origin_dir / filename
    remover = HybridWatermarkRemover(img_path)
    remover.save(output_dir / filename, threshold=30)
