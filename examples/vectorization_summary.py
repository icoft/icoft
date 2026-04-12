"""Generate summary report for batch vectorization test."""

from pathlib import Path

output_base = Path("examples/vectorization_final_test")

# 收集所有结果
results = []
for svg_dir in output_base.iterdir():
    if svg_dir.is_dir():
        svg_file = svg_dir / "04_vectorized.svg"
        png_file = svg_dir / "03_transparent.png"

        if svg_file.exists():
            file_size = svg_file.stat().st_size
            results.append(
                {
                    "name": svg_dir.name,
                    "svg_size": file_size,
                    "svg_path": svg_file,
                    "png_path": png_file if png_file.exists() else None,
                }
            )

# 按文件名排序
results.sort(key=lambda x: x["name"])

# 生成报告
print("=" * 80)
print("📊 矢量化测试结果汇总")
print("=" * 80)
print(f"\n📁 输出目录：{output_base}")
print(f"📈 成功数量：{len(results)}/21")
print()

# 按文件大小分类
small = [r for r in results if r["svg_size"] < 100_000]  # < 100KB
medium = [r for r in results if 100_000 <= r["svg_size"] < 500_000]  # 100KB - 500KB
large = [r for r in results if r["svg_size"] >= 500_000]  # >= 500KB

print("📊 文件大小分布:")
print(f"  小型 (< 100KB):   {len(small)} 张")
print(f"  中型 (100-500KB): {len(medium)} 张")
print(f"  大型 (> 500KB):   {len(large)} 张")
print()

# 详细列表
print("📋 详细列表:")
print("-" * 80)
print(f"{'文件名':<30} {'SVG 大小':>12} {'状态':<10}")
print("-" * 80)

for r in results:
    size_str = f"{r['svg_size'] / 1024:.1f} KB"
    if r["svg_size"] < 100_000:
        status = "✅ 优秀"
    elif r["svg_size"] < 500_000:
        status = "✅ 良好"
    else:
        status = "⚠️  较大"

    print(f"{r['name']:<30} {size_str:>12} {status:<10}")

print("-" * 80)
print()

# 推荐查看的文件
print("💡 推荐查看的文件（不同复杂度代表）:")
print()

# 从小到大各选几个代表
if small:
    rep = small[len(small) // 2]
    print(f"  小型代表：{rep['name']} ({rep['svg_size'] / 1024:.1f} KB)")
    print(f"    查看：open {rep['svg_path']}")
    print()

if medium:
    rep = medium[len(medium) // 2]
    print(f"  中型代表：{rep['name']} ({rep['svg_size'] / 1024:.1f} KB)")
    print(f"    查看：open {rep['svg_path']}")
    print()

if large:
    rep = large[0]
    print(f"  大型代表：{rep['name']} ({rep['svg_size'] / 1024:.1f} KB)")
    print(f"    查看：open {rep['svg_path']}")
    print()

# 统计信息
total_size = sum(r["svg_size"] for r in results)
avg_size = total_size / len(results)
print("📊 统计信息:")
print(f"  总大小：{total_size / 1024 / 1024:.2f} MB")
print(f"  平均大小：{avg_size / 1024:.1f} KB")
print(f"  最小：{min(r['svg_size'] for r in results) / 1024:.1f} KB")
print(f"  最大：{max(r['svg_size'] for r in results) / 1024:.1f} KB")
print()

# 下一步建议
print("=" * 80)
print("💡 下一步建议:")
print("=" * 80)
print()
print("1. 查看不同大小的 SVG 文件，检查边缘质量")
print("2. 重点关注:")
print("   - 边缘是否平滑（放大查看）")
print("   - 是否有黑色颗粒或噪点")
print("   - 颜色分层是否正确")
print("3. 如果发现问题，调整参数后重新测试")
print()
print("参数调整建议:")
print("  - 边缘锯齿：调整 corner_threshold, length_threshold")
print("  - 黑色颗粒：增加 filter_speckle")
print("  - 颜色失真：调整 color_precision")
print()
