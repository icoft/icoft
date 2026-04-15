# Icoft - Icon Forge

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/pypi/v/icoft.svg)](https://pypi.org/project/icoft/)

Icoft is a command-line tool that converts a single image (PNG, JPG, JPEG, WEBP) into app icons for all platforms (Windows, macOS, Linux, Web). It runs on almost all mainstream desktop operating systems, supports AI image recognition, vectorized lossless scaling, and reverse rasterization. In addition, it can perform simple image preprocessing tasks such as cropping, background transparency based on color recognition and AI recognition, and vectorization. Therefore, it can also be used as a cutout tool or image conversion tool.

## Features

- **Icon Generation**: Generate complete app icon sets for Windows, macOS, Linux, and Web
- **Image Cropping**: Remove outer borders by specifying command options, with customizable margins
- **Background Removal**: Simple background transparency algorithm based on background color sampling and specified thresholds, or AI-based background removal using U²-Net
- **Vectorization**: High-quality raster to SVG conversion (based on vector tracing or embedded PNG)
- **Flexible Output**: Generate complete icon sets or single processed images
- **CLI Friendly**: Unix-style composable parameters with Rich terminal output

## Installation

### Install with uv (Recommended)

```bash
# Install uv first (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install icoft to local tool directory
uv tool install icoft

# Or run directly with uvx (no installation required)
uvx icoft --help
```

### Install with pipx

```bash
pipx install icoft
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

### Example 4: CI/CD Pipeline

```yaml
# .github/workflows/release.yml
- name: Generate icons
  run: |
    uvx icoft logo.png resources/icons/
```

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

- **cairosvg** - For rendering SVG to PNG in icon generation (install with `uv sync --extra icon`)

***

**Icoft** = **Icon** + **Forge** 🛠️

Made with ❤️ for developers everywhere
