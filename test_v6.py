import sys
from pathlib import Path

sys.path.insert(0, "examples")
from watermark_hybrid import HybridWatermarkRemover

origin_dir = Path("examples/origin")
output_dir = Path("examples/processed_hybrid_v6")

files = ["cogist2.png", "cogst4.png", "cogst7.png"]

print("手动测试保存:\n")

for filename in files:
    img_path = origin_dir / filename
    print(f"处理 {filename}...")

    remover = HybridWatermarkRemover(img_path)
    result = remover.remove(threshold=30)

    output_path = output_dir / filename
    print(f"  保存到 {output_path}...")
    result.save(output_path, "PNG")
    print("  ✓ 已保存")

print("\n完成！")
