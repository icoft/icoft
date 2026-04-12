"""Batch test vectorization for all images in origin directory."""

import subprocess
import sys
from pathlib import Path

# 配置
origin_dir = Path("examples/origin")
output_base = Path("examples/vectorization_final_test")
output_base.mkdir(exist_ok=True)

# 查找所有 PNG 文件
png_files = sorted([f for f in origin_dir.glob("*.png") if f.name.startswith("cogist")])

if not png_files:
    print(f"❌ 在 {origin_dir} 目录中没有找到 cogist*.png 文件")
    sys.exit(1)

print(f"📊 找到 {len(png_files)} 张图片:")
for png_file in png_files:
    print(f"  - {png_file.name}")

print("\n🚀 开始批量矢量化测试...")
print(f"📁 输出目录：{output_base}\n")

# 处理每张图片
success_count = 0
error_count = 0

for i, png_file in enumerate(png_files, 1):
    # 为每个文件创建带前缀的临时输出目录，最后重命名
    temp_output_dir = output_base / f"temp_{i:02d}"
    temp_output_dir.mkdir(exist_ok=True)

    print(f"[{i}/{len(png_files)}] 处理：{png_file.name}")

    try:
        # 调用 icoft 程序 - 所有输出到同一个目录
        # --smart-cutout: 启用智能抠图
        # --vectorize: 启用矢量化
        # --output-step=vectorize: 矢量化后停止，不生成图标
        cmd = [
            sys.executable,
            "-m",
            "icoft.cli",
            str(png_file),
            str(temp_output_dir),
            "--smart-cutout",
            "--vectorize",
            "--output-step=vectorize",
            "--cutout-threshold=30",
            "--bg-threshold=10",
            "--margin=5%",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            success_count += 1
            print("  ✓ 成功")

            # 重命名输出文件，添加原始文件名前缀
            svg_file = temp_output_dir / "04_vectorized.svg"
            png_file_output = temp_output_dir / "03_transparent.png"

            if svg_file.exists():
                new_svg_name = f"{i:02d}_{png_file.stem}_vectorized.svg"
                new_svg_path = output_base / new_svg_name
                svg_file.rename(new_svg_path)
                print(f"    → {new_svg_name}")

            if png_file_output.exists():
                new_png_name = f"{i:02d}_{png_file.stem}_transparent.png"
                new_png_path = output_base / new_png_name
                png_file_output.rename(new_png_path)

            # 删除临时目录
            temp_output_dir.rmdir()
        else:
            error_count += 1
            print("  ✗ 失败:")
            if result.stderr:
                print(f"    错误：{result.stderr.strip()}")

        print()

    except subprocess.TimeoutExpired:
        error_count += 1
        print("  ✗ 超时（>60 秒）\n")
    except Exception as e:
        error_count += 1
        print(f"  ✗ 异常：{str(e)}\n")

# 总结
print("=" * 60)
print("📊 测试完成")
print(f"✅ 成功：{success_count}/{len(png_files)}")
print(f"❌ 失败：{error_count}/{len(png_files)}")
print(f"📁 输出目录：{output_base}")
print("=" * 60)

if success_count > 0:
    print("\n💡 查看方法:")
    print("1. 打开各个子目录查看 SVG 文件")
    print("2. 推荐用浏览器或矢量软件（如 Inkscape）查看")
    print("3. 放大检查边缘质量和是否有噪点")
    print("\n示例命令:")
    print(f"   open {output_base}/cogist/04_vectorized.svg")
