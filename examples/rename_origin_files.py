"""Rename origin images from '思在 (X).png' to 'cogistXX.png'."""

import re
from pathlib import Path

origin_dir = Path("examples/origin")

if not origin_dir.exists():
    print(f"❌ 目录不存在：{origin_dir}")
    exit(1)

# 查找所有 PNG 文件
png_files = list(origin_dir.glob("*.png"))

print(f"📊 找到 {len(png_files)} 张图片:\n")

# 重命名计数
renamed_count = 0
skipped_count = 0

for png_file in png_files:
    old_name = png_file.name

    # 匹配 "思在 (X).png" 格式
    match = re.match(r"思在\s*\((\d+)\)\.png", old_name)

    if match:
        num = match.group(1)
        # 格式化为两位数：1 -> 01, 10 -> 10
        new_name = f"cogist{num.zfill(2)}.png"
        new_path = origin_dir / new_name

        # 检查新文件名是否已存在
        if new_path.exists():
            print(f"⚠️  跳过：{old_name} → {new_name} (目标文件已存在)")
            skipped_count += 1
        else:
            png_file.rename(new_path)
            print(f"✓ {old_name} → {new_name}")
            renamed_count += 1
    else:
        # 不符合命名模式的文件（如 cogist.png）
        print(f"- {old_name} (无需重命名)")
        skipped_count += 1

print(f"\n{'=' * 60}")
print("✅ 完成!")
print(f"   重命名：{renamed_count} 个")
print(f"   跳过：{skipped_count} 个")
print(f"{'=' * 60}")
