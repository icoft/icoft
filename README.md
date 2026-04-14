# Icoft - Icon Forge

**From Single Image to Full-Platform App Icons**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/pypi/v/icoft.svg)](https://pypi.org/project/icoft/)

Icoft is a command-line tool that converts a single image (PNG, JPG, JPEG, WEBP) into icons for all platforms (Windows, macOS, Linux, Web), or performs image processing tasks like cropping, background removal, and vectorization.

## Features

- **Icon Generation**: Complete icon sets for Windows, macOS, Linux, and Web
- **Image Cropping**: Manual border removal with customizable margins
- **Background Removal**: Convert solid-color backgrounds to transparent
- **Vectorization**: High-quality PNG to SVG conversion (vector tracing or embedded PNG)
- **Flexible Output**: Generate full icon sets or single processed images
- **CLI Friendly**: Unix-style composable parameters with Rich terminal output

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd icoft

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

## Quick Start

```bash
# Generate full icon set (default)
icoft source_file.png dest_dir/

# Crop and generate icons
icoft -m 10% source_file.png dest_dir/

# Background removal + crop + icons
icoft -m 10% -t source_file.png dest_dir/

# Output single processed PNG
icoft -m 10% source_file.png output.png -o png

# Output single SVG (auto-vectorizes with vector tracing)
icoft source_file.png output.svg -o svg

# Output single SVG with embedded PNG (preserves gradients perfectly)
icoft source_file.png output.svg -s embed -o svg

# Crop + background removal + SVG
icoft -m 10% -t source_file.png output.svg -o svg

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
icoft -m 10% -t source_file.png dest_dir/
```

This performs:

1. Crop borders with 10% margin
2. Make background transparent
3. Generate full icon set

### Example 3: Output Single Processed Image

```bash
# Crop and save as PNG
icoft -m 10% source_file.png cropped.png -o png

# Background removal and save as PNG
icoft -t source_file.png transparent.png -o png

# Crop + background removal + vectorization to SVG
icoft -m 10% -t source_file.png output.svg -o svg
```

### Example 4: CI/CD Pipeline

```yaml
# .github/workflows/release.yml
- name: Generate icons
  run: |
    pip install icoft
    icoft logo.png resources/icons/
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
  -m, --crop-margin        Margin for cropping (e.g., 5%, 10px)
  -t, --transparent        Make background transparent
  -B, --bg-threshold=10    Background threshold (0-255)
  -s, --svg=normal       Enable SVG output: normal (vector tracing) or embed (PNG in SVG)
  -S, --svg-speckle=10   Filter SVG noise (1-100, only for 'normal' mode)
  -P, --svg-precision=6  SVG color precision (1-16, only for 'normal' mode)
  -o, --output=icon        Output format: icon, png, svg
  -p, --platforms=all      Platforms: windows, macos, linux, web
  -V, --version            Show version
  -h, --help               Show help message
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

## Roadmap

### v0.3.2 (Current)

- ✅ Unix-style CLI parameter design
- ✅ Step-by-step processing control
- ✅ Dual-mode SVG generation: `normal` (vector tracing for lossless scaling) and `embed` (PNG embedding for gradient preservation)
- ✅ Smart cutout improvements
- ✅ Edge artifact removal
- ✅ Configuration parameters with auto-enable
- ✅ Single file output mode (-o png/svg)
- ✅ Improved CLI help and error messages
- ✅ AI-based background removal (U²-Net)

### v0.5.0 (Planned)

- [ ] Improve edge detection for better cropping
- [ ] Support more input formats (WEBP, AVIF)
- [ ] Optimize SVG output quality
- [ ] Add progress indicators for long operations
- [ ] Support custom icon sizes
- [ ] Add platform-specific output options
- [ ] Improve error messages

### v1.0.0 (Future)

- [ ] iOS icon optimization
- [ ] Android adaptive icons
- [ ] Full UWP/WinUI 3 support (14 sizes + 3 themes + tiles)
- [ ] CI/CD integration templates
- [ ] GUI application (optional)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI
- Image processing powered by [Pillow](https://pillow.readthedocs.io/) and [OpenCV](https://opencv.org/)
- Terminal output美化 with [Rich](https://rich.readthedocs.io/)

***

**Icoft** = **Icon** + **Forge** 🛠️

Made with ❤️ for developers everywhere
