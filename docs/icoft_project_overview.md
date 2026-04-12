# Icoft 项目概述

## 项目信息

**项目名称**: Icoft (Icon Forge)  
**创建日期**: 2026-04-11  
**项目位置**: `~/projects/icoft`  
**当前版本**: v0.1.0 (规划中)

---

## 项目定位

**一句话介绍**: 从 AI Logo 到全平台应用图标的命令行工具

**目标用户**:
- 程序员/开发者（主要用户）
- 独立开发者
- 小企业主/创业者

**核心价值**: 一键生成全平台图标，让开发者专注产品开发

---

## 背景故事

### 问题来源

1. **AI 生成 Logo 普及**: Midjourney、豆包等 AI 工具可以生成 Logo，但输出是位图
2. **跨平台需求**: 发布应用需要为 Windows、macOS、Linux、Web 生成不同格式的图标
3. **程序员痛点**: 
   - 不会用 PS/GIMP 等专业工具
   - 只有 AI 生成的 PNG（带边框、背景、水印）
   - 需要手动处理多个平台的不同要求

### 解决方案

创建一个命令行工具，专门解决从 AI Logo 到全平台图标的完整工作流：

```
AI 生成的 PNG → Icoft → 所有平台图标
(有边框、背景)     (自动处理)  (直接使用)
```

---

## 功能需求

### P0 - 核心功能（MVP）

#### 1. 图像预处理
- ✅ 自动裁切纯色边框
- ✅ 背景转透明（单色背景）
- ✅ 基础降噪（JPG 压缩痕迹）
- ✅ 可配置 margin（默认 10%）

#### 2. 图标生成
- **Windows**: .ico 文件（16, 32, 48, 64, 128, 256 px）
- **macOS**: .icns 文件 + icon_512x512.png
- **Linux**: PNG 套图 + SVG（可选）
- **Web**: favicon.ico + PWA 图标

#### 3. CLI 接口
```bash
icoft logo.png output/ --margin=10% --platforms=all
```

### P1 - 增强功能

#### 1. 智能预处理
- AI 去背景（rembg，可选依赖）
- 水印检测和简单去除
- 图像质量优化

#### 2. 矢量化
- Potrace 集成（PNG 转 SVG）
- SVG 优化

#### 3. 批量处理
- 多文件同时处理
- YAML 配置文件支持

### P2 - 扩展功能

- iOS 图标优化（圆角、Contents.json）
- Android 自适应图标
- CI/CD 集成（GitHub Actions）
- 质量分析报告

---

## 技术架构

### 技术栈

**核心依赖**:
- Python 3.13+
- Click - CLI 框架
- Pillow - 图像处理
- OpenCV - 降噪、边缘检测
- Rich - 终端美化

**可选依赖**:
- Potrace - 矢量化（PNG 转 SVG）
- CairoSVG - SVG 渲染
- rembg - AI 去背景

### 目录结构（规划）

```
icoft/
├── src/icoft/
│   ├── cli.py              # CLI 入口
│   ├── core/
│   │   ├── processor.py    # 图像预处理
│   │   └── generator.py    # 图标生成
│   ├── platforms/
│   │   ├── windows.py
│   │   ├── macos.py
│   │   ├── linux.py
│   │   └── web.py
│   └── utils/
│       └── image.py
├── tests/
├── docs/
└── examples/
```

---

## 命名由来

**Icoft** = **Icon** + **Forge**

- **Icon**: 图标
- **Forge**: 锻造工坊
- **含义**: 图标的锻造工坊，打造精美图标

**命名特点**:
- ✅ 简短（5 个字母）
- ✅ 易读易记
- ✅ 含义清晰
- ✅ GitHub/PyPI/NPM 无重名
- ✅ 域名可用（icoft.dev / icoft.io）

---

## 实施计划

### 阶段 1: MVP（1-2 周）

**目标**: 可用的核心功能

**Week 1**:
- 项目初始化（uv）
- CLI 框架（Click）
- 基础命令结构
- 图像加载/保存

**Week 2**:
- 自动裁切
- 背景处理
- 各平台图标生成
- 基础测试

**交付**: v0.1.0

### 阶段 2: 增强（2-3 周）

**目标**: 更好的用户体验

- Potrace 集成
- 质量检查系统
- 批量处理
- 配置文件
- 完整文档

**交付**: v0.2.0

### 阶段 3: 扩展（可选）

- AI 去背景
- 平台优化
- CI/CD 集成
- GUI 应用（可选）

**交付**: v1.0.0

---

## 典型使用场景

### 场景 1: AI 生成 Logo

```bash
# 1. 用豆包/Midjourney 生成 Logo
# 2. 保存为 logo.png（有白色边框和背景）
# 3. 一键生成所有图标
icoft logo.png icons/

# 4. 输出:
#    icons/windows/app.ico
#    icons/macos/app.icns
#    icons/linux/hicolor/...
#    icons/web/favicon.ico
```

### 场景 2: Python 包发布

```bash
# 在 pyproject.toml 中配置
[tool.icoft]
source = "logo.png"
output = "package/icons/"

# 构建时自动生成
icoft --config=pyproject.toml
```

### 场景 3: CI/CD

```yaml
# .github/workflows/release.yml
- name: Generate icons
  run: |
    pip install icoft
    icoft logo.png resources/icons/
```

---

## 与现有工具对比

| 工具 | 优势 | 劣势 |
|------|------|------|
| **在线工具** | 本地运行、隐私安全、批量处理 | 需要安装 |
| **专业工具** | 命令行友好、自动化 | 功能相对单一 |
| **其他 CLI** | 针对 AI Logo 优化、完整工作流 | 新兴工具 |

**差异化**:
- 专门针对 AI 生成的 Logo
- 一键搞定所有平台
- 程序员友好（CLI、CI/CD）
- 开源免费

---

## 商业模式（未来）

### 阶段 1: 开源积累用户
- 完全开源免费
- 建立口碑
- 快速迭代

### 阶段 2: 增值服务
- 核心功能免费
- AI 功能付费（去背景、超分辨率）
- 批量处理付费

### 阶段 3: 商业化
- 专业版（GUI、高级功能）
- API 服务（AI 处理）
- 企业定制

---

## 成功标准

### 短期（v0.1.0）
- 能处理 AI 生成的 PNG
- 生成所有平台基础格式
- CLI 可用

### 中期（v0.2.0）
- 质量检查系统
- 批量处理
- 完整文档

### 长期（v1.0.0）
- 10+ 真实项目使用
- GitHub 100+ stars
- 稳定的用户群

---

## 相关链接

- **项目位置**: `~/projects/icoft`
- **GitHub**: （待创建）
- **PyPI**: （待发布）
- **文档**: `~/projects/icoft/docs/`

---

## 待办事项

- [x] 项目命名（icoft）
- [x] 名称可用性检查
- [x] 创建项目（uv init）
- [x] 项目文档（本文档）
- [ ] 实施计划文档
- [ ] 技术设计文档
- [ ] 实现 CLI 框架
- [ ] 实现预处理
- [ ] 实现图标生成
- [ ] 编写测试
- [ ] 发布 v0.1.0

---

*文档创建日期：2026-04-11*  
*最后更新：2026-04-11*
