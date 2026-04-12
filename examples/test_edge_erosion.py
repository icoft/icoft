"""Test optimized edge erosion in smart cutout."""

from pathlib import Path

from icoft.core.processor import ImageProcessor

# 测试一张图
img_path = "examples/origin/cogist.png"
output_dir = Path("examples/edge_erosion_test")
output_dir.mkdir(exist_ok=True)

print("测试优化后的边缘腐蚀效果:\n")

processor = ImageProcessor(img_path)
processor.crop_borders(margin="5%")
processor.smart_cutout(threshold=30)
processor.make_background_transparent()

# 保存结果
output_path = output_dir / "01_cutout_eroded.png"
processor.save(output_path)

print(f"✓ 抠图完成（已腐蚀 2px）: {output_path}")
print("\n查看方法:")
print("1. 打开图片，放大边缘")
print("2. 检查是否还有深色像素残留")
print("3. 对比之前的效果")
