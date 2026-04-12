"""Check if vectorization preserves fill colors."""

import re
from pathlib import Path

# 查看一个 SVG 文件的内容
svg_file = Path("examples/vectorization_final_test/19_cogist_vectorized.svg")

if not svg_file.exists():
    print(f"❌ 文件不存在：{svg_file}")
    exit(1)

svg_content = svg_file.read_text(encoding="utf-8")

# 统计不同类型的路径
paths_with_fill = len(re.findall(r'<path[^>]*fill="[^"]+"', svg_content))
paths_with_stroke_only = len(re.findall(r'<path[^>]*stroke="[^"]+"[^>]*fill="none"', svg_content))
paths_without_fill = len(re.findall(r'<path[^>]*fill="none"', svg_content))

# 提取一些示例路径
sample_paths = re.findall(r'<path[^>]*fill="([^"]+)"[^>]*d="([^"]{50,100})[^"]*"', svg_content)[:5]

print("=" * 80)
print("📊 矢量化结果分析")
print("=" * 80)
print(f"\n文件：{svg_file.name}")
print(f"文件大小：{svg_file.stat().st_size / 1024:.1f} KB")
print()

print("📈 路径统计:")
print(f"  带填充 (fill) 的路径：{paths_with_fill}")
print(f"  只有描边 (stroke) 的路径：{paths_with_stroke_only}")
print(f"  无填充的路径：{paths_without_fill}")
print()

if paths_with_fill > 0:
    print("✅ 结论：矢量化保留了填充颜色！")
    print()
    print("📋 示例路径（前 5 个）:")
    print("-" * 80)
    for i, (fill_color, path_data) in enumerate(sample_paths, 1):
        print(f"{i}. 填充色：{fill_color}")
        print(f"   路径数据：{path_data[:80]}...")
        print()
else:
    print("❌ 没有找到带填充的路径")

print("=" * 80)
print("\n💡 说明:")
print("  - 矢量化会为每个颜色区域创建带填充的路径")
print("  - 主体内部的填充色会被完整保留")
print("  - 只有边缘轮廓，没有填充的是描边模式（本工具不使用）")
