# icoft - AI-Powered CLI Icon Generator & Vector Scaler

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/pypi/v/icoft.svg)](https://pypi.org/project/icoft/)

Icoft is a command-line tool that converts a single image (PNG, JPG, JPEG, WEBP) into app icons for all platforms (Windows, macOS, Linux, Web). It runs on almost all mainstream desktop operating systems, supports AI image recognition, vectorized lossless scaling, and reverse rasterization. In addition, it can perform simple image preprocessing tasks such as cropping, background transparency based on color recognition and AI recognition, and vectorization. Therefore, it can also be used as a cutout tool or image conversion tool.

## Features

- **Icon Generation**: Generate complete app icon sets for Windows, macOS, Linux, and Web
- **Image Cropping**: Remove outer borders by specifying command options, with customizable margins
- **Background Removal**: Simple background transparency algorithm based on background color sampling and specified thresholds, or AI-based background removal using U²-Net
- **Vectorization**: High-quality raster to SVG conversion
  - `normal` mode: True vector tracing for infinite scaling (best for simple graphics)
  - `embed` mode: PNG embedded in SVG wrapper (preserves gradients/photos, NOT scalable)
  - Optional: Install `cairosvg` for high-quality SVG to PNG rendering in icon generation
- **Flexible Output**: Generate complete icon sets or single processed images
- **CLI Friendly**: Unix-style composable parameters with Rich terminal output

## Background Removal & Vectorization Examples

The following examples demonstrate different background removal and vectorization methods using a logo with gradient colors on white background. All examples are displayed on a neutral gray background (`#808080`) to show transparent areas.

| Original | Color-based (-b 70) | AI-based (-a) | Vectorized (-s normal) | Embedded (-s embed) |
|:---:|:---:|:---:|:---:|:---:|
| <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/icoft02.png" width="100"> | <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/icoft02-b70.png" width="100"> | <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/icoft02-a.png" width="100"> | <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/icoft02-b70-S0-P16.svg" width="100"> | <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/icoft02-b70-embed.svg" width="100"> |
| White background with gradient logo | Clean removal of simple background | Cannot handle center cutout | Gradient banding due to SVG limitations | Perfect gradient, NOT scalable |

### Example 2: Complex Background (Low Contrast, Shadows, Gradients)

This example shows a logo with low contrast between foreground and background, with shadows and gradient effects:

| Original | Color-based (-b 30) | AI-based (-a) | Vectorized (-s normal) | Embedded (-s embed) |
|:---:|:---:|:---:|:---:|:---:|
| <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/cogist05.png" width="100"> | <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/cogist05-b30.png" width="100"> | <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/cogist05-a.png" width="100"> | <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/cogist05-a-S0-P16.svg" width="100"> | <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/cogist05-a-embed.svg" width="100"> |
| Low contrast, shadows, gradients | Cannot preserve foreground | Removes shadows, clear edges | Gradient banding | Perfect gradient, NOT scalable |

### Example 3: High Contrast Simple Geometry

This example shows a high-contrast simple geometric shape, ideal for color-based background removal:

| Original | Color-based (-b 100) | AI-based (-a) | Vectorized (-s normal) | Embedded (-s embed) |
|:---:|:---:|:---:|:---:|:---:|
| <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/cogist07.png" width="100"> | <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/cogist07-b100.png" width="100"> | <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/cogist07-a.png" width="100"> | <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/cogist07-b100-normal.svg" width="100"> | <img src="https://raw.githubusercontent.com/icoft/icoft/main/docs/images/cogist07-b100-embed.svg" width="100"> |
| High contrast simple geometry | Perfect removal | Cannot handle center cutout | Perfect vectorization | Perfect, NOT scalable |

> **Note**: All examples above are displayed on a neutral gray background (`#808080`) to show transparent areas.

## Installation

### Install with uv (Recommended)

```bash
# Install uv first (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install icoft to local tool directory
uv tool install icoft

# Or run directly with uvx (no installation required)
uvx icoft --help

# Install with optional cairosvg for high-quality SVG rendering
uv tool install icoft --with cairosvg
```

### Install with pipx

```bash
pipx install icoft

# Install with optional cairosvg
pipx install icoft[cairosvg]
```

### Install with pip

```bash
pip install icoft

# Install with optional cairosvg
pip install icoft[cairosvg]
```

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd icoft

# Install with uv
uv sync

# Or install with pip
pip install -e .
```

## Quick Start

```bash
# Generate full icon set (default)
icoft source_file.png dest_dir/

# Crop and generate icons
icoft -c 10% source_file.png dest_dir/

# AI background removal + generate icons
icoft -a source_file.png dest_dir/

# Color threshold background removal (threshold 30)
icoft -b 30 source_file.png dest_dir/

# AI + color threshold refinement + generate icons
icoft -a -b 30 source_file.png dest_dir/

# Output single processed PNG
icoft -c 10% -a source_file.png output.png -o png

# Output single SVG (vector tracing)
icoft source_file.png output.svg -o svg

# Output single SVG with embedded PNG (preserves gradients perfectly)
icoft source_file.png output.svg -s embed -o svg

# Crop + AI background removal + output SVG
icoft -c 10% -a source_file.png output.svg -o svg

# Generate icons for specific platforms only
icoft source_file.png icons/ -p windows,web
icoft source_file.png icons/ -p macos,linux
```

## Usage Examples

### Example 1: Generate Full Icon Set

```bash
# Generate icons for all platforms
icoft source_file.png dest_dir/
```

Output structure:

```
dest_dir/
├── windows/
│   └── app.ico                              # Windows ICO (8 sizes: 16-256px)
├── macos/
│   ├── app.icns                             # macOS ICNS container
│   ├── icon_16x16.png                       # 16×16 @1x
│   ├── icon_16x16@2x.png                    # 16×16 @2x (32×32)
│   ├── icon_32x32.png                       # 32×32 @1x
│   ├── icon_32x32@2x.png                    # 32×32 @2x (64×64)
│   ├── icon_128x128.png                     # 128×128 @1x
│   ├── icon_128x128@2x.png                  # 128×128 @2x (256×256)
│   ├── icon_256x256.png                     # 256×256 @1x
│   ├── icon_256x256@2x.png                  # 256×256 @2x (512×512)
│   ├── icon_512x512.png                     # 512×512 @1x
│   └── icon_512x512@2x.png                  # 512×512 @2x (1024×1024)
├── linux/
│   └── hicolor/
│       ├── 16x16/apps/app.png
│       ├── 22x22/apps/app.png
│       ├── 24x24/apps/app.png
│       ├── 32x32/apps/app.png
│       ├── 48x48/apps/app.png
│       ├── 64x64/apps/app.png
│       ├── 128x128/apps/app.png
│       ├── 256x256/apps/app.png
│       └── scalable/apps/app.svg
└── web/
    ├── favicon.ico                          # Browser favicon
    ├── apple-touch-icon.png                 # iOS home screen icon
    ├── icon-192x192.png                     # PWA icon
    ├── icon-512x512.png                     # PWA icon
    └── manifest.json                        # PWA manifest
```

### Example 2: Crop and Remove Background

```bash
# For images with solid-color borders and backgrounds
icoft -c 10% -b 30 source_file.png dest_dir/
```

This performs:

1. Crop borders with 10% margin
2. Make background transparent using color threshold 30
3. Generate full icon set

### Example 3: Output Single Processed Image

```bash
# Crop and save as PNG
icoft -c 10% source_file.png cropped.png -o png

# AI background removal and save as PNG
icoft -a source_file.png transparent.png -o png

# Crop + AI background removal + color refinement + save as PNG
icoft -c 10% -a -b 30 source_file.png output.png -o png

# Crop + AI background removal + vectorization to SVG
icoft -c 10% -a source_file.png output.svg -o svg
```

### Example 4: CI/CD Pipeline Integration

Icoft is designed for seamless CI/CD integration. Generate icons automatically on every release:

**GitHub Actions Example:**

```yaml
# .github/workflows/release.yml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Generate icons from logo
        run: |
          uvx icoft assets/logo.png src/resources/icons/ -a -c 5%

      - name: Build application
        run: |
          # Your build commands here
          # Icons are now ready in src/resources/icons/
```

**Key Benefits for CI/CD:**

- **Zero Configuration**: No config files needed, everything via CLI arguments
- **Single Source of Truth**: One logo file generates all platform icons
- **Consistent Output**: Same icons across all builds and team members
- **Fast Execution**: Optimized for CI environments with minimal dependencies
- **Version Controlled**: Logo changes trigger automatic icon regeneration

**Popular Use Cases:**

- **Electron Apps**: Generate icons before `electron-builder`
- **Tauri Apps**: Build icons before `tauri build`
- **Flutter Apps**: Create icons before `flutter build`
- **Python GUI Apps**: Generate icons before PyInstaller/py2app
- **Web Apps**: Create favicons and PWA icons on deploy

## Command-Line Options

```
Usage: icoft [OPTIONS] SOURCE_FILE DEST_DIR
       icoft [OPTIONS] SOURCE_FILE OUTPUT_FILE -o FORMAT

Icoft - From Single Image to Full-Platform App Icons.

Output Modes:
  DEST_DIR              Generate full icon set for selected platforms
  OUTPUT_FILE -o png    Save processed image as single PNG
  OUTPUT_FILE -o svg    Save processed image as single SVG (auto-vectorizes)

Options:
  -c, --crop-margin TEXT      Margin for cropping (e.g., 5%, 10px)
  -a, --use-ai-bg             Use AI for background removal (U²-Net)
  -b, --bg-threshold INTEGER  Enable color-based background removal with threshold (0-255, default: 10 when enabled)
  -s, --svg [normal|embed]    Enable SVG output: normal (vector tracing) or embed (PNG in SVG)
  -S, --svg-speckle INTEGER   Filter SVG noise (1-100, default: 10, only for 'normal' mode)
  -P, --svg-precision INTEGER SVG color precision (1-16, default: 6, only for normal mode)
  -o, --output [icon|png|svg] Output format: icon (directory), png (single file), svg (single file)
  -p, --platforms TEXT        Platforms: windows, macos, linux, web (default: all)
  -V, --version               Show version
  -h, --help                  Show help message
```

## Development

### Setup Development Environment

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest tests/ -v

# Run linter
uv run ruff check .

# Run formatter
uv run ruff format .

# Run type checker
uv run pyright .
```

### Project Structure

```
icoft/
├── src/icoft/
│   ├── cli.py              # CLI entry point
│   ├── core/
│   │   ├── processor.py    # Image preprocessing
│   │   └── generator.py    # Icon generation
│   └── platforms/          # Platform-specific modules
├── tests/
│   ├── test_cli.py
│   ├── test_processor.py
│   └── test_generator.py
├── docs/
└── examples/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Dependencies

### Core Dependencies

- **[Click](https://click.palletsprojects.com/)** (>=8.1.0) - CLI framework
- **[Pillow](https://pillow.readthedocs.io/)** (>=10.0.0) - Image processing
- **[NumPy](https://numpy.org/)** (>=1.24.0) - Numerical computing
- **[Rich](https://rich.readthedocs.io/)** (>=13.0.0) - Terminal output
- **[vtracer](https://github.com/visioncortex/vtracer)** (>=0.6.0) - Vector tracing
- **[ONNX Runtime](https://onnxruntime.ai/)** (>=1.19.0) - AI inference

### Optional Dependencies

- **cairosvg** - For high-quality SVG to PNG rendering in icon generation
  - Install with pip: `pip install icoft[cairosvg]`
  - Install with uv: `uv tool install icoft --with cairosvg`

***

**Icoft** = **Icon** + **Forge** 🛠️

Made with ❤️ for developers everywhere
